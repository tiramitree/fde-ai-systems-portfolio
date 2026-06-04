from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_SUFFIXES = {".gif", ".png", ".svg"}
REQUIRED_IMAGE_SIZES = {
    "docs/assets/github-preview.png": (1200, 520),
}
REQUIRED_README_CAPTIONS = [
    "Desktop: role-aware knowledge access, visible documents, eval gate, and trace/audit surfaces for permission-aware RAG.",
    "Desktop: investigator workflow with case context, governed action buttons, eval gate, and approval-driven operations controls.",
    "Desktop: release and incident triage workspace with eval evidence, rollout blocking, and audit/trace context.",
    "Mobile: narrow layout keeps user context, visible documents, and permission-aware knowledge controls readable.",
    "Mobile: approval workflow remains usable with case selection, eval gate, and governed action controls stacked for scanning.",
    "Mobile: release gate and incident triage stay readable while preserving blocked-rollout evidence.",
]
REQUIRED_PROJECT_RISK_BADGES = [
    "Risk badges:",
    "| Secure Enterprise Knowledge Copilot | `permissions` `citations` `abstention` `prompt-injection handling` `evals` `traces` `audit logs` | [Evidence Matrix](#evidence-matrix), [Threat Model](docs/threat_model.md), [Observability Integrity](docs/observability_integrity.md) |",
    "| Regulated Customer Operations Agent | `tool governance` `approvals` `side-effect blocking` `supervisor review` `evals` `traces` `audit logs` | [Evidence Matrix](#evidence-matrix), [Threat Model](docs/threat_model.md), [Observability Integrity](docs/observability_integrity.md) |",
    "| AI Reliability Incident Console | `eval-regression evidence` `release blocking` `remediation planning` `incident triage` `traces` `audit logs` | [Evidence Matrix](#evidence-matrix), [Threat Model](docs/threat_model.md), [Observability Integrity](docs/observability_integrity.md) |",
]
REQUIRED_SCREENSHOT_REVIEWER_CHECKLIST = [
    "Screenshot reviewer checklist:",
    "| Desktop and mobile assets cover all three demos. | Six PNGs are listed above and checked by `python -B scripts/dev.py visual-assets`. |",
    "| The screenshots still match the live behavior. | Run `python -B scripts/dev.py start`, follow the [Demo Path Map](#demo-path-map), and compare the visible role, approval, release, trace, and audit surfaces. |",
    "| Refreshed screenshots are reviewable. | Run `python -B scripts/dev.py visual-asset-diff` and keep refreshed PNGs plus `docs/visual_assets_manifest.json` in the same change. |",
    "| Reviewer expectations stay honest. | Use [Visual Asset Hygiene](docs/visual_asset_hygiene.md) and the [Reviewer Perspective Checklist](docs/reviewer_perspective_checklist.md) before publishing or approving visual changes. |",
]
REQUIRED_COMMAND_QUICK_REFERENCE = [
    "Command quick-reference:",
    "| Local run | `python -B scripts/dev.py start` |",
    "| Verification | `python -B scripts/dev.py verify`, `python -B scripts/dev.py quality`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py demo-presets`, `python -B scripts/dev.py evals`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py safety` |",
    "| Release evidence | `python -B scripts/dev.py replay-artifact`, `python -B scripts/dev.py report`, `python -B scripts/dev.py readiness-report`, `python -B scripts/dev.py fresh-clone`, `python -B scripts/post_publish_check.py` |",
    "| Visual assets | `python -B scripts/dev.py visual-assets`, `python -B scripts/dev.py visual-asset-diff`, `python -B scripts/dev.py refresh-visual-assets` |",
    "| GitHub maintenance | `python -B scripts/dev.py github-readiness`, `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py github-maintenance`, `python -B scripts/dev.py github-community` |",
    "| Optional environment checks | `python -B scripts/dev.py container-release`, `python -B scripts/dev.py docker-runtime`, `python -B scripts/dev.py openai-live` |",
    "Full command index:",
]
REQUIRED_COMMAND_DECISION_TREE = [
    "Command decision tree:",
    "| Prove the local repo works from a normal checkout. | `python -B scripts/dev.py verify` | Use the command output expectations table below if a gate fails. |",
    "| Review a code or docs change before publishing it. | `python -B scripts/dev.py quality` | Run `python -B scripts/dev.py fresh-clone-local` when the change affects public setup, docs, assets, or runtime paths. |",
    "| Prepare release-facing evidence after a push. | `python -B scripts/dev.py fresh-clone` | Run `python -B scripts/post_publish_check.py`, then `python -B scripts/dev.py github-readiness`. |",
    "| Check screenshots or frontend visual drift. | `python -B scripts/dev.py visual-assets` | Use `python -B scripts/dev.py visual-asset-diff`; refresh with `python -B scripts/dev.py refresh-visual-assets` only when screenshots intentionally change. |",
    "| Review GitHub state or public PRs. | `python -B scripts/dev.py pr-triage` | Use `python -B scripts/dev.py github-maintenance` and `python -B scripts/dev.py github-community` for dry-run account setup or community sync plans. |",
    "| Check optional environments. | `python -B scripts/dev.py container-release` | Run `python -B scripts/dev.py docker-runtime` only on Docker-enabled machines, and `python -B scripts/dev.py openai-live` only in an API-key environment. |",
]
REQUIRED_COMMAND_OUTPUT_EXPECTATIONS = [
    "Command output expectations:",
    "| `python -B scripts/dev.py verify` | Starts or reuses the three local services, runs the CI-quality gate, and ends with `Quality gate passed.` | Use before local release review when the demo services should be exercised. |",
    "| `python -B scripts/dev.py quality` | Runs repository safety, docs/assets, UI contracts, service health, smoke flows, evals, replay artifacts, and claim checks; ends with `Quality gate passed.` | This is the main local quality gate. |",
    "| `python -B scripts/dev.py demo-presets` | Validates `docs/demo_state_presets.json` against seed and eval data; ends with `Demo state presets check passed.` | Use before recording, reviewing, or sharing canonical local demo paths. |",
    "| `python -B scripts/dev.py fresh-clone-local` | Clones the current checkout into `out/fresh-clone-tmp/`, runs release-facing checks, starts isolated demo ports, and ends with `Fresh clone experience check passed.` | Use before push when the remote branch may not include the current commit yet. |",
    "| `python -B scripts/dev.py fresh-clone` | Clones `origin`, runs the same fresh-clone checks, starts isolated demo ports, and ends with `Fresh clone experience check passed.` | Requires network access and a pushed commit. |",
    "| `python -B scripts/post_publish_check.py` | Prints `[PASS]` rows for the GitHub page, raw README/workflow, and required published files; ends with `Post-publish check passed.` | Use after push to confirm public GitHub assets are reachable. |",
    "| `python -B scripts/dev.py github-readiness` | Prints `[PASS]`, `[WARN]`, or `[MANUAL]` rows and a `Readiness summary`. | GitHub API rate limits and account-level setup can remain warning/manual items until authenticated launch setup is complete. |",
    "| `python -B scripts/dev.py pr-triage` | Prints `Open PRs: 0` when no visible PRs await review, or lists each PR with risk findings and required gates. | If the API is rate-limited, public HTML fallback can prove no visible open PRs; authenticate before approving workflows or merging. |",
    "For recurring environment-specific failures, see [Development Issue Solutions](docs/development_issue_solutions.md).",
]
REQUIRED_TROUBLESHOOTING_POINTERS = [
    "Troubleshooting pointers:",
    "| GitHub API rate limits or pending Actions status | Rerun `python -B scripts/dev.py github-readiness` after a short wait, or use an authenticated GitHub environment for account-level checks; see [Development Issue Solutions](docs/development_issue_solutions.md). |",
    "| Docker is unavailable locally | The verified default path is local Python. `python -B scripts/dev.py container-release` checks container files without Docker, while `python -B scripts/dev.py docker-runtime` is only for Docker-enabled machines; see [Container Release Hygiene](docs/container_release_hygiene.md). |",
    "| Optional OpenAI mode is unavailable | Local deterministic mode remains the default. `python -B scripts/dev.py openai-live` is an optional API-key-environment proof for model-facing routes only; see [Model Runtime Configuration](docs/model_runtime_configuration.md). |",
    "| Generated local artifacts appear | Runtime outputs under ignored paths such as `out/` are local evidence, not source changes. Run `python -B scripts/dev.py safety` before committing if a generated file appears in the worktree. |",
]
REQUIRED_RELEASE_EVIDENCE_FAQ = [
    "## Release Evidence FAQ",
    "| Which check should run before a local commit? | Use `python -B scripts/dev.py quality`; it proves local safety, docs/assets, UI contracts, service health, smoke flows, evals, replay artifacts, and claim checks are aligned. |",
    "| When should `fresh-clone-local` run? | Run `python -B scripts/dev.py fresh-clone-local` before push when README, setup paths, public assets, or runtime wiring changed; it validates a clean clone of the current checkout before the remote has the commit. |",
    "| What does remote `fresh-clone` prove? | After push, `python -B scripts/dev.py fresh-clone` clones `origin`, runs release-facing static gates, starts isolated services, and runs smoke flows from the public branch. |",
    "| What does post-publish prove? | `python -B scripts/post_publish_check.py` proves the GitHub page, raw README/workflow, and required published files are reachable; compare with [Published Repository Status](docs/published_repository_status.md). |",
    "| Is a warning the same as a failing release gate? | No. Treat `quality`, `fresh-clone-local`, `fresh-clone`, and post-publish failures as blockers for code or docs changes; treat GitHub `[WARN]`/`[MANUAL]` items as account-level follow-up unless strict mode is being used. |",
    "| How should GitHub readiness warnings be handled? | `python -B scripts/dev.py github-readiness` warnings for API rate limits, repository metadata, branch protection, release pages, social preview, or profile pin are account-level/manual items unless a gate reports a failure; see [Development Issue Solutions](docs/development_issue_solutions.md). |",
]
REQUIRED_EVIDENCE_FRESHNESS_CHECKLIST = [
    "## Evidence Freshness Checklist",
    "Ignored outputs under `out/` are local evidence by default. Do not claim Docker runtime, OpenAI live mode, branch protection, or release page freshness until the matching command or account-level action is complete.",
    "| README screenshots and mobile screenshots | Run `python -B scripts/dev.py visual-assets` and `python -B scripts/dev.py visual-asset-diff`; use `python -B scripts/dev.py refresh-visual-assets` only for intentional screenshot updates. | [Visual Asset Hygiene](docs/visual_asset_hygiene.md) and [Screenshots](#screenshots). |",
    "| Demo walkthrough GIF | Run `python -B scripts/dev.py assets` and inspect `docs/assets/demo-walkthrough.gif` before sharing; refresh it only for intentional demo-flow changes. | [Visual Asset Hygiene](docs/visual_asset_hygiene.md). |",
    "| Eval summary counts | Run `python -B scripts/dev.py evals`, `python -B scripts/dev.py report`, and `python -B scripts/dev.py claims`; commit source docs only when the claimed metrics intentionally change. | [Demo Report](docs/demo_report.md) and [Evidence Matrix](#evidence-matrix). |",
    "| Published repository status | After push, run `python -B scripts/dev.py fresh-clone`, `python -B scripts/post_publish_check.py`, and `python -B scripts/dev.py github-readiness`; treat `[WARN]` and `[MANUAL]` rows as account-level follow-up unless strict mode is required. | [Published Repository Status](docs/published_repository_status.md) and [Release Evidence FAQ](#release-evidence-faq). |",
    "| Generated local artifacts | Run `python -B scripts/dev.py replay-artifact` when a fresh local replay package is needed; keep ignored `out/` artifacts uncommitted unless a release process explicitly asks for them. | [Demo Report](docs/demo_report.md) and [Release Evidence FAQ](#release-evidence-faq). |",
]
REQUIRED_ARCHITECTURE_CARDS = [
    "Architecture cards:",
    "Read these with [Architecture Boundaries](docs/architecture_boundaries.md), [API Contracts](docs/api_contracts.md), and [Runtime UI Contracts](docs/runtime_ui_contracts.md).",
    "| [Secure Enterprise Knowledge Copilot](secure-enterprise-knowledge-copilot/docs/architecture.md) | `secure-enterprise-knowledge-copilot/src/copilot` owns retrieval, answering, storage, security, evals, and the opt-in model gateway. | `secure-enterprise-knowledge-copilot/web/js` keeps local ES modules for API calls, rendering, trace links, theme, clipboard, and scenario drafts. | Permission filtering before generation, citation-required answers, abstention, prompt-injection handling, traces, audit logs. | Run `python -B scripts/dev.py smoke` and inspect the Alice/Morgan finance path in the [Demo Path Map](#demo-path-map). |",
    "| [Regulated Customer Operations Agent](regulated-customer-operations-agent/docs/architecture.md) | `regulated-customer-operations-agent/src/ops_agent` owns workflow routing, governed tools, storage, evals, and the opt-in model gateway. | `regulated-customer-operations-agent/web/js` keeps local ES modules for case investigation, approvals, trace links, theme, clipboard, and scenario drafts. | Side-effect tools require application approval, bypass attempts are refused, supervisor execution is auditable. | Run `python -B scripts/dev.py smoke` and inspect the Ivy `case-1001` approval path in the [Demo Path Map](#demo-path-map). |",
    "| [AI Reliability Incident Console](ai-reliability-incident-console/docs/architecture.md) | `ai-reliability-incident-console/src/reliability_console` owns release state, incident triage, eval evidence, storage, and audit records. | `ai-reliability-incident-console/web/js` keeps local ES modules for incident selection, triage rendering, trace links, theme, clipboard, and scenario drafts. | Failed eval evidence blocks unsafe rollout, remediation stays traceable, audit events link release decisions to incidents. | Run `python -B scripts/dev.py smoke` and inspect the unsafe canary release path in the [Demo Path Map](#demo-path-map). |",
]
REQUIRED_README_GLOSSARY = [
    "## Core Terms",
    "| Release gate | The repository-level checks that keep public docs, evidence, runtime contracts, screenshots, and safety claims aligned before a change is published; see the [Evidence Matrix](#evidence-matrix) and [launch asset hygiene](docs/launch_assets_hygiene.md). |",
    "| Eval gate | Deterministic regression cases that must keep permission leaks, unsafe side effects, and unsafe release approvals at zero; see `python -B scripts/dev.py evals` and the [System Evidence Matrix](docs/portfolio_evidence_matrix.md). |",
    "| Approval gate | Application code that blocks external side effects until an authorized supervisor approves the pending action; see [Project 2](#project-2-regulated-customer-operations-agent) and [observability integrity](docs/observability_integrity.md). |",
    "| Trace ID | A per-response identifier that connects UI output to stored trace records, linked audit events, approvals, blocked actions, or release decisions; see [observability integrity](docs/observability_integrity.md). |",
    "| Audit log | Structured records of security, workflow, approval, and release-decision events that explain what happened after a run; see [threat model](docs/threat_model.md) and [observability integrity](docs/observability_integrity.md). |",
    "| Abstention | The answer behavior used when accessible evidence is missing, unauthorized, or unsafe after filtering; see [Project 1](#project-1-secure-enterprise-knowledge-copilot) and the [System Evidence Matrix](docs/portfolio_evidence_matrix.md). |",
]
REQUIRED_EVIDENCE_LEGEND = [
    "## Evidence Legend",
    "| Smoke | `python -B scripts/dev.py smoke` proves the three running demos complete the canonical permission, approval, and release-blocking flows. | It is not exhaustive security, load, or browser-compatibility coverage. |",
    "| Eval | `python -B scripts/dev.py evals` proves deterministic regression cases keep unsafe leak, direct side-effect, and release-approval failures at zero; see [System Evidence Matrix](docs/portfolio_evidence_matrix.md). | It does not cover every possible prompt, data set, or production integration. |",
    "| Trace | `python -B scripts/dev.py observability` proves responses can be followed through stored trace records, IDs, and linked decisions; see [Observability Integrity](docs/observability_integrity.md). | It does not mean an external OpenTelemetry backend is configured by default. |",
    "| Audit | The same observability gate proves security, approval, blocked-action, and release-decision events are recorded and link back to the run. | It does not replace enterprise retention, SIEM, or compliance controls. |",
    "| Visual | `python -B scripts/dev.py visual-assets` proves desktop and mobile screenshots match the recorded manifest, source hashes, and contrast samples; see [Visual Asset Hygiene](docs/visual_asset_hygiene.md). | It is a deterministic screenshot guard, not a complete accessibility audit. |",
]
REQUIRED_README_PR_CHECKLIST = [
    "## Maintainer PR Checklist",
    "Public PRs are treated as untrusted input. Before approving workflows, running contributor code, or merging:",
    "| Triage first | Run `python -B scripts/dev.py pr-triage`, then read the changed files and diff before running code. |",
    "| High-risk surfaces | Treat workflow files, dependency policy, model gateways, safety scans, quality gates, shell commands, network calls, and binary/generated artifacts as high scrutiny. |",
    "| Secrets and access | Do not ask contributors for secrets, tokens, account access, private files, local paths, or collaborator permissions. |",
    "| Merge bar | Use the [PR review security gate](docs/pr_review_security.md) and [PR review runbook](docs/pr_review_runbook.md); merge only after `pr-policy`, `governance`, `workflow-security`, `safety`, and `verify` pass. |",
]
REQUIRED_REVIEWER_HANDOFF_CHECKLIST = [
    "## Reviewer Handoff Checklist",
    "Use this with the [Maintainer PR Checklist](#maintainer-pr-checklist), [Contributor Route Map](#contributor-route-map), [Visual Asset Hygiene](docs/visual_asset_hygiene.md), [Published Repository Status](docs/published_repository_status.md), [PR Review Runbook](docs/pr_review_runbook.md), and [Release Evidence FAQ](#release-evidence-faq).",
    "| Local quality | Run `python -B scripts/dev.py quality` after source, docs, asset, or runtime changes. | Any failure blocks commit, approval, or public sharing. |",
    "| Local fresh clone | Run `python -B scripts/dev.py fresh-clone-local` before push when setup paths, README guidance, public assets, or runtime wiring changed. | Any failure blocks push until a clean checkout works. |",
    "| Visual evidence | Run `python -B scripts/dev.py visual-assets` and `python -B scripts/dev.py visual-asset-diff`; use `refresh-visual-assets` only for intentional screenshot updates. | Unexpected screenshot or manifest drift blocks visual claims. |",
    "| Remote evidence | After push, run `python -B scripts/dev.py fresh-clone` and `python -B scripts/post_publish_check.py`. | Remote clone or published-file failures block sharing the public branch. |",
    "| PR state | Run `python -B scripts/dev.py pr-triage`, then inspect high-risk diffs before running contributor code. | Do not merge while review findings, high-risk files, or required gates are unresolved. |",
    "| GitHub readiness | Run `python -B scripts/dev.py github-readiness`; treat `[WARN]` and `[MANUAL]` rows as account-level follow-up unless strict mode is required. | Do not claim metadata, branch protection, release page, social preview, or profile pin freshness until those actions are complete. |",
]
REQUIRED_CONTRIBUTOR_ROUTE_MAP = [
    "## Contributor Route Map",
    "| Docs-only | The command decision tree above, [Launch Asset Hygiene](docs/launch_assets_hygiene.md), and [System Evidence Matrix](docs/portfolio_evidence_matrix.md). | `python -B scripts/dev.py assets`, `python -B scripts/dev.py launch-assets`, then `python -B scripts/dev.py quality` before publishing. |",
    "| Frontend/UI | [Frontend Integrity](docs/frontend_integrity.md), [Runtime UI Contracts](docs/runtime_ui_contracts.md), and [Visual Asset Hygiene](docs/visual_asset_hygiene.md). | `python -B scripts/dev.py frontend`, `python -B scripts/dev.py ui-contracts`, `python -B scripts/dev.py visual-assets`, then `python -B scripts/dev.py quality`. |",
    "| Backend/API | [API Contracts](docs/api_contracts.md), [Architecture Boundaries](docs/architecture_boundaries.md), and the service `src/` package being changed. | `python -B scripts/dev.py contracts`, `python -B scripts/dev.py api-docs`, `python -B scripts/dev.py architecture`, then `python -B scripts/dev.py quality`. |",
    "| Eval/data | [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Scenario Data Integrity](docs/scenario_data_integrity.md), and the project `data/` folder. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py claims`, then `python -B scripts/dev.py quality`. |",
    "| Visual assets | The [Screenshots](#screenshots) section and [Visual Asset Hygiene](docs/visual_asset_hygiene.md). | `python -B scripts/dev.py visual-assets` and `python -B scripts/dev.py visual-asset-diff`; use `python -B scripts/dev.py refresh-visual-assets` only for intentional screenshot updates. |",
    "| GitHub maintenance | [Maintainer PR Checklist](#maintainer-pr-checklist), [PR Review Security](docs/pr_review_security.md), and [PR Review Runbook](docs/pr_review_runbook.md). | `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py github-readiness`, and dry-run `python -B scripts/dev.py github-maintenance` before any account-level action. |",
]
REQUIRED_PRODUCTION_UPGRADE_POINTER = [
    "Production upgrade pointer:",
    "| FastAPI service adapter | [Production Upgrade Notes](docs/production_upgrade_notes.md), [API Contracts](docs/api_contracts.md), and [Architecture Boundaries](docs/architecture_boundaries.md). | Keep the stdlib HTTP server as the default local path; run `python -B scripts/dev.py contracts`, `python -B scripts/dev.py api-docs`, and `python -B scripts/dev.py quality`. |",
    "| PostgreSQL and pgvector | [PostgreSQL And pgvector Adapter Design](docs/postgres_pgvector_adapter_design.md). | Preserve permission checks before retrieval or side effects, keep eval state isolated, and run `python -B scripts/dev.py scenario-data` plus `python -B scripts/dev.py quality`. |",
    "| Connector stubs | [Production Upgrade Notes](docs/production_upgrade_notes.md) and project service packages. | Keep external side effects behind approval, idempotency, audit, and trace boundaries; run `python -B scripts/dev.py model-gateway-safety`, `python -B scripts/dev.py contracts`, and `python -B scripts/dev.py quality`. |",
    "| OpenTelemetry export | [OpenTelemetry Trace Export](docs/otel_trace_export.md) and [Observability Integrity](docs/observability_integrity.md). | Local traces export without a collector by default; run `python -B scripts/dev.py replay`, `python -B scripts/dev.py otel-traces`, and `python -B scripts/dev.py observability`. |",
    "| OpenAI runtime mode | [Model Runtime Configuration](docs/model_runtime_configuration.md) and [Model Gateway Safety](docs/model_gateway_safety.md). | Local deterministic mode remains the verified default; run `python -B scripts/dev.py openai-live` only in an API-key environment before claiming live model evidence. |",
    "| Docker runtime | [Container Release Hygiene](docs/container_release_hygiene.md). | Static container config is covered by `python -B scripts/dev.py container-release`; run `python -B scripts/dev.py docker-runtime` on a Docker-enabled machine before claiming container runtime evidence. |",
]
REQUIRED_DEMO_PATH_MAP = [
    "## Demo Path Map",
    "| [Secure Enterprise Knowledge Copilot](#project-1-secure-enterprise-knowledge-copilot) | Open `http://127.0.0.1:8765`, select Alice, and ask `What is the finance retention plan?`; then switch to Morgan for the same question. | Compare abstention vs citation-backed access, copy the trace ID, then run `python -B scripts/dev.py smoke`. |",
    "| [Regulated Customer Operations Agent](#project-2-regulated-customer-operations-agent) | Open `http://127.0.0.1:8770`, select Ivy and `case-1001`, then run the investigation. | Inspect the pending approval, blocked side effect, audit event, and `python -B scripts/dev.py smoke`. |",
    "| [AI Reliability Incident Console](ai-reliability-incident-console/README.md) | Open `http://127.0.0.1:8780`, select the unsafe canary incident, then run triage. | Inspect failed eval evidence, blocked rollout, remediation steps, trace/audit records, and `python -B scripts/dev.py smoke`. |",
]
REQUIRED_DEMO_STATE_PRESETS = [
    "Demo-state reset presets:",
    "`docs/demo_state_presets.json` stores the shareable local reset presets for the canonical Project 1 finance-access path, Project 2 `case-1001` approval path, and Project 3 unsafe canary release path. Run `python -B scripts/dev.py demo-presets` to verify the preset IDs, reset commands, seed references, eval references, and POST payloads still match the fictional seed data before recording or sharing.",
]
REQUIRED_DEMO_RECORDING_READINESS = [
    "Demo recording readiness:",
    "Use the [Demo Recording Checklist](docs/demo_recording_checklist.md) with the [Demo Path Map](#demo-path-map), [Demo State Presets](docs/demo_state_presets.json), [Visual Asset Hygiene](docs/visual_asset_hygiene.md), and [Demo Replay Artifact](docs/demo_replay_artifact.md). Before recording, run `python -B scripts/dev.py demo-presets`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py visual-assets`, and `python -B scripts/dev.py replay-artifact`.",
]
REQUIRED_LAUNCH_CHANNEL_READINESS = [
    "Launch-channel readiness:",
    "Use the [Launch Copy Pack](docs/launch_copy_pack.md) with the [Star Growth Plan](docs/star_growth_plan.md), [Launch Assets Hygiene](docs/launch_assets_hygiene.md), [GitHub Launch Plan](docs/github_launch_plan.md), and [Published Repository Status](docs/published_repository_status.md). Before sharing public launch posts, run `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py assets`, `python -B scripts/dev.py fresh-clone`, and `python -B scripts/post_publish_check.py`; keep Docker runtime, OpenAI live mode, branch protection, release pages, repo topics, profile pins, and social preview setup as manual claims until their checks or account actions are complete.",
]
REQUIRED_CONTRIBUTION_SAFETY_READINESS = [
    "Contribution safety readiness:",
    "Use [CONTRIBUTING](CONTRIBUTING.md), [SECURITY](SECURITY.md), [PR Review Security](docs/pr_review_security.md), [PR Review Runbook](docs/pr_review_runbook.md), the [Maintainer PR Checklist](#maintainer-pr-checklist), and the [Contributor Route Map](#contributor-route-map) before reviewing outside changes. For external PRs, inspect the diff before running untrusted code, then run `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_RELEASE_ARTIFACT_READINESS = [
    "Release artifact readiness:",
    "Use the [Demo Replay Artifact](docs/demo_replay_artifact.md), [GitHub Release Commands](docs/github_release_commands.md), [Post-Publish Checklist](docs/post_publish_checklist.md), [Published Repository Status](docs/published_repository_status.md), and [Final Readiness Report](docs/final_readiness_report.md) before preparing release evidence. Regenerate attachable evidence with `python -B scripts/dev.py replay-artifact`, then run `python -B scripts/dev.py fresh-clone`, `python -B scripts/post_publish_check.py`, and `python -B scripts/dev.py quality`; do not claim a GitHub release page is ready until the page is created and the artifacts are attached.",
]
REQUIRED_OPTIONAL_ENVIRONMENT_READINESS = [
    "Optional-environment readiness:",
    "Use [Container Release Hygiene](docs/container_release_hygiene.md), [Model Runtime Configuration](docs/model_runtime_configuration.md), [Model Gateway Safety](docs/model_gateway_safety.md), the GitHub readiness notes in [Published Repository Status](docs/published_repository_status.md), and [Development Issue Solutions](docs/development_issue_solutions.md) before claiming optional environment evidence. Run `python -B scripts/dev.py container-release` for static container config, `python -B scripts/dev.py docker-runtime` only on a Docker-enabled machine, `python -B scripts/dev.py openai-live` only in an API-key environment, and `python -B scripts/dev.py github-readiness` after a public push; Docker runtime and OpenAI live mode stay manual or environment-dependent until their matching commands pass in the right environment.",
]
REQUIRED_CONNECTOR_ROADMAP_READINESS = [
    "Connector roadmap readiness:",
    "Use [Production Upgrade Notes](docs/production_upgrade_notes.md), [Project Case Notes](docs/project_case_notes.md), [Model Gateway Safety](docs/model_gateway_safety.md), [Architecture Boundaries](docs/architecture_boundaries.md), and the [Connector stubs](#contributor-route-map) row before adding external-system adapters. Connector stubs must keep external side effects behind approval, idempotency, audit, and trace boundaries; run `python -B scripts/dev.py architecture`, `python -B scripts/dev.py model-gateway-safety`, `python -B scripts/dev.py contracts`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_EVAL_REGRESSION_READINESS = [
    "Eval regression readiness:",
    "Use [Demo Report](docs/demo_report.md), [Demo Replay Artifact](docs/demo_replay_artifact.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Scenario Data Integrity](docs/scenario_data_integrity.md), and the [Evidence Legend](#evidence-legend) before changing eval or regression evidence. Run `python -B scripts/dev.py evals`, `python -B scripts/dev.py eval-csv`, `python -B scripts/dev.py claims`, and `python -B scripts/dev.py quality`; unsafe leak, unsafe direct side-effect, and unsafe release approval failure counts must remain zero.",
]
REQUIRED_STORAGE_ADAPTER_READINESS = [
    "Storage adapter readiness:",
    "Use [PostgreSQL And pgvector Adapter Design](docs/postgres_pgvector_adapter_design.md), [Production Upgrade Notes](docs/production_upgrade_notes.md), [Scenario Data Integrity](docs/scenario_data_integrity.md), [Architecture Boundaries](docs/architecture_boundaries.md), and the [Evidence Matrix](#evidence-matrix) before adding persistent storage prototypes. Storage adapters must preserve permission checks before retrieval or side effects, eval-state isolation, trace/audit compatibility, and local JSON default behavior; run `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py dependency-surface`, `python -B scripts/dev.py contracts`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_RED_TEAM_EVAL_READINESS = [
    "Red-team eval readiness:",
    "Use [Threat Model](docs/threat_model.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Scenario Data Integrity](docs/scenario_data_integrity.md), [Technical Review Playbook](docs/technical_review_playbook.md), and the [Evidence Legend](#evidence-legend) before adding attack or bypass eval cases. Prompt-injection, unauthorized-access, approval-bypass, and unsafe-release cases must keep unsafe leak, unsafe direct side-effect, and unsafe release approval failure counts at zero; run `python -B scripts/dev.py threat-model`, `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py evals`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_OPENTELEMETRY_BACKEND_READINESS = [
    "OpenTelemetry backend readiness:",
    "Use [OpenTelemetry Trace Export](docs/otel_trace_export.md), [Observability Integrity](docs/observability_integrity.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Production Upgrade Notes](docs/production_upgrade_notes.md), and the [Evidence Legend](#evidence-legend) before adding hosted collector support. Local JSON trace export remains the default proof path and hosted collectors are optional environment-dependent extensions; run `python -B scripts/dev.py replay`, `python -B scripts/dev.py otel-traces`, `python -B scripts/dev.py observability`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_DOCKER_RUNTIME_READINESS = [
    "Docker runtime readiness:",
    "Use [Container Release Hygiene](docs/container_release_hygiene.md), [Production Upgrade Notes](docs/production_upgrade_notes.md), [Published Repository Status](docs/published_repository_status.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), and the [Release Evidence FAQ](#release-evidence-faq) before claiming container runtime evidence. `python -B scripts/dev.py container-release` is the local static proof path; `python -B scripts/dev.py docker-runtime` is environment-dependent and should be claimed only after it passes on a Docker-enabled machine. Run `python -B scripts/dev.py container-release`, `python -B scripts/dev.py fresh-clone-local`, and `python -B scripts/dev.py quality` before publishing Docker-facing docs.",
]
REQUIRED_DEPENDENCY_SURFACE_READINESS = [
    "Dependency surface readiness:",
    "Use [Supply Chain Security](docs/supply_chain_security.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), the [Contributor Route Map](#contributor-route-map), [Development Issue Solutions](docs/development_issue_solutions.md), and the [Evidence Matrix](#evidence-matrix) before adding packages, CDNs, or runtime manifests. The default posture is stdlib-only Python, first-party frontend assets, pinned Docker bases, and explicit Dependabot coverage until a dependency is intentionally reviewed; run `python -B scripts/dev.py dependency-surface`, `python -B scripts/dev.py safety`, `python -B scripts/dev.py workflow-security`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_API_CONTRACT_READINESS = [
    "API contract readiness:",
    "Use [API Contracts](docs/api_contracts.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Architecture Boundaries](docs/architecture_boundaries.md), [Runtime UI Contracts](docs/runtime_ui_contracts.md), and the [Evidence Matrix](#evidence-matrix) before changing backend routes or frontend API calls. Documented response shapes, read-only scenario snapshot endpoints, static route handling, and frontend API modules must stay aligned; run `python -B scripts/dev.py api-docs`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py ui-contracts`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_ERROR_HYGIENE_READINESS = [
    "Error hygiene readiness:",
    "Use [Error Hygiene](docs/error_hygiene.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Runtime UI Contracts](docs/runtime_ui_contracts.md), [API Contracts](docs/api_contracts.md), and the [Evidence Matrix](#evidence-matrix) before changing app shells or API error handling. Unexpected server exceptions must return generic JSON errors without local paths, stack details, source file names, secret-like markers, or raw exception text, while typed application errors can still return user-safe messages; run `python -B scripts/dev.py error-hygiene`, `python -B scripts/dev.py safety`, `python -B scripts/dev.py ui-contracts`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_MODEL_GATEWAY_READINESS = [
    "Model gateway readiness:",
    "Use [Model Gateway Safety](docs/model_gateway_safety.md), [Model Runtime Configuration](docs/model_runtime_configuration.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [Production Upgrade Notes](docs/production_upgrade_notes.md), and the [Evidence Matrix](#evidence-matrix) before changing gateway code or runtime configuration. OpenAI mode stays opt-in, API keys stay outside the repo, structured outputs are required, failures fall back locally, and models do not authorize permissions, approvals, audit logs, or eval success; run `python -B scripts/dev.py model-gateway-safety`, `python -B scripts/dev.py safety`, `python -B scripts/dev.py contracts`, and `python -B scripts/dev.py quality`, with `python -B scripts/dev.py openai-live` only in API-key environments before claiming live model evidence.",
]
REQUIRED_PR_TRIAGE_READINESS = [
    "PR triage readiness:",
    "Use [PR Review Security](docs/pr_review_security.md), [PR Review Runbook](docs/pr_review_runbook.md), the [Maintainer PR Checklist](#maintainer-pr-checklist), [Development Issue Solutions](docs/development_issue_solutions.md), and the [Evidence Matrix](#evidence-matrix) before approving workflows, running contributor code, or merging public contributions. Treat public PRs as untrusted input: read changed files and diffs before running code, and give workflow, dependency, model gateway, safety, eval, binary, network, shell, and environment changes extra scrutiny; run `python -B scripts/dev.py pr-triage`, `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_THREAT_MODEL_READINESS = [
    "Threat model readiness:",
    "Use [Threat Model](docs/threat_model.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), the [Evidence Legend](#evidence-legend), [Architecture Boundaries](docs/architecture_boundaries.md), and the [Evidence Matrix](#evidence-matrix) before changing security-sensitive behavior. Information disclosure, prompt injection, unsafe side effects, public PR abuse, dependency drift, optional model gateway risk, observability gaps, and UI route surprises must map to deterministic owners and evidence commands; run `python -B scripts/dev.py threat-model`, `python -B scripts/dev.py safety`, `python -B scripts/dev.py evals`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_WORKFLOW_SECURITY_READINESS = [
    "Workflow security readiness:",
    "Use [Workflow Security](docs/workflow_security.md), [System Evidence Matrix](docs/portfolio_evidence_matrix.md), [PR Review Security](docs/pr_review_security.md), [PR Review Runbook](docs/pr_review_runbook.md), and the GitHub Actions row in the [Evidence Matrix](#evidence-matrix) before changing GitHub Actions or automation paths. Public PR workflows must preserve read-only tokens, no secrets, safe triggers, hardened checkout, approved actions, and no CI push or GitHub authentication path; run `python -B scripts/dev.py workflow-security`, `python -B scripts/dev.py governance`, `python -B scripts/dev.py pr-policy`, and `python -B scripts/dev.py quality`.",
]
REQUIRED_OPERATIONAL_RUNBOOK_INDEX = [
    "Operational runbook index:",
    "| Project 1 retrieval, citation-backed answer, and unauthorized abstention | Use the [Demo Path Map](#demo-path-map) Alice/Morgan finance path and the Project 1 sequence in [Final Demo Runbook](docs/final_demo_runbook.md). | [Project Case Notes](docs/project_case_notes.md), [Technical Review Playbook](docs/technical_review_playbook.md), and the permission-aware RAG rows in the [Evidence Matrix](#evidence-matrix). |",
    "| Project 2 investigation, approval queue, side-effect blocking, and supervisor approval | Use the [Demo Path Map](#demo-path-map) Ivy `case-1001` path and the Project 2 sequence in [Final Demo Runbook](docs/final_demo_runbook.md). | [Project Case Notes](docs/project_case_notes.md), [Technical Review Playbook](docs/technical_review_playbook.md), and the governed tool-use rows in the [Evidence Matrix](#evidence-matrix). |",
    "| Project 3 unsafe release triage, failed-eval evidence, rollout blocking, and remediation | Use the [Demo Path Map](#demo-path-map) unsafe canary path and the reliability-console review flow in [Project Case Notes](docs/project_case_notes.md). | [Final Demo Runbook](docs/final_demo_runbook.md), [Technical Review Playbook](docs/technical_review_playbook.md), and the release-triage rows in the [Evidence Matrix](#evidence-matrix). |",
]


