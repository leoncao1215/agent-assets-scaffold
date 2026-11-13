#!/usr/bin/env python3
"""Apply a reviewed regular-file plan under process-held physical-scope locks.

No network, package installation, arbitrary commands, directory deletion or
automatic rollback. Python 3.10+ standard library; Windows and POSIX local locks.
See references/shared-skills.md for plan format, ownership and migration gates.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import time
import uuid


class Busy(RuntimeError):
    pass


class Drift(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plain_path(value: str | Path) -> Path:
    """Reject indirection before resolve; normalize equivalent local spellings."""
    path = Path(value)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Paths must be absolute without parent traversal.')
    if os.name == 'nt' and (str(path).startswith('\\\\') or ':' in str(path)[2:]):
        raise ValueError('UNC/device paths and alternate streams are unsupported.')
    if os.name == 'nt':
        for component in path.parts[1:]:
            stem = component.split('.')[0].rstrip(' ').upper()
            if (component.endswith(('.', ' ')) or
                    any(ord(char) < 32 or char in '<>"|?*' for char in component) or
                    stem in {'CON', 'PRN', 'AUX', 'NUL'} or
                    re.fullmatch(r'(COM|LPT)[1-9¹²³]', stem)):
                raise ValueError('Ambiguous or reserved Windows path component.')
    for candidate in [*reversed(path.parents), path]:
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Unexpected symlink/junction/reparse point: ' + str(candidate))
    return path.resolve(strict=False)


def identity(path: Path) -> str:
    return os.path.normcase(str(plain_path(path)))


def within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def file_hash(path: Path) -> str | None:
    path = plain_path(path)
    try:
        info = path.stat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('Expected an ordinary single-link file: ' + str(path))
    return sha256(path.read_bytes())


def entries(path: Path) -> list[str] | None:
    path = plain_path(path)
    if not path.exists():
        return None
    if not path.is_dir():
        raise ValueError('Expected a directory: ' + str(path))
    # Membership only, never recursively read unselected children.
    return sorted(child.name for child in path.iterdir())


class ScopeLocks:
    """All cooperating writers use the same state directory and scope roots.

    Windows: CreateFileW with share mode zero, held open for the entire write.
    POSIX: flock on a permanent lock inode. Never unlink lock files, even on crash.
    """

    def __init__(self, scopes: list[Path], state_dir: Path, timeout: float = 10):
        if not math.isfinite(timeout) or not 0 <= timeout <= 60:
            raise ValueError('Lock timeout must be between 0 and 60 seconds.')
        self.scopes = sorted({identity(p) for p in scopes})
        self.lock_dir = plain_path(state_dir) / 'locks'
        self.timeout = timeout
        self.handles: list[object] = []

    def __enter__(self):
        plain_path(self.lock_dir).mkdir(parents=True, exist_ok=True, mode=0o700)
        deadline = time.monotonic() + self.timeout
        try:
            for scope in self.scopes:
                path = plain_path(self.lock_dir / (sha256(scope.encode('utf-8')) + '.lock'))
                while True:
                    try:
                        handle = self._acquire(path)
                        self.handles.append(handle)
                        break
                    except Busy:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise Busy('Physical scope is busy: ' + scope)
                        time.sleep(min(0.05, remaining))
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    @staticmethod
    def _acquire(path: Path):
        if os.name == 'nt':
            from ctypes import wintypes
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            create = kernel.CreateFileW
            create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                               ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                               wintypes.HANDLE]
            create.restype = wintypes.HANDLE
            # GENERIC_READ|WRITE, no sharing, OPEN_ALWAYS, normal attributes.
            handle = create(str(path), 0xC0000000, 0, None, 4, 0x80, None)
            if handle == wintypes.HANDLE(-1).value:
                code = ctypes.get_last_error()
                if code in (32, 33):
                    raise Busy(str(path))
                raise ctypes.WinError(code)
            close = kernel.CloseHandle
            close.argtypes = [wintypes.HANDLE]
            close.restype = wintypes.BOOL
            return (handle, close)
        import fcntl
        flags = os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0)
        fd = os.open(path, flags, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                raise Busy(str(path)) from exc
            raise
        return fd

    def __exit__(self, *_):
        for handle in reversed(self.handles):
            if os.name == 'nt':
                handle[1](handle[0])
            else:
                os.close(handle)
        self.handles.clear()


def exact_fields(obj, names: set[str]):
    if not isinstance(obj, dict) or set(obj) != names:
        raise ValueError('Unexpected or missing plan fields.')


def valid_hash(value, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Expected lowercase SHA-256.')


def parse_plan(raw: bytes, state_dir: Path):
    def unique_keys(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError('Duplicate JSON key.')
            obj[key] = value
        return obj
    plan = json.loads(raw, object_pairs_hook=unique_keys)
    exact_fields(plan, {'formatVersion', 'operationId', 'roots', 'directories', 'files'})
    if type(plan['formatVersion']) is not int or plan['formatVersion'] != 1:
        raise ValueError('Unsupported plan version.')
    if not isinstance(plan['operationId'], str) or str(uuid.UUID(plan['operationId'])) != plan['operationId']:
        raise ValueError('operationId must be a canonical UUID.')
    if not isinstance(plan['roots'], list) or not plan['roots']:
        raise ValueError('A physical root selection is required.')
    roots = [plain_path(p) for p in plan['roots']]
    if len({identity(p) for p in roots}) != len(roots):
        raise ValueError('Duplicate roots.')
    for root in roots:
        if any(part.lower() in {'.git', '.system'} for part in root.parts):
            raise ValueError('Vendor/system and Git metadata cannot be installation roots.')
        if root == Path(root.anchor) or root == Path.home().resolve():
            raise ValueError('Use a specific physical installation root, not home or a drive.')
        if within(state_dir, root) or within(root, state_dir):
            raise ValueError('Installation roots and local state must be separate.')
        if any(root != other and within(root, other) for other in roots):
            raise ValueError('Overlapping roots are ambiguous.')
        if root.exists() and not root.is_dir():
            raise ValueError('A root must be a directory.')
        if os.name == 'nt':
            from ctypes import wintypes
            drive_type = ctypes.WinDLL('kernel32').GetDriveTypeW
            drive_type.argtypes = [wintypes.LPCWSTR]
            drive_type.restype = wintypes.UINT
            if drive_type(root.anchor) == 4:
                raise ValueError('Network drives are unsupported.')
    if not isinstance(plan['files'], list) or not plan['files']:
        raise ValueError('No file operations; report no-op without calling apply.')
    if not isinstance(plan['directories'], list):
        raise ValueError('Directory baselines must be an array.')

    def owner(path):
        for root in roots:
            if path != root and within(path, root):
                if any(part.lower() in {'.git', '.system'} for part in path.relative_to(root).parts):
                    raise ValueError('Vendor/system and Git metadata are not managed targets.')
                return root
        if path == state_dir / 'registry.json' or within(path, state_dir / 'installations'):
            if path.suffix != '.json':
                raise ValueError('Local installation metadata must be JSON.')
            return state_dir
        raise ValueError('Target is outside selected roots/local installation metadata.')

    ops = []
    seen = set()
    scopes = list(roots)
    for item in plan['files']:
        if not isinstance(item, dict):
            raise ValueError('File operation must be an object.')
        required = {'action', 'target', 'beforeSha256', 'source', 'sourceSha256'}
        if not required.issubset(item) or set(item) - required - {'beforeMode', 'afterMode'}:
            raise ValueError('Unexpected or missing file operation fields.')
        for field in ('beforeMode', 'afterMode'):
            if field in item and (type(item[field]) is not int or not 0 <= item[field] <= 0o777):
                raise ValueError('File modes must be ordinary permission bits, without special bits.')
        if os.name == 'nt' and ('beforeMode' in item or 'afterMode' in item):
            raise ValueError('Explicit POSIX modes are unsupported on Windows.')
        path = plain_path(item['target'])
        root = owner(path)
        key = identity(path)
        if key in seen:
            raise ValueError('Duplicate physical target.')
        seen.add(key)
        valid_hash(item['beforeSha256'], nullable=True)
        if item['action'] == 'write':
            valid_hash(item['sourceSha256'])
            source = plain_path(item['source'])
        elif item['action'] == 'retire':
            if item['source'] is not None or item['sourceSha256'] is not None or item['beforeSha256'] is None:
                raise ValueError('Retirement requires an existing baseline and no source.')
            if root == state_dir:
                raise ValueError('Installation metadata cannot be retired by this helper.')
            source = None
            if 'afterMode' in item:
                raise ValueError('Retirement cannot set a target mode.')
        else:
            raise ValueError('Unknown file action.')
        if item['beforeSha256'] is None and 'beforeMode' in item:
            raise ValueError('Absent targets have no beforeMode.')
        if os.name != 'nt':
            if item['beforeSha256'] is not None and 'beforeMode' not in item:
                raise ValueError('POSIX existing targets require beforeMode.')
            if item['action'] == 'write' and 'afterMode' not in item:
                raise ValueError('POSIX writes require an approved afterMode.')
        if root == state_dir:
            scopes.append(state_dir / 'metadata')
        ops.append(dict(item, path=path, root=root, sourcePath=source))

    directories = {}
    for item in plan['directories']:
        exact_fields(item, {'path', 'entries'})
        path = plain_path(item['path'])
        if not any(within(path, root) for root in roots) and not within(path, state_dir / 'installations'):
            raise ValueError('Directory baseline is outside installation scope.')
        baseline = item['entries']
        if baseline is not None and (not isinstance(baseline, list) or
                any(not isinstance(n, str) or n in {'', '.', '..'} or '/' in n or '\\' in n for n in baseline) or
                len(set(baseline)) != len(baseline)):
            raise ValueError('Expected unique immediate directory entry names or null.')
        key = identity(path)
        if key in directories:
            raise ValueError('Duplicate directory baseline.')
        directories[key] = (path, sorted(baseline) if baseline is not None else None)
    for op in ops:
        # State directories also contain locks/receipts, so only file baselines
        # are required there. Their metadata writes share a separate fixed lock.
        if op['root'] == state_dir:
            continue
        parent = op['path'].parent
        while within(parent, op['root']):
            if identity(parent) not in directories:
                raise ValueError('Missing parent membership baseline: ' + str(parent))
            if parent == op['root']:
                break
            parent = parent.parent
    return plan, ops, directories, scopes


def atomic_bytes(path: Path, data: bytes, mode: int | None = None):
    path = plain_path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.parent / ('.asset-sync-' + str(uuid.uuid4()) + '.tmp')
    try:
        with temporary.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        if os.name == 'nt' and path.exists():
            from ctypes import wintypes
            replace = ctypes.WinDLL('kernel32', use_last_error=True).ReplaceFileW
            replace.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
                                wintypes.DWORD, ctypes.c_void_p, ctypes.c_void_p]
            replace.restype = wintypes.BOOL
            # Preserve the existing file's DACL; do not ignore metadata merge errors.
            if not replace(str(path), str(temporary), None, 0, None, None):
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            if path.exists():
                shutil.copystat(path, temporary, follow_symlinks=False)
            if mode is not None:
                os.chmod(temporary, mode)
            os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def apply_plan(plan_path: Path, expected_plan_sha: str, state_dir: Path, timeout=10):
    state_dir = plain_path(state_dir)
    valid_hash(expected_plan_sha)
    raw = plain_path(plan_path).read_bytes()
    if sha256(raw) != expected_plan_sha:
        raise Drift('Plan changed after preview.')
    plan, ops, directories, scopes = parse_plan(raw, state_dir)
    with ScopeLocks(scopes, state_dir, timeout):
        # Validation before lock acquisition is not the authoritative baseline.
        if sha256(plain_path(plan_path).read_bytes()) != expected_plan_sha:
            raise Drift('Plan changed while waiting for locks.')
        for path, baseline in directories.values():
            if entries(path) != baseline:
                raise Drift('Directory membership changed: ' + str(path))
        payloads = []
        before_bytes = []
        before_modes = []
        after_modes = []
        for op in ops:
            if file_hash(op['path']) != op['beforeSha256']:
                raise Drift('Target baseline changed: ' + str(op['path']))
            before_bytes.append(op['path'].read_bytes() if op['beforeSha256'] else None)
            old_mode = stat.S_IMODE(op['path'].stat().st_mode) if op['beforeSha256'] else None
            if 'beforeMode' in op and old_mode != op['beforeMode']:
                raise Drift('Target permission mode changed: ' + str(op['path']))
            before_modes.append(old_mode)
            if op['sourcePath'] is not None:
                file_hash(op['sourcePath'])  # type/indirection validation
                data = op['sourcePath'].read_bytes()
                if sha256(data) != op['sourceSha256']:
                    raise Drift('Source changed: ' + str(op['sourcePath']))
                if op['root'] == state_dir and not isinstance(json.loads(data), dict):
                    raise ValueError('Installation metadata must be a JSON object.')
                payloads.append(data)
                source_mode = stat.S_IMODE(op['sourcePath'].stat().st_mode) & 0o777
                after_modes.append(op.get('afterMode', old_mode if old_mode is not None else source_mode))
            else:
                payloads.append(None)
                after_modes.append(None)
        run_dir = plain_path(state_dir / 'runs' / plan['operationId'])
        run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
        receipt_path = run_dir / 'receipt.json'
        receipt = {'formatVersion': 1, 'operationId': plan['operationId'],
                   'planSha256': expected_plan_sha, 'status': 'preparing',
                   'static': 'not-run', 'runtime': 'not-run', 'files': []}

        def save():
            atomic_bytes(receipt_path, (json.dumps(receipt, indent=2) + '\n').encode())

        expected_dirs = {key: (path, set(baseline) if baseline is not None else None)
                         for key, (path, baseline) in directories.items()}

        def verify_membership():
            for path, expected in expected_dirs.values():
                actual = entries(path)
                if actual != (sorted(expected) if expected is not None else None):
                    raise Drift('Directory membership changed during application: ' + str(path))

        def advance_membership(op):
            child = op['path']
            while identity(child.parent) in expected_dirs:
                key = identity(child.parent)
                parent, names = expected_dirs[key]
                if op['action'] == 'retire':
                    if child == op['path'] and names is not None:
                        names.discard(child.name)
                else:
                    names = set() if names is None else names
                    names.add(child.name)
                expected_dirs[key] = (parent, names)
                child = parent

        try:
            atomic_bytes(run_dir / 'plan.json', raw)
            save()
            for number, (op, data) in enumerate(zip(ops, before_bytes)):
                backup = None
                if data is not None:
                    backup = run_dir / 'backups' / str(number)
                    backup.parent.mkdir(exist_ok=True, mode=0o700)
                    if os.name == 'nt':
                        from ctypes import wintypes
                        copy = ctypes.WinDLL('kernel32', use_last_error=True).CopyFileW
                        copy.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.BOOL]
                        copy.restype = wintypes.BOOL
                        if not copy(str(op['path']), str(backup), True):
                            raise ctypes.WinError(ctypes.get_last_error())
                    else:
                        with backup.open('xb') as stream:
                            stream.write(data)
                        shutil.copystat(op['path'], backup, follow_symlinks=False)
                    if sha256(backup.read_bytes()) != op['beforeSha256']:
                        raise Drift('Backup does not match approved baseline.')
                receipt['files'].append({'target': str(op['path']), 'action': op['action'],
                    'beforeSha256': op['beforeSha256'], 'afterSha256': op['sourceSha256'],
                    'beforeMode': before_modes[number], 'afterMode': after_modes[number],
                    'backup': str(backup) if backup else None, 'applied': False})
                save()
            receipt['status'] = 'applying'
            save()
            for number, (op, data) in enumerate(zip(ops, payloads)):
                # Detect most non-cooperating edits too; this is not their lock.
                verify_membership()
                if file_hash(op['path']) != op['beforeSha256']:
                    raise Drift('Target changed during application: ' + str(op['path']))
                if data is None:
                    op['path'].unlink()
                else:
                    atomic_bytes(op['path'], data, after_modes[number])
                advance_membership(op)
                if file_hash(op['path']) != op['sourceSha256']:
                    raise Drift('Post-write verification failed: ' + str(op['path']))
                if os.name != 'nt' and data is not None and stat.S_IMODE(op['path'].stat().st_mode) != after_modes[number]:
                    raise Drift('Post-write mode verification failed: ' + str(op['path']))
                receipt['files'][number]['applied'] = True
                save()
            for op in ops:
                if file_hash(op['path']) != op['sourceSha256']:
                    raise Drift('Final file verification failed: ' + str(op['path']))
            verify_membership()
            receipt.update(status='complete', static='verified')
            save()  # Evidence is durable before releasing any handle.
        except BaseException as exc:
            receipt.update(status='partial-failure', error=type(exc).__name__)
            save()
            raise
        return receipt_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--plan-sha256', required=True)
    parser.add_argument('--state-dir', type=Path, default=Path.home() / '.agent-assets')
    parser.add_argument('--timeout', type=float, default=10)
    args = parser.parse_args()
    try:
        receipt = apply_plan(args.plan, args.plan_sha256, args.state_dir, args.timeout)
    except Busy as exc:
        print('busy: ' + str(exc), file=sys.stderr)
        return 3
    except Drift as exc:
        print('baseline-drift: ' + str(exc), file=sys.stderr)
        return 4
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print('apply-failed: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({'status': 'complete', 'receipt': str(receipt), 'runtime': 'not-run'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
