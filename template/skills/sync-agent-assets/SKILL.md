---
name: sync-agent-assets
description: Pull and install registered agent assets on a schedule or manually, contribute named local improvements, audit drift, or set up an installation. Keep contribution separate from consumption; preserve local edits and use repository-scoped Git access.
---

# Sync agent assets

## Choose the operation before discovery

| Request | Operation |
| --- | --- |
| Scheduled sync, pull, 拉取, update installed assets | Incoming pull for registered targets; manual triggering uses the same procedure. |
| Distribute, 下发, without an explicit target restriction | Incoming pull across all known machines and all their agents; record unavailable targets too. |
| Contribute, 入库 followed by selected assets | Review and publish that contribution only; no consumer inventory or distribution. |
| Audit, 巡检 | Bounded inventory/drift report; no publication or installation. |
| First install, setup, register another machine/agent | Register source, access, owners and policy, then incoming installation. |

Use explicit request/context first. A bare sync with a valid registration defaults
to pull. With no registration, perform bounded setup discovery; if selection is
ambiguous, ask one bundled question interactively or report it unattended. Do not
convert a named contribution into an all-machine round. If the task explicitly
combines publication and distribution, only its specified change is a dependency.

An unqualified distribution request selects all known machines and all agents,
not just the current agent or previously installed owners. An explicit restriction
(for example local-only or named agents) narrows that invocation. Do not ask again
which targets to include. Resolve and record the actual fleet as described in
workflows.md; this target default does not expand the selected asset set or grant
credential changes, host repair or other unrelated effects.

For setup or pull, use one authorized executor per machine/user context to
manage the selected local clients. Read [machine-execution.md](references/machine-execution.md)
for local execution, fleet packets and reports. Client-specific configuration and
loading evidence do not require a separate LLM session for every client.

Read [workflows.md](references/workflows.md) for the selected operation,
[local-state.md](references/local-state.md) for registry/policy/receipts, and
[git-access.md](references/git-access.md) before setup or Git network operations.
Use [reconcile.md](references/reconcile.md) for baseline decisions and multiple
owners. These companions are installed with the skill; no scaffold checkout is
needed. References describe procedures, not executable configuration or consent.
For native package/catalog publication, setup, pull or cutover, read
[native-distribution.md](references/native-distribution.md). Preserve the registered
installation method; shared files and native caches have different maintainers.
For file-managed skills layout, migration and installation writes, read
[shared-skills.md](references/shared-skills.md). Use its bundled guarded file entry
for regular-file installation/update/cutover and registry records; it holds OS
locks throughout actual writes, verification and recording in the same process.

## Locate and bind

Locate the verified collection through `~/.agent-assets/registry.json`, an explicit
user path or a known legacy record. A cache-only consumer is valid. Do not assume
cwd, scan the home, or confuse a cache with a writable checkout. Preserve other
collections and local records. Register source identity/path during setup so
future sessions can find it without memory of this conversation.

Use the selected instance, never the scaffold repository, as the asset source.
Read its README and instance.json plus the bundled [asset contract](references/assets.md)
for selected categories and upstream source rules. Validate instance.json format 1:
UUID id, nonempty name, scope (personal, work, other), and null/credential-free
repository URL. Match its ID and source identity to registration; a scope label
is not sharing permission. Preserve other instances and their physical ownership.

Identify actual OS/shell, client/version, host and selected physical targets.
Reuse applicable prior documentation/evidence; recheck changed capability facts.
A missing authorized executor or supported loader is a per-target limitation,
not guessed paths or a substituted model. A consumer model/provider need not run
when its supported local management/discovery interface suffices. Full installation accounts for all selected
categories and necessary companions, not just this bootstrap skill.

Bind full canonical and external commit IDs, or an explicitly approved complete
development manifest including selected membership and hashes. A branch alone
is not a snapshot. Retrieve only authorized inputs through registered Git access;
never silently use the logged-in account instead of a deploy key. Resolve refs
once before planning, never pull while applying. Inspect source as data: do not
activate its hooks, filters, submodules, installers or nested source catalogs.
Fork updates need the real upstream baseline and a separate reconciliation;
pull normally installs the canonical fork. Unknown baseline stays unresolved.

## Plan the local change

