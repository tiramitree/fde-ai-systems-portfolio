# Fresh Clone Experience

Run:

```bash
python -B scripts/dev.py fresh-clone-local
python -B scripts/dev.py fresh-clone
```

`fresh-clone-local` clones the current local repository path, so it can verify committed local work before the next GitHub push. `fresh-clone` clones the configured GitHub `origin`, so it should be run again after the pushed commit is visible. Both commands run release-facing static checks in the clone, start all demo services on isolated local ports, and run the user-facing health and smoke paths against those ports.

Temporary clones are created under the ignored `out/fresh-clone-tmp/` workspace. Cleanup is best-effort so Windows file handles or restricted local sandboxes cannot turn a successful fresh-clone verification into a false failure.

## Why It Exists

A polished local repository can still fail for a reviewer after `git clone`. This check proves the public repository has enough source, docs, and scripts to work from a clean checkout rather than relying on hidden local state.

The command verifies:

- public safety scan
- Markdown links and public assets
- README screenshot manifest
- Docker/Compose release hygiene
- dependency-surface policy
- repository governance files
- launch asset hygiene
- model gateway safety
- PR review policy
- threat model mapping
- all demo health endpoints on isolated ports
- the critical Project 1, Project 2, and Project 3 smoke flows

## Technical Review Framing

Use this answer:

```text
The public repository is treated as the product surface. The fresh-clone check clones GitHub into a temp directory, runs the release-facing gates there, starts all apps on isolated ports, and exercises the core user flows. That catches hidden local-state assumptions before a reviewer does.
```
