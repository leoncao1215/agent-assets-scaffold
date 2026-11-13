# Agent asset lifecycle

Optional supplement, applied only at the user's approved scope. It does not
authorize publication, schedule creation or changes to credentials/permissions.

For an explicitly selected collection-owned skill development task, use
`develop-agent-skill` when available to manage source, companions, packaging and
validation. It does not depend on a vendor's authoring skill. If unavailable,
follow the collection contracts and retain this bounded completion check.

After creating or modifying a reusable skill, instruction supplement, MCP
description or preference asset, check only the task's known changed content:

- Locate its owning collection using `~/.agent-assets/registry.json` (the actual
  execution user's home), an explicit source path or a verified local record.
  Missing/ambiguous ownership is reported; do not scan other client directories.
- Distinguish reusable owned content from local adaptations, secrets, runtime
  state, project-only assets and private upstream content. Keep those local or in
  their owning project. A private destination does not grant sharing rights.
- Use `sync-agent-assets` in **contribute / 入库** mode when the current request
  or a user-approved local `autoAfterEdit` policy covers the exact source,
  destination, content and publication effects. Otherwise report/record a pending
  contribution without automatically asking a new question after every edit.
- Prefer editing the canonical checkout over a native package cache. Include
  distribution membership and a package version/manifest update when packaged
  bytes change. Keep private configuration and runtime state outside packages.
  Publication does not delete development copies: install and verify the published
  revision before a separate cutover, preserving other consumers and local edits.
- Contribution handles only that selected change. Do not inventory all machines
  or start distribution. Follow the configured direct-push or PR policy; PRs are
  not mandatory unless required by the user or repository protection.
- Scheduled and manually requested **pull / 拉取** share the incoming workflow.
  An unqualified **distribution / 下发** covers all known machines and all their
  agents; explicit target restrictions narrow it. Include unavailable targets in
  the results without making them block independent work.
  Preserve local edits and report exceptions per target; do not publish them as
  a side effect of pull. Do not recursively invoke this check for writes already
  accounted for by the active sync operation.

This completion check works only where the actual host loads this supplement.
It is not a filesystem watcher or a claim that the skill runs after arbitrary
edits. Install it together with the sync skill and its companion references.
