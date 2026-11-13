#!/usr/bin/env python3
"""Validate skill-package metadata and build an offline, immutable distribution.

Reads committed Git blobs by default; --working-tree is an explicitly labelled
development preview. No fetch, package installation, client changes or publishing.
Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys


CONFIG = "distribution.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def relative(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a relative file path.")
    for part in value.split("/"):
        if (part in {"", ".", ".."} or part.endswith((".", " ")) or
                any(ord(c) < 32 or c in '\\:<>"|?*' for c in part) or
                part.casefold() == ".git" or
                re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part)):
            raise ValueError("Unsafe relative path: " + value)
    return value


def plain(path: Path) -> Path:
    path = path.absolute()
    if os.name == "nt":
        if str(path).startswith("\\\\") or ":" in str(path)[2:]:
            raise ValueError("UNC/device paths and alternate streams are unsupported.")
        for component in path.parts[1:]:
            relative(component)
    for candidate in [*reversed(path.parents), path]:
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/reparse paths are not distribution inputs or destinations.")
    return path.resolve()


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Git read failed: " + args[0])
    return result.stdout


class Source:
    def __init__(self, root: Path, ref: str = "HEAD", working_tree: bool = False):
        self.root = plain(root)
        self.working_tree = working_tree
        self.commit = None
        self.entries: dict[str, tuple[str, str, str]] = {}
        if not working_tree:
            top = Path(git(self.root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
            if top != self.root:
                raise ValueError("Select the collection Git root.")
            self.commit = git(self.root, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()
            for entry in git(self.root, "ls-tree", "-rz", "--full-tree", self.commit).split(b"\0"):
                if entry:
                    meta, name = entry.split(b"\t", 1)
                    self.entries[name.decode("utf-8")] = tuple(meta.decode().split())

    def read(self, name: str) -> bytes:
        relative(name)
        if self.working_tree:
            path = plain(self.root / name)
            if not path.is_file() or self.root not in path.parents:
                raise ValueError("Missing regular input: " + name)
            return path.read_bytes()
        mode, kind, oid = self.entries.get(name, ("", "", ""))
        if mode not in {"100644", "100755"} or kind != "blob":
            raise ValueError("Missing or non-regular committed input: " + name)
        return git(self.root, "cat-file", "blob", oid)

    def paths(self) -> set[str]:
        if not self.working_tree:
            return set(self.entries)
        # Inspect only implicit component roots; private/unrelated trees stay unread.
        found = set()
        for root_name in ("skills", "hooks", "commands", "agents", "extensions", "prompts", "themes", "outputStyles", "com.github.copilot"):
            directory = plain(self.root / root_name)
            if not directory.exists():
                continue
            for parent, directories, files in os.walk(directory, followlinks=False):
                directories[:] = [d for d in directories if d not in {"__pycache__", "node_modules", ".git"}]
                for child in directories + files:
                    plain(Path(parent) / child)
                found.update((Path(parent) / f).relative_to(self.root).as_posix() for f in files)
        for name in ("mcp.json", ".mcp.json", ".app.json", ".lsp.json"):
            if (self.root / name).exists():
                found.add(name)
        return found


def manifests(config: dict) -> dict[str, bytes]:
    name, version, description = (config[k] for k in ("name", "version", "description"))
    plugin = {"name": name, "version": version, "description": description}
    return {
        "package.json": encoded({**plugin, "private": True, "pi": {
            "skills": ["./skills/" + s["name"] for s in config["skills"]]}}),
        "plugin.json": encoded({"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **plugin}),
        ".claude-plugin/plugin.json": encoded(plugin),
        ".codex-plugin/plugin.json": encoded(plugin),
        ".agents/plugins/marketplace.json": encoded({"name": name, "plugins": [{
            "name": name, "source": {"source": "local", "path": "./"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity"}]}),
        ".claude-plugin/marketplace.json": encoded({"name": name,
            "owner": {"name": config["owner"]}, "description": description,
            "plugins": [{"name": name, "source": "./"}]}),
    }


def prepare(source: Source, check_metadata: bool = True) -> tuple[dict, dict[str, bytes]]:
    raw_config = source.read(CONFIG)
    config = json.loads(raw_config)
    fields = {"formatVersion", "name", "version", "description", "owner", "skills", "notices"}
    if not isinstance(config, dict) or set(config) != fields or type(config["formatVersion"]) is not int or config["formatVersion"] != 1:
        raise ValueError("Unsupported distribution format or fields.")
    if not isinstance(config["name"], str) or not NAME.fullmatch(config["name"]) or len(config["name"]) > 64:
        raise ValueError("Use a unique kebab-case package name, at most 64 characters.")
    if not isinstance(config["version"], str) or not VERSION.fullmatch(config["version"]):
        raise ValueError("Use a numeric major.minor.patch version.")
    if any(not isinstance(config[k], str) or not config[k].strip() for k in ("owner", "description")):
        raise ValueError("Owner and description must be nonempty strings.")
    if not isinstance(config["skills"], list) or not config["skills"]:
        raise ValueError("Select at least one skill explicitly.")
    if not isinstance(config["notices"], list):
        raise ValueError("Notices must be a list of explicitly selected files.")

    payload: dict[str, bytes] = {}
    names = set()
    indexes = []
    for skill in config["skills"]:
        if not isinstance(skill, dict) or set(skill) != {"name", "files"}:
            raise ValueError("Skill entries require exactly name and files.")
        name, files = skill["name"], skill["files"]
        if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64 or name in names:
            raise ValueError("Invalid or duplicate skill name.")
        names.add(name)
        if not isinstance(files, list) or "SKILL.md" not in files:
            raise ValueError("Each skill needs an explicit file list including SKILL.md.")
        seen = set()
        hashes = {}
        for file in files:
            relative(file)
            if file.casefold() in seen:
                raise ValueError("Duplicate/case-colliding skill file.")
            seen.add(file.casefold())
            path = f"skills/{name}/{file}"
            data = source.read(path)
            payload[path] = data
            hashes[file] = digest(data)
        # Validate discovery identity, without executing or parsing arbitrary YAML.
        entry = payload[f"skills/{name}/SKILL.md"].decode("utf-8-sig").replace("\r\n", "\n")
        front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", entry, re.S)
        if (not front or not re.search(r"(?m)^name: *" + re.escape(name) + r" *$", front[1]) or
                not re.search(r"(?m)^description: *\S", front[1])):
            raise ValueError("Skill frontmatter name/description mismatch: " + name)
        indexes.append({"name": name, "version": digest(encoded(hashes)), "files": sorted(files)})

    paths = source.paths()
    actual_skills = {p.split("/")[1] for p in paths if re.fullmatch(r"skills/[^/]+/SKILL.md", p)}
    if actual_skills != names:
        raise ValueError("Native default discovery differs from the selected skill set.")
    for path in paths:
        if (path in {"mcp.json", ".mcp.json", ".app.json", ".lsp.json"} or
                path.split("/")[0] in {"hooks", "commands", "agents", "extensions", "prompts", "themes", "outputStyles", "com.github.copilot"}):
            raise ValueError("Unreviewed implicit native component: " + path)
        if path.startswith("skills/") and len(path.split("/")) >= 3:
            if path.endswith("/SKILL.md") and len(path.split("/")) != 3:
                raise ValueError("Nested skill entrypoints are unsupported: " + path)
            if path not in payload:
                raise ValueError("Unlisted skill companion: " + path)

    metadata = manifests(config)
    for path, expected in metadata.items():
        if check_metadata and json.loads(source.read(path)) != json.loads(expected):
            raise ValueError("Package metadata differs from distribution.json: " + path)
    payload.update(metadata)
    payload[CONFIG] = raw_config
    notice_paths = set()
    for path in config["notices"]:
        relative(path)
        if "/" in path or path.casefold() in notice_paths or path.casefold() in {p.casefold() for p in payload}:
            raise ValueError("Notices must be unique root files, separate from metadata.")
        notice_paths.add(path.casefold())
        payload[path] = source.read(path)

    outputs = {"package/" + path: data for path, data in payload.items()}
    for path, data in payload.items():
        if path.startswith("skills/"):
            outputs["catalog/" + path[len("skills/"):]] = data
    # Catalog entries also retain required package-level attribution per skill.
    for item in indexes:
        for path in config["notices"]:
            target = "_notices/" + path
            if target in item["files"]:
                raise ValueError("Notice output collides with a skill companion.")
            outputs[f"catalog/{item['name']}/{target}"] = payload[path]
            item["files"].append(target)
        item["files"].sort()
        item["version"] = digest(encoded({p: digest(outputs[f"catalog/{item['name']}/{p}"]) for p in item["files"]}))
    outputs["catalog/index.json"] = encoded({"skills": indexes})
    hashes = {path: digest(data) for path, data in sorted(outputs.items())}
    outputs["release.json"] = encoded({"formatVersion": 1, "name": config["name"],
        "version": config["version"], "sourceCommit": source.commit,
        "sourceMode": "development" if source.working_tree else "commit",
        "contentSha256": digest(encoded(hashes)), "files": hashes})
    return config, outputs


def write_output(source: Source, output: Path, files: dict[str, bytes]) -> None:
    output = plain(output)
    if output == source.root or source.root in output.parents or output in source.root.parents:
        raise ValueError("Output must be outside the source tree and its ancestors.")
    if output.exists() or not output.parent.is_dir():
        raise ValueError("Use a new output directory with an existing parent.")
    output.mkdir()  # Exclusive creation; partial IO failures retain evidence.
    for name, data in sorted(files.items()):
        relative(name)
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--ref", default="HEAD", help="Commit/ref to read once; default HEAD")
    source_group.add_argument("--working-tree", action="store_true", help="Development bytes, not a published release")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--check", action="store_true")
    destination.add_argument("--output", type=Path)
    destination.add_argument("--metadata-output", type=Path,
        help="Render proposed native manifests to a new external directory for review")
    args = parser.parse_args()
    try:
        source = Source(args.root, args.ref, args.working_tree)
        config, files = prepare(source, check_metadata=not args.metadata_output)
        if args.output:
            write_output(source, args.output, files)
        if args.metadata_output:
            write_output(source, args.metadata_output, manifests(config))
        print(json.dumps({"name": config["name"], "version": config["version"],
            "skills": len(config["skills"]), "sourceCommit": source.commit,
            "sourceMode": "development" if source.working_tree else "commit",
            "result": "checked" if args.check else "metadata-proposed" if args.metadata_output else "built",
            "runtime": "not-run"}))
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print("Distribution failed: " + str(exc), file=sys.stderr)
        print("No cleanup attempted; inspect any partial new output before retrying.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
