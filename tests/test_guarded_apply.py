"""Offline subprocess tests; every target, lock and receipt is in a temp directory."""

import importlib.util
import json
import os
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid


SCRIPT = Path(__file__).resolve().parents[1] / 'template/skills/sync-agent-assets/scripts/guarded_apply.py'
SPEC = importlib.util.spec_from_file_location('guarded_apply', SCRIPT)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

HOLDER = r'''
import importlib.util, pathlib, sys, time
spec = importlib.util.spec_from_file_location('guard', sys.argv[1])
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
root, state, ready, release = map(pathlib.Path, sys.argv[2:6])
with g.ScopeLocks([root], state, 1):
    ready.write_text('held')
    deadline = time.monotonic() + 15
    while not release.exists() and time.monotonic() < deadline:
        time.sleep(.02)
    if len(sys.argv) > 6:
        (root / 'SKILL.md').write_bytes(b'changed by first writer')
'''

FINALIZING = r'''
import importlib.util, json, pathlib, sys, time
spec = importlib.util.spec_from_file_location('guard', sys.argv[1])
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
plan, state, ready, release = map(pathlib.Path, sys.argv[2:6])
original = g.atomic_bytes
def pause_at_receipt(path, data, mode=None):
    if path.name == 'receipt.json' and json.loads(data).get('status') == 'complete':
        ready.write_text('finalizing')
        deadline = time.monotonic() + 15
        while not release.exists() and time.monotonic() < deadline:
            time.sleep(.02)
    return original(path, data, mode)
g.atomic_bytes = pause_at_receipt
g.apply_plan(plan, g.sha256(plan.read_bytes()), state)
'''


class GuardedApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='asset-lock-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'skills'
        self.root.mkdir()
        self.state = self.base / 'state'
        self.target = self.root / 'SKILL.md'
        self.target.write_bytes(b'old')
        self.source = self.base / 'candidate'
        self.source.write_bytes(b'new')

    def plan(self, **changes):
        plan = {'formatVersion': 1, 'operationId': str(uuid.uuid4()),
                'roots': [str(self.root)],
                'directories': [{'path': str(self.root), 'entries': ['SKILL.md']}],
                'files': [{'action': 'write', 'target': str(self.target),
                           'beforeSha256': guard.sha256(b'old'), 'source': str(self.source),
                           'sourceSha256': guard.sha256(b'new')}]}
        plan.update(changes)
        if os.name != 'nt':
            for item in plan['files']:
                target = Path(item['target'])
                if item['beforeSha256'] is not None:
                    item['beforeMode'] = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
                if item['action'] == 'write':
                    item['afterMode'] = item.get('beforeMode', stat.S_IMODE(Path(item['source']).stat().st_mode))
        path = self.base / (plan['operationId'] + '.json')
        data = json.dumps(plan).encode()
        path.write_bytes(data)
        return path, guard.sha256(data)

    def command(self, path, digest, timeout='1'):
        return [sys.executable, str(SCRIPT), '--plan', str(path), '--plan-sha256', digest,
                '--state-dir', str(self.state), '--timeout', timeout]

    def holder(self, mutate=False):
        ready, release = self.base / 'ready', self.base / 'release'
        args = [sys.executable, '-c', HOLDER, str(SCRIPT),
                str(self.root), str(self.state), str(ready), str(release)]
        proc = subprocess.Popen(args + (['mutate'] if mutate else []))
        def cleanup():
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=5)
        self.addCleanup(cleanup)
        deadline = time.monotonic() + 5
        while not ready.exists() and proc.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(ready.exists(), 'holder did not acquire the lock')
        return proc, release

    def test_apply_backups_and_records_before_return(self):
        path, digest = self.plan()
        receipt_path = guard.apply_plan(path, digest, self.state)
        receipt = json.loads(receipt_path.read_text())
        self.assertEqual(self.target.read_bytes(), b'new')
        self.assertEqual(Path(receipt['files'][0]['backup']).read_bytes(), b'old')
        self.assertEqual((receipt['status'], receipt['static'], receipt['runtime']),
                         ('complete', 'verified', 'not-run'))
        self.assertEqual(guard.entries(self.root), ['SKILL.md'])

    def test_second_process_is_busy_and_unrelated_scope_can_proceed(self):
        holder, release = self.holder()
        path, digest = self.plan()
        result = subprocess.run(self.command(path, digest, '.15'), capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(self.target.read_bytes(), b'old')
        other = self.base / 'other-skills'
        with guard.ScopeLocks([other], self.state, 0):
            self.assertIsNone(holder.poll())
        release.write_text('done')
        holder.wait(timeout=5)
        self.assertFalse((self.state / 'runs').exists())

    def test_crash_releases_handle_without_deleting_lock_file(self):
        holder, _ = self.holder()
        lock_files = list((self.state / 'locks').glob('*.lock'))
        self.assertEqual(len(lock_files), 1)
        holder.kill()
        holder.wait(timeout=5)
        path, digest = self.plan()
        result = subprocess.run(self.command(path, digest), capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.read_bytes(), b'new')
        self.assertEqual(list((self.state / 'locks').glob('*.lock')), lock_files)

    def test_apply_process_holds_lock_through_final_receipt(self):
        path, digest = self.plan()
        ready, release = self.base / 'finalizing', self.base / 'finish'
        writer = subprocess.Popen([sys.executable, '-c', FINALIZING, str(SCRIPT),
                                   str(path), str(self.state), str(ready), str(release)])
        def cleanup():
            if writer.poll() is None:
                writer.kill()
            writer.wait(timeout=5)
        self.addCleanup(cleanup)
        deadline = time.monotonic() + 5
        while not ready.exists() and writer.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(ready.exists())
        self.assertEqual(self.target.read_bytes(), b'new')
        contender = subprocess.run(self.command(path, digest, '.1'), capture_output=True, timeout=5)
        self.assertEqual(contender.returncode, 3, contender.stderr)
        release.write_text('done')
        self.assertEqual(writer.wait(timeout=5), 0)
        receipt = self.state / 'runs' / json.loads(path.read_text())['operationId'] / 'receipt.json'
        self.assertEqual(json.loads(receipt.read_text())['status'], 'complete')

    def test_waiter_rechecks_baseline_after_lock_acquisition(self):
        holder, release = self.holder(mutate=True)
        path, digest = self.plan()
        waiter = subprocess.Popen(self.command(path, digest, '3'), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.addCleanup(lambda: waiter.kill() if waiter.poll() is None else None)
        time.sleep(.15)
        self.assertIsNone(waiter.poll())
        # The first lock owner changes the target before releasing its handle.
        release.write_text('done')
        holder.wait(timeout=5)
        stdout, stderr = waiter.communicate(timeout=5)
        self.assertEqual(waiter.returncode, 4, (stdout, stderr))
        self.assertEqual(self.target.read_bytes(), b'changed by first writer')
        self.assertFalse((self.state / 'runs').exists())

    def test_membership_drift_and_source_drift_do_not_write(self):
        path, digest = self.plan()
        extra = self.root / 'unreviewed.txt'
        extra.write_bytes(b'keep')
        with self.assertRaises(guard.Drift):
            guard.apply_plan(path, digest, self.state)
        extra.unlink()
        self.source.write_bytes(b'not approved')
        with self.assertRaises(guard.Drift):
            guard.apply_plan(path, digest, self.state)
        self.assertEqual(self.target.read_bytes(), b'old')

    def test_partial_failure_retains_backups_and_releases_locks(self):
        companion = self.root / 'companion.txt'
        path, digest = self.plan(files=[
            {'action': 'write', 'target': str(self.target), 'beforeSha256': guard.sha256(b'old'),
             'source': str(self.source), 'sourceSha256': guard.sha256(b'new')},
            {'action': 'write', 'target': str(companion), 'beforeSha256': None,
             'source': str(self.source), 'sourceSha256': guard.sha256(b'new')}])
        original = guard.atomic_bytes
        def fail_second(target, data, mode=None):
            if guard.identity(target) == guard.identity(companion):
                raise OSError('simulated second-file failure')
            return original(target, data, mode)
        guard.atomic_bytes = fail_second
        try:
            with self.assertRaises(OSError):
                guard.apply_plan(path, digest, self.state)
        finally:
            guard.atomic_bytes = original
        receipt_path = self.state / 'runs' / json.loads(path.read_text())['operationId'] / 'receipt.json'
        receipt = json.loads(receipt_path.read_text())
        self.assertEqual(receipt['status'], 'partial-failure')
        self.assertTrue(receipt['files'][0]['applied'])
        self.assertFalse(receipt['files'][1]['applied'])
        self.assertEqual(Path(receipt['files'][0]['backup']).read_bytes(), b'old')
        self.assertEqual(self.target.read_bytes(), b'new')
        self.assertFalse(companion.exists())
        with guard.ScopeLocks([self.root], self.state, 0):
            pass

    def test_registry_write_uses_same_transaction_and_metadata_lock(self):
        metadata = self.base / 'registry-candidate.json'
        metadata.write_text('{"formatVersion":1,"collections":[],"physicalTargets":[]}')
        registry = self.state / 'registry.json'
        metadata_op = {'action': 'write', 'target': str(registry), 'beforeSha256': None,
                       'source': str(metadata), 'sourceSha256': guard.sha256(metadata.read_bytes())}
        path, digest = self.plan(files=[
            {'action': 'write', 'target': str(self.target), 'beforeSha256': guard.sha256(b'old'),
             'source': str(self.source), 'sourceSha256': guard.sha256(b'new')}, metadata_op])
        with guard.ScopeLocks([self.state / 'metadata'], self.state, 0):
            with self.assertRaises(guard.Busy):
                guard.apply_plan(path, digest, self.state, 0)
        self.assertEqual(self.target.read_bytes(), b'old')
        guard.apply_plan(path, digest, self.state)
        self.assertEqual(json.loads(registry.read_text())['formatVersion'], 1)
        self.assertEqual(self.target.read_bytes(), b'new')

    def test_metadata_only_native_receipt_uses_metadata_lock_without_cache_root(self):
        candidate = self.base / 'native-record.json'
        candidate.write_text('{"formatVersion":2,"collections":[],"physicalTargets":[],"managedPackages":[]}')
        registry = self.state / 'registry.json'
        record = self.state / 'installations' / 'native.json'
        ops = [{'action': 'write', 'target': str(target), 'beforeSha256': None,
                'source': str(candidate), 'sourceSha256': guard.sha256(candidate.read_bytes())}
               for target in (record, registry)]
        path, digest = self.plan(roots=[], directories=[], files=ops)
        with guard.ScopeLocks([self.state / 'metadata'], self.state, 0):
            with self.assertRaises(guard.Busy):
                guard.apply_plan(path, digest, self.state, 0)
        self.assertFalse(registry.exists())
        guard.apply_plan(path, digest, self.state)
        self.assertEqual(json.loads(registry.read_text())['formatVersion'], 2)
        self.assertEqual(record.read_bytes(), candidate.read_bytes())
        self.assertEqual(self.target.read_bytes(), b'old')

    def test_empty_roots_do_not_authorize_cache_or_policy_writes(self):
        for target in (self.base / 'native-cache' / 'SKILL.md', self.state / 'policy.json'):
            path, digest = self.plan(roots=[], directories=[], files=[{
                'action': 'write', 'target': str(target), 'beforeSha256': None,
                'source': str(self.source), 'sourceSha256': guard.sha256(b'new')}])
            with self.assertRaisesRegex(ValueError, 'outside'):
                guard.apply_plan(path, digest, self.state)
            self.assertFalse(target.exists())

    def test_plan_digest_escape_and_vendor_files_are_rejected(self):
        path, digest = self.plan()
        with self.assertRaises(guard.Drift):
            guard.apply_plan(path, '0' * 64, self.state)
        for target in [self.base / 'outside', self.root / '.system' / 'SKILL.md']:
            data = json.loads(path.read_text())
            data['files'][0]['target'] = str(target)
            raw = json.dumps(data).encode()
            path.write_bytes(raw)
            with self.assertRaises(ValueError):
                guard.apply_plan(path, guard.sha256(raw), self.state)
        self.assertEqual(self.target.read_bytes(), b'old')

    def test_vendor_directory_cannot_itself_be_a_lock_root(self):
        for name in ['.system', '.git']:
            vendor = self.root / name
            vendor.mkdir()
            path, digest = self.plan(roots=[str(vendor)])
            with self.assertRaises(ValueError):
                guard.apply_plan(path, digest, self.state)

    @unittest.skipUnless(os.name == 'nt', 'Windows path spelling rules')
    def test_absent_windows_alias_roots_and_device_names_are_rejected(self):
        for leaf in ['new-root.', 'new-root ', 'NUL', 'con.txt', 'LPT1', 'COM¹.log']:
            root = self.base / leaf
            path, digest = self.plan(roots=[str(root)])
            with self.assertRaises(ValueError):
                guard.apply_plan(path, digest, self.state)
        self.assertFalse((self.base / 'new-root').exists())
        self.assertEqual(self.target.read_bytes(), b'old')

    @unittest.skipIf(os.name == 'nt', 'POSIX permission modes')
    def test_migration_preserves_executable_mode_and_rejects_mode_drift(self):
        self.source.chmod(0o755)
        new_target = self.root / 'executable'
        path, digest = self.plan(files=[{'action': 'write', 'target': str(new_target),
            'beforeSha256': None, 'source': str(self.source), 'sourceSha256': guard.sha256(b'new')}])
        guard.apply_plan(path, digest, self.state)
        self.assertEqual(stat.S_IMODE(new_target.stat().st_mode), 0o755)
        new_target.unlink()
        path, digest = self.plan()
        self.target.chmod(0o600 if stat.S_IMODE(self.target.stat().st_mode) != 0o600 else 0o644)
        with self.assertRaises(guard.Drift):
            guard.apply_plan(path, digest, self.state)

    def test_migration_creates_shared_copy_and_retires_only_selected_files(self):
        shared = self.base / 'shared-skills'
        shared_file = shared / 'example' / 'SKILL.md'
        path, digest = self.plan(roots=[str(self.root), str(shared)], directories=[
            {'path': str(self.root), 'entries': ['SKILL.md']},
            {'path': str(shared), 'entries': None},
            {'path': str(shared / 'example'), 'entries': None}], files=[
            {'action': 'retire', 'target': str(self.target), 'beforeSha256': guard.sha256(b'old'),
             'source': None, 'sourceSha256': None},
            {'action': 'write', 'target': str(shared_file), 'beforeSha256': None,
             'source': str(self.source), 'sourceSha256': guard.sha256(b'new')}])
        receipt = json.loads(guard.apply_plan(path, digest, self.state).read_text())
        self.assertEqual(shared_file.read_bytes(), b'new')
        self.assertFalse(self.target.exists())
        self.assertEqual(Path(receipt['files'][0]['backup']).read_bytes(), b'old')
        self.assertTrue(self.root.is_dir())  # No recursive directory deletion.

    def test_same_root_spelling_uses_same_lock_and_repeated_run_is_not_replayed(self):
        variant = Path(str(self.root) + os.sep + '.')
        if os.name == 'nt':
            variant = Path(str(variant).upper())
        with guard.ScopeLocks([self.root], self.state):
            with self.assertRaises(guard.Busy):
                with guard.ScopeLocks([variant], self.state, 0):
                    self.fail('same physical scope acquired twice')
        path, digest = self.plan()
        guard.apply_plan(path, digest, self.state)
        with self.assertRaises(guard.Drift):
            guard.apply_plan(path, digest, self.state)


if __name__ == '__main__':
    unittest.main()
