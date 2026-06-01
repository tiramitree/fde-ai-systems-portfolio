# Container Release Hygiene

This project keeps Docker support as a release path for reviewers who prefer containerized demos, while the default verified path remains local Python. The container release gate makes the Docker files inspectable even on machines where Docker is not installed.

## Verification

Run from the repository root:

```bash
python -B scripts/dev.py container-release
```

The check verifies:

- both project Dockerfiles use digest-pinned Python bases
- both images use the expected `app.py --reset --host 0.0.0.0 --port ...` command
- exposed ports match the compose ports and service health checks
- compose defaults to local model behavior while allowing optional OpenAI runtime configuration through environment variables
- build contexts ignore local env files, runtime state, logs, SQLite files, caches, and temporary write-test files
- container config does not request host Docker sockets, privileged mode, host networking, bind volumes, or env files

## Interview Framing

The honest claim is:

```text
Docker packaging is present and statically gated for release hygiene. On this machine I verified the local Python runtime end to end; on a Docker-enabled machine the next check is `docker compose up --build` followed by `python -B scripts/dev.py smoke`.
```

This avoids overstating runtime evidence while still showing that the repository treats container config as production-facing code instead of incidental packaging.
