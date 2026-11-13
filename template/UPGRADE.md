# Upgrade the scaffold conventions

This updates the instance's inherited template files. Installing instance
assets into clients is a separate operation. No automatic upstream merge or
background updater is provided.

## Establish three inputs

1. **Base:** `scaffold-lock.json.source.repository` at its full `commit`, using
   each entry in `files` to map an instance path to its `sourcePath` and SHA-256.
2. **Local:** this instance's current files, including intentional edits and
   deletions. The lock hashes describe upstream bytes, not local ownership.
3. **Candidate:** a selected, reviewed newer scaffold commit, never a moving
   branch tip. Obtain it only through authorized access.

Verify the base tree's bytes match the recorded hashes. A Git commit alone is
not a signature or evidence of trust; verify the chosen source. Missing base
content, changed source identity, or an unknown lock format blocks automatic
application. Do not invent a baseline from current local content.

## Review the merge

Map candidate `template/<path>` files to `<path>` in the instance and candidate
`LICENSE` to `SCAFFOLD-LICENSE`. Compare raw file content across the three inputs:

- If local equals base and candidate changed, propose the candidate version.
- If candidate equals base and local changed, retain local.
- If both changed, perform a three-way merge and resolve overlapping edits.
- Treat additions, deletions, renames, and collisions with instance-owned files
  as explicit proposals. An upstream deletion must not discard local changes.

Preserve `instance.json`, collection assets, source selections, preferences,
and local state. Even template-origin files such as `skills/sources.json` may
now contain instance choices. A scaffold update does not reset them to defaults.
Changes to identity or configuration format need a separately reviewed migration.

Show the diff, source commits, unresolved conflicts, and changed behavior. Apply
only within the user's authorized scope, with a recoverable local checkpoint.
Never re-run the creation helper over an existing instance or replace its tree.

## Advance the baseline

After every candidate file has a reviewed outcome and the merge is complete,
replace the lock's source commit and file map with the candidate's upstream
paths and SHA-256 hashes. Retained local edits/deletions remain differences from
that new baseline. Include candidate additions and remove upstream-deleted paths.
Do not hash merged local bytes as if they were pristine upstream content.

If only part of an upgrade is accepted or applied, retain the previous lock and
record the partial result locally. The current format has one source commit;
do not claim a complete upgrade by advancing it over unresolved files.

Validate the new documents, JSON, companion files, and intended changes. Commit
or publish only when authorized. Client installation records are unchanged until
a separate sync actually applies assets from the updated instance.

## Registry and workflow migration

For upgrades introducing the registry and independent workflows, include the
sync skill's new companion references and optional asset-lifecycle supplement in
the reviewed change set. At subsequent client setup, migrate only evidenced old
installation paths/baselines into the local registry; retain legacy records.
Do not fabricate a prior policy or write grant, start schedules, migrate credentials,
or cancel an in-progress sync as a side effect of upgrading template files.
Existing instance choices of direct push or PR remain explicit user policy.
For shared-skills/guarded-writer upgrades, include the bundled application script
and shared-skills reference. Do not collapse existing per-owner records into a
physical installation until paths, complete content and host loading are verified.
Record consumers separately and retain legacy baselines. Existing copies and
vendor `.system` remain untouched until a separately authorized guarded cutover.
Install the guarded entry as a companion and validate the available runtime;
an absent helper/runtime is not permission to continue using unlocked writes.

## Lock format 1

`scaffold-lock.json` contains exactly `formatVersion`, `source`, and `files`.
`source` contains a credential-free `repository` and a full Git `commit`.
`files` maps instance-relative POSIX paths to `sourcePath` and lowercase `sha256`.
Paths must be relative, without empty, `.` or `..` segments or backslashes;
never follow a path or symlink outside either checkout.

The generated `instance.json` and the lock itself are not inherited files and
are not in this map. The lock has no timestamps, machine paths, credentials, or
client installation information and is suitable to commit with the instance.
