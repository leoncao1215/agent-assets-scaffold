---
name: develop-agent-skill
description: Manage the agent-assets repository lifecycle when creating or changing a reusable skill for a selected collection, or preparing a named local skill for contribution. Cover source ownership, companion files, package metadata, validation and the handoff to contribution; do not trigger for unrelated project code or routine skill execution.
---

# Develop a collection-owned skill

Manage the collection-specific lifecycle, not general skill-writing methodology.
The host may have its own authoring assistance (such as Codex's skill-creator);
use it when appropriate and available. It is optional: this workflow works without
a particular client, model or vendor skill. Do not copy vendor instructions into
the collection, edit vendor-managed skills, or install authoring tools implicitly.

## Establish ownership and the writable source

Use the user's explicit collection/path, then `~/.agent-assets/registry.json` or
a verified local record. Verify repository/instance identity and the selected
checkout. Read its category/source and distribution contracts. Missing or
ambiguous ownership calls for bounded clarification, not a scan of all clients.

Keep project-only skills with their project and private runtime/configuration
outside reusable source. An upstream reference remains a reference unless an
authorized fork with a real baseline is being created. Preserve attribution and
sharing rights; a private destination does not grant permission to copy content.

Edit `skills/<name>/` in the canonical writable checkout. If the task started from
an installed copy, first compare its full selected companions with the recorded
source baseline and extract only reusable changes. Preserve local adaptations
and private bindings. Never use a native package cache as the working checkout:
its manager may reset or clean it. Do not create a commit just to obtain a baseline.

## Develop and account for the complete change

Create or change the requested workflow and its required companions. Document
actual runtime/host capabilities and private configuration inputs. Keep resource
paths relative to the installed skill where possible; private configuration and
writable state need stable external locations. Loading files does not establish
that dependencies, account access or business permissions are available.

For collection workflow details, resolve `sync-agent-assets` from the actual
host catalog/registry or the selected checkout's `skills/sync-agent-assets/`.
Read only its needed references: native-distribution for packaging, workflows
and git-access for contribution, and assets/source contracts for upstream content.
Do not assume separately installed skills have adjacent directories. If those
required contracts cannot be located, retain the local work and report the
dependent packaging/publication step pending; do not guess a publication route.

When `distribution.json` exists:

- Add every required skill-relative file to the selected membership and remove
  stale entries only when the corresponding source removal is intentional.
  A new skill must be represented in all applicable native metadata. Bundle
  membership changes affect consumers' update authorization; they are not merely
  a hidden packaging detail.
- Advance the package version once for this logical release when packaged bytes
  change, including references and scripts. Keep edits within the same unshipped
  release on that version rather than bumping after every file edit or test.
- Use the reviewed offline distribution helper to propose matching manifests in
  a new external directory. Review/apply only those metadata changes; do not copy
  an entire client configuration or execute the helper from an unverified source.
- Keep upstream references outside the bundle. Building a catalog does not upload
  it; Git publication and HTTP artifact publication have separate outcomes.

For a file-only collection, preserve that choice. Do not introduce native package
metadata, a plugin system or distribution infrastructure solely to add a skill.

## Validate the changed behavior and packaging

Check discovery metadata, referenced companion existence, relative paths and
changed scripts using relevant existing tools. Run the collection's distribution
check when packaged. If a changed script or fragile behavior warrants a test,
use an isolated fixture that does not invoke business actions. A syntax check
or mock test is not a live workflow result.

Native loader tests use an authorized isolated profile and actual client tools.
Check inherited/shared discovery paths before exposing duplicate skills. Keep
source revision, installed bytes, advertised skill names and model/business
execution evidence distinct. Missing runtime/login/host support leaves that
check unverified, not fabricated as success or repaired through extra permissions.

Report the coherent source diff, metadata/version changes, validation and limits.
Do not reinstall every consumer just to validate one contribution.

## Hand off contribution without coupling it to distribution

If the task or approved after-edit policy covers publication, invoke the named
contribution operation from sync-agent-assets with the verified collection,
selected files/companions, baseline, tests and existing authorization. Otherwise
record the pending contribution and preserve the source work. Do not require
Codex's skill-creator, another model, a PR, or a fresh approval for an already
authorized publication step.

Contribution only publishes the selected change; it does not collect fleet
inventories, reinstall clients or delete development copies. A subsequent pull
uses the published revision. Retire a temporary development discovery entry only
after a separately authorized, verified cutover, preserving consumers and any
unpublished edits. Do not recursively trigger the lifecycle check for edits
already accounted for by this development/contribution operation.
