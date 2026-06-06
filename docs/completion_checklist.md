# Completion Checklist

This checklist tracks the repository evidence needed before claiming a public release is complete.

## Current Verified State

- Project 1 local service runs on `8765`.
- Project 2 local service runs on `8770`.
- Project 3 local service runs on `8780`.
- `scripts/check_health.py` passes for all services.
- `scripts/run_all_evals.py` passes:
  - Project 1: 11/11, unsafe leaks 0.
  - Project 2: 8/8, unsafe direct side-effect failures 0.
  - Project 3: 6/6, unsafe release approval failures 0.
- `scripts/smoke_test_demo_flows.py` passes 13/13 smoke checks.
- `scripts/check_api_contracts.py` passes 88/88 API contract checks.
- `scripts/check_runtime_ui_contracts.py` passes 294/294 runtime UI contract checks.
- `scripts/check_observability_integrity.py` passes 42/42 trace, audit, approval, blocked-action, and release-decision checks.
- `scripts/check_threat_model.py` maps 12/12 threats to controls, files, and evidence commands.
- `scripts/check_pr_review_policy.py` passes.
- `scripts/check_launch_assets.py` passes.
- `scripts/summarize_visual_asset_diff.py` passes without printing binary image contents.
- `scripts/quality_gate.py` passes.
- All three projects have README files, architecture docs, demo scripts, threat models, implementation status files, and technical review notes.
- Optional OpenAI Responses API gateway code exists but is disabled by default.
- Dockerfiles and Compose files exist.
- Project-level `.dockerignore` files exist.
- Production upgrade notes exist.
- Real desktop and mobile UI screenshots, an architecture diagram, a demo walkthrough GIF, and the GitHub social preview image are stored under `docs/assets/`.
- `PROJECT_CONTENT_INDEX.md` exists as the compact context-recovery map.
- `CHANGELOG.md` exists for public release history.
- The repository is public at `https://github.com/tiramitree/fde-ai-systems-portfolio`.
- The repository description and topics are set.
- The default branch is `main`.
- Branch protection is enabled on `main`.
- The release tag `v0.1.0` exists.
- The GitHub release page for `v0.1.0` exists with current replay artifact attachments.
- GitHub labels are synced from `docs/github_labels.json`.
- The latest observed `quality-gate` run on `main` passed.
- The latest post-publish check passed.
- Open PRs observed: 0.
- Open issues observed: 0.

## Still Not Fully Verified

- Docker runtime was not verified because Docker is not installed in the current environment; `python -B scripts/dev.py docker-runtime` is the tracked runtime proof for Docker-enabled machines.
- Optional OpenAI mode was not called because no API key was provided; `python -B scripts/dev.py openai-live` is the tracked live proof for API-key environments.
- Social preview upload and profile pinning still require GitHub UI/account-level confirmation.
- Star growth cannot be claimed until real launch feedback accumulates.

## Remaining Work Before Claiming Release Completion

1. Verify Docker Compose on a machine with Docker by running `python -B scripts/dev.py docker-runtime`.
2. Optionally verify OpenAI Responses API mode with a valid key by running `python -B scripts/dev.py openai-live`.
3. Do one final browser walkthrough of all projects from a clean reset.
4. Upload the social preview from `docs/assets/github-preview.png`.
5. Pin the repository on the GitHub profile after GitHub readiness is clean except for the pin row.
6. Re-run `python -B scripts/check_github_readiness.py --strict`.
7. Re-run `python -B scripts/post_publish_check.py`.
8. Re-run `python -B scripts/dev.py github-maintenance` and `python -B scripts/review_open_prs.py` before merging or responding to any external contribution.

## Latest Verification

Date: 2026-06-06

```text
python -B scripts/dev.py quality
python -B scripts/dev.py replay-artifact
python -B scripts/maintain_github_state.py --apply --sync-community
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
python -B scripts/review_open_prs.py
```

Result:

- Quality gate passed.
- GitHub repository description, topics, branch protection, release page, replay artifact attachments, and labels were applied.
- Post-publish check passed.
- GitHub readiness has 0 failures and 2 manual items.
- No open PRs are awaiting review.

## Quality Bar

- If `quality` fails, fix behavior before changing public copy.
- If `post_publish_check` fails, do not treat the pushed repository as ready.
- If `github-readiness --strict` fails on account-level setup, close the setup item before claiming launch completion.
- If external PRs appear, run `python -B scripts/dev.py pr-policy` and follow `docs/maintainer_review_policy.md` before merging.
- If generated runtime files appear in Git status, investigate `.gitignore` and the safety scan before publishing.
