# Create a separate collection

An instance is an independent asset repository. Its repository name, owner,
hosting platform, and visibility are the user's choices; none is inferred from
this scaffold's remote. Creating one does not migrate an existing collection.

## Agent prompt

Use this prompt after selecting a local scaffold checkout and a new destination:

```text
Create a new agent asset collection using the scaffold checkout and destination
I specified. Read its README.md and CREATE.md. Use a clean, committed scaffold
snapshot, record its full commit, and run tools/create_instance.py with my chosen
name and scope. If these inputs are missing, ask for them before creating files.
Keep the generated identity unique to this collection. Review the generated
files and report the exact output path and source version.

Creating this collection does not authorize reading other agents' configurations,
copying another instance's assets, authenticating, installing into a client,
setting up Git hosting, or publishing. Honor any authorization I already gave
for those specific actions. Preserve existing repositories and global settings.
```

The helper deliberately rejects even an empty existing destination. Choose a
new path; do not remove a user's directory to make the helper succeed. A failed
copy can leave a partial directory; inspect it before choosing a fresh destination.

When using a fork of the scaffold, pass `--source-repository` with that fork's
credential-free Git URL. The default records this project's public URL. The
helper records the supplied source identity without contacting it; verify that
the recorded commit is available there before sharing the generated instance.

`--scope` is `personal`, `work`, or `other`. `--name` is a readable label, not a
filesystem path or repository URL. Both can later be edited in `instance.json`;
the generated UUID is the stable identity. That identity helps track ownership,
but is not an authentication or access-control mechanism.

## After creation

1. Review `instance.json`, `scaffold-lock.json`, and the empty asset categories.
2. Set `instance.json.repository` to the intended credential-free remote URL,
   or retain `null` for a local-only collection. This value is metadata and does
   not configure Git or authorize network access.
3. If repository initialization/publication is requested, check the intended
   commit identity and destination; use a fresh Git history. Do not inherit
   a work email for a personal repository without the owner's intent.
   Follow the generated Git-access contract for a repository-specific deploy key
   and user-granted read/write scope where supported. Do not silently use the
   logged-in account's Git permissions. Direct push or PR follows the selected
   publication policy and host protection; neither is implied by generation.
4. Add only selected, publishable assets, with their sources and rights. The
   instance may be private, but that does not authorize sharing others' content.
5. Bootstrap selected clients from the instance's `BOOTSTRAP.md` when requested.

GitHub's **Use this template** would copy the scaffold itself, including its
helper and nested template. It is not the documented instance creation path.
Use the helper to produce the small instance tree for GitHub or another host.
