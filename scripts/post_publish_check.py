from __future__ import annotations

import re
import subprocess
import sys
import time
import http.client
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def print_check(ok: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    suffix = f": {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")
    return ok


def repo_from_remote(remote: str) -> str | None:
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def url_exists_once(url: str) -> tuple[bool, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "fde-reference-post-publish-check"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return 200 <= response.status < 400, str(response.status)
    except urllib.error.HTTPError as exc:
        return False, str(exc.code)
    except urllib.error.URLError as exc:
        return False, str(exc.reason)
    except (TimeoutError, ConnectionError, http.client.RemoteDisconnected) as exc:
        return False, str(exc)


def url_exists(url: str, attempts: int = 3) -> tuple[bool, str]:
    last_detail = ""
    for attempt in range(1, attempts + 1):
        ok, detail = url_exists_once(url)
        if ok:
            return ok, detail if attempt == 1 else f"{detail} after retry {attempt}"
        last_detail = detail
        if attempt < attempts:
            time.sleep(1)
    return False, last_detail


def main() -> int:
    failures = 0

    code, remote = run(["git", "remote", "get-url", "origin"])
    if not print_check(code == 0 and bool(remote), "origin remote configured", remote):
        return 1

    repo = repo_from_remote(remote)
    if not print_check(repo is not None, "origin points to a GitHub repository", remote):
        return 1

    code, branch = run(["git", "branch", "--show-current"])
    failures += 0 if print_check(code == 0 and branch == "main", "local branch is main", branch) else 1

    code, status = run(["git", "status", "--short"])
    failures += 0 if print_check(code == 0 and not status, "tracked worktree clean") else 1

    code, ls_remote = run(["git", "ls-remote", "--heads", "origin", "main"])
    failures += 0 if print_check(code == 0 and "refs/heads/main" in ls_remote, "remote main branch exists") else 1

    repo_url = f"https://github.com/{repo}"
    ok, detail = url_exists(repo_url)
    failures += 0 if print_check(ok, "GitHub repository page reachable", f"{repo_url} ({detail})") else 1

    raw_readme = f"https://raw.githubusercontent.com/{repo}/main/README.md"
    ok, detail = url_exists(raw_readme)
    failures += 0 if print_check(ok, "raw README reachable", f"{detail}") else 1

    raw_workflow = f"https://raw.githubusercontent.com/{repo}/main/.github/workflows/ci.yml"
    ok, detail = url_exists(raw_workflow)
    failures += 0 if print_check(ok, "GitHub Actions workflow reachable", f"{detail}") else 1

    expected_files = [
        "README.md",
        "PROJECT_CONTENT_INDEX.md",
        ".github/CODEOWNERS",
        ".github/dependabot.yml",
        "docs/portfolio_evidence_matrix.md",
        "docs/supply_chain_security.md",
        "docs/architecture_boundaries.md",
        "docs/workflow_security.md",
        "docs/frontend_integrity.md",
        "docs/visual_asset_hygiene.md",
        "docs/visual_assets_manifest.json",
        "docs/fresh_clone_experience.md",
        "docs/runtime_ui_contracts.md",
        "docs/api_contracts.md",
        "docs/github_branch_protection.json",
        "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/public_roadmap_issue_comment_examples.md",
        "docs/github_discussions_launch_checklist.md",
        "docs/dependabot_secret_scanning_verification_examples.md",
        "docs/branch_protection_verification_examples.md",
        "docs/github_repository_settings.md",
        "docs/social_preview_verification_examples.md",
        "docs/profile_pin_verification_examples.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_actions_warning_examples.md",
        "docs/github_actions_badge_verification_examples.md",
        "docs/github_label_troubleshooting_examples.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_labels.json",
        "docs/github_release_notes_v0.1.0.md",
        "docs/launch_copy_pack.md",
        "docs/launch_feedback_collection_examples.md",
        "docs/public_maintainer_status_update_examples.md",
        "docs/contributor_attribution_examples.md",
        "docs/issue_triage_sla_wording_examples.md",
        "docs/discussion_to_issue_conversion_examples.md",
        "docs/postgres_pgvector_adapter_design.md",
        "docs/otel_trace_export.md",
        "docs/model_gateway_safety.md",
        "docs/eval_csv_troubleshooting_examples.md",
        "docs/launch_assets_hygiene.md",
        "docs/observability_integrity.md",
        "docs/threat_model.md",
        "docs/scenario_data_integrity.md",
        "docs/error_hygiene.md",
        "docs/development_issue_solutions.md",
        "docs/final_readiness_report.md",
        "docs/demo_replay_artifact.md",
        "docs/release_attachment_verification_examples.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/release_note_refresh_checklist.md",
        "docs/release_note_changelog_drift_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/demo_state_presets.json",
        "docs/container_release_hygiene.md",
        "docs/pr_review_runbook.md",
        "docs/pr_review_security.md",
        "docs/project_case_notes.md",
        "docs/technical_review_playbook.md",
        "docs/assets/github-preview.png",
        "docs/assets/demo-walkthrough.gif",
        "docs/assets/secure-knowledge-copilot-screenshot.png",
        "docs/assets/secure-knowledge-copilot-mobile.png",
        "docs/assets/regulated-ops-agent-screenshot.png",
        "docs/assets/regulated-ops-agent-mobile.png",
        "docs/assets/ai-reliability-incident-console-screenshot.png",
        "docs/assets/ai-reliability-incident-console-mobile.png",
        "scripts/check_claim_consistency.py",
        "scripts/check_container_release.py",
        "scripts/check_docker_runtime.py",
        "scripts/check_launch_assets.py",
        "scripts/check_architecture_boundaries.py",
        "scripts/check_workflow_security.py",
        "scripts/check_model_gateway_safety.py",
        "scripts/check_openai_live_mode.py",
        "scripts/check_observability_integrity.py",
        "scripts/check_threat_model.py",
        "scripts/check_scenario_data_integrity.py",
        "scripts/check_error_hygiene.py",
        "scripts/check_frontend_integrity.py",
        "scripts/check_visual_asset_manifest.py",
        "scripts/summarize_visual_asset_diff.py",
        "scripts/refresh_visual_assets.py",
        "scripts/check_fresh_clone_experience.py",
        "scripts/check_runtime_ui_contracts.py",
        "scripts/check_api_documentation.py",
        "scripts/check_dependency_surface.py",
        "scripts/check_demo_state_presets.py",
        "scripts/configure_github_launch.py",
        "scripts/community_issue_pack.py",
        "scripts/check_community_issue_pack.py",
        "scripts/manage_community_issues.py",
        "scripts/export_demo_replay_artifact.py",
        "scripts/check_repository_governance.py",
        "scripts/check_pr_review_policy.py",
        "scripts/review_open_prs.py",
        "scripts/maintain_github_state.py",
        "ai-reliability-incident-console/README.md",
        "ai-reliability-incident-console/app.py",
        "ai-reliability-incident-console/Dockerfile",
        "ai-reliability-incident-console/.dockerignore",
        "ai-reliability-incident-console/docs/architecture.md",
        "ai-reliability-incident-console/docs/technical_review_notes.md",
        "ai-reliability-incident-console/src/reliability_console/api.py",
        "ai-reliability-incident-console/src/reliability_console/triage.py",
        "ai-reliability-incident-console/web/index.html",
        "secure-enterprise-knowledge-copilot/Dockerfile",
        "secure-enterprise-knowledge-copilot/docs/technical_review_notes.md",
        "regulated-customer-operations-agent/Dockerfile",
        "regulated-customer-operations-agent/docs/technical_review_notes.md",
        ".github/workflows/ci.yml",
    ]
    for rel_path in expected_files:
        url = f"https://raw.githubusercontent.com/{repo}/main/{rel_path}"
        ok, detail = url_exists(url)
        failures += 0 if print_check(ok, f"published file: {rel_path}", detail) else 1

    if failures:
        print(f"\nPost-publish check failed with {failures} issue(s).")
        return 1

    print("\nPost-publish check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
