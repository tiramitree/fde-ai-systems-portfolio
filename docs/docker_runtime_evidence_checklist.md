# Docker Runtime Evidence Checklist

Use this checklist only on a Docker-enabled machine. The local Python path remains the verified default in environments where Docker is unavailable.

Read this with `docs/container_release_hygiene.md`, `docs/readme_navigation_audit.md`, and `docs/command_output_troubleshooting_map.md`.

## Evidence Boundary

There are two different Docker checks:

| Check | What It Proves | What It Does Not Prove |
| --- | --- | --- |
| `python -B scripts/dev.py container-release` | Dockerfiles, Compose ports, health checks, startup commands, optional env defaults, pinned base images, and build-context ignores are statically aligned. | It does not build images, start containers, or prove containerized smoke flows. |
| `python -B scripts/dev.py docker-runtime` | On a Docker-enabled machine, Compose can build and start all services, health checks pass, smoke flows pass through containerized endpoints, and the stack tears down. | It is not verified on machines without Docker and should not be claimed from README text alone. |

Do not claim Docker runtime verification until `python -B scripts/dev.py docker-runtime` passes on the machine where the evidence is being collected. Treat `container-release` as static config evidence and `docker-runtime` as runtime evidence only on a Docker-enabled machine.

## Environment Capture

Before running the runtime proof, record the environment details in the release notes or review comment:

```bash
docker --version
docker compose version
docker info
git rev-parse HEAD
git status --short --branch
```

Do not include private Docker registry credentials, personal paths, account tokens, environment dumps, or unrelated machine identifiers.

## Command Sequence

Run from the repository root:

```bash
python -B scripts/dev.py container-release
python -B scripts/dev.py docker-runtime
```

`docker-runtime` performs this sequence internally:

1. Verify Docker CLI, Docker Compose, and Docker daemon availability.
2. Run the static container release hygiene gate.
3. Stop any previous stack for the dedicated Compose project name.
4. Refuse to run if host ports `8765`, `8770`, or `8780` are already in use.
5. Run `docker compose config`.
6. Build and start the Compose stack.
7. Wait for all three `/api/health` endpoints.
8. Run the same smoke flows against the containerized URLs.
9. Tear the stack down with `docker compose down --remove-orphans`.

## Expected Evidence

A passing runtime proof should include:

- Docker CLI version output
- Docker Compose version output
- Docker daemon info output without secrets
- `Container release check passed`
- Compose config/build/up output
- health success for all three services
- `Smoke tests: 13/13 passed`
- `Docker runtime check passed: compose build/up, health endpoints, and smoke flows succeeded.`
- teardown output or confirmation that the stack was removed

If screenshots are added later, they must reflect the current running services and should be reviewed with `docs/visual_asset_hygiene.md`. Screenshots are not required for this checklist.

## Failure Notes

| Failure | Meaning | Safe Next Step |
| --- | --- | --- |
| Docker CLI is not installed or not on PATH | The machine cannot run the runtime proof. | Keep the claim limited to `container-release`; run the runtime proof on a Docker-enabled machine. |
| `docker compose version` or `docker info` fails | Docker Desktop/Engine or Compose is unavailable. | Fix the Docker environment; do not edit app safety behavior. |
| host ports are already in use | Local demos or another service is using `8765`, `8770`, or `8780`. | Stop those local services, then rerun `python -B scripts/dev.py docker-runtime`. |
| static container release hygiene failed | Dockerfiles, Compose, health checks, env defaults, or build-context ignores drifted. | Fix the static container config and rerun `python -B scripts/dev.py container-release`. |
| a container health endpoint times out | A service did not become healthy in Compose. | Inspect the command output and service logs printed by the runtime check. |
| smoke flow fails | The containerized app behavior does not match the local critical path. | Treat it as a blocker for Docker runtime claims and rerun `python -B scripts/dev.py quality` after fixing. |

## Review Guardrails

- Do not commit generated container logs, local runtime state, Docker Desktop diagnostics, registry credentials, `.env` files, or machine-specific dumps.
- Do not add required Docker runtime verification to the default `quality` or `verify` gates.
- Do not change ports, health checks, or Dockerfiles without rerunning `python -B scripts/dev.py container-release`.
- Do not claim Docker runtime proof from `container-release`; it is static config evidence only.
- Do not merge Docker runtime-baseline changes without coordinated release policy, docs, and verification evidence.

## Claim Wording

Use this wording when Docker is unavailable:

```text
Docker packaging is statically gated by `python -B scripts/dev.py container-release`. Docker runtime verification was not run in this environment; run `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine before claiming Compose runtime evidence.
```

Use this wording only after the runtime command passes:

```text
Docker runtime verification passed on this commit: Compose built and started all three services, health checks passed, smoke flows passed, and the stack was torn down by `python -B scripts/dev.py docker-runtime`.
```
