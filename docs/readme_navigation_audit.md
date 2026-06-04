# README Navigation Audit

Use this audit when README links, release-facing sections, or contributor-facing routes change. It maps public README pointers to supporting docs and verification gates so navigation drift is visible before a public push.

This page is local-only. It does not claim fresh runtime, Docker, OpenAI, branch-protection, release-page, social-preview, profile-pin, or account-level evidence unless the matching command or manual proof exists.

## Release-Facing Navigation

| README Section | Supporting Docs | Owner/Gate | Drift Risk |
| --- | --- | --- | --- |
| Command decision tree | `docs/command_output_troubleshooting_map.md`, `docs/development_issue_solutions.md` | `python -B scripts/dev.py assets`, `python -B scripts/dev.py quality` | Commands or failure wording change while README still sends users to stale first checks. |
| Release Evidence FAQ | `docs/published_repository_status.md`, `docs/post_publish_checklist.md`, `docs/fresh_clone_experience.md` | `python -B scripts/dev.py assets`, `python -B scripts/dev.py fresh-clone-local` | Local, remote, and account-level evidence become blurred. |
| Evidence Freshness Checklist | `docs/visual_asset_hygiene.md`, `docs/demo_report.md`, `docs/demo_replay_artifact.md`, `docs/published_repository_status.md` | `python -B scripts/dev.py visual-assets`, `python -B scripts/dev.py claims` | README claims screenshots, eval metrics, or published state are fresh without the matching proof. |
| Demo recording readiness | `docs/demo_recording_checklist.md`, `docs/demo_state_presets.json`, `docs/visual_asset_hygiene.md`, `docs/demo_replay_artifact.md` | `python -B scripts/dev.py demo-presets`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py visual-assets` | Recording instructions drift from the canonical demo path or stale browser state. |
| Launch-channel readiness | `docs/launch_copy_pack.md`, `docs/star_growth_plan.md`, `docs/launch_assets_hygiene.md`, `docs/github_launch_plan.md`, `docs/published_repository_status.md` | `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py assets` | Public copy starts claiming Docker runtime, OpenAI live mode, branch protection, releases, or launch feedback early. |
| Release artifact readiness | `docs/demo_replay_artifact.md`, `docs/github_release_commands.md`, `docs/post_publish_checklist.md`, `docs/final_readiness_report.md` | `python -B scripts/dev.py replay-artifact`, `python -B scripts/dev.py quality` | Generated `out/` artifacts are mistaken for source files or release-page proof. |
| Reviewer handoff readiness | `docs/reviewer_perspective_checklist.md`, `docs/final_demo_runbook.md`, `docs/final_readiness_report.md`, `docs/published_repository_status.md` | `python -B scripts/dev.py quality`, `python -B scripts/dev.py fresh-clone-local` | Reviewer-facing language drifts away from current local evidence. |
| Post-publish readiness | `docs/post_publish_checklist.md`, `docs/published_repository_status.md`, `docs/github_repository_settings.md`, `docs/github_release_commands.md` | `python -B scripts/dev.py fresh-clone`, `python -B scripts/post_publish_check.py`, `python -B scripts/dev.py github-readiness` | Remote checks are treated as done before the local commits are pushed or the GitHub page is reachable. |
| GitHub readiness | `docs/published_repository_status.md`, `docs/github_repository_settings.md`, `docs/github_release_commands.md`, `docs/development_issue_solutions.md` | `python -B scripts/dev.py github-readiness`, `python -B scripts/dev.py github-maintenance` | Account-level items such as topics, branch protection, release page, social preview, and profile pin are described as completed too early. |
| Release page readiness | `docs/demo_replay_artifact.md`, `docs/github_release_commands.md`, `docs/post_publish_checklist.md`, `docs/published_repository_status.md` | `python -B scripts/dev.py replay-artifact`, `python -B scripts/post_publish_check.py` | Release notes or attachments are claimed before the `v0.1.0` page and current artifacts exist. |

## Contribution And Review Navigation

| README Section | Supporting Docs | Owner/Gate | Drift Risk |
| --- | --- | --- | --- |
| Contribution safety readiness | `CONTRIBUTING.md`, `SECURITY.md`, `docs/pr_review_security.md`, `docs/docs_only_pr_review_examples.md`, `docs/pr_review_runbook.md` | `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py safety` | Docs-only PRs or external PRs are treated as harmless without diff review. |
| PR triage readiness | `docs/pr_review_security.md`, `docs/docs_only_pr_review_examples.md`, `docs/pr_review_runbook.md`, `docs/maintainer_review_policy.md` | `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py pr-policy` | Unsafe docs, workflow, dependency, model gateway, or generated-artifact changes bypass scrutiny. |
| Maintainer PR Checklist | `docs/pr_review_security.md`, `docs/pr_review_runbook.md`, `.github/pull_request_template.md` | `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py governance` | Merge bar weakens while README still suggests public PR handling is protected. |
| Contributor Route Map | `docs/first_pull_request_checklist.md`, `docs/code_tour.md`, `docs/launch_assets_hygiene.md`, `docs/portfolio_evidence_matrix.md` | `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py quality` | Contributors run the wrong narrow gate for docs, frontend, backend, eval, visual, or GitHub-maintenance changes. |
| GitHub Community Issue Pack | `docs/github_initial_issues.md`, `docs/community_backlog.md`, `docs/github_labels.json` | `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py github-community` | Completed issues remain active, or issue labels drift from the label manifest. |

## Technical Navigation

| README Section | Supporting Docs | Owner/Gate | Drift Risk |
| --- | --- | --- | --- |
| Optional-environment readiness | `docs/container_release_hygiene.md`, `docs/model_runtime_configuration.md`, `docs/model_gateway_safety.md`, `docs/openai_live_mode_troubleshooting.md`, `docs/published_repository_status.md` | `python -B scripts/dev.py container-release`, `python -B scripts/dev.py model-gateway-safety` | Optional Docker or OpenAI paths sound required for the default local demo. |
| Connector roadmap readiness | `docs/production_upgrade_notes.md`, `docs/project_case_notes.md`, `docs/model_gateway_safety.md`, `docs/architecture_boundaries.md` | `python -B scripts/dev.py architecture`, `python -B scripts/dev.py contracts` | Connector work weakens approval, idempotency, audit, or trace boundaries. |
| Eval regression readiness | `docs/demo_report.md`, `docs/demo_replay_artifact.md`, `docs/portfolio_evidence_matrix.md`, `docs/scenario_data_integrity.md`, `docs/eval_authoring_guide.md` | `python -B scripts/dev.py evals`, `python -B scripts/dev.py claims` | Eval counts or unsafe failure counts change without matching docs and report evidence. |
| Storage adapter readiness | `docs/postgres_pgvector_adapter_design.md`, `docs/production_upgrade_notes.md`, `docs/scenario_data_integrity.md`, `docs/architecture_boundaries.md` | `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py dependency-surface` | Optional persistence becomes the default path or weakens permission checks. |
| Red-team eval readiness | `docs/threat_model.md`, `docs/portfolio_evidence_matrix.md`, `docs/scenario_data_integrity.md`, `docs/technical_review_playbook.md` | `python -B scripts/dev.py threat-model`, `python -B scripts/dev.py evals` | New attack cases lower the bar instead of preserving zero unsafe failures. |
| OpenTelemetry backend readiness | `docs/otel_trace_export.md`, `docs/observability_integrity.md`, `docs/portfolio_evidence_matrix.md`, `docs/production_upgrade_notes.md` | `python -B scripts/dev.py replay`, `python -B scripts/dev.py otel-traces`, `python -B scripts/dev.py observability` | Local trace export is confused with a configured hosted collector. |
| Docker runtime readiness | `docs/container_release_hygiene.md`, `docs/docker_runtime_evidence_checklist.md`, `docs/production_upgrade_notes.md`, `docs/published_repository_status.md` | `python -B scripts/dev.py container-release`; `python -B scripts/dev.py docker-runtime` only on a Docker-enabled machine | Static container hygiene is mistaken for live container runtime proof. |
| Dependency surface readiness | `docs/supply_chain_security.md`, `docs/development_issue_solutions.md`, `docs/portfolio_evidence_matrix.md` | `python -B scripts/dev.py dependency-surface`, `python -B scripts/dev.py workflow-security` | New packages, CDNs, or package-manager commands enter the default path casually. |
| API contract readiness | `docs/api_contracts.md`, `docs/api_request_cookbook.md`, `docs/runtime_ui_contracts.md`, `docs/architecture_boundaries.md` | `python -B scripts/dev.py api-docs`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py ui-contracts` | README route examples or response-shape claims drift from running APIs. |
| Error hygiene readiness | `docs/error_hygiene.md`, `docs/runtime_ui_contracts.md`, `docs/api_contracts.md` | `python -B scripts/dev.py error-hygiene`, `python -B scripts/dev.py safety` | Error examples start leaking local paths, stack details, or raw exception text. |
| Model gateway readiness | `docs/model_gateway_safety.md`, `docs/model_runtime_configuration.md`, `docs/openai_live_mode_troubleshooting.md`, `docs/production_upgrade_notes.md` | `python -B scripts/dev.py model-gateway-safety`; `python -B scripts/dev.py openai-live` only in an API-key environment | Optional OpenAI mode is described as the authority for permissions, approvals, or eval success. |
| Threat model readiness | `docs/threat_model.md`, `docs/portfolio_evidence_matrix.md`, `docs/architecture_boundaries.md` | `python -B scripts/dev.py threat-model`, `python -B scripts/dev.py safety` | New behavior lacks a threat owner, control, source file, or evidence command. |
| Workflow security readiness | `docs/workflow_security.md`, `docs/pr_review_security.md`, `docs/pr_review_runbook.md` | `python -B scripts/dev.py workflow-security`, `python -B scripts/dev.py governance`, `python -B scripts/dev.py pr-policy` | GitHub Actions stop preserving read-only tokens, safe PR triggers, and hardened checkout. |
| Governance readiness | `docs/github_repository_settings.md`, `docs/github_branch_protection.json`, `docs/maintainer_review_policy.md`, `.github/CODEOWNERS` | `python -B scripts/dev.py governance`, `python -B scripts/dev.py workflow-security` | Policy docs claim protections that account-level GitHub settings have not applied. |

## Audit Steps

Before approving README navigation changes:

```bash
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/
python -B scripts/dev.py assets
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Run `python -B scripts/dev.py fresh-clone-local` when the change affects README setup paths, public docs navigation, runtime paths, screenshots, or release-facing claims.

## Manual-Evidence Rule

Do not mark these as complete from README text alone:

- Docker runtime verification
- OpenAI live-mode verification
- branch protection
- GitHub release page
- repository topics
- social preview
- profile pin
- launch feedback
- star-growth results

Those are either environment-dependent, account-level, or remote-public checks. The README may point to the command or checklist, but the claim becomes current only after the matching command or manual action is verified.