def tracked_markdown_files() -> list[Path]:
    return sorted([ROOT / "README.md", *ROOT.glob("docs/**/*.md")])


def strip_code_fences(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            lines.append("")
            continue
        lines.append("" if in_fence else line)
    return "\n".join(lines)


def markdown_anchor(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def anchors_for(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()
    anchors = set()
    seen: dict[str, int] = {}
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = markdown_anchor(match.group(2))
        if not base:
            continue
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def is_external(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "mailto"}


def normalize_link(raw: str) -> str:
    link = raw.strip()
    if link.startswith("<") and ">" in link:
        link = link[1 : link.index(">")]
    elif " " in link:
        link = link.split(" ", 1)[0]
    return unquote(link)


def target_for(source: Path, raw_link: str) -> tuple[Path | None, str | None]:
    link = normalize_link(raw_link)
    if not link or is_external(link):
        return None, None
    if link.startswith("#"):
        return source, link[1:]
    if link.startswith(("app://", "file://")):
        return None, None

    path_part, _, fragment = link.partition("#")
    path_part = path_part.split("?", 1)[0]
    if not path_part:
        return source, fragment
    target = (source.parent / path_part).resolve()
    return target, fragment or None


def within_repo(path: Path) -> bool:
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def gif_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 10 or data[:6] not in {b"GIF87a", b"GIF89a"}:
        return None
    return int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")


def svg_ok(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return "<svg" in text and "</svg>" in text


def check_image(path: Path) -> list[str]:
    failures = []
    suffix = path.suffix.lower()
    if suffix == ".png":
        size = png_size(path)
        if not size:
            failures.append(f"invalid PNG asset: {path.relative_to(ROOT).as_posix()}")
        elif size[0] < 200 or size[1] < 200:
            failures.append(f"PNG asset too small: {path.relative_to(ROOT).as_posix()} {size[0]}x{size[1]}")
    elif suffix == ".gif":
        size = gif_size(path)
        if not size:
            failures.append(f"invalid GIF asset: {path.relative_to(ROOT).as_posix()}")
        elif size[0] < 400 or size[1] < 300:
            failures.append(f"GIF asset too small: {path.relative_to(ROOT).as_posix()} {size[0]}x{size[1]}")
    elif suffix == ".svg" and not svg_ok(path):
        failures.append(f"invalid SVG asset: {path.relative_to(ROOT).as_posix()}")
    return failures


def check_markdown_links() -> list[str]:
    failures = []
    anchor_cache: dict[Path, set[str]] = {}
    for source in tracked_markdown_files():
        if not source.exists():
            continue
        text = strip_code_fences(source.read_text(encoding="utf-8"))
        for raw_link in LINK_RE.findall(text):
            target, fragment = target_for(source, raw_link)
            if target is None:
                continue
            rel_source = source.relative_to(ROOT).as_posix()
            if not within_repo(target):
                failures.append(f"{rel_source}: link escapes repo: {raw_link}")
                continue
            if not target.exists():
                failures.append(f"{rel_source}: missing local link target: {raw_link}")
                continue
            if fragment:
                anchors = anchor_cache.setdefault(target, anchors_for(target))
                normalized = markdown_anchor(fragment)
                if normalized and normalized not in anchors:
                    failures.append(f"{rel_source}: missing anchor {fragment!r} in {target.relative_to(ROOT).as_posix()}")
    return failures


def check_assets() -> list[str]:
    failures = []
    for path in sorted((ROOT / "docs" / "assets").glob("*")):
        if path.suffix.lower() in IMAGE_SUFFIXES:
            failures.extend(check_image(path))
    for rel_path, minimum in REQUIRED_IMAGE_SIZES.items():
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"missing required image asset: {rel_path}")
            continue
        size = png_size(path)
        if not size:
            failures.append(f"invalid required PNG asset: {rel_path}")
            continue
        if size[0] < minimum[0] or size[1] < minimum[1]:
            failures.append(f"required image asset too small: {rel_path} {size[0]}x{size[1]}")
    return failures


def check_readme_captions() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for caption in REQUIRED_README_CAPTIONS:
        if caption not in text:
            failures.append(f"README.md: missing screenshot caption: {caption}")
    return failures


def check_project_risk_badges() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_PROJECT_RISK_BADGES:
        if expected not in text:
            failures.append(f"README.md: missing project risk badge entry: {expected}")
    return failures


def check_screenshot_reviewer_checklist() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_SCREENSHOT_REVIEWER_CHECKLIST:
        if expected not in text:
            failures.append(f"README.md: missing screenshot reviewer checklist entry: {expected}")
    return failures


def check_command_quick_reference() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_COMMAND_QUICK_REFERENCE:
        if expected not in text:
            failures.append(f"README.md: missing command quick-reference entry: {expected}")
    return failures


def check_command_decision_tree() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_COMMAND_DECISION_TREE:
        if expected not in text:
            failures.append(f"README.md: missing command decision tree entry: {expected}")
    return failures


def check_command_output_expectations() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_COMMAND_OUTPUT_EXPECTATIONS:
        if expected not in text:
            failures.append(f"README.md: missing command output expectations entry: {expected}")
    return failures


def check_troubleshooting_pointers() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_TROUBLESHOOTING_POINTERS:
        if expected not in text:
            failures.append(f"README.md: missing troubleshooting pointer entry: {expected}")
    return failures


def check_release_evidence_faq() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_RELEASE_EVIDENCE_FAQ:
        if expected not in text:
            failures.append(f"README.md: missing release evidence FAQ entry: {expected}")
    return failures


def check_architecture_cards() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_ARCHITECTURE_CARDS:
        if expected not in text:
            failures.append(f"README.md: missing architecture card entry: {expected}")
    return failures


def check_evidence_freshness_checklist() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_EVIDENCE_FRESHNESS_CHECKLIST:
        if expected not in text:
            failures.append(f"README.md: missing evidence freshness checklist entry: {expected}")
    return failures


def check_readme_glossary() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_README_GLOSSARY:
        if expected not in text:
            failures.append(f"README.md: missing core glossary entry: {expected}")
    return failures


def check_evidence_legend() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_EVIDENCE_LEGEND:
        if expected not in text:
            failures.append(f"README.md: missing evidence legend entry: {expected}")
    return failures


def check_readme_pr_checklist() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_README_PR_CHECKLIST:
        if expected not in text:
            failures.append(f"README.md: missing maintainer PR checklist entry: {expected}")
    return failures


def check_reviewer_handoff_checklist() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_REVIEWER_HANDOFF_CHECKLIST:
        if expected not in text:
            failures.append(f"README.md: missing reviewer handoff checklist entry: {expected}")
    return failures


def check_contributor_route_map() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_CONTRIBUTOR_ROUTE_MAP:
        if expected not in text:
            failures.append(f"README.md: missing contributor route map entry: {expected}")
    return failures


def check_production_upgrade_pointer() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_PRODUCTION_UPGRADE_POINTER:
        if expected not in text:
            failures.append(f"README.md: missing production upgrade pointer entry: {expected}")
    return failures


def check_demo_path_map() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_DEMO_PATH_MAP:
        if expected not in text:
            failures.append(f"README.md: missing demo path map entry: {expected}")
    return failures


def check_demo_state_presets() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_DEMO_STATE_PRESETS:
        if expected not in text:
            failures.append(f"README.md: missing demo-state preset entry: {expected}")
    return failures


def check_demo_recording_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_DEMO_RECORDING_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing demo recording readiness entry: {expected}")
    return failures


def check_launch_channel_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_LAUNCH_CHANNEL_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing launch-channel readiness entry: {expected}")
    return failures


def check_contribution_safety_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_CONTRIBUTION_SAFETY_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing contribution safety readiness entry: {expected}")
    return failures


def check_release_artifact_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_RELEASE_ARTIFACT_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing release artifact readiness entry: {expected}")
    return failures


def check_optional_environment_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_OPTIONAL_ENVIRONMENT_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing optional-environment readiness entry: {expected}")
    return failures


def check_connector_roadmap_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_CONNECTOR_ROADMAP_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing connector roadmap readiness entry: {expected}")
    return failures


def check_eval_regression_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_EVAL_REGRESSION_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing eval regression readiness entry: {expected}")
    return failures


def check_storage_adapter_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_STORAGE_ADAPTER_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing storage adapter readiness entry: {expected}")
    return failures


def check_red_team_eval_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_RED_TEAM_EVAL_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing red-team eval readiness entry: {expected}")
    return failures


def check_opentelemetry_backend_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_OPENTELEMETRY_BACKEND_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing OpenTelemetry backend readiness entry: {expected}")
    return failures


def check_docker_runtime_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_DOCKER_RUNTIME_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing Docker runtime readiness entry: {expected}")
    return failures


def check_dependency_surface_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_DEPENDENCY_SURFACE_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing dependency surface readiness entry: {expected}")
    return failures


def check_api_contract_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_API_CONTRACT_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing API contract readiness entry: {expected}")
    return failures


def check_error_hygiene_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_ERROR_HYGIENE_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing error hygiene readiness entry: {expected}")
    return failures


def check_model_gateway_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_MODEL_GATEWAY_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing model gateway readiness entry: {expected}")
    return failures


def check_pr_triage_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_PR_TRIAGE_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing PR triage readiness entry: {expected}")
    return failures


def check_threat_model_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_THREAT_MODEL_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing threat model readiness entry: {expected}")
    return failures


def check_workflow_security_readiness() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_WORKFLOW_SECURITY_READINESS:
        if expected not in text:
            failures.append(f"README.md: missing workflow security readiness entry: {expected}")
    return failures


def check_operational_runbook_index() -> list[str]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return ["missing README.md"]
    text = readme.read_text(encoding="utf-8")
    failures = []
    for expected in REQUIRED_OPERATIONAL_RUNBOOK_INDEX:
        if expected not in text:
            failures.append(f"README.md: missing operational runbook index entry: {expected}")
    return failures


def main() -> int:
    failures = []
    failures.extend(check_markdown_links())
    failures.extend(check_assets())
    failures.extend(check_readme_captions())
    failures.extend(check_project_risk_badges())
    failures.extend(check_screenshot_reviewer_checklist())
    failures.extend(check_command_quick_reference())
    failures.extend(check_command_decision_tree())
    failures.extend(check_command_output_expectations())
    failures.extend(check_troubleshooting_pointers())
    failures.extend(check_release_evidence_faq())
    failures.extend(check_architecture_cards())
    failures.extend(check_evidence_freshness_checklist())
    failures.extend(check_readme_glossary())
    failures.extend(check_evidence_legend())
    failures.extend(check_readme_pr_checklist())
    failures.extend(check_reviewer_handoff_checklist())
    failures.extend(check_contributor_route_map())
    failures.extend(check_production_upgrade_pointer())
    failures.extend(check_demo_path_map())
    failures.extend(check_demo_state_presets())
    failures.extend(check_demo_recording_readiness())
    failures.extend(check_launch_channel_readiness())
    failures.extend(check_contribution_safety_readiness())
    failures.extend(check_release_artifact_readiness())
    failures.extend(check_optional_environment_readiness())
    failures.extend(check_connector_roadmap_readiness())
    failures.extend(check_eval_regression_readiness())
    failures.extend(check_storage_adapter_readiness())
    failures.extend(check_red_team_eval_readiness())
    failures.extend(check_opentelemetry_backend_readiness())
    failures.extend(check_docker_runtime_readiness())
    failures.extend(check_dependency_surface_readiness())
    failures.extend(check_api_contract_readiness())
    failures.extend(check_error_hygiene_readiness())
    failures.extend(check_model_gateway_readiness())
    failures.extend(check_pr_triage_readiness())
    failures.extend(check_threat_model_readiness())
    failures.extend(check_workflow_security_readiness())
    failures.extend(check_operational_runbook_index())
    if failures:
        print("Public asset check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Public asset check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
