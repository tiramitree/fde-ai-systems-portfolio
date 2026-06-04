# Docker Runtime Failure Examples

Use this page when `python -B scripts/dev.py docker-runtime` fails on a Docker-enabled machine. Read it with `docs/docker_runtime_evidence_checklist.md`, `docs/container_release_hygiene.md`, and `docs/command_output_troubleshooting_map.md`.

Docker runtime verification is optional and environment-dependent. The default verified demo path remains local Python, and `python -B scripts/dev.py quality` must not require Docker.

## Review Rules

- Run `python -B scripts/dev.py container-release` before debugging runtime behavior.
- Run `python -B scripts/dev.py docker-runtime` only on a Docker-enabled machine.
- Do not claim Docker runtime proof until the runtime command passes on the machine collecting evidence.
- Do not commit generated container logs, Docker Desktop diagnostics, `.env` files, registry credentials, local runtime state, machine-specific dumps, or screenshots that do not match current running services.
- Do not weaken permission checks, approval gates, smoke flows, health checks, ports, or build-context ignores to make Docker pass.

## Missing Docker Daemon

Symptom:

```text
Docker runtime check failed: Docker CLI, Docker Compose, or Docker daemon is unavailable
```

Meaning:

- Docker Desktop or Docker Engine is not running
- the user is on a machine where Docker is not installed
- the shell cannot reach the Docker daemon

Safe next step:

```bash
python -B scripts/dev.py container-release
```

Keep public wording limited to static container hygiene until Docker is available. Do not edit app code, smoke tests, or Dockerfiles just because the local machine cannot reach Docker.

Reviewer comment:

```text
This machine cannot collect Docker runtime evidence yet. The static container release gate is still useful, but please keep runtime verification unclaimed until `python -B scripts/dev.py docker-runtime` passes on a Docker-enabled machine.
```

## Compose Command Mismatch

Symptom:

```text
docker compose config fails, or the service command in docker-compose.yml differs from the Dockerfile command.
```

Meaning:

- Compose command, Dockerfile `CMD`, exposed port, or health check drifted
- a service may start locally but fail in the container path
- optional model environment defaults may have changed unexpectedly

Safe next step:

```bash
python -B scripts/dev.py container-release
git diff -- docker-compose.yml */Dockerfile
```

Fix the static config first, then rerun:

```bash
python -B scripts/dev.py container-release
```

Do not run broader runtime claims until the static gate passes.

Reviewer comment:

```text
The Docker runtime failure starts with static config drift. Please fix the Compose/Dockerfile/health-check mismatch and rerun `python -B scripts/dev.py container-release` before collecting runtime evidence.
```

## Unhealthy Service

Symptom:

```text
One of the containerized /api/health endpoints does not become healthy.
```

Meaning:

- the service failed during container startup
- the container command, port, working directory, or seed data path is wrong
- a runtime error appears only in the container environment

Safe next step:

```bash
python -B scripts/dev.py container-release
python -B scripts/dev.py quality
```

On the Docker-enabled machine, inspect only the relevant Compose service logs. Redact local paths, machine identifiers, environment values, and tokens before sharing any excerpt.

Reviewer comment:

```text
The runtime proof should stay blocked until all three container health endpoints pass. Please keep the local Python path verified with `quality`, inspect the failing service log locally, and avoid committing generated logs or environment dumps.
```

## Stale Generated Logs

Symptom:

```text
A PR adds copied Compose logs, Docker Desktop diagnostics, runtime_state files, or old `out/` artifacts as evidence.
```

Meaning:

- generated local evidence is being treated as source
- logs can expose paths, hostnames, environment values, trace IDs, or stale runtime behavior
- review cannot tell whether the evidence matches the current commit

Safe next step:

```bash
git status --short --branch
git diff --stat
python -B scripts/dev.py safety
```

Remove generated logs and rely on the command result instead. Release evidence should be added only through a deliberate release process.

Reviewer comment:

```text
Please remove generated Docker logs and stale runtime artifacts from the source diff. The safe evidence path is the command result from `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine, plus the static `container-release` gate.
```

## Port Conflicts

Symptom:

```text
host port(s) already in use: 8765, 8770, or 8780
```

Meaning:

- local demo servers are already running
- another process owns the public demo ports
- the runtime proof refuses to hide port conflicts by changing verified ports

Safe next step:

```bash
git status --short --branch
python -B scripts/dev.py container-release
```

Stop the conflicting local service, then rerun on the Docker-enabled machine:

```bash
python -B scripts/dev.py docker-runtime
```

Do not change Compose ports only to bypass a local conflict. Port changes must be reviewed with README, API docs, screenshots, and `container-release`.

Reviewer comment:

```text
This looks like a local port conflict, not an app change. Please stop the process using the demo ports and rerun `python -B scripts/dev.py docker-runtime`; do not change the published ports just to make the local machine pass.
```

## Merge Bar

Before approving Docker-facing docs or config changes:

```bash
git diff --stat
git diff -- docker-compose.yml */Dockerfile */.dockerignore README.md PROJECT_CONTENT_INDEX.md docs/ scripts/
git diff --check
python -B scripts/dev.py container-release
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Run `python -B scripts/dev.py docker-runtime` only on a Docker-enabled machine. If it is not run, say so plainly and keep Docker runtime verification optional, manual, and unclaimed.

## Claim Wording

Good when Docker runtime was not run:

```text
Docker packaging is statically checked by `python -B scripts/dev.py container-release`; runtime verification remains optional and should be collected with `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine.
```

Good after runtime proof passes:

```text
Docker runtime verification passed on this commit with `python -B scripts/dev.py docker-runtime`: Compose built and started all services, health checks passed, smoke flows passed, and the stack was torn down.
```

Avoid:

```text
Docker runtime is verified because the static container release gate passed.
```
