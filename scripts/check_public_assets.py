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
    "| Verification | `python -B scripts/dev.py verify`, `python -B scripts/dev.py quality`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py evals`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py safety` |",
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
    "Evidence legend:",
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
REQUIRED_CONTRIBUTOR_ROUTE_MAP = [
    "Contributor route map:",
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
    failures.extend(check_evidence_freshness_checklist())
    failures.extend(check_readme_glossary())
    failures.extend(check_evidence_legend())
    failures.extend(check_readme_pr_checklist())
    failures.extend(check_contributor_route_map())
    failures.extend(check_production_upgrade_pointer())
    failures.extend(check_demo_path_map())
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
