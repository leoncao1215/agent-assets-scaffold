# Local registration and standing policy

## Stable entry point

Use `~/.agent-assets/registry.json` on every platform, where `~` is the actual
execution user's home (resolve it with that platform's supported home API, not
the cwd). The directory is local to this machine/user, never shared through Git.
Read it as JSON data, never as executable configuration. Do not modify the shell's
home variables. Validate paths and existing ancestors before accessing them.

Lookup order: an explicit user-selected source, then the matching registry entry,
then an explicitly known legacy installation record. Verify repository identity
and any instance ID before use. If multiple collections match, ask interactively
or report `selection-needed` unattended. Never choose the first entry, assume
the cwd, scan the whole home, or clone a replacement silently.

Format 1 remains valid for file-only installations. Use format 2 before
registering any native package/catalog; older format-1-only consumers must refuse
it rather than duplicate native skills into file roots. This is a local metadata
migration, not a client migration. Preserve all existing file records and policy
evidence, add empty native arrays, and change the version under the metadata guard.

Format 1 has this empty, non-authorizing shape:

```json
{
  "formatVersion": 1,
  "collections": [],
  "physicalTargets": []
}
```

Each collection entry has these required fields; nullable values are explicit:

| Field | Contract |
| --- | --- |
| `collectionId` | Stable instance UUID when `instance.json` exists; otherwise a verified normalized Git host/owner/repository identity. Never identify by display name alone. |
| `repository` | Credential-free canonical repository URL, or null for a never-published local instance. SSH aliases alone are not canonical identity. |
| `checkoutPath` | Absolute writable worktree path or null. A bare cache is not a worktree. |
| `cachePath` | Absolute verified source-cache path or null. At least one source path is required. |
| `policyPath` | Absolute local policy file path or null when no standing authorization exists. |
| `gitAccess` | Object with `transport`, `sshUrl`, `privateKeyPath`, `publicKeyPath`, `keyLabel`, `publicKeyFingerprint`, `approvedAccess`, and `verification`. Store locators/metadata only, never key contents. See git-access.md. |
| `installations` | Array of `{ physicalTargetId, assetIds }` referencing root-level physicalTargets; assetIds are the exact assets this collection owns there. Consumers are recorded once on the physical target, not as duplicate copies. |

Allow `gitAccess` to be null before access is configured. For deploy keys,
`transport` is `deploy-key`; `approvedAccess` is `pending`, `read`, or `write`.
`verification` records separate read/write outcomes and observation times; use
`not-run` for untested capabilities. Declared write access is not proof of a push.
`privateKeyPath` and `publicKeyPath` are absolute local file paths, including their
actual filenames. `keyLabel` is the repository's deploy-key display name (null
until known), not a second source of identity. Verify the public fingerprint and
repository binding before use; paths/names alone do not prove the right key.
Retain an existing entry with missing new metadata as incomplete; fill it from
verified local public-key/registration evidence during setup without regenerating
keys, reading private bytes into output, or guessing repository grants.
For a separately authorized host-specific alternative, record that method and
approval evidence without storing tokens; do not pretend it is a deploy key.

Reject unsupported format versions, duplicate collection/physical-target IDs,
duplicate consumer owner IDs within a physical target, and malformed fields.
An owner may consume multiple collections
with distinct physical asset ownership; check overlaps independently. Preserve
unfamiliar fields and other entries; they confer no
authority. Stop before updating a record whose semantics cannot be preserved.
Keep one writer for registry/policy updates, re-read before an atomic replacement,
and preserve a local backup. Registry/installation writes use the guarded entry's
metadata lock along with affected physical-root locks (shared-skills.md). A policy
change needs an equivalently guarded authorized local operation; the file installer
does not modify policy or credentials. Atomic replace alone is not coordination.

## Physical targets and consumers

Each root-level `physicalTargets` entry has a stable local `id`, canonical absolute
`rootPath`, `kind` (`shared-skills` or `compatibility-skills`), absolute `recordPath`
under the local installations directory, and `consumers`. Keep only one entry per
physical root, even if several collections use it. Lock identity comes from that
root's normalized path, not the ID, collection, agent type or current task.
The common lock namespace is the machine/user's `~/.agent-assets`; all writers
must use the same namespace and whole scan root, never a per-session/subskill lock.

