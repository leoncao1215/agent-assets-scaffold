# One physical skills installation, multiple consumers

## Layout and evidence

Prefer `~/.agents/skills` for reusable skills on each machine/user **when the
actual client and host support discovering that root**. Keep native roots for
vendor-managed content (including Codex `.system`), required exclusive adaptations,
and compatibility copies for consumers without shared-root support. Configuration,
MCP settings, preferences and user instructions remain client-specific.

Verify discovery for each actual client/version/host/profile, not just its model
or another client's documentation. A standalone CLI and an embedding host can
differ. Explicit instruction text pointing at a skill is not evidence that the
loader advertises/discovers it. A supported extra skill-root setting can be proposed
when needed, with its own narrow config authorization; do not assume native support.
Record `documented`, `observed-loaded`, `unsupported` and `unverified` separately.
Missing runtime permission leaves validation pending, not automatically supported.

Multiple effective scan roots must not contain the same logical skill name.
Do not depend on undocumented precedence or disable a name globally to hide a
duplicate. If a client scans shared content but needs an incompatible exclusive
edition, establish a documented per-root exclusion/profile separation first;
otherwise keep that asset's migration blocked. One consumer's manual-only/disabled
semantics or path adaptation cannot silently become the default for everybody.

## Physical installation versus consumers

The registry's `physicalTargets` describes canonical machine-local scan roots,
not one copy per provider. Collections reference them by ID; each physical target
has a single installation record containing per-asset provenance and baseline,
and a `consumers` array with per-host discovery/loading evidence. See local-state.md.
Different collections may own different assets in a root, never silently the same
asset. Several aliases of a path are one physical target, not extra installations.

For distribution, resolve all requested machine/agent consumers, group by verified
physical root, and prepare one write plan per root. Each consumer verifies its own
host behavior; it does not reinstall identical bytes. Separate machines retain
independent physical installs, credentials, hashes, backups and outcomes. A broken
consumer does not prevent already-supported consumers from receiving safe updates.
Deduplication does not claim that every consumer loaded the shared result.

## Migrate existing copies deliberately

1. Inventory only selected source/destination skills and all required companions.
   Compare complete selected manifests and reusable semantics, not just SKILL.md
   or names. Exclude runtime/private state before content collection. Do not copy
   vendor `.system`, unrelated skills, credentials or one client's configuration.
2. Record each copy's real provenance and installed baseline. Byte-identical
   content can be adopted; local-only changes, path wrappers, invocation restrictions
   and disabled/manual-only behavior need a reviewed common edition or retained
   exception. Do not choose an arbitrary agent's copy as authoritative. Verify
   each machine independently; prior remote receipts are not a current disk audit.
3. Verify shared-root discovery and required restrictions in the actual host using
   an authorized isolated loader check/profile or a distinct temporary probe name,
   without exposing two active same-name editions. If this cannot be verified,
   stage the candidate outside all scan roots and retain the original installation.
4. Preview the exact shared files, each old file to retire, preserved exceptions,
   consumer mappings and physical records. Only after the common edition and host
   support are verified may the approved cutover remove old copies from scanning.
   Use the guarded entry below, holding every affected scan-root lock. Retire old
   SKILL.md entries before exposing the shared same-name entry; a short unavailable
   interval is preferable to duplicate discovery. Keep every selected companion
   backed up outside scan roots. Do not retire a still-needed compatibility copy.
5. Verify the resulting manifests and each authorized consumer's loading. The
   helper verifies files only; runtime checks remain explicit, with failure recorded
   per consumer. If runtime checks run later, update their records in a new guarded
   plan after revalidating the installed state. Failed loading is not migration
   success. Restore only from a new reviewed rollback plan against current hashes,
   under the same locks; never overwrite later edits or reintroduce duplicates.

There is no claim of an atomic whole-directory cutover for readers. Coordinate
with live readers/reloads when needed. A crash may leave a partial cutover; retained
plans, receipts and backups identify what needs recovery. Do not silently resume
using fabricated baselines or delete recovery evidence.

## Guarded file application

Use the bundled `scripts/guarded_apply.py` for approved regular-file installation,
update, retirement/cutover and local registry/installation-record writes. It requires
an existing Python 3.10+ runtime, no packages. If unavailable, report the target
blocked or use a separately reviewed equivalent with demonstrated OS locking;
do not install Python or fall back to unlocked shell copies implicitly.

All cooperating sessions, regardless of provider or agent type, use the same
canonical **whole scan root** (not individual skill subdirectories), resolved paths,
and `~/.agent-assets` state directory. Lock filenames are SHA-256 of normalized
absolute physical scope paths under `~/.agent-assets/locks/`, outside scan roots.
Collection IDs, agent names and operation IDs do not change lock identity. For
shared directories across OS users, establish one mutually accessible protected
lock namespace first; per-user defaults cannot coordinate different users.
Use local filesystems. UNC/network filesystems and unusual mount/alias arrangements
need a separately verified implementation; they are not claimed supported here.

