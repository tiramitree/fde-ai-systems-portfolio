# Published Repository Status

Date: 2026-06-06

Use `docs/public_maintainer_status_update_examples.md` before turning this status page into a public maintainer update. Keep local quality, pushed code, remote GitHub evidence, account-level/manual setup, and roadmap promises separate.

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
https://github.com/tiramitree/fde-ai-systems-portfolio/actions/runs/27048923720/job/79840487564
```

Current expected result:

```text
success
```

Release page:

```text
https://github.com/tiramitree/fde-ai-systems-portfolio/releases/tag/v0.1.0
```

Release attachments:

```text
demo_replay_artifact.md
demo_replay_artifact.json
```

README badge and workflow status should be compared with `docs/github_actions_badge_verification_examples.md` before claiming the rendered badge is current.

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
API contract checks: 86/86 passed
Runtime UI contracts: 294/294 passed
Observability integrity: 42/42 passed
Threat model: 12/12 mapped
PR review policy: passed
Fresh clone experience: command published; run after each public push
Fresh clone static checks include launch asset hygiene
API documentation gate: passed
Demo replay artifact: command published; writes ignored files under `out/`
Container release hygiene: passed
Visual asset manifest: passed
Visual asset diff summary: passed
Launch asset hygiene: passed
Quality gate: passed
```

Confirmed:

- repository page reachable
- repository description and topics are set
- raw README reachable
- GitHub Actions workflow reachable
- main branch-protection readiness row is `PASS: protected`
- `v0.1.0` release evidence is visible on GitHub
- `demo_replay_artifact.md` and `demo_replay_artifact.json` are attached to the release
- GitHub labels are synced from `docs/github_labels.json`
- key documentation files published
- observability integrity script and documentation published
- threat model script and documentation published
- PR review policy script and documentation published
- fresh clone script and documentation published
- API documentation script and documentation published
- demo replay artifact script and documentation published
- container release hygiene script and documentation published
- visual asset manifest script, visual asset diff script, documentation, manifest, and desktop/mobile screenshot contrast samples published
- README desktop screenshots, mobile / narrow viewport screenshots, and demo walkthrough GIF are tracked and published
- keyboard-friendly trace deep links, copy-link controls, and refreshed desktop/mobile screenshots are tracked and published
- copyable and diffable browser-local scenario drafts and read-only scenario snapshot endpoints are tracked and published
- focus-visible and reduced-motion CSS markers are tracked and verified across all browser demos
- browser-local light/dark theme controls are tracked and verified across all browser demos
- desktop and mobile screenshot contrast samples are tracked and verified by the visual asset gate
- launch copy and star-growth materials published with a deterministic anti-hype gate
- remote `main` exists
- local tracked worktree clean
- open issues observed: 0
- open PRs observed: 0

Release note freshness should still be reviewed with `docs/release_note_refresh_checklist.md`, release upload evidence with `docs/release_asset_upload_dry_run_examples.md`, and release attachment screenshots with `docs/github_release_attachment_screenshot_checklist.md` before reusing release evidence in public copy.

## Initial Public Issues Created

- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/1
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/2
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/3
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/4
- https://github.com/tiramitree/fde-ai-systems-portfolio/issues/5

## Still Manual

- Add social preview using `docs/assets/github-preview.png`.
- Pin repository on profile.
- Verify Docker runtime with `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine; static Docker/Compose release hygiene is already gated.
- Verify optional OpenAI mode with `python -B scripts/dev.py openai-live` and a live API key.
- Verify Dependabot alerts, Dependabot security updates, secret scanning, and push protection using `docs/dependabot_secret_scanning_verification_examples.md`; compare stale alert evidence with `docs/stale_dependabot_alert_evidence_examples.md` before treating old security alert screenshots, wrong dependency scopes, dismissed alert rows, private security-tab crops, or local safety-scan output as current.
- Enable GitHub Discussions only after reviewing `docs/github_discussions_launch_checklist.md`; keep Discussions separate from issues, PRs, private feedback, and roadmap acceptance.
- Collect launch feedback and star-growth evidence using `docs/launch_feedback_collection_examples.md`.

Public maintainer updates should summarize only current, reviewable evidence from this page and should not imply delivery dates, production support, private access, or completed setup before the matching evidence exists.
