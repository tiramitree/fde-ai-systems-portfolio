# Published Repository Status

Date: 2026-06-02

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

Latest observed successful main run:

```text
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/runs/26861617523/job/79216313917
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
Project 3 eval: 6/6 passed, unsafe release approval failures 0
Smoke tests: 13/13 passed
API contract checks: 43/43 passed
Runtime UI contracts: 123/123 passed
Observability integrity: 42/42 passed
Threat model: 12/12 mapped
PR review policy: passed
Fresh clone experience: command published; run after each public push
Fresh clone static checks include launch asset hygiene
API documentation gate: passed
Demo replay artifact: command published; writes ignored files under `out/`
Container release hygiene: passed
Visual asset manifest: passed
Launch asset hygiene: passed
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
- visual asset manifest script, documentation, and manifest published
- README screenshots and demo walkthrough GIF are tracked and published
- launch copy and star-growth materials published with a deterministic anti-hype gate
- remote `main` exists
- local tracked worktree clean
- open issues observed: 0
- open PRs observed: 0

## Initial Public Issues Created

- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/1
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/2
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/3
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/4
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/5

## Still Manual

- Add repository description and topics from `docs/github_repository_settings.md`; `python -B scripts/dev.py github-maintenance` dry-runs the required authenticated maintenance commands.
- Enable branch protection on `main`; `docs/github_branch_protection.json` is the tracked API payload used by `python -B scripts/maintain_github_state.py --apply`.
- Add social preview using `docs/assets/github-preview.png`.
- Create a GitHub release page for `v0.1.0`; `python -B scripts/maintain_github_state.py --apply` can do this after `gh auth login`.
- Pin repository on profile.
- Verify Docker runtime with `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine; static Docker/Compose release hygiene is already gated.
- Verify optional OpenAI mode with `python -B scripts/dev.py openai-live` and a live API key.
- Collect launch feedback and star-growth evidence.
