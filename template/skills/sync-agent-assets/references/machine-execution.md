# One executor per machine, independent client outcomes

Use one authorized executor per selected machine/user execution context for a
normal pull. A machine with four installed clients does not need four LLM runs.
The executor can use each client's supported CLI/RPC/app-server interfaces to
manage all selected local profiles. Different OS users, protected profiles or an
explicit executor restriction can require separate authorized contexts; do not
cross them merely because they share hardware.

Client ownership describes configuration/cache boundaries, not which model must
perform the operation. Native managers still own their caches and file targets
still use the guarded helper. An unavailable consumer model/provider does not
block a supported local package-management or discovery command. Do not substitute
models to pretend that model-level verification succeeded.

## First setup versus routine pull

At setup, discover selected clients/profiles once, verify their installation
method and update/discovery interfaces, establish local access bindings, inspect
duplicates and record each client's capability evidence. Register which targets
and effects the machine executor may manage. A current task or existing policy
already covering those clients/effects needs no new per-provider opt-in. Honor an
explicit owner/executor restriction and do not infer cross-user/admin authority.

Routine pull reuses still-valid registrations and evidence. Recheck changed
versions, paths, policy or capabilities, not every unchanged client setup. Never
launch a client conversation just to ask whether a package exists.

## Machine-local execution

1. Read the local registry/policy and resolve the assigned consumers, including
   unavailable profiles. Reuse an approved executor on that machine; do not pick
   a new provider/model because another consumer uses it.
2. Resolve/verify the selected canonical and upstream snapshots once for this
   machine, using its access bindings. A coordinator can supply fixed identities;
   each machine verifies them locally. Native managers may need their own fetches,
   but the reasoning/planning step is shared rather than repeated per client.
3. Group file work by physical scan root and native work by manager store/profile
   and package identity. Update each shared file target once. Keep each native
   package store, profile settings and their supported update interface distinct.
4. Execute the reviewed eligible operations under existing file locks and verified
   native-manager exclusion. A single executor is not itself a concurrency lock:
   another manual or scheduled run may overlap. Preserve local changes, use
   bounded busy/deferred results and continue independent targets.
5. Verify installed state and native discovery separately for every affected
   client/profile. Prefer supported non-LLM CLI/RPC/app-server checks. Launch a
   model session only for an explicitly needed model-behavior check with its
   effects authorized, not to obtain another installation receipt.
6. Persist local records and return one machine report containing per-client and
   per-asset outcomes. Do not claim a whole machine succeeded because one client
   updated. Keep private config, logs and credentials local.

## Scheduling and manual fleet distribution

For normal scheduled pulls, each machine can run its own task independently.
Do not create/change schedules just by reading this contract. For a manual fleet
request, a coordinator resolves the target/source set and dispatches at most one
normal worker per selected machine context. It may do its own machine locally.
The worker receives all selected clients on that machine, not one packet per
client. Use the actual host's supported delegation lifecycle; a worker does not
recursively delegate. No matching authorized machine executor means a deferred
machine, not a silent provider substitution or a fallback to twelve client runs.

The packet names collection, mode/operation ID, immutable source identities,
machine context, client/profile selection, policy/effect limits and expected
machine report. Do not transfer other machines' paths, credentials or raw state.
Missing local access affects only its dependent targets. Offline/failed machines
remain in the aggregate report; others need not wait for them before completion.

Record one run-local `executor` identity (machine, OS user, host/client/profile,
operation ID), the resolved target snapshot, and client results referencing the
physical/native installation records. Consumer `ownerId` remains the identity
of a configuration scope, not a requirement for a separate LLM or record rewrite.
Policy may optionally name a `pull.executor` with its local identity and permitted
client/profile targets. Existing authorization governs when no preferred executor
is registered; absence is not a grant. Changes to preferred executors do not
change asset ownership or installed baselines.

To assess latency, record observed wall time for source resolution, planning,
updates, discovery and any human wait/deferred work in the local run report.
Removing repeated discovery/LLM handoffs should reduce coordination overhead;
network, client startup, authentication, conflicts and reloads still take time.
Do not claim a speedup factor from the number of workers or invent a fleet
benchmark from isolated local loader checks.
