# Optional contributions and multiple targets

Use only when the user requests contributions, multiple clients, or multiple
machines. A simple incoming sync does not require discovery or contribution
collection. T3 or another orchestrator can implement coordination when available;
no specific tool names, provider, or orchestration product are required.

## Select and assign ownership

Keep one instance per reconciliation round. Identify it by `instance.json.id`
and the verified source checkout. Do not add a different instance, personal
machine, or work machine merely because it is discoverable or connected.

Use supported passive discovery within the authorized scope. Offer additional
local agents and linked machines as separate choices when discovery is requested.
Do not scan the network, read unselected client directories, launch providers,
link machines, or infer permission from connectivity. Respect explicit selections.

Assign one writer per physical target, including shared directories and owned
configuration sections. Resolve overlaps before applying anything. If delegation
is requested and supported, verify the selected executor's actual client/host and
give it a bounded brief: instance, source, target ownership, phase, authorized
effects, exclusions, and expected result. A delegated executor must not expand
scope, launch more delegates, publish independently, or install an earlier source.

Use the host's supported delegation lifecycle. If no suitable executor is
available, report the gap and provide a manual handoff; do not assume one model
can configure every client's live host. Coordinator-applied changes are possible
only within explicit authorization and verified support for the selected target.

## Incoming-only distribution

Freeze one canonical source snapshot and selected upstream commits. Each target
verifies that same content through its own authorized access, prepares its local
plan, and applies authorized changes. No local contributions or repository push
are needed. A dirty source requires an explicit complete snapshot transfer; its
base commit does not identify those uncommitted bytes.

Report each target separately. One successful installation does not establish
that every selected target succeeded. Do not copy credentials, adapted machine
configuration, or local install records to make another target match.

## Contribution plus distribution

Use three phases when local improvements are part of the task:

1. **Collect:** each selected owner returns exact reusable candidates, a
   no-candidates result, or a blocker. Inventory metadata first; read and return
   only selected content after removing private bindings and checking rights.
2. **Integrate and freeze:** one coordinator deduplicates and reviews candidates
   against the instance baseline, resolves conflicts, and makes the authorized
   repository changes. Publish only if authorized and needed for distribution;
   otherwise agree on a complete local snapshot. Freeze the resulting canonical
   and upstream source versions before any target installs.
3. **Distribute:** all targets re-preview against that final snapshot, recheck
   local state, and apply only approved changes to their owned scope.

Wait for all selected contribution results or have the user explicitly defer
missing participants. Do not let a target install early or let multiple agents
push competing changes. Keep round records local and report partial results.

## Contribution boundaries

Contribute to the selected instance only. Preserve upstream ownership and fork
baselines; do not copy private upstream content merely because it can be read.
Do not harvest whole skill directories or client configuration trees without
selecting their actual content and necessary companions.

A machine override may be intentional and should remain local. Credentials,
auth caches, paths, histories, installation records, raw diagnostics, and private
service catalogs are never implicit contribution candidates. Publication approval
must cover the actual destination and diff, including metadata. An available
write key or installation approval does not grant publication authority.

Reusable improvements to the scaffold require a separate request and a fresh
public-content review; this round never pushes there as a side effect.
