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
are needed. The generated repository has no Python runtime dependency.

Clone this repository using your normal authorized Git access. From its checkout,
run the following, choosing a new destination outside this checkout:

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
The default bootstrap handles the current agent; multiple agents or machines
are an explicit expansion using the optional reconciliation procedure. No
particular workbench or provider is required.

## Two different update paths

**Scaffold to instance:** review changes to conventions and workflows against
the baseline recorded in `scaffold-lock.json`, preserving instance edits. See
[the upgrade procedure](template/UPGRADE.md). This is a documented manual
three-way review, not an automatic updater or a live template subscription.

**Instance to machine:** use the instance's `sync-agent-assets` skill to preview,
adapt, and apply selected assets. Local contributions return only to that
instance. Promoting reusable improvements to this scaffold is a separate task.

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

## License and contributions

The scaffold, including its template, is [MIT licensed](LICENSE). Generated
instances retain that notice as `SCAFFOLD-LICENSE`; it does not license assets
you add later. Choose rights and publication scope for your own content and
preserve third-party attribution separately.

Contribute generic workflows and fictional examples. Do not contribute private
connections, organization catalogs, histories, credentials, or machine state.
See [CONTRIBUTING.md](CONTRIBUTING.md).
