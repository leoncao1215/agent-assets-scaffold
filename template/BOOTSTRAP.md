# Bootstrap this instance

Bootstrap uses this collection's source checkout. It does not require the sync
skill to be preinstalled. Read that skill directly from the checkout, then
install its complete directory only within the selected scope.

## Copy-paste prompt

Supply this prompt with the instance identity, absolute checkout path or repository
URL. Existing sources are found through `~/.agent-assets/registry.json`. A consumer
may have only a source cache; a writable checkout is needed for contribution.

```text
Bootstrap the current agent from the instance I specified. First inspect the
matching entry in ~/.agent-assets/registry.json under my actual home, or a known
legacy record; verify its instance ID and repository. Do not scan home directories.

For authorized network setup on a deploy-key-capable host, prefer a dedicated
key per machine/user/repository. Reuse a verified one or prepare a fresh pair
locally in a protected nonconflicting location. Show only its public key and
fingerprint for me to grant repository read/write access. Pull-only consumers
need read access; contributors need write access. Wait for that grant before
dependent retrieval. Pin subsequent Git operations to that identity; do not
silently use a logged-in gh account, copy private keys or change global settings.
For unsupported hosts, prepare a repository-scoped alternative for approval.

Retrieve/reuse a verified source checkout or cache through that access.
Read README.md, instance.json, BOOTSTRAP.md, and
skills/sync-agent-assets/SKILL.md and its local-state/git-access references.
Register the verified source promptly even if a later installation is blocked.

Identify my actual OS, shell, client/version, and execution host. Use a fixed
source commit and review any selected uncommitted changes separately. Include
sync-agent-assets and its companions in the proposed installation. Ask which
additional asset categories to include if I have not selected them. Empty
categories and fictional examples do not require installation.

Check selected destinations and any prior installation records for this
instance. Preserve local changes and other instances' assets. Show exact paths,
selected assets and upstream versions, conflicts, dependencies, and side effects
before applying changes not already authorized. Use supported native mechanisms;
leave unsupported assets uninstalled and explain the limitation.
Choose and register each skill's file or native package/catalog method using
references/native-distribution.md. Preserve existing methods unless migration is
selected. Native support includes access, immutable version binding, update
exclusion and actual host discovery; CLI support does not prove T3 support.
Use registry/policy format 2 before registering native installations; retain
file baselines. Package installation does not apply the other asset categories.
For file-managed skills, prefer one ~/.agents/skills physical installation for
actual hosts that support it. Keep vendor/system assets and necessary exclusive compatibility editions in
native roots; client configuration stays independent. Compare all companions and
semantics, verify actual loader support/restrictions, then retire approved duplicate
files with backups. Register physical installations separately from consumers.
Native managers own their caches; the file helper does not update or lock them.
Use references/shared-skills.md and its guarded file entry for file installation,
update, migration and registry writes. The writing process must hold every affected
physical-root lock through revalidation, backup, writes, verification and recording.
This helper needs an existing Python 3.10+ runtime, not additional packages.

Record what was applied locally, including the instance ID and source versions.
Save installation pointers in the registry and detailed records locally. Offer
one concrete policy for future scheduled/manual pulls and optional after-edit
contributions; save only what I approve.
For distribution, default to all known machines and all their agents unless I
explicitly restrict it; record that selector without repeated opt-in questions.
Direct push and PR are alternatives, subject to repository protection;
PRs are not mandatory. Do not create a schedule
unless requested. Include the optional asset-lifecycle supplement in the preview.
Record private/public key paths and filenames, the deploy-key display label,
public fingerprint and granted scope locally, never key contents.
Report static checks separately from actual client loading. Do not start MCP
servers, install dependencies, initiate login, publish, or include other clients
or machines unless covered by my request. Unavailable targets are reported
individually; complete independent work without repairing hosts during sync.
```

The default is incoming installation into the current agent. Bootstrap does not
require harvesting local contributions first. For an explicitly requested
multi-target pull or named contribution, use the skill's
[reconciliation procedure](skills/sync-agent-assets/references/reconcile.md).
Unqualified distribution selects all known machines/all agents; explicit target
restrictions narrow it. Reuse verified ownership; routine pulls do not repeat opt-in questions or
require consumer contribution receipts. Use [local-state.md](skills/sync-agent-assets/references/local-state.md)
for migration of prior records and class-based standing authorization, and
[git-access.md](skills/sync-agent-assets/references/git-access.md) for deploy-key
grants, transport isolation and separate optional PR API access.

Do not copy another machine's adapted configuration or credentials. Select the
same instance on another machine and independently inspect that machine's host
and supported installation paths. A CLI and an embedded agent can load assets
differently even when they use the same model/provider.
