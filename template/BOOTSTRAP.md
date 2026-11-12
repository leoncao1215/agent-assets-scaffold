# Bootstrap this instance

Bootstrap uses this collection's source checkout. It does not require the sync
skill to be preinstalled. Read that skill directly from the checkout, then
install its complete directory only within the selected scope.

## Copy-paste prompt

Supply this prompt with the absolute path to this instance's checkout. If the
checkout is not yet available, first provide its repository URL and authorize
retrieval using this machine's own Git access.

```text
Bootstrap the current agent from the instance checkout I specified.
Read README.md, instance.json, BOOTSTRAP.md, and
skills/sync-agent-assets/SKILL.md from that checkout.

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

Record what was applied locally, including the instance ID and source versions.
Report static checks separately from actual client loading. Do not start MCP
servers, install dependencies, authenticate, publish, or include other clients
or machines unless those actions are covered by my request. Do not expand an
explicitly selected scope merely because other targets are discoverable.
```

The default is incoming installation into the current agent. Bootstrap does not
require harvesting local contributions first. For an explicitly requested
multi-target reconciliation or contribution, use the skill's
[reconciliation procedure](skills/sync-agent-assets/references/reconcile.md).

Do not copy another machine's adapted configuration or credentials. Select the
same instance on another machine and independently inspect that machine's host
and supported installation paths. A CLI and an embedded agent can load assets
differently even when they use the same model/provider.
