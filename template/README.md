# Agent assets

This collection has its own identity in `instance.json`. It can have any
repository name, remote, and visibility. Its assets are independent of other
collections created from the same scaffold.

Start with [BOOTSTRAP.md](BOOTSTRAP.md) to install a selected subset into an
agent. To add or synchronize assets later, use
[sync-agent-assets](skills/sync-agent-assets/SKILL.md).
Use [develop-agent-skill](skills/develop-agent-skill/SKILL.md) for the
collection-owned skill development lifecycle, without depending on a vendor
authoring helper.
Use **pull / 拉取** for scheduled or manually triggered incoming updates,
**contribute / 入库** for selected improvements, and **audit / 巡检** for bounded
drift reports. Publishing a contribution does not require checking every consumer.
Register source/cache locations and installation pointers at
`~/.agent-assets/registry.json`; a user-approved local policy governs unattended
work. Independent targets continue when another target is unavailable. Use one
authorized executor per machine/user context to manage selected local clients
through supported interfaces, with separate client results and unchanged physical
locking. See [machine execution](skills/sync-agent-assets/references/machine-execution.md).
An unqualified **distribution / 下发** covers all known machines and all their
agents; only an explicit target restriction narrows it. Unavailable targets stay
in the report rather than being silently dropped.
Native skill packaging is an optional instance choice: see [DISTRIBUTION.md](DISTRIBUTION.md).
The template supplies the offline helper and workflow, without choosing a package
identity or adding business skills. Existing methods are preserved on pull.
For file-managed skills, supported clients/hosts prefer one physical `~/.agents/skills` installation
per machine/user. Native roots retain vendor/system content and compatibility
editions; configuration stays separate. The registry tracks physical installations
and their consumers so shared bytes are updated once. See
[shared skills and guarded migration](skills/sync-agent-assets/references/shared-skills.md).
The bundled file-application helper needs existing Python 3.10+ and uses OS locks
held by the writing process. It does not block non-participating manual editors.

## Content

| Location | Purpose |
| --- | --- |
| `skills/` | Owned skills and necessary companion files. |
| [skills/sources.json](skills/sources.json) | Selected upstream references or customized-fork baselines; initially empty. |
| `mcp/servers/` | Real server descriptions selected for this collection; initially empty. |
| [mcp/examples/](mcp/examples/README.md) | Fictional documentation, never installation targets. |
| `instructions/` | Optional additive guidance, including an asset lifecycle completion check; nothing activates by file presence. |
| `preferences/` | Small, selected native-client preferences; initially empty. |
| `instance.json` | Collection identity and optional credential-free remote metadata. |
| `scaffold-lock.json` | Scaffold provenance and original template hashes for upgrade review. |

Read the [asset contract](skills/sync-agent-assets/references/assets.md) before
adding content. Keep one canonical asset rather than copying it into separate
client trees. The consuming agent adapts it to its real client and host.

## Boundaries

Keep credentials, endpoints that are private, machine paths, authentication
caches, logs, history, installation records, and backups outside Git. `.local/`
is ignored but is not a secure vault; use local credential storage for secrets.
Review actual staged files, even in a private repository.

A machine's selected clients consume this instance only within their approved
scope. Local contributions return here, not to the scaffold or another instance.
If an installation target is already managed by another collection, review the
overlap; matching asset names are not permission to overwrite.

Updating these files does not install them or grant permission to start tools.
Installation, runtime loading, networking, and publication have distinct effects;
honor the user's existing authorization for each requested task.
Setup prefers a dedicated deploy key per machine/user/repository with the user's
read/write grant; routine Git operations do not fall back to account credentials.
Authorized publication can push directly or use a focused PR. Repository protection
still applies; PR APIs need separate access from an SSH deploy key.

## Maintaining this instance

Keep `instance.json.id` when cloning this collection to other machines. Use a
new identity when creating an independent collection, even if it starts with
selected copies of your own assets. Bind local install records to this identity.

Scaffold upgrades follow [UPGRADE.md](UPGRADE.md); they are separate from syncing
assets into clients. Keep the scaffold license notice in `SCAFFOLD-LICENSE`.
It covers the inherited scaffold material only. Choose and document the rights
for assets added to this collection; they are not automatically MIT licensed.
