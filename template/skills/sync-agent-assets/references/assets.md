# Instance asset contract

These are semantic source formats. The consuming agent checks its actual
client's documented loader, paths, precedence, configuration format, and supported
capabilities before adapting them. No client adapter or universal compatibility
claim is supplied. Unknown format versions or fields require review, not guessing.

## Skills and their upstream sources

Owned skills live at `skills/<name>/SKILL.md` with necessary companions under
that directory. Keep installed links self-contained. Record runtime dependencies
and side effects in the skill; a script's presence is not permission to execute
it. Project-owned skills stay with their project unless explicitly selected for
reuse with appropriate rights.

`skills/sources.json` has exactly `version: 1` and a `skills` array. Each entry
has `name`, `mode`, and `upstream`; `upstream` has `repository`, `path`, and `ref`,
plus `baseCommit` for a fork only:

- `name`: unique lowercase letters/digits separated by single hyphens; also the
  installation identity. Surface differences from upstream skill metadata.
- `mode: reference`: fetch the selected skill from upstream without storing a
  copy in this instance. A same-name canonical directory is a collision.
- `mode: fork`: this instance contains `skills/<name>/` with customized content;
  `baseCommit` is the full upstream commit from which it was derived or last
  reconciled, not an arbitrary recently observed commit.
- `repository`: credential-free HTTPS or SSH Git URL, never shell commands or
  a machine-local path. An SSH transport username is allowed; tokens/passwords
  are not. Even a private upstream URL must be authorized for publication here.
- `path`: Git-tree-relative POSIX path, or `.` for the root; no absolute paths,
  backslashes, empty or `..` segments, globs, or symlink escape.
- `ref`: explicit full branch/tag ref such as `refs/heads/main`, used to discover
  a candidate only. Resolve it to a full commit before installation.

Select entries before retrieving anything. Do not recursively follow external
catalogs or pull unrelated upstream content. Include explicitly selected companion
dependencies and preserve applicable licenses and notices. A fixed instance
commit does not pin moving upstream refs; record resolved commits in the local
installation record and use one agreed set for a multi-target distribution.

## MCP descriptions

Put real descriptions in `mcp/servers/*.json`; `mcp/examples/` is documentation
only and always excluded. Each description is a UTF-8 JSON object:

| Field | Contract |
| --- | --- |
| `id` | Stable lowercase letters/digits separated by hyphens; unique in the selection. |
| `example` | Boolean; `true` is never executable or installable. |
| `enabledByDefault` | Boolean initial preference; examples must use `false`. Existing explicit local state takes precedence unless a change is approved. |
| `transport` | `stdio`, `streamable-http`, or legacy `sse`; no ambiguous `http`. |
| `command`, `argv` | Required for stdio only: executable name and ordered array of literal argument strings or references. |
| `env` | Optional stdio-only map from environment variable names to references. |
| `url` | Required for HTTP transports only: complete non-secret URL or a whole-value `local-value` reference to a private endpoint. |
| `auth` | Required for HTTP transports only: `none`, `headers`, or `oauth`. |
| `headers` | Required nonempty reference map for `auth: headers`; absent otherwise. |
| `dependencies` | Required array of plain-text prerequisites; state known runtimes/versions and acquisition sources. Empty if none. |
| `requirements` | Required array of host/platform, working-directory, OAuth, permission, and other constraints. Empty if none. |

Stdio descriptions must not contain `url`, `auth`, or `headers`. HTTP descriptions
must not contain `command`, `argv`, or `env`. Do not substitute transports or infer
authentication from an empty header map.

A reference is exactly `{"source": "local-value", "name": "EXAMPLE_ENDPOINT"}`,
where `name` is a non-secret lookup label. Allowed sources depend on the field:

- `argv`: `local-value`, `environment`, or `local-secret`, resolving to one
  complete argument. Never split the result or evaluate shell syntax. Secret
  arguments can be exposed in process listings; use only a supported and
  explicitly approved mechanism and report that exposure before applying it.
- `url`: `local-value` only, resolving to a complete URL without credentials.
- `env` and `headers`: `environment` or `local-secret` only. A resolved header
  supplies its entire value, including any scheme such as `Bearer`.

References are not interpolation expressions. Resolve them only through an
approved local mechanism supported by the client. Keep values out of the source
tree and displayed diffs. Missing required references block that installation;
do not stringify unresolved objects or remove authentication. `local-value`
must not carry secrets. A missing secure credential mechanism leaves the server
uninstalled. Local mappings and credentials never travel with a multi-machine sync.

`command` is a program, not shell code. Preserve argument boundaries and inspect
executable resolution in the real host. No automatic download, repository-path
expansion, working-directory assumption, or wrapper is implied. OAuth uses the
server/client's supported flow and authorized scopes; caches stay local.

Enabled defaults grant no runtime permission. If the client cannot preserve a
disabled state, leave a disabled-by-default description uninstalled. Even an
enabled default must be staged disabled or deferred when startup is not authorized.

Static checks cover JSON types, required/forbidden fields, IDs, transports,
references, and dependencies. A protocol or connection check is a separately
authorized runtime action; never contact example endpoints.

## Instruction supplements

Keep narrowly scoped Markdown under `instructions/`. Supplements are optional,
additive content; they neither activate themselves nor override the actual
client's instruction hierarchy. Preserve unrelated user/project instructions.
Track managed sections separately and surface contradictions before merging.
Environment-specific access or package-source rules belong only in the relevant
instance and must state their scope and evidence.

## Native preference profiles

A profile under `preferences/` has exactly `version: 1`, `agent`,
`observedVersion`, and `settings`. The agent and observed version are strings;
settings is a small object of selected native keys and values. Native keys are
not a shared cross-client schema. Verify current support and report unavailable
models/options instead of substituting them.

Preview related provider/model/effort choices together, including cost effects.
Merge selected keys or list additions; preserve unrelated settings and explicit
local choices. Use supported native setters or a precise documented file edit.
Saved defaults and the current session's effective settings may differ.

Do not include credentials, permission modes, trusted folders, tool/URL
allowlists, auth flags, logging of private content, plugin code/state, or
client runtime databases in these profiles. Plugin activation, dependency
installation, and permission changes are separate actions. MCP enabled defaults
belong in their descriptions rather than duplicated client-specific lists.
