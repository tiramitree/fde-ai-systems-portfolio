from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from public_safety_scan import check_forbidden_content, check_runtime_artifacts


ROOT = Path(__file__).resolve().parents[1]
SERVICES = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "path": ROOT / "secure-enterprise-knowledge-copilot",
        "port": 8765,
        "health": "http://127.0.0.1:8765/api/health",
    },
    {
        "name": "regulated-customer-operations-agent",
        "path": ROOT / "regulated-customer-operations-agent",
        "port": 8770,
        "health": "http://127.0.0.1:8770/api/health",
    },
]

REQUIRED_FILES = [
    "README.md",
    "PROJECT_CONTENT_INDEX.md",
    "CHANGELOG.md",
    ".gitattributes",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "ROADMAP.md",
    "CODE_OF_CONDUCT.md",
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/eval_case.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    "docs/final_demo_runbook.md",
    "docs/final_readiness_report.md",
    "docs/demo_report.md",
    "docs/demo_replay_artifact.md",
    "docs/container_release_hygiene.md",
    "docs/visual_asset_hygiene.md",
    "docs/visual_assets_manifest.json",
    "docs/resume_and_interview_package.md",
    "docs/production_upgrade_notes.md",
    "docs/postgres_pgvector_adapter_design.md",
    "docs/otel_trace_export.md",
    "docs/model_runtime_configuration.md",
    "docs/model_gateway_safety.md",
    "docs/observability_integrity.md",
    "docs/threat_model.md",
    "docs/scenario_data_integrity.md",
    "docs/error_hygiene.md",
    "docs/supply_chain_security.md",
    "docs/architecture_boundaries.md",
    "docs/workflow_security.md",
    "docs/frontend_integrity.md",
    "docs/fresh_clone_experience.md",
    "docs/runtime_ui_contracts.md",
    "docs/api_contracts.md",
    "docs/public_release_audit.md",
    "docs/differentiation_strategy.md",
    "docs/hard_interview_playbook.md",
    "docs/system_design_deep_dive.md",
    "docs/portfolio_evidence_matrix.md",
    "docs/adr_0001_local_first_portfolio.md",
    "docs/adr_0002_model_is_not_security_boundary.md",
    "docs/adr_0003_eval_state_isolated_from_demo_state.md",
    "docs/github_branch_protection.json",
    "docs/github_repository_settings.md",
    "docs/community_backlog.md",
    "docs/github_initial_issues.md",
    "docs/post_publish_checklist.md",
    "docs/published_repository_status.md",
    "docs/case_study_secure_enterprise_knowledge_copilot.md",
    "docs/case_study_regulated_customer_operations_agent.md",
    "docs/demo_video_script.md",
    "docs/demo_recording_checklist.md",
    "docs/star_growth_plan.md",
    "docs/launch_copy_pack.md",
    "docs/reviewer_perspective_checklist.md",
    "docs/github_release_commands.md",
    "docs/github_release_notes_v0.1.0.md",
    "docs/maintainer_review_policy.md",
    "docs/pr_review_runbook.md",
    "docs/pr_review_security.md",
    "docs/assets/github-preview.png",
    "docs/assets/github-preview.svg",
    "docs/assets/architecture-overview.svg",
    "docs/assets/demo-walkthrough.gif",
    "docs/assets/secure-knowledge-copilot-screenshot.png",
    "docs/assets/regulated-ops-agent-screenshot.png",
    "scripts/dev.py",
    "scripts/check_architecture_boundaries.py",
    "scripts/check_workflow_security.py",
    "scripts/check_model_gateway_safety.py",
    "scripts/check_observability_integrity.py",
    "scripts/check_threat_model.py",
    "scripts/check_scenario_data_integrity.py",
    "scripts/check_error_hygiene.py",
    "scripts/check_claim_consistency.py",
    "scripts/check_container_release.py",
    "scripts/check_visual_asset_manifest.py",
    "scripts/check_frontend_integrity.py",
    "scripts/check_fresh_clone_experience.py",
    "scripts/check_runtime_ui_contracts.py",
    "scripts/check_api_documentation.py",
    "scripts/check_dependency_surface.py",
    "scripts/public_safety_scan.py",
    "scripts/check_public_assets.py",
    "scripts/check_github_readiness.py",
    "scripts/check_repository_governance.py",
    "scripts/check_api_contracts.py",
    "scripts/configure_github_launch.py",
    "scripts/generate_final_readiness_report.py",
    "scripts/check_pr_review_policy.py",
    "scripts/review_open_prs.py",
    "scripts/replay_demo.py",
    "scripts/export_demo_replay_artifact.py",
    "scripts/export_eval_csv.py",
    "scripts/export_traces_otel.py",
    "scripts/post_publish_check.py",
    "secure-enterprise-knowledge-copilot/src/copilot/api.py",
    "secure-enterprise-knowledge-copilot/.dockerignore",
    "secure-enterprise-knowledge-copilot/README.md",
    "secure-enterprise-knowledge-copilot/web/js/api.js",
    "secure-enterprise-knowledge-copilot/web/js/app.js",
    "secure-enterprise-knowledge-copilot/web/js/dom.js",
    "secure-enterprise-knowledge-copilot/web/js/renderers.js",
    "regulated-customer-operations-agent/src/ops_agent/api.py",
    "regulated-customer-operations-agent/.dockerignore",
    "regulated-customer-operations-agent/README.md",
    "regulated-customer-operations-agent/web/js/api.js",
    "regulated-customer-operations-agent/web/js/app.js",
    "regulated-customer-operations-agent/web/js/dom.js",
    "regulated-customer-operations-agent/web/js/renderers.js",
]