The process actually writing files opens Windows handles with sharing disabled,
or holds POSIX flock descriptors, until baseline recheck, backup, writes, static
verification and receipt persistence finish. No subprocess performs the writes.
Acquisition is ordered with a bounded 0–60 second total wait (default 10); `busy`
does not launch a replacement writer. Registry/installation metadata uses an
additional shared metadata lock; unrelated physical targets can proceed when they
do not need the same metadata transaction. OS process termination releases handles.
Permanent lock files are not stale locks: never delete them or use PID/existence
checks as the mutex. Do not acquire a lock in one command and write in another.

These are **cooperative writer locks**, not protection against non-participating
manual edits or arbitrary code. Hash and membership checks detect many such edits
but do not eliminate their TOCTOU races. The helper is not a permission engine:
the agent still checks authorization, provenance, correct registry ownership,
host support and private-content exclusions before building the plan.
During rollout, finish or explicitly stop legacy installation jobs before cutover
and route future writes through this protocol. Merely adding the helper to Git
does not retrofit locks into old installed skills or running sessions; report
those writers as not yet migrated rather than claiming machine-wide enforcement.

### Plan format 1

The plan is JSON data with exactly these top-level fields:

| Field | Meaning |
| --- | --- |
| `formatVersion` | Integer 1. |
| `operationId` | New canonical UUID; also the recovery directory name. Never reuse a previous applied/partial operation. |
| `roots` | Absolute registered whole scan roots involved in this transaction. No nested/duplicate roots, home/drive roots, links or vendor/Git targets. Include native roots being retired and the shared destination. |
| `directories` | Array of `{path, entries}`: immediate membership of every target parent through its scan root, null for absent directories. Read names only; never recursively hash unrelated skills. |
| `files` | Ordered array of `{action, target, beforeSha256, source, sourceSha256}` as below. |

`action: write` takes an absolute reviewed regular source file with its lowercase
SHA-256, an absolute target, and the expected target SHA-256 (null if absent).
`action: retire` requires a non-null target baseline and null source/hash. Retired
bytes are backed up before unlinking the named file; no recursive delete occurs.
The helper leaves empty directories. It refuses `.system`/`.git` target components,
symlinks/reparse points, hard-linked files and paths outside the approved roots.
On POSIX, add `beforeMode` for existing targets and `afterMode` for writes, as
integers containing only ordinary permission bits (0 through 511 decimal).
Capture and approve these with the hashes, preserving executable companions.
Mode drift is checked after locking; special bits are rejected. Omit these fields
on Windows, where existing-file DACLs are preserved by the replacement API.

Registry JSON and JSON records under the state directory's `installations/` may
also be explicit write targets. Prepare their merged contents as reviewed sources,
preserving other records. They use file-hash baselines and the metadata lock, not
directory snapshots containing volatile run state. Put metadata writes last.
Validate their documented schema in planning; the helper checks JSON-object syntax
and exact bytes, not the full registry semantics. Credential policy/key files are
not targets of this installer.

Capture the plan's SHA-256 in the approved task/plan, then invoke once in the actual
shell, with literal correctly quoted paths. Example argument shape (not a command
to execute unchanged):

```text
python /absolute/skill/scripts/guarded_apply.py --plan /absolute/reviewed-plan.json --plan-sha256 <approved-sha256> --timeout 10
```

`--state-dir` is for an explicitly agreed common namespace or isolated tests;
never pick a per-session directory to bypass contention. The helper checks the
approved plan digest and rechecks it, target hashes, directory membership and
source bytes **after acquiring locks**. It backs up all selected existing files
before the first mutation. Source bytes are captured and verified, not executed.
Windows replacements preserve the existing file DACL via ReplaceFileW; new files
and backup directories inherit their parent access. Protect the local state root
appropriately before use. Windows backups use CopyFileW (including security
metadata on supported modern Windows); POSIX backups retain file metadata and
receipts record permission modes. New Windows targets inherit destination access:
restoring a retired file's custom ACL is a separately reviewed recovery step under
the same guard, not something inferred from the source bytes. POSIX replacements
apply approved modes and retain available metadata; cross-user ownership or special
ACL requirements need validation. Runtime loading is not tested by this helper.

Exit 0 means file/static application complete, 3 means busy, 4 means baseline
drift, and 2 means invalid plan/IO failure. Recovery evidence lives under
`~/.agent-assets/runs/<operationId>/`: the reviewed plan, original bytes and receipt.
`runtime` remains `not-run`. A failure after writes can be partial; inspect that
receipt before a new plan. It never automatically rolls back or deletes evidence.
Recorded before/after hashes support recovery even if a process crashes between
a write and its receipt update. Read-only preflight planning is allowed unlocked;
the final baseline decision and all mutations must use this entry.

For an unsupported adaptation needing native setters, keep its client-exclusive
scope separate and use an equivalent reviewed in-process guard with the same scope
protocol; do not claim the regular-file helper implements arbitrary client adapters.
