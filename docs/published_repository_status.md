# Published Repository Status

Date: 2026-06-01

## Repository

```text
https://github.com/tiramitree/fde-ai-systems-portfolio
```

Visibility:

```text
public
```

Default branch:

```text
main
```

Release tag:

```text
v0.1.0
```

## GitHub Actions

Workflow:

```text
quality-gate
```

Actions page:

```text
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml
```

Current expected result:

```text
success
```

## Post-Publish Check

Command:

```powershell
python -B scripts/post_publish_check.py
```

Result:

```text
passed
```

Latest local verification:

```text
Project 1 eval: 11/11 passed, unsafe leaks 0
Project 2 eval: 8/8 passed, unsafe direct side-effect failures 0
Smoke tests: 9/9 passed
Observability integrity: 30/30 passed
Threat model: 12/12 mapped
PR review policy: passed
Fresh clone experience: command published; run after each public push
API documentation gate: passed
Demo replay artifact: command published; writes ignored files under `out/`
Container release hygiene: passed
Quality gate: passed
```

Confirmed:

- repository page reachable
- raw README reachable
- GitHub Actions workflow reachable
- key documentation files published
- observability integrity script and documentation published
- threat model script and documentation published
- PR review policy script and documentation published
- fresh clone script and documentation published
- API documentation script and documentation published
- demo replay artifact script and documentation published
- container release hygiene script and documentation published
- remote `main` exists
- local tracked worktree clean

## Initial Public Issues

- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/1
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/2
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/3
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/4
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/5

## Still Manual

- Add repository description and topics from `docs/github_repository_settings.md`; `python -B scripts/dev.py github-launch-setup` dry-runs the required `gh` commands.
- Enable branch protection on `main`; `docs/github_branch_protection.json` is the tracked API payload used by `python -B scripts/configure_github_launch.py --apply`.
- Add social preview using `docs/assets/github-preview.png`.
- Create a GitHub release page for `v0.1.0`; `python -B scripts/configure_github_launch.py --apply` can do this after `gh auth login`.
- Pin repository on profile.
- Record demo GIF/video.
- Verify Docker runtime; static Docker/Compose release hygiene is already gated.
- Verify optional OpenAI mode with a live API key.
- Collect launch feedback and star-growth evidence.
