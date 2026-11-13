# Repository-scoped Git access

## First setup on a machine

For a host supporting deploy keys, prefer one dedicated SSH key pair per
machine/user and repository. Reuse an existing verified repository-specific key;
otherwise generate a fresh pair locally during authorized setup, before private
clone/fetch. Do not use the logged-in `gh` account's Git permissions as a fallback.
Read-only access suffices for pull-only targets; a contributor needs write access.
The user chooses and authorizes that access on the repository.

1. Establish the exact host/repository, approved local key location, SSH/Git
   availability and intended read/write scope. Key generation is a setup effect,
   not a normal pull operation. Preserve existing keys; never overwrite or copy
   another machine's private key. Use a unique filename outside the checkout,
   under a user-protected SSH directory, with an appropriate OS ACL/file mode.
2. Generate with the installed SSH implementation and its supported algorithm
   (normally Ed25519). Agree on passphrase/unlock handling if needed. Do not
   weaken an encrypted key for unattended use; a locked key can block that run.
   Secrets go through the host's supported secret input, never ordinary chat.
3. Show only the **public key**, fingerprint, repository's deploy-key settings
   location, and requested read/write scope. Ask the user to register/authorize
   it. Keep private-key material off tool output, messages, tasks and shared Git.
   Do not register keys using broad account credentials without an explicit request.
4. Bind Git operations to that key and exact repository. Prefer a reviewed
   per-repository SSH alias or command-scoped SSH invocation with the explicit
   identity and `IdentitiesOnly=yes`. To prevent another account's key from
   authenticating, also disable agent identity fallback and isolate configuration
   from unrelated identities (for example a reviewed dedicated SSH config and
   `IdentityAgent=none`, retaining host trust checks);
   inspect effective SSH options before claiming only this key will be offered.
   Use `BatchMode=yes` for scheduled work. Preserve host-key verification and
   establish new host trust using an authoritative fingerprint, not blind accept.
5. Test authorized read access with a repository-specific read operation such
   as `git ls-remote` through the selected identity. `ssh -T` alone is not proof
   of access to the intended repository. Do not create a test commit/branch just
   to prove write access: record the user's grant, and confirm actual write use
   on the first authorized push. A dry run is not proof of a successful write.
6. Record the credential-free URL, absolute private/public key paths (including
   filenames), deploy-key display label, public fingerprint, approved scope and
   separate verification outcomes in the local registry. Never record
   key contents or the passphrase. Source catalogs retain portable repository URLs,
   not machine SSH aliases or key paths.

Do not silently rewrite an existing remote/global Git configuration or credential
helper. Use an explicitly scoped SSH URL/invocation for the operation or preview a
repository-local configuration change. Inspect relevant URL rewrites and SSH
configuration so a nominal SSH URL cannot silently route through account HTTPS
credentials. Keep connection settings data-only; never evaluate arbitrary stored
command strings. Preserve unrelated projects' Git access.

Other hosts may not support GitHub-style deploy keys or writable keys. Explain
the actual limitation and prepare a repository-scoped alternative for explicit
approval; do not claim portable support or silently use account-wide credentials.
An offline/local-source setup can proceed without network access, with remote
access marked pending. Each external upstream needs its own authorized access;
the canonical repository's deploy key does not grant upstream access.

## Routine operations and migration

Pull and contribution reuse the registered repository-specific access. On expired,
revoked, missing, locked or insufficient credentials, report `access-blocked` for
that source/target and continue independent work. Do not log in, generate new keys,
retry with an account token, or change permissions during unattended work.

For an existing account-authenticated installation, migrate as a separate setup
step: prepare the local key, obtain the user's repository grant, verify the new
route, then update only the approved local binding. Preserve existing account
sessions/configuration used by unrelated work. Do not claim migration until Git
actually used the selected route. Local asset edits alone do not trigger migration.

## Git operations versus repository APIs

An SSH deploy key authenticates Git transport, not GitHub's PR/issues API.
Default to the user's selected publication mode; **PRs are optional**, unless
branch protection or the host requires them. Authorized direct push to the named
branch needs no account login solely for PR management.

If the user selects PR publication, prepare and push the focused branch via the
deploy key. PR create/merge uses separately authorized API access (prefer a
repository-scoped app/token where supported), or a user handoff with the compare
link and ready description. Do not silently use `gh auth` as a new authority or
fallback to direct main when PR access is missing. Existing explicitly authorized
API access does not change the required Git transport identity.

A write-enabled deploy key narrows access to a repository; it is still powerful
within that repository and does not enforce per-asset or per-branch policy.
Apply the approved diff/branch scope and server-side protection independently.
