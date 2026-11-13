"""Offline artifact and publication-boundary tests; never installs a client package."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


def find_builder():
    for parent in Path(__file__).resolve().parents:
        for prefix in ("", "template"):
            path = parent / prefix / "skills/sync-agent-assets/scripts/build_distribution.py"
            if path.is_file():
                return path
    raise RuntimeError("Distribution builder not found")


SPEC = importlib.util.spec_from_file_location("distribution", find_builder())
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill-distribution-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "source"
        self.root.mkdir()
        self.config = {"formatVersion": 1, "name": "example-assets", "version": "0.1.0",
            "owner": "Example Maintainer", "description": "Example skills", "notices": [],
            "skills": [{"name": "hello", "files": ["SKILL.md", "references/workflow.md"]}]}
        self.put("skills/hello/SKILL.md", b"---\nname: hello\ndescription: Greet someone\n---\nRead references/workflow.md.\n")
        self.put("skills/hello/references/workflow.md", b"Greet the user.\n")
        self.metadata()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Distribution Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "commit.gpgsign", "false")
        self.commit()

    def put(self, path, data):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)

    def metadata(self):
        self.put("distribution.json", builder.encoded(self.config))
        for name, data in builder.manifests(self.config).items():
            self.put(name, data)

    def git(self, *args, input=None):
        return subprocess.run(["git", "-C", str(self.root), *args], input=input,
            check=True, capture_output=True).stdout

    def commit(self):
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Fixture")

    def prepare(self, working_tree=False):
        return builder.prepare(builder.Source(self.root, working_tree=working_tree))[1]

    def test_committed_release_is_reproducible_complete_and_independent_of_dirty_tree(self):
        original = self.prepare()
        self.put("skills/hello/references/workflow.md", b"Unpublished edit")
        self.put("skills/hello/private.json", b"Do not export this")
        self.assertEqual(original, self.prepare())
        self.assertNotIn("package/skills/hello/private.json", original)
        release = json.loads(original["release.json"])
        self.assertEqual(release["sourceCommit"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertEqual(release["sourceMode"], "commit")
        self.assertEqual(set(release["files"]), set(original) - {"release.json"})
        for path, expected in release["files"].items():
            self.assertEqual(hashlib.sha256(original[path]).hexdigest(), expected)
        index = json.loads(original["catalog/index.json"])
        for skill in index["skills"]:
            for path in skill["files"]:
                self.assertEqual(original[f"catalog/{skill['name']}/{path}"],
                    original[f"package/skills/{skill['name']}/{path}"])

    def test_companion_and_notice_changes_invalidate_catalog_version(self):
        self.config["notices"] = ["NOTICE"]
        self.put("NOTICE", b"Original attribution")
        self.metadata()
        before = self.prepare(True)
        self.put("skills/hello/references/workflow.md", b"New workflow")
        after = self.prepare(True)
        version = lambda data: json.loads(data["catalog/index.json"])["skills"][0]["version"]
        self.assertNotEqual(version(before), version(after))
        self.put("NOTICE", b"Updated attribution")
        final = self.prepare(True)
        self.assertNotEqual(version(after), version(final))
        self.assertEqual(final["catalog/hello/_notices/NOTICE"], b"Updated attribution")

    def test_development_is_explicit_and_never_claims_head_commit(self):
        release = json.loads(self.prepare(True)["release.json"])
        self.assertIsNone(release["sourceCommit"])
        self.assertEqual(release["sourceMode"], "development")

    def test_rejects_unlisted_companion_or_implicit_component(self):
        for name in ("skills/hello/private.json", "hooks/hooks.json", "mcp.json", "extensions/code.ts"):
            with self.subTest(name=name):
                self.put(name, b"{}")
                with self.assertRaisesRegex(ValueError, "Unlisted|Unreviewed"):
                    self.prepare(True)
                (self.root / name).unlink()

    def test_rejects_undeclared_skill_and_wrong_metadata(self):
        self.put("skills/extra/SKILL.md", b"Extra")
        with self.assertRaisesRegex(ValueError, "discovery"):
            self.prepare(True)
        (self.root / "skills/extra/SKILL.md").unlink()
        self.put("package.json", b"{}")
        with self.assertRaisesRegex(ValueError, "metadata differs"):
            self.prepare(True)

    def test_metadata_proposal_does_not_change_source(self):
        self.config["version"] = "0.2.0"
        self.put("distribution.json", builder.encoded(self.config))
        source = builder.Source(self.root, working_tree=True)
        before = (self.root / "package.json").read_bytes()
        config, _ = builder.prepare(source, check_metadata=False)
        destination = self.parent / "proposed"
        builder.write_output(source, destination, builder.manifests(config))
        self.assertEqual((self.root / "package.json").read_bytes(), before)
        self.assertEqual(json.loads((destination / "package.json").read_bytes())["version"], "0.2.0")

    def test_rejects_traversal_and_case_collisions(self):
        for path in ("../../outside", "/absolute", "C:/secret", "x\\y", "x/../y", "NUL", "tail."):
            with self.subTest(path=path), self.assertRaises(ValueError):
                builder.relative(path)
        self.config["skills"][0]["files"].append("skill.md")
        self.metadata()
        with self.assertRaisesRegex(ValueError, "case-colliding"):
            self.prepare(True)

    def test_rejects_linked_committed_companion_without_following_it(self):
        oid = self.git("hash-object", "-w", "--stdin", input=b"../../outside").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", f"120000,{oid},skills/hello/references/workflow.md")
        self.git("commit", "--quiet", "-m", "Linked fixture")
        with self.assertRaisesRegex(ValueError, "non-regular"):
            self.prepare()

    def test_output_is_new_and_outside_source(self):
        source = builder.Source(self.root)
        outputs = self.prepare()
        with self.assertRaisesRegex(ValueError, "outside"):
            builder.write_output(source, self.root / "dist", outputs)
        destination = self.parent / "release"
        builder.write_output(source, destination, outputs)
        with self.assertRaisesRegex(ValueError, "new output"):
            builder.write_output(source, destination, outputs)
        self.assertEqual((destination / "release.json").read_bytes(), outputs["release.json"])

    def test_notice_cannot_alias_metadata(self):
        self.config["notices"] = ["PACKAGE.JSON"]
        self.metadata()
        with self.assertRaisesRegex(ValueError, "Notices"):
            self.prepare(True)

    def test_committed_cache_files_are_not_silently_distributed(self):
        self.put("skills/hello/__pycache__/SKILL.md", b"Unexpected skill")
        self.commit()
        with self.assertRaisesRegex(ValueError, "Nested|Unlisted"):
            self.prepare()

    @unittest.skipUnless(os.name == "nt", "Windows path aliases")
    def test_windows_destination_aliases_are_rejected(self):
        for leaf in ("release.", "release ", "NUL", "COM1.txt"):
            with self.subTest(leaf=leaf), self.assertRaises(ValueError):
                builder.plain(self.parent / leaf)

    def test_runtime_state_outside_selected_skills_is_not_exported(self):
        self.put("private/credentials.json", b"Not for distribution")
        self.put("mcp/servers/example.json", b"{}")
        self.commit()
        outputs = self.prepare()
        self.assertFalse(any("credentials" in path or "mcp/servers" in path for path in outputs))


if __name__ == "__main__":
    unittest.main()
