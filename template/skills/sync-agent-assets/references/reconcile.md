# Ownership and non-destructive reconciliation

Use this contract for selected targets and contributions. Pull does not require
contribution collection. A named contribution does not require consumer inventory.
There is no global all-owner completion gate.

## Select once and assign physical ownership

Stay within one verified collection and its approved local policy. With instance
metadata, verify its ID as well as repository identity; other collections do not
share targets just because they use this skill. A model/provider name alone is
not proof of the actual client, host, user or profile being configured.

For unqualified **distribution / 下发**, all known machines and all their agents
are selected by default. Resolve their identities using the host/linked inventory
and bounded passive discovery; do not ask for per-machine/agent opt-in again.
Explicit target restrictions take precedence. Include unavailable targets and
unknown inventories in the result instead of silently excluding them.

For standalone current-agent setup or an explicitly restricted pull, retain that
scope and offer expansion only when relevant. Use each machine's own inventory,
paths and access; no whole-home/network scanning, automatic linking or provider
substitution. Registered ownership and capability evidence can be reused; new
targets still need verified physical ownership and supported loading. The default
fleet selector does not permit reading unrelated private content or other collections.

Each selected agent owns its client-exclusive installation scope. One coordinating
owner handles each shared physical directory/configuration section, including
aliases or mounts referring to the same target. Resolve overlaps before dependent
writes. Different source repositories do not isolate shared user skill directories.
Do not silently edit another client's settings merely because they are writable.
For supported skills loaders, use one physical shared-root installation with many
consumers rather than separate provider copies. Native-only assets and client
configuration remain exclusive. Follow [shared-skills.md](shared-skills.md) for
semantic migration and the actual cross-instance OS lock protocol. Any cooperating
instance may become the writer after acquiring the same physical-root lock; naming
a coordinator for one round is not a global mutex. Do not use the agent type or
individual skill subdirectory as the lock scope.

Use supported delegation only within the authorized scope and host lifecycle.
Use the host's supported provider/environment inventory and delegation interfaces
only when needed; no particular workbench or tool name is required. Without a
matching executor, report a manual/blocked target; do not install an orchestrator,
switch providers or invent transport. Source access failures affect dependent
targets only, not unrelated installations.

A bounded delegate receives the verified collection, fixed canonical/external
commits, selected assets/companions, machine/client/physical ownership, mode and
operation ID, baseline/policy evidence, allowed effects and expected results.
It does not rediscover scope, ask already answered questions, delegate again,
publish during pull or alter the frozen source. Return exact per-asset outcomes,
conflicts, local record pointers and separate static/runtime evidence. Never
send raw private configuration, credentials or other machines' installation state.

For a coordinated pull, resolve source inputs once and distribute their identities;
each owner retrieves/verifies them with its own registered access. Parallel work
is allowed for non-overlapping targets. A failed, cancelled or unreachable target
is neither synchronized nor a no-candidates result; report it and finish independent
work. Follow cancellation to termination before replacing a potential writer.

## Baseline decisions

Compare reusable content after accounting for *recorded* adaptations. Never label
unknown local edits as mere formatting. Preserve a reconstructable common baseline
`B`, current selected local content `L`, and proposed canonical content `R`.

| State | Pull | Contribution |
| --- | --- | --- |
| New selected asset, target absent and never installed | Install if additions are authorized. | Verify provenance and selected destination. |
| Local and canonical reusable content equal | Managed target: record no-op; unknown target: adopt only with authorization. | No empty commit/push. |
| `L = B`, canonical changed | Update under policy, preserving unrelated entries. | No return change needed. |
| `R = B`, local changed | Preserve; report pending contribution. | Propose sanitized local diff. |
| Both changed | Preserve affected asset; report conflict/divergence. | Review both diffs and a three-way proposal, even if Git merges cleanly. |
| Same name, unknown baseline or another owner's target | Preserve; adoption/merge needs explicit decision. | Establish provenance/baseline or report blocked. |
| Local-only asset | Leave local; no automatic upload. | Select actual content and rights before proposing. |
| Previously installed target missing or source removed | Report possible deliberate removal; no automatic delete/resurrection. | Removal requires an explicit reviewed proposal. |

An unrelated dirty source checkout does not prevent reading immutable committed
objects. Inspect Git tree entries and materialize only selected regular blobs in
an approved cache, without executing checkout hooks/filters, submodules, LFS or
source code. Never clean/stash/reset user work. Uncommitted development inputs
require a complete approved file/membership/hash manifest; do not auto-commit them.

Read only approved file/section contents and companions. Metadata inventory is
not permission to recursively hash/read/upload everything in a skill directory.
Exclude auth/token files, logs, histories, caches, generated output and machine
bindings before content collection. Hashing does not authorize publication.
Keep private upstream content upstream unless sharing is explicitly permitted;
preserve source ownership, attribution and fork baselines.

## Full installation and exceptions

A full selection includes canonical skills, catalog references, real MCP entries,
optional instruction supplements and matching preference profiles, with necessary
companions; examples, category README files, project-owned assets and explicit
omissions are excluded. List installed/current/preserved/unsupported/blocked items.
Missing business inputs needed when invoking a skill do not prevent installing
its files. Runtime prerequisites and permissions are separate from file placement.

Preserve local enable/disable choices. An MCP default is intent, not launch
authorization. Stage disabled only when supported and consistent with approved
effects; if writing would start a server without authority, defer it. Permission,
plugin, dependency and authentication changes require their own authorized scope.

If an explicit task combines contribution and distribution, only the specified
published change is a dependency. Do not reintroduce a machine-wide collection
barrier. Migration of an in-progress legacy round requires explicit phase/source
binding and stopping obsolete writers; do not cancel another live task merely
because a new skill version exists.
