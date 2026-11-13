# Optional native skill distribution

Each instance can publish its canonical skills as a Pi package, a portable plugin
with Codex and Claude-compatible marketplace metadata, and an OpenCode HTTP skill
catalog. This template does not enable any of those sources, choose your package
name, install clients or provide a business skill bundle. Ordinary shared-file
installation remains available.

Read the installed sync skill's
[native distribution contract](skills/sync-agent-assets/references/native-distribution.md)
before choosing a method. Use a package/marketplace name unique to this collection;
do not reuse a scaffold-wide name for different instances. Keep instance identity
separate from display names. A host that does not support your native format can
continue using the existing file-managed method; do not silently switch it.

## Opt in for this instance

1. Select the canonical local skills and their complete reviewed companion file
   lists. This initial whole-tree package must account for every skill discovered
   in the root `skills/` directory, including sync-agent-assets. External source
   references remain outside the bundle. Smaller independently selected bundles
   need a separately reviewed layout; copying content into per-client trees is
   not the default solution.
2. Create root `distribution.json` using format 1 described in the linked contract:
   `formatVersion`, unique kebab-case `name`, numeric `version`, `description`,
   `owner`, `skills` (each with `name` and explicit relative `files` including
   SKILL.md) and `notices`. Keep `SCAFFOLD-LICENSE` in notices when distributing
   inherited scaffold material; preserve any other required notices too.
3. Generate native metadata proposals into a new directory outside the instance:

   ```text
   python skills/sync-agent-assets/scripts/build_distribution.py --root . --working-tree --metadata-output /new-metadata-directory
   ```

   Replace the example destination with a real path for your shell. Review and
   apply the six generated files to this instance: package.json, plugin.json,
   .codex-plugin/plugin.json, .claude-plugin/plugin.json and the two marketplace
   catalogs under .agents/plugins/ and .claude-plugin/. No skills are duplicated.
4. Run `--working-tree --check`. Resolve any missing/extra companions or implicit
   components. Metadata equality is checked, so later changes to package identity,
   version or membership must update the related manifests together. The checker
   does not scan for secrets or prove host compatibility.
5. Commit/publish under the contribution policy. Build a release from the resulting
   full commit with `--ref FULL_COMMIT --output /new-release-directory`. The output
   parent must exist; the destination must not exist and must be outside source.

The helper uses existing Python 3.10+ and Git, with no package dependencies. It
does not execute packaged scripts, initialize Git, fetch sources or install
packages. Git builds read committed blobs without checkout hooks/filters; an
explicit development build has no claimed source commit. Output includes a
`package/` tree, `catalog/` and `release.json` with complete output hashes.

For native Git consumption, register this instance's repository and approved
revision, not the scaffold repository. For OpenCode, publishing `catalog/` at an
authorized HTTP location is a separate action; never make private material public
to work around unsupported authentication. Keep index and files from one immutable
release. No HTTP hosting or automatic deployment is configured by the template.

## Update and contribution lifecycle

Edit the canonical checkout, include distribution membership/version changes,
then publish. The next manual/scheduled pull follows each consumer's registered
method: guarded file update or a supported native manager operation. Source
refresh, installed bytes, activation and actual session loading are separate
outcomes. Runtime prerequisites and non-skill categories remain separately managed.

Use registry/policy format 2 before registering native installations; retain all
file-only records and baselines. Do not copy packages into native caches with the
file helper or assume its locks constrain native updaters. Establish supported
access, immutable revision selection and update exclusion in the actual host.
Creating this distribution metadata does not authorize client migration or native
auto-update. Existing installation methods and user policies remain unchanged.

Keep writable source checkouts and private runtime/configuration outside client
caches. After publication, retire a temporary development discovery entry only
after the published copy is installed and loaded, and only if no other consumer
still needs it. Never treat a successful push as proof that any consumer updated.
