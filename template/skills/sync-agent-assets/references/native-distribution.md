# Native packages and skill catalogs

Use this reference when publishing a package/catalog, choosing a consumption
method, or updating a registered native installation. It complements file-managed
shared skills; it does not migrate existing consumers merely by being installed.

## Choose and record the installation method

Select one method per logical skill and actual consumer/profile:

- `files`: shared `~/.agents/skills` where verified, otherwise a compatibility
  root. The guarded file helper owns the selected regular files.
- `pi-package`: a Pi package source; Pi owns its clone/cache and package settings.
- `opencode-catalog`: an HTTP skill catalog; OpenCode owns its downloaded cache.
- `codex-plugin`, `claude-plugin`, `copilot-plugin`: a registered marketplace and
  installed plugin; that client owns the cache and activation configuration.

Preserve an existing method on routine pull. For new setup, offer supported native
distribution when it fits the selected package, access and update policy; retain
files for clients without verified native support or for shared-root deduplication.
Choosing native loading trades some shared storage for native package management.
Do not silently fallback or switch methods because one operation failed.

A package can contain several skills. Approving one skill does not approve every
skill in its package. Verify supported resource filters, or choose a reviewed
smaller package/file installation. Additions to a bundle require the standing
policy to cover new assets. External reference catalogs are not native packages:
resolve those upstreams separately; never vendor private references implicitly.
Plugin namespaces may change invocation names; record the actual names and check
cross-skill references and invocation restrictions in the consumer.

Package installation does not load optional common instructions, apply native
preferences, translate this collection's MCP descriptions, install skill runtime
dependencies, or supply authentication and private service bindings. Those retain
their existing category procedures and separate outcomes.

## Three copies with different owners

The writable source checkout is for development and contributions. A temporary
development installation may expose it for a bounded test. The installed shared
copy or native cache is for running published content. Native caches are not
authoring directories, and a moving development checkout is not a pinned release.

After editing a source skill, validate its required companions and distribution
membership. Publish only under contribution authority. For versioned plugin
packages, increment the package version and update all matching manifests in the
same contribution whenever packaged bytes change, including scripts/references.
Rebuild any catalog from the published commit; a content-derived skill version
must change when any of its listed files or notices changes. Do not mix a catalog
index from one release with files from another.

Publication does not retire local development copies or advance installation
baselines. First install/verify the published revision, preserve any additional
local edits, then explicitly cut over active discovery. Keep the writable source.
Extract accidental native-cache edits as a bounded contribution before updating;
native update/reset may discard them. Runtime/private state belongs outside caches.

## Incoming pull through a native manager

1. Reuse the registered method, package identity, source, resource selection,
   consumer host/version, access binding, update policy and concurrency evidence.
   Resolve the run's candidate commit or immutable HTTP artifact and inspect its
   manifests and selected bytes. Detect changed hooks, MCP, extensions, lifecycle
   scripts and package dependencies before native installation can activate them.
2. Verify Git operations use the registered repository-scoped identity. A native
   manager does not read our registry automatically. Establish a supported scoped
   SSH binding and verify it; do not silently use account-wide credentials. HTTP
   catalog authentication is separate: verify supported private access or report
   `access-blocked`. Never publish private skills publicly to avoid authentication.
3. Check current package content against its reconstructable installed baseline.
   Modified/unknown copies are preserved as conflicts, not overwritten with a
   force/reset update. Preserve unrelated packages and settings. Select the named
   package/marketplace, not an update-all or self-update command by default.
4. Fix the revision actually to be installed using the native client's supported
   immutable ref/local snapshot mechanism. A tracking branch is an update discovery
   policy, not an immutable version. Do not inspect commit A and install a moving
   branch that may now resolve to B. If exact binding cannot be supported, defer
   with `unsupported` or prepare an explicitly reviewed alternative. Record the
   tracking ref separately so a temporary pin does not accidentally end updates.
5. Execute only the reviewed native operation under the existing task/policy.
   Serialize operations affecting the same manager store/profile, including
   settings. Reuse documented manager locking or verified scheduler/maintenance
   exclusion covering all writers. Our file helper does not lock a native process,
   its UI or background auto-updater. Without a verified exclusion method, do not
   run overlapping/unattended updates; report `busy` or `unsupported`. Do not edit
   client caches/databases or create an arbitrary shell-command adapter to hide it.
6. Read back the source revision, installed package version and selected content
   hashes using supported read-only evidence. Catalog refresh alone is not package
   installation. Check unexpected deletions/additions and activation changes; do
   not adopt an unexpected revision as the approved baseline. Retain the previous
   installed baseline for failures, and describe partial cache/config changes.
7. Record source refresh, installed bytes, activation and actual host loading
   separately. Report `reload-required` when appropriate; reload/start only when
   authorized. A CLI help screen or cache directory does not prove a T3/SDK/IDE host
   loaded the package. Update registry records through the metadata guard only
   after verifying their current state; native operations and records are not one
   atomic transaction. Retain operation evidence for reconciliation after a crash.

Scheduled and manual pulls use the same procedure. Client background updates are
a separate updater: default to the registered scheduled/manual owner, and do not
turn on auto-update implicitly. If the user selects client-managed auto-update,
record its scope/timing and let our pull reconcile actual state rather than race
another updater. A refreshed source, installed package and active session can be
three different revisions; report that explicitly.

## Switching an existing consumer

Inspect all effective roots, complete companion files, enabled/manual-only
semantics, namespace changes and consumers of each shared copy. Verify a native
candidate in an isolated supported profile before cutover, or leave it staged
and pending. Do not expose two active editions to test which wins.

