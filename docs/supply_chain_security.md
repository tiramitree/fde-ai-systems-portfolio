# Supply Chain Security

This repository is intentionally local-first and dependency-light. The current runtime uses Python standard library modules, first-party browser assets, and no npm or pip package manifest.

## Current Posture

- Python services and scripts use standard library imports plus local packages only.
- Frontend code is first-party HTML, CSS, and JavaScript with no CDN dependency.
- Docker images pin the Python base image by digest.
- Dependabot watches GitHub Actions and all three Dockerfile directories weekly, while ignoring Python Docker semver-minor and semver-major bumps until the runtime baseline is intentionally upgraded across policy, docs, and verification evidence.
- Public safety checks scan for secret-like tokens, private local paths, and tracked runtime artifacts.

Verify the dependency surface:

```bash
python -B scripts/dev.py dependency-surface
```

Use `docs/dependabot_secret_scanning_verification_examples.md` before claiming Dependabot alerts, Dependabot security updates, secret scanning, or push protection are enabled on GitHub.

The full release gate also runs this check:

```bash
python -B scripts/dev.py verify
```

## Adding A Dependency

Do not add a package casually. A new dependency should have a clear production reason, exact versioning, a lockfile or equivalent reproducibility story, and eval coverage for any behavior it changes.

Required steps before accepting a dependency PR:

1. Explain why the behavior cannot stay in first-party code.
2. Add the dependency manifest or lockfile intentionally.
3. Update `docs/supply_chain_security.md` with the new trust boundary.
4. Update `scripts/check_dependency_surface.py` so the dependency is explicit instead of accidental.
5. Run `python -B scripts/dev.py verify`.

## Technical Review Framing

The point is not that production systems should avoid every library forever. The point is that a local reference demo should be easy to clone, audit, and run. Keeping the local path dependency-light reduces setup friction and makes safety claims easier to inspect.
