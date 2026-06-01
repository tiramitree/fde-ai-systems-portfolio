# Fresh Clone Experience

Run:

```bash
python -B scripts/dev.py fresh-clone
```

This command clones the configured GitHub `origin` into a temporary directory, runs release-facing static checks in that clone, starts both demo services on isolated local ports, and runs the user-facing health and smoke paths against those ports.

## Why It Exists

A polished local repository can still fail for a reviewer after `git clone`. This check proves the public repository has enough source, docs, and scripts to work from a clean checkout rather than relying on hidden local state.

The command verifies:

- public safety scan
- Markdown links and public assets
- Docker/Compose release hygiene
- dependency-surface policy
- repository governance files
- model gateway safety
- PR review policy
- threat model mapping
- both demo health endpoints on isolated ports
- the critical Project 1 and Project 2 smoke flows

## Interview Framing

Use this answer:

```text
I treat the public repository as the product surface. The fresh-clone check clones GitHub into a temp directory, runs the release-facing gates there, starts both apps on isolated ports, and exercises the core user flows. That catches hidden local-state assumptions before a reviewer does.
```
