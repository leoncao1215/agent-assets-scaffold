"""Offline behavior checks using temporary, independently committed source trees."""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("create_instance", ROOT / "tools/create_instance.py")
creator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(creator)


class CreationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agent-assets-scaffold-test-")
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.source = self.parent / "source"
        self.source.mkdir()
        shutil.copytree(ROOT / "template", self.source / "template")
        shutil.copyfile(ROOT / "LICENSE", self.source / "LICENSE")
        self.git("init", "--quiet")
        self.git("config", "user.name", "Scaffold Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "commit.gpgsign", "false")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Test template baseline")

    def git(self, *args, input=None):
        result = subprocess.run(
            ["git", "-C", str(self.source), *args], input=input,
            capture_output=True, check=True,
        )
        return result.stdout

    def create(self, leaf="instance"):
        destination = self.parent / leaf
        result = creator.create_instance(self.source, destination, "Personal collection", "personal")
        return destination, result

    def test_creates_complete_independent_instances_with_reproducible_baselines(self):
        before = self.git("status", "--porcelain")
        first, first_result = self.create("first instance")
        second, second_result = self.create("second")
        self.assertNotEqual(first_result["instanceId"], second_result["instanceId"])
        uuid.UUID(first_result["instanceId"])
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.assertFalse((first / ".git").exists())
        self.assertFalse((first / "tools").exists())
        self.assertFalse((first / ".local").exists())
        instance = json.loads((first / "instance.json").read_text())
        self.assertIsNone(instance["repository"])
        self.assertEqual(instance["scope"], "personal")
        lock = json.loads((first / "scaffold-lock.json").read_text())
        self.assertEqual(lock, json.loads((second / "scaffold-lock.json").read_text()))
        self.assertEqual(lock["source"]["commit"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertNotIn("instance.json", lock["files"])
        self.assertNotIn("scaffold-lock.json", lock["files"])
        actual = {p.relative_to(first).as_posix() for p in first.rglob("*") if p.is_file()}
        self.assertEqual(actual, set(lock["files"]) | {"instance.json", "scaffold-lock.json"})
        for path, entry in lock["files"].items():
            raw = self.git("show", f"HEAD:{entry['sourcePath']}")
            self.assertEqual((first / path).read_bytes(), raw)
            self.assertEqual(entry["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(json.loads((first / "skills/sources.json").read_text())["skills"], [])
        self.assertEqual(list((first / "mcp/servers").glob("*.json")), [])
        for example in (first / "mcp/examples").glob("*.json"):
            data = json.loads(example.read_text())
            self.assertTrue(data["example"])
            self.assertFalse(data["enabledByDefault"])

    def test_rejects_existing_directory_without_touching_user_content(self):
        destination = self.parent / "existing"
        destination.mkdir()
        with self.assertRaisesRegex(ValueError, "already exists"):
            creator.create_instance(self.source, destination, "Example", "work")
        sentinel = destination / "keep.txt"
        sentinel.write_bytes(b"user content")
        with self.assertRaisesRegex(ValueError, "already exists"):
            creator.create_instance(self.source, destination, "Example", "work")
        self.assertEqual(sentinel.read_bytes(), b"user content")

    def test_recorded_baseline_supports_reviewed_three_way_upgrade(self):
        instance, _ = self.create("original")
        original_lock = json.loads((instance / "scaffold-lock.json").read_text())
        local_readme = instance / "README.md"
        local_readme.write_bytes(local_readme.read_bytes().replace(
            b"# Agent assets", b"# My independent collection", 1
        ))
        upstream_readme = self.source / "template/README.md"
        upstream_readme.write_bytes(upstream_readme.read_bytes() + b"\nNew upstream guidance.\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "New scaffold version")
        candidate, _ = self.create("candidate")
        candidate_lock = json.loads((candidate / "scaffold-lock.json").read_text())
        old_commit = original_lock["source"]["commit"]
        base_bytes = self.git("show", f"{old_commit}:template/README.md")
        self.assertEqual(hashlib.sha256(base_bytes).hexdigest(),
                         original_lock["files"]["README.md"]["sha256"])
        base_file = self.parent / "base-readme.md"
        base_file.write_bytes(base_bytes)
        merged = subprocess.run(
            ["git", "merge-file", "-p", str(local_readme), str(base_file), str(candidate / "README.md")],
            capture_output=True, check=True,
        ).stdout
        self.assertIn(b"# My independent collection", merged)
        self.assertIn(b"New upstream guidance.", merged)
        self.assertNotEqual(hashlib.sha256(merged).hexdigest(),
                            candidate_lock["files"]["README.md"]["sha256"])
        # Reviewing an upgrade must not advance the old instance's lock or write it.
        self.assertEqual(json.loads((instance / "scaffold-lock.json").read_text()), original_lock)
        self.assertNotIn(b"New upstream guidance.", local_readme.read_bytes())

    def test_rejects_dirty_source_before_creating_output(self):
        (self.source / "template/README.md").write_text("uncommitted content")
        with self.assertRaisesRegex(ValueError, "dirty"):
            self.create()
        self.assertFalse((self.parent / "instance").exists())

    def test_rejects_nested_destination(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            creator.create_instance(self.source, self.source / "nested", "Example", "other")
        self.assertFalse((self.source / "nested").exists())

    def test_rejects_committed_symlink_without_following_it(self):
        blob = self.git("hash-object", "-w", "--stdin", input=b"../../outside").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", f"120000,{blob},template/escape")
        self.git("commit", "--quiet", "-m", "Symlink fixture")
        # A skip-worktree entry allows this platform-independent Git tree fixture.
        self.git("update-index", "--skip-worktree", "template/escape")
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.create()
        self.assertFalse((self.parent / "instance").exists())

    def test_rejects_reserved_template_metadata(self):
        (self.source / "template/instance.json").write_text("{}")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Invalid identity fixture")
        with self.assertRaisesRegex(ValueError, "metadata"):
            self.create()
        self.assertFalse((self.parent / "instance").exists())

    def test_rejects_credentials_and_shell_text_in_provenance(self):
        for value in (
            "https://secret@example.invalid/repo.git",
            "https://example.invalid/repo.git?token=secret",
            "ssh://git:secret@example.invalid/repo.git",
            "git@example.invalid:repo.git;echo oops",
            "C:/private/repository",
        ):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "credential-free"):
                creator.create_instance(self.source, self.parent / "instance", "Example", "other", value)
        self.assertFalse((self.parent / "instance").exists())


if __name__ == "__main__":
    unittest.main()
