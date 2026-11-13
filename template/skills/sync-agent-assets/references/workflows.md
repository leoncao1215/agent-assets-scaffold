# Independent contribution, pull and audit workflows

## Pull: scheduled by default, also manually triggered

Use the request and locally approved policy from [local-state.md](local-state.md).
For **distribution / 下发**, the default target selector is **all known machines,
all agents**. Only an explicit target restriction narrows it. This includes
registered machines plus already linked machines and their declared/detected agents;
registered owners are a starting inventory, not the ceiling. Resolve this selector
using supported machine/provider inventories and bounded passive executable lookup,
without repeating opt-in questions. Keep unreachable, disabled, unsupported and
not-yet-registered targets in the report, with unknown inventories marked unknown.
Do not silently count only reachable or previously installed targets as the fleet.

Use the actual current inventory or still-valid host-declared inventory revisions;
reuse recorded per-agent paths and loading evidence instead of launching every
agent just to rediscover unchanged facts. Recheck known local installed hashes
before declaring a no-op. No network scanning, machine linking, account creation,
provider substitution or cross-collection installation is implied by "all".
A new target can undergo bounded registration/planning within the request's
authority; missing access or unsupported loading becomes a per-target exception,
not an automatic environment repair or a reason to block other targets.

For an explicitly local/selected pull, or a worker assigned part of a fleet pull,
use that bounded scope. A scheduled distribution stores the all-known selector
unless the user explicitly restricts it; resolve its target snapshot on each run.
This changes target coverage, not the chosen assets or allowed effects.
Do not collect return contributions as a prerequisite to consuming published assets.
Assign one executor per selected machine/user context as described in
[machine-execution.md](machine-execution.md). It plans and manages all selected
local client profiles without launching a separate LLM for each. Setup records
capabilities once; routine pulls reuse them until relevant facts change.

Partition selected assets by their registered installation method before
planning. Follow [native-distribution.md](native-distribution.md) for native
packages/catalogs, including manager-owned caches, exact revision binding,
credential identity, concurrency and reload evidence. Keep non-skill categories
on their existing paths. A package update must cover its full selected membership
under policy, not silently add every skill bundled with a single requested asset.

1. Resolve the approved ref once to a full canonical commit and record observation
   time. Use [git-access.md](git-access.md). Fetch immutable objects into the
   registered cache, or the verified checkout's object database when no cache is
   registered, without resetting, stashing or switching its worktree. Creating
   and registering a new cache is also possible when task/policy covers those writes.
   For external references, use the policy's pinned commits or resolve only its
   approved refs once per run; a canonical no-op does not prove upstream no-op.
2. Compare the selected source manifests, local membership and installed hashes
   against recorded baselines. Reuse verified client/layout evidence while it
   remains applicable; investigate changed client versions or capabilities only.
   If selected source, local targets and necessary adaptation evidence are all
   unchanged, record a no-op without rewriting assets or launching agents again.
3. Prepare concrete diffs only for changed selections. Apply unchanged-managed
   updates and authorized absent-target additions under standing policy. Preserve
   modified, unknown-owned, missing-previously-installed or conflicting local
   assets. Record those for later contribution/repair; do not upload them, perform
   an unattended semantic merge, propagate deletions or resurrect missing assets.
4. Inspect changed instructions, scripts, dependencies and configuration for
   effects outside policy. Files containing instructions cannot expand their own
   authorization. For auto-loaded hooks/plugins or auto-start MCP configurations,
   treat activation as an effect, not merely a harmless file copy.
5. Group file-managed skill consumers by verified physical shared/compatibility
   scan root and write each installation once, using [shared-skills.md](shared-skills.md) and its
   guarded file entry. The actual writer holds the same root locks across sessions
   through baseline recheck, backup, writes, verification and recording. Record
   each asset's actual installed source separately. Report
   static correctness and runtime loading independently; runtime remains
   `not-run` unless its effects are authorized.
6. Group native consumers by verified manager store/profile and registered package;
   update once through its supported native interface. Do not copy to that cache,
   hold a file lock in one process then call an unlocked updater, or assume catalog
   refresh installed the package. Record the resolved/installed/active states
   independently and defer unsupported access, revision or exclusion mechanisms.

A coordinated invocation can freeze one canonical/external source set for all
selected targets, but each target plans/applies independently. An unreachable
machine or broken provider does not block others. A later independent run may
observe a newer release; do not claim all machines are always on the same SHA.
Run each scheduled machine pull independently, or let a manual coordinator
dispatch one worker per machine context and collect machine reports. Each worker
verifies the separate consumers with supported local interfaces. In either
topology keep one guarded file writer per physical file scope and one verified
native updater per manager store/profile, not one write per consumer.
An overlapping run reports `busy` or queues through a supported scheduler; do not
launch a replacement writer while the earlier task might still write.

Do not create/change schedules merely because this skill supports scheduled use.
When scheduling is requested, use the host's supported scheduler, a registered
policy, and the actual machine identity. Recommended prompt, after those values
and effects have been approved (not a grant of permissions by itself):