Retire a shared copy only after every consumer that needs it has a verified
replacement or compatible exclusion. If one native consumer still scans a shared
copy required by another consumer, use a supported per-resource exclusion/profile
or keep its existing file method. Never globally disable a skill name, break the
other consumer, or move vendor/system content. File retirement uses guarded_apply;
native activation uses the manager. These are coordinated, recoverable steps,
not an atomic transaction. Keep backups and separate failed/pending outcomes.

## Client interfaces: evidence, not an automatic adapter

Recheck installed versions/help before using these examples. SOURCE, MARKETPLACE
and PLUGIN below stand for verified registered values, not literal arguments.
Do not launch a client merely to obtain help if that host activates extensions.

| Client | Interface and update boundary |
| --- | --- |
| Pi | `pi install SOURCE`, `pi update SOURCE`, `pi list`; `/reload` or a new session reloads resources. Pi 1.5.0 help was checked on Windows: bare `pi update` updates Pi itself; `--extensions` updates all packages. `-e SOURCE` is temporary and can refresh at startup/reload, so it is for reviewed development use rather than our default unattended policy. |
| OpenCode V2 | `skills: ["https://example.invalid/skills/"]` loads an HTTP `index.json` catalog. Each skill lists relative files and a version. No universal refresh timer/CLI is asserted; establish the actual host's refresh mechanism before scheduling. A generic Git URL is not this catalog. |
| Codex | `codex plugin marketplace add SOURCE --ref REF`, `codex plugin add PLUGIN@MARKETPLACE`, `codex plugin marketplace upgrade MARKETPLACE`, `codex plugin list --marketplace MARKETPLACE --json`. Windows CLI 0.168.0-alpha.1 help was checked. Upgrade refreshes marketplace snapshots; verify installed bytes separately. Official guidance calls for a new session after install. T3/IDE behavior is not inferred from CLI support. |
| Claude Code | Register a Git marketplace, install `PLUGIN@MARKETPLACE`, then `claude plugin update PLUGIN@MARKETPLACE`; use the client's reload/new-session result. Custom marketplace auto-update is off by default in the checked docs. |
| Copilot CLI | Register a marketplace and `copilot plugin install PLUGIN@MARKETPLACE`; `copilot plugin update NAME` updates the selected plugin. Marketplace catalog refresh and installed-plugin update are separate operations. Verify the actual host/session refresh behavior. |

Documentation checked 2026-11-13; no live installations are claimed:

- [Pi packages](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/packages.md)
- [Pi CLI](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/cli.md)
- [OpenCode skills](https://opencode.ai/docs/skills/)
- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Codex plugin use](https://developers.openai.com/codex/plugins/)
- [Claude plugin management](https://code.claude.com/docs/en/plugins/install)
- [Copilot plugin reference](https://docs.github.com/en/copilot/reference/cli-plugin-reference)

## Offline packaging helper

If the collection opts into native packaging, keep `distribution.json` at its
root. Format 1 contains exactly `formatVersion`, a unique kebab-case `name`,
numeric `major.minor.patch` `version`, `description`, `owner`, `skills` (each with
`name` and an explicit skill-relative `files` list including `SKILL.md`), and
`notices` (explicit root-level attribution files, possibly empty). No client
settings, secrets, service URLs, credentials or automatic install scripts belong
in this file. Names must distinguish independent collections.

Use the bundled `scripts/build_distribution.py` with existing Python 3.10+:

```text
python /installed/sync-agent-assets/scripts/build_distribution.py --root /collection --working-tree --check
python /installed/sync-agent-assets/scripts/build_distribution.py --root /collection --ref FULL_COMMIT --output /new-release-directory
```

For a new package or version/membership change, `--working-tree --metadata-output
/new-directory` renders the six proposed native manifests without changing source.
Review/apply that proposal with the canonical change, then run `--check` again.
The metadata proposal validates selected files but intentionally does not require
the old source manifests to match yet.

These are argument examples, not platform-independent literal paths. The first
checks a development snapshot. The second reads immutable Git blobs, validates
the package/marketplace manifests against the explicit selection, and writes a
new directory outside the source tree. No fetch, installation, upload or cleanup
runs. Missing/linked files, unlisted companions, extra discovered skills, native
entrypoints outside the skills-only contract and inconsistent manifests fail.
The file allowlist is not a content/secret scanner: review permitted content.

Output contains `package/` (Pi package and plugin/marketplace formats sharing one
skills tree), `catalog/` (OpenCode index plus skill trees) and `release.json`
(source commit or explicit development marker, output file hashes and aggregate
digest). Catalog versions include every companion and notice hash. Preserve
required notice files per skill. Scripts are data and are not executed; use their
declared interpreters, not an assumed executable permission bit on exported files.

Commit the thin native manifests with the canonical skills if using direct Git
packages. Root plugin.json serves portable Agent Plugins readers (including
current Codex/Copilot); matching .codex-plugin/plugin.json and
.claude-plugin/plugin.json provide compatibility metadata. The two
marketplace files refer to the same root plugin. They are metadata, not copies of
the skills. Validate this root layout in the actual client before fleet migration.
Do not add incompatible metadata or executable components to bypass a missing loader.

For HTTP publication, upload one reviewed immutable catalog release to an
authorized endpoint, then change the configured source/release pointer coherently.
Build into a new destination; the helper will not overwrite an existing release.
Publishing and private access setup require their own task authority. Generated
artifacts stay outside the source tree; no HTTP server or CI deployment is created.