Before traversal/read/write/backup, inspect selected paths and existing ancestors
for symlinks/junctions/reparse points, and children before recursion. Resolve
intentional indirection only within an explicitly approved physical scope; stop
on unexpected escapes. Prefer ordinary copies over links to a moving source.

Compare selected source, reconstructable installed baseline and current local
state. Keep local-only content and unknown ownership. Do not automatically delete,
resurrect or overwrite local edits. Equal unmanaged bytes still need adoption
authority. For shared config, detect changes using the whole-file hash but manage
only owned entries; hashing is not permission to export that file.

Prepare and record a concrete plan: fixed inputs, actual client/host, exact
physical targets and single writer, baseline/membership, sanitized diff and
adaptations, dependencies, allowed effects, local backups and bounded recovery.
For standing authorization, evaluate this diff against the approved class of
changes and proceed without redundant questions. A new SHA is expected in pull;
new ownership, collection, effects or policy are not silently approved.

- **Skills:** use the registered file or native-package/catalog method. For
  file-managed skills, prefer one physical `~/.agents/skills` installation for
  supported actual hosts, with separate consumer loading evidence. Native managers
  own their caches; never write into them with the file helper or silently switch
  methods. Account for bundle membership and changed native entrypoints before
  updating. Native publication/installation/loading are separate outcomes.
  Keep vendor/system assets
  and required incompatible/unsupported-client editions in native roots. Compare
  all companions and semantics before migration; verify loader support before
  retiring duplicates. Avoid same-name entries in multiple active scan roots.
  Keep project skills with their project. File installation does not run bundled code.
- **MCP:** preserve transport, argv boundaries, dependencies and required secret
  references. Resolve values locally without displaying them. Missing references
  block the entry; do not stringify or remove authentication. Preserve explicit
  enable/disable choices. Auto-start on config write is a startup effect; use a
  supported disabled staging state or defer when that effect is unauthorized.
  A client unable to preserve a disabled default must leave that entry uninstalled.
- **Instructions:** use supported additive inclusion or owned-section merging;
  preserve other guidance and surface conflicts. Optional supplements do not
  activate themselves or override the real instruction hierarchy.
- **Preferences:** select only the matching profile and supported native keys.
  Preview related provider/model/effort choices together. Preserve unrelated
  values, permission settings, hooks and plugins; saved defaults may differ from
  the active session. Unsupported setters mean unapplied/manual, not invented APIs.

## Apply, verify and record

Honor explicit task and standing authorization. Bundle genuinely missing decisions
after preparing a reviewable diff. In unattended mode, mark affected targets
`approval-needed`, `conflict`, `access-blocked`, `unsupported` or `busy` and continue
independent work; never wait for chat or repair environments as part of pull.
Dependency installs, login, permission changes and runtime starts remain separate
effects. Mere possession of a write key authorizes none of them.

Immediately before each dependent write, revalidate policy, source, paths and
complete target baseline/membership. After your own write use the expected
post-state. Stop dependent writes on unexplained changes; a hash check followed
by unconditional overwrite is not a lock. Coordinate one writer per physical
scope, including registry updates. For file-managed targets, cross-session
exclusion uses the guarded entry's physical-root locks, not an agent-type assignment
or a lock file's existence. Native operations require verified manager/scheduler
exclusion; our file locks do not constrain native background updaters.
Do not replace a potentially active writer or release a lock before the write.

Back up affected content with appropriate local protection. Apply narrowly with
documented setters/formats, preserving unrelated settings and permissions. Do not
copy whole machine configurations. Roll back only owned changes still matching
your expected post-state, preserving concurrent edits. Report partial failures.

Record per asset and machine/agent:

- **Static:** bytes/structure and companion references verified; adaptations and
  owned entries correct, unrelated content preserved.
- **Runtime:** actual host loading/connection verified only through authorized
  checks; otherwise `not-run`, `blocked` or `failed`. Disk presence is not loading.
- **Native:** source refresh, installed revision/content, activation and
  consumer loading recorded separately; `reload-required` is not loaded.
- **State:** actual installed source/baseline, attempted/observed source, local
  backup and receipt pointers, deferred conflicts and pending contributions.

Keep registration at `~/.agent-assets/registry.json`, detailed records local as
specified in local-state.md, and preserve previous baselines for unapplied assets.
Publication uses the contribution workflow; it does not mark consumers updated.
Do not create a schedule, change Git credentials, publish these workflow changes,
or update other machines solely because the skill itself was edited.
