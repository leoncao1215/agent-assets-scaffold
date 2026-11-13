# agent-assets-scaffold

Create an independent repository for your agent skills, MCP descriptions,
instruction supplements, and selected preferences. Keep work, personal, and
other people's collections separate while reusing the same management workflow.

The scaffold supplies conventions and an agent-readable sync skill. Each
**instance** owns its actual assets and sources. Each **machine** keeps its own
credentials, paths, adapted configuration, and installation records.

An existing asset repository can continue unchanged. It does not need to be
renamed, moved, or connected to this scaffold to keep working.

## Create an instance

Requires Git and Python 3.10+ for the small creation helper; no Python packages
are needed. The generated sync skill's optional invocation requires Python 3.10+
for its guarded file-application helper; merely reading or cloning assets runs none
of it. No Python packages are needed for that helper either.

Obtain this public scaffold without account credentials, or use approved
repository-scoped Git access for a private fork. From its checkout, run the
following, choosing a new destination outside this checkout:

```text
python tools/create_instance.py ../my-agent-assets --name my-agent-assets --scope personal
```

This copies only the reviewed `template/` tree and the MIT notice, creates a
unique instance identity, and records the exact scaffold commit and initial
file hashes. It refuses an existing destination or a dirty scaffold checkout.
It does not initialize Git, contact a service, install assets, or edit an agent.

Open the generated `README.md`. Initialize a new Git repository there and choose
its own remote and visibility when ready. Any Git host and any repository name
are suitable. Do not copy this scaffold's `.git` directory or another instance's
history. Keep the instance ID stable when cloning it onto additional machines;
creating a separate collection requires a new ID.

For agent-assisted creation, use [CREATE.md](CREATE.md). For installing an
instance into a client, use the generated `BOOTSTRAP.md`.

## What is included

- `template/`: an empty collection, a portable sync skill with its contracts,
  bootstrap and upgrade procedures, and fictional MCP examples.
- `tools/create_instance.py`: an offline, new-directory-only creation helper.
- `tests/`: offline checks for generation and isolation boundaries.

There are no business skills, private upstream catalogs, real MCP services,
personal model choices, company package-source settings, client adapters,
background services, or implicit dependency installation.

The template's catalogs are empty. Examples never become installation targets.
The default bootstrap handles the current agent. An unqualified distribution
request covers all known machines and all their agents; an explicit restriction
narrows that scope. Setup and distribution use the reconciliation procedure. No
particular workbench or provider is required.

## Two different update paths

**Scaffold to instance:** review changes to conventions and workflows against
the baseline recorded in `scaffold-lock.json`, preserving instance edits. See
[the upgrade procedure](template/UPGRADE.md). This is a documented manual
three-way review, not an automatic updater or a live template subscription.

**Instance to machine:** use the instance's `sync-agent-assets` skill to preview,
adapt, and apply selected assets through scheduled or manual **pull**. Setup
records source/cache locations at `~/.agent-assets/registry.json` and the user's
bounded standing policy. Named **contributions** publish independently; an
**audit** reports drift without installation. A failing consumer does not block
other targets or publication. Local contributions return only to that instance.
Promoting reusable improvements to this scaffold is a separate task.

The generic setup contract prefers repository-scoped deploy keys where supported,
with the user granting read/write access to the public key. It does not silently
use a logged-in account for Git. Publication can use direct push or a focused PR,
according to authorization and branch protection; PR APIs have separate access.
An optional lifecycle supplement connects asset edits to contribution checks when
actually loaded, without a watcher or blanket publish permission.
Instances can opt into native Pi packages, plugin marketplaces and HTTP skill
catalogs using the generic distribution contract and offline builder. No package
identity, business assets, source URL or active installation is injected by the
scaffold. Native managers own their caches; file-managed installations retain
the guarded writer. Registry/policy format 2 adds explicit native ownership and
source/installed/loaded evidence, while format 1 remains valid for file-only use.
Supported file-managed hosts share one physical skills root per machine/user, with
separate consumer loading evidence. The template includes a regular-file apply
helper holding OS locks across baseline recheck, backup, writes and recording;
native configuration remains separate. It is not a general client adapter.

Two instances do not share assets or synchronization targets merely because
they use the same scaffold. Repository separation alone does not isolate a
shared user-level client directory: use separate supported profiles/accounts,
or explicitly reconcile ownership before writing overlapping targets.

## Scope and validation

The helper uses Python's standard library. The included tests are offline:

```text
python -m unittest discover -s tests -v
```

The initial version was exercised on Windows with Python 3.12. Other platforms
and actual client loading have not been verified. Successful generation or
static validation is not evidence that a client loaded an asset. The consuming
agent checks its real host's supported formats and installation mechanisms.
The file-application tests additionally exercise Windows process contention,
crash release, post-wait drift, static verification and recovery records in
temporary directories. The POSIX flock/mode branch remains platform-qualified.

## License and contributions

The scaffold, including its template, is [MIT licensed](LICENSE). Generated
instances retain that notice as `SCAFFOLD-LICENSE`; it does not license assets
you add later. Choose rights and publication scope for your own content and
preserve third-party attribution separately.

Contribute generic workflows and fictional examples. Do not contribute private
connections, organization catalogs, histories, credentials, or machine state.
See [CONTRIBUTING.md](CONTRIBUTING.md).