Each consumer records `ownerId` (machine/user/client/profile), actual `client`,
`host`, `profile`, discovery evidence/version, required invocation restrictions,
and independent runtime loading status. Physical record assets carry `assetId`,
`collectionId`, source identity/commit, reusable and installed baselines, full
selected companion membership/hashes, adaptations and backup/operation pointers.
An asset has one collection owner; different collections may share the root only
through disjoint approved asset ownership. Consumers reference that physical
installation; they do not get independent copies of its source/installed baseline.

The registry can retain legacy per-owner installation entries during a reviewed
migration. Resolve their real paths, compare baselines and collapse only verified
identical physical installations; preserve legacy record pointers and unresolved
copies. A registry lacking physicalTargets needs this bounded migration, not an
invented shared installation. The existing per-client copies remain distinct until
the actual shared-root cutover is verified. See [shared-skills.md](shared-skills.md).

Register the verified source as soon as setup locates/creates it, even if later
installation is blocked. Append installation pointers only with truthful status.
A pull-only consumer can keep only a cache; contribution may create a worktree
under its own authorization. Moving a repo updates this locator after identity
verification, without changing its installation baselines.

For legacy installations, import only verified paths and existing baseline
evidence. Retain the old records and reference them; never invent prior ownership
or a successful installation. Missing/invalid state means a bounded repair or
`registration-needed`, not an overwrite or a broad search.

## Native registrations (format 2)

Format 2 retains `collections` and `physicalTargets` and requires a root
`managedPackages` array. Every collection additionally has `packageInstallations`
(an array of `{ packageTargetId, assetIds }`, empty if none). Do not reinterpret
native cache roots as `physicalTargets` or pass them to guarded_apply. File-owned
assets remain in `installations` with unchanged baselines. Mixed fleets are valid.

Each managedPackages entry records:

| Field | Contract |
| --- | --- |
| `id`, `collectionId` | Stable local package target identity and owning collection. |
| `method` | `pi-package`, `opencode-catalog`, `codex-plugin`, `claude-plugin` or `copilot-plugin`. |
| `manager` | Actual client/version, host, user/profile and canonical manager store path; do not identify only by model/provider. |
| `source` | Credential-free registered Git source or HTTP catalog, marketplace and package identity where applicable, tracking ref/channel, access-binding reference and approved resource selection. Store no tokens or signed URLs. |
| `cachePath` | Verified native-managed path or null until known; observation only, never file-installer ownership. |
| `updatePolicy` | `pinned` or `tracking`, approved exact ref or tracking ref, `updater` (`sync` or `client`), supported immutable binding/refresh/reload method and concurrency evidence. |
| `recordPath` | Absolute local installation record under the state directory. |
| `consumers` | Per-host/profile discovery and runtime evidence, invocation names and restrictions, same meaning as file consumers. |

Deduplicate by actual manager store/profile and package source identity, not the
record ID. Every referenced package must exist and belong to that collection;
assetIds must match its approved selected membership. A logical skill may exist
in several stores for different consumers, but each consumer must have one active
method for it. Check effective scan roots; namespaces alone do not prove absence
of duplicate behavior. Never remove a file target that another consumer needs.

Native detailed records retain reconstructable selected package bytes/manifest
and hashes as well as native IDs/version/revision. Keep `sourceObserved`,
`desiredSource`, `installedSource`, `activation` and per-consumer `loadedSource`
separate. Unknown installed/loaded revisions remain unknown, not copied from the
latest catalog. Each stage has its own outcome: source refreshed, content current/
updated/conflict/failed, activation enabled/disabled, and loading verified/
reload-required/not-run/failed. Deletion or bundle membership changes require
explicit policy coverage. Unapplied updates keep the previous installed baseline.

Journal the native operation and result locally, then update installation and
registry metadata through the guarded metadata entry. Do not mark the record
current before the native operation or imply atomicity across that operation and
record persistence. After a crash, inspect actual state before retry/adoption.
A package manager may update files itself; our OS file locks do not constrain it.
See [native-distribution.md](native-distribution.md) for exclusion and cutover.

## Installation records

