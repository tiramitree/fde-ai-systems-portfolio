# Container Release Hygiene

This project keeps Docker support as a release path for reviewers who prefer containerized demos, while the default verified path remains local Python. The container release gate makes the Docker files inspectable even on machines where Docker is not installed.

## Verification

Run from the repository root:

```bash
python -B scripts/dev.py container-release
```

The check verifies:

- all project Dockerfiles use digest-pinned Python bases
- all service images use the expected `app.py --reset --host 0.0.0.0 --port ...` command
- exposed ports match the compose ports and service health checks
- compose defaults to local model behavior while allowing optional OpenAI runtime configuration through environment variables
- build contexts ignore local env files, runtime state, logs, SQLite files, caches, and temporary write-test files
- container config does not request host Docker sockets, privileged mode, host networking, bind volumes, or env files
- optional Project 1 PostgreSQL/pgvector compose config is kept in `docker-compose.postgres.yml` and checked by `python -B scripts/dev.py postgres-compose`

The optional Postgres compose stack uses host port `55432`, applies Project 1 migration and seed SQL through Docker configs, and creates a non-owner local app role `fde_app` with the public local-only demo password `fde_app_demo_password`. Use `COPILOT_POSTGRES_DSN=postgresql://fde_app:fde_app_demo_password@127.0.0.1:55432/fde_portfolio` only for local compose verification.

On a Docker-enabled machine, run the runtime proof:

```bash
python -B scripts/dev.py docker-runtime
```

That command verifies Docker CLI and Compose availability, runs the static container release gate, brings the Compose stack up with a dedicated project name, waits for all health endpoints, runs the smoke flows against the containerized services, and then tears the stack down. It is intentionally not part of `quality` because Docker availability is environment-specific.

Use [Docker Runtime Evidence Checklist](docker_runtime_evidence_checklist.md) before collecting or publishing Docker runtime evidence, and use [Docker Runtime Failure Examples](docker_runtime_failure_examples.md) when a Docker-enabled runtime proof fails.

## Technical Review Framing

The honest claim is:

```text
Docker packaging is present and statically gated for release hygiene. On this machine Docker is not installed, so I verified the local Python runtime end to end. On a Docker-enabled machine, `python -B scripts/dev.py docker-runtime` builds the Compose stack, checks health, runs smoke flows, and tears it down.
```

This avoids overstating runtime evidence while still showing that the repository treats container config as production-facing code instead of incidental packaging.
