#!/usr/bin/env python3
"""Create a new instance from committed template blobs; no network or installation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


DEFAULT_SOURCE = "https://github.com/leoncao1215/agent-assets-scaffold.git"
RESERVED_OUTPUTS = {"instance.json", "scaffold-lock.json", "SCAFFOLD-LICENSE"}


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False
    )
    if result.returncode:
        raise ValueError(f"Git operation failed: {args[0]}; check the selected checkout.")
    return result.stdout


def valid_repository(value: str) -> bool:
    """Accept credential-free HTTPS, SSH, or git@host:path metadata, never execute it."""
    if not value or any(char.isspace() or ord(char) < 32 for char in value):
        return False
    if re.fullmatch(r"git@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+", value):
        return True
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"https", "ssh"} or not parsed.hostname:
            return False
        if parsed.password is not None or parsed.query or parsed.fragment:
            return False
        if parsed.scheme == "https" and parsed.username is not None:
            return False
        # Restrict SSH transport identity to the conventional, non-secret user.
        if parsed.scheme == "ssh" and parsed.username not in {None, "git"}:
            return False
        return bool(parsed.path and parsed.path != "/")
    except ValueError:
        return False


def check_relative(path: str) -> None:
    parts = path.split("/")
    if (
        not path
        or PurePosixPath(path).is_absolute()
        or "\\" in path
        or ":" in path
        or any(part in {"", ".", ".."} or part.lower() == ".git" for part in parts)
    ):
        raise ValueError("Unsafe path in the committed template.")


def read_source(root: Path) -> tuple[str, dict[str, tuple[str, bytes]]]:
    root = root.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != root:
        raise ValueError("The scaffold must be the root of its own Git checkout.")
    commit = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
        raise ValueError("Expected a full Git commit ID.")
    if git(root, "status", "--porcelain", "--untracked-files=normal").strip():
        raise ValueError("Scaffold checkout is dirty; review and commit it first.")

    entries = git(root, "ls-tree", "-rz", "--full-tree", commit, "--", "template/", "LICENSE")
    files: dict[str, tuple[str, bytes]] = {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.decode("ascii").split()
        source_path = raw_path.decode("utf-8")
        check_relative(source_path)
        if mode not in {"100644", "100755"} or kind != "blob":
            raise ValueError("Template symlinks, submodules, and special files are unsupported.")
        if source_path == "LICENSE":
            output_path = "SCAFFOLD-LICENSE"
        elif source_path.startswith("template/"):
            output_path = source_path[len("template/"):]
            check_relative(output_path)
            if output_path in RESERVED_OUTPUTS:
                raise ValueError("Template conflicts with generated instance metadata.")
        else:
            raise ValueError("Unexpected source path.")
        if output_path in files:
            raise ValueError("Duplicate output path.")
        files[output_path] = (source_path, git(root, "cat-file", "blob", object_id))
    required = {"README.md", "BOOTSTRAP.md", "skills/sync-agent-assets/SKILL.md", "SCAFFOLD-LICENSE"}
    if not required.issubset(files):
        raise ValueError("Committed template or license is incomplete.")
    return commit, files


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def create_instance(
    root: Path, destination: Path, name: str, scope: str, source_repository: str = DEFAULT_SOURCE
) -> dict:
    if not name.strip() or any(ord(char) < 32 for char in name):
        raise ValueError("Use a nonempty single-line instance name.")
    if scope not in {"personal", "work", "other"}:
        raise ValueError("Scope must be personal, work, or other.")
    if not valid_repository(source_repository):
        raise ValueError("Use a credential-free HTTPS or SSH source repository URL.")

    # Inspect the lexical ancestors before resolve() could hide links/junctions.
    destination = destination.absolute()
    for path in (destination, *destination.parents):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("Choose a destination without symlink or junction ancestors.")
    destination = destination.resolve()
    root = root.resolve()
    if destination == root or root in destination.parents:
        raise ValueError("Choose a destination outside the scaffold checkout.")
    if destination.exists():
        raise ValueError("Destination already exists; no files were changed.")
    if not destination.parent.is_dir():
        raise ValueError("Destination parent must already exist.")

    commit, files = read_source(root)
    instance = {
        "formatVersion": 1,
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "scope": scope,
        "repository": None,
    }
    lock = {
        "formatVersion": 1,
        "source": {"repository": source_repository, "commit": commit},
        "files": {
            path: {"sourcePath": source_path, "sha256": hashlib.sha256(content).hexdigest()}
            for path, (source_path, content) in sorted(files.items())
        },
    }
    outputs = {path: content for path, (_, content) in files.items()}
    outputs["instance.json"] = json_bytes(instance)
    outputs["scaffold-lock.json"] = json_bytes(lock)

    # Exclusive creation: never repurpose an existing directory, even if empty.
    destination.mkdir()
    for relative, content in sorted(outputs.items()):
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)
    return {"destination": str(destination), "instanceId": instance["id"], "sourceCommit": commit}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New directory outside the scaffold checkout")
    parser.add_argument("--name", required=True, help="Readable collection label")
    parser.add_argument("--scope", choices=("personal", "work", "other"), required=True)
    parser.add_argument(
        "--source-repository", default=DEFAULT_SOURCE,
        help="Credential-free scaffold origin for provenance; set explicitly when using a fork",
    )
    args = parser.parse_args()
    try:
        result = create_instance(
            Path(__file__).resolve().parents[1], args.destination, args.name, args.scope,
            args.source_repository,
        )
    except (ValueError, OSError) as exc:
        print(f"Creation failed: {exc}", file=sys.stderr)
        print("If a new directory was partially written, inspect it; no cleanup was attempted.", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