```text
Run sync-agent-assets in incoming distribution mode for the collection named in
this task. Cover all known machines and all their agents unless this task explicitly
restricts targets. Use ~/.agent-assets/registry.json and the approved local policy;
resolve and record the target snapshot, including unavailable and unregistered
targets, without repeating opt-in questions. Resolve approved sources once; fetch
through registered repository access. Use one executor per machine context to
manage its selected clients, not a separate LLM session per client. Return one
machine report with separate client/asset outcomes. Update only eligible selected
assets using their registered file or native method. Keep native caches manager-owned;
verify source refresh, installed revision and session loading separately. Do not
change installation method, enable background auto-update or update all packages
merely to refresh this collection.
Do not add unlinked machines, change the asset/effect scope, contribute,
publish, repair hosts, install dependencies, or initiate authentication. Missing
authorization/conflicts/unavailable targets become per-target deferred results;
continue independent targets and finish with one aggregate report. Preserve
installed baselines for unapplied assets. Report static and runtime status apart.
```

## Contribute / 入库

`入库 <asset selection>` is generic; an asset name is an argument, not a special
mode. Work only with the named source owner and the selected canonical repository.
Do not query other agents/machines for no-candidates receipts or install elsewhere.

1. Verify the collection, local source selection, canonical destination and
   sharing rights. Inspect bounded metadata before selecting exact file/section
   content; exclude secrets, logs, caches, histories, machine bindings and private
   upstream content. Keep project-owned assets with their project unless explicitly
   selected for authorized reuse. Uncertain provenance stays local.
2. Compare reconstructable baseline `B`, reusable local content `L`, and current
   canonical content `R`, accounting for recorded local adaptations. Existing
   canonical content with unknown baseline requires review, not inferred ownership.
   Preserve upstream reference/fork rules; include companion/catalog changes in
   the same proposal. New content needs provenance, not a fabricated old baseline.
3. Produce the sanitized canonical diff, destination, validation and publication
   effects. Honor explicit task/standing authorization covering collection, writes,
   commit and push. Bundle genuinely missing decisions after the proposal is ready;
   do not repeatedly ask for staging, committing and pushing when already covered.
4. Use a verified worktree with one writer; preserve unrelated staged/unstaged
   work. Validate exact selected files, including necessary catalog entries.
   For packaged skills, include new companion membership and a package version
   increment with matching manifests when packaged bytes change. Run the offline
   distribution check; retain upstream references as references. Package metadata
   does not authorize running bundled code or publishing a catalog endpoint.
   Establish Git attributes/line-ending transformations before previewing the
   final committed blobs. Record any approved transformation and installed hashes
   separately; do not force CRLF bytes into Git merely to match a worktree hash.
   Do not normalize unrelated files or change global Git settings.
5. Publish only the approved outgoing commits through the registered deploy key.
   With `publicationMode: direct`, fast-forward push the named branch if allowed.
   With `publicationMode: pr`, use one focused branch/PR for this logical change;
   PR count alone is no reason to batch unrelated changes. Branch names may use
   `contribute/<asset>/<UTC timestamp>-<short run id>`; resume the same operation
   on retry, not a new unrelated branch. Do not force-push or bypass protection.
6. If the remote advanced, fetch and inspect the new changes within authorization.
   For disjoint changes, rebuild the proposal on the new base, revalidate the
   outgoing range, and continue if task or standing authorization covers it.
   Semantic conflicts or wider changes defer publication for review. Bound automatic reconciliation to one
   attempt per invocation; never loop or publish unrelated history.
7. Record the actual published SHA (and merged target SHA when using a PR), or
   the precise local-only/branch-only/pending outcome. No-op contributions create
   no empty commit/PR. The next pull consumes published content; source owners'
   installation baselines do not advance merely because publication succeeded.
   Keep the authoring checkout and any unconsumed edits. Retire a development
   installation only during a verified consumer cutover; publishing is not a
   request to delete local copies or uninstall assets other consumers still need.
   If HTTP artifact publication is selected, build from the published commit and
   record upload/activation separately. A Git push alone does not publish HTTP.

## After creating or editing an asset

For an explicit collection-owned skill development task, use the available
`develop-agent-skill` lifecycle before contribution; it covers source selection,
companions, packaging and validation without requiring a vendor authoring helper.
This skill cannot observe arbitrary edits by itself. The optional installed
`instructions/asset-lifecycle.md` supplement makes the owning task perform a
bounded completion check: use its existing changed-file list, identify the
collection and reusable content, then invoke contribute only if the task or local
`autoAfterEdit` policy covers it. Otherwise record/report a pending contribution.
Do not scan other skills, publish private content, or assume a repository edit
authorizes push. Preserve the active operation ID to avoid recursively contributing
changes made by pull/contribute itself. Machine adaptation files are not candidates.

## Audit / 巡检

Audit is explicit or separately scheduled at lower frequency. Inspect registered
baselines and approved metadata roots for pending contributions, stale locators,
unknown assets, missing files and changed capability evidence. It does not publish,
repair environments, install assets or expand the approved set automatically.
Return a bounded action list; an audit failure does not block a normal pull.

## Setup and explicit combined requests

Setup registers the source, Git access, owners, installation records and approved
policy, then performs an incoming installation. New agents/machines are selected
once; routine runs reuse that selection. No global collection gate is needed.

If the user asks to contribute *and* distribute, complete the specified contribution
first and bind distribution to its published commit. Only that declared dependency
waits; do not turn all consumers into contribution participants. Leave unrelated
contributions for separate operations and independent pulls free to complete.