def run(args: list[str]) -> tuple[bool, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def healthy(url: str) -> bool:
    try:
        with urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def wait_for_health(url: str, seconds: int = 15) -> bool:
    for _ in range(seconds):
        if healthy(url):
            return True
        time.sleep(1)
    return False


def start_service(service: dict) -> subprocess.Popen | None:
    if healthy(service["health"]):
        print(f"{service['name']} already healthy on port {service['port']}")
        return None

    print(f"Starting {service['name']} on port {service['port']}")
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--port",
            str(service["port"]),
        ],
        cwd=service["path"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def check_required_files() -> list[str]:
    failures = []
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).exists():
            failures.append(f"missing required file: {rel_path}")
    return failures


def main() -> int:
    failures = []
    failures.extend(check_required_files())
    failures.extend(check_forbidden_content())
    failures.extend(check_runtime_artifacts())
    started: list[subprocess.Popen] = []

    command_checks = [
        ("architecture", [sys.executable, "-B", "scripts/check_architecture_boundaries.py"]),
        ("workflow-security", [sys.executable, "-B", "scripts/check_workflow_security.py"]),
        ("model-gateway-safety", [sys.executable, "-B", "scripts/check_model_gateway_safety.py"]),
        ("observability", [sys.executable, "-B", "scripts/check_observability_integrity.py"]),
        ("threat-model", [sys.executable, "-B", "scripts/check_threat_model.py"]),
        ("scenario-data", [sys.executable, "-B", "scripts/check_scenario_data_integrity.py"]),
        ("error-hygiene", [sys.executable, "-B", "scripts/check_error_hygiene.py"]),
        ("assets", [sys.executable, "-B", "scripts/check_public_assets.py"]),
        ("visual-assets", [sys.executable, "-B", "scripts/check_visual_asset_manifest.py"]),
        ("frontend", [sys.executable, "-B", "scripts/check_frontend_integrity.py"]),
        ("ui-contracts", [sys.executable, "-B", "scripts/check_runtime_ui_contracts.py"]),
        ("api-docs", [sys.executable, "-B", "scripts/check_api_documentation.py"]),
        ("dependency-surface", [sys.executable, "-B", "scripts/check_dependency_surface.py"]),
        ("governance", [sys.executable, "-B", "scripts/check_repository_governance.py"]),
        ("pr-policy", [sys.executable, "-B", "scripts/check_pr_review_policy.py"]),
        ("contracts", [sys.executable, "-B", "scripts/check_api_contracts.py"]),
        ("health", [sys.executable, "-B", "scripts/check_health.py"]),
        ("evals", [sys.executable, "-B", "scripts/run_all_evals.py"]),
        ("smoke", [sys.executable, "-B", "scripts/smoke_test_demo_flows.py"]),
        ("replay-artifact", [sys.executable, "-B", "scripts/export_demo_replay_artifact.py"]),
        ("report", [sys.executable, "-B", "scripts/generate_demo_report.py"]),
        ("claims", [sys.executable, "-B", "scripts/check_claim_consistency.py"]),
        ("container-release", [sys.executable, "-B", "scripts/check_container_release.py"]),
    ]
    try:
        for service in SERVICES:
            process = start_service(service)
            if process is not None:
                started.append(process)

        for service in SERVICES:
            if not wait_for_health(service["health"]):
                failures.append(f"service did not become healthy: {service['name']}")

        for name, command in command_checks:
            ok, output = run(command)
            print(f"\n=== {name} ===")
            print(output)
            if not ok:
                failures.append(f"command failed: {name}")
    finally:
        for process in started:
            process.terminate()
        for process in started:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    if failures:
        print("\nQuality gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nQuality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