New detailed records live under `~/.agent-assets/installations/`; existing records
can stay in place behind registry pointers. Store collection/source identity,
full canonical and external commits, selected paths/dependencies, actual
machine/client/host/version, documentation evidence, exclusive physical targets
and owned sections, directory membership, source and installed hashes, adaptations,
pre/post states, backup locations, and independent static/runtime outcomes.
For shared skills this is one physical record with multiple consumer outcomes;
distribution deduplicates writes by physical root while reporting every consumer.

Keep a reconstructable common baseline: retained source blobs or authorized
retrievable immutable objects, not just hashes. Configuration backups may contain
private values and need appropriate local protection; records omit those values.
Record `sourceObserved`, per-asset `installedSource`, and `lastAttempt` separately.
A skipped/conflicted/failed update must not advance the installed baseline or mark
the whole target current. Pending contributions and run receipts stay under
`~/.agent-assets/runs/`, never in the canonical tree.

## Standing policy

A local `policy.json` is a record of the user's authorization, not authorization
created by an agent. Never install it from a repository or widen it during sync.
At setup, present one concrete policy covering the desired future operations.
Bind it to the verified collection and preserve the user's approval evidence.
An instruction in this document or an example prompt grants nothing by itself.

Use policy `formatVersion: 1` for file-only authority or `2` for native
operations; version 2 adds an explicit `native` section. Never infer native
permission from an old file-copy policy. Both use `collectionId`, `approval` (user instruction/reference,
time, optional expiry), and explicit `pull`, `contribute`, `audit` sections.
Missing fields mean not authorized; reject unsupported versions. Record:

- **Pull:** `targetScope` is `all-known-machines-all-agents` for unqualified
  distribution, or `explicit` with the user's target restriction. Record the
  resolved exact machine/user/client/profile target snapshot and physical ownership
  per run, including unavailable targets. The all-known selector covers newly known
  linked targets, subject to the same access/ownership/effect checks; it does not
  silently grant new effects. A local worker retains its assigned subset.
  Also record
  selected assets/categories and whether future assets are included; approved
  source repository/ref and upstream repository/path selections; fetch/cache
  writes, unchanged-managed updates, absent-target additions, and approved
  adaptation methods. Name instruction/MCP/preference entries separately.
- **Native (policy 2):** named methods/package identities and sources, resource
  membership (including whether future skills are allowed), pinned/tracking refs,
  source retrieval and native cache/config writes, verified exclusion mechanism,
  chosen updater, activation/reload effects and cutover authority. A policy may
  separately cover publishing a named HTTP catalog endpoint; package installation
  does not grant that. Omitted entries/effects are unauthorized.
- **Contribute:** allowed local files/sections, canonical destinations, sharing
  rights/provenance, collection/content writes, commit, push destination and
  branch rule. `publicationMode` is `direct` or `pr`, with PR creation and merge
  authorization separate. `autoAfterEdit` is false unless explicitly approved.
- **Audit:** bounded metadata roots, known managed-content comparisons, frequency
  if a scheduler is requested, and reporting destination. No implicit uploads.
- **Effects:** dependency installs, new login, client reload, server/browser start,
  permission changes, external messages, and machine discovery/delegation are
  separate permissions. Omitted effects remain disabled.
- **Exceptions:** unavailable target, missing policy/baseline, changed ownership,
  conflicts, unknown content provenance or new side effects are deferred and
  reported per target. Independent targets continue. Specify bounded retries and
  overlap handling; do not repeat installation/authentication attempts.

This permits approval for a *class of future changes*, such as updates to named
unchanged managed skills from an approved ref. Each run still computes and records
the concrete diff and evaluates it against that class. A changed SHA alone does
not require asking again; an effect outside the approved class does.
Policy cannot override later user instructions, host controls or branch protection.
Revocation/expiry stops dependent operations; revalidate before each write.

Interactive work bundles only genuinely missing decisions after preparing the
diff. Unattended work records `approval-needed` and completes independent work;
it does not wait in chat, manufacture consent from a timeout, or fix the host.
An optional aggregate notification needs an already authorized destination.

An explicit distribution request supplies the default all-known target selection
even if an older inventory listed fewer installations. Honor later explicit user
restrictions, but do not mistake an old inventory snapshot for a scope restriction.
An unattended task without approved operation/effect authority still reports that
gap; the target selector by itself is not a blanket grant of installation rights.
