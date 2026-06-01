from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = {
    "api-docs": ["scripts/check_api_documentation.py"],
    "architecture": ["scripts/check_architecture_boundaries.py"],
    "start": ["scripts/start_demo_servers.py"],
    "assets": ["scripts/check_public_assets.py"],
    "claims": ["scripts/check_claim_consistency.py"],
    "container-release": ["scripts/check_container_release.py"],
    "docker-runtime": ["scripts/check_docker_runtime.py"],
    "dependency-surface": ["scripts/check_dependency_surface.py"],
    "contracts": ["scripts/check_api_contracts.py"],
    "error-hygiene": ["scripts/check_error_hygiene.py"],
    "health": ["scripts/check_health.py"],
    "evals": ["scripts/run_all_evals.py"],
    "eval-csv": ["scripts/export_eval_csv.py"],
    "frontend": ["scripts/check_frontend_integrity.py"],
    "fresh-clone": ["scripts/check_fresh_clone_experience.py"],
    "github-launch-setup": ["scripts/configure_github_launch.py"],
    "github-readiness": ["scripts/check_github_readiness.py"],
    "governance": ["scripts/check_repository_governance.py"],
    "model-gateway-safety": ["scripts/check_model_gateway_safety.py"],
    "observability": ["scripts/check_observability_integrity.py"],
    "otel-traces": ["scripts/export_traces_otel.py"],
    "pr-policy": ["scripts/check_pr_review_policy.py"],
    "pr-triage": ["scripts/review_open_prs.py"],
    "readiness-report": ["scripts/generate_final_readiness_report.py"],
    "refresh-visual-assets": ["scripts/refresh_visual_assets.py"],
    "replay": ["scripts/replay_demo.py"],
    "replay-artifact": ["scripts/export_demo_replay_artifact.py"],
    "scenario-data": ["scripts/check_scenario_data_integrity.py"],
    "smoke": ["scripts/smoke_test_demo_flows.py"],
    "report": ["scripts/generate_demo_report.py"],
    "safety": ["scripts/public_safety_scan.py"],
    "quality": ["scripts/quality_gate.py"],
    "threat-model": ["scripts/check_threat_model.py"],
    "ui-contracts": ["scripts/check_runtime_ui_contracts.py"],
    "verify": ["scripts/ci_quality_gate.py"],
    "visual-assets": ["scripts/check_visual_asset_manifest.py"],
    "workflow-security": ["scripts/check_workflow_security.py"],
}


def run_script(script: str) -> int:
    return subprocess.run([sys.executable, "-B", script], cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-platform developer entrypoint for the FDE AI Systems Portfolio.",
    )
    parser.add_argument(
        "command",
        choices=sorted(COMMANDS.keys()),
        help=(
            "start: run both demo servers; api-docs/architecture/assets/claims/container-release/docker-runtime/dependency-surface/contracts/error-hygiene/health/evals/eval-csv/frontend/fresh-clone/github-launch-setup/github-readiness/governance/model-gateway-safety/observability/otel-traces/pr-policy/pr-triage/readiness-report/refresh-visual-assets/replay/replay-artifact/scenario-data/smoke/report/safety/quality/threat-model/ui-contracts/visual-assets/workflow-security: run individual gates; "
            "verify: start services if needed and run the full CI-quality gate."
        ),
    )
    args = parser.parse_args()
    return run_script(COMMANDS[args.command][0])


if __name__ == "__main__":
    raise SystemExit(main())
