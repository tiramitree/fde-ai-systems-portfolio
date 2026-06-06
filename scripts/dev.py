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
    "community-issues": ["scripts/check_community_issue_pack.py"],
    "container-release": ["scripts/check_container_release.py"],
    "docker-runtime": ["scripts/check_docker_runtime.py"],
    "dependency-surface": ["scripts/check_dependency_surface.py"],
    "demo-presets": ["scripts/check_demo_state_presets.py"],
    "contracts": ["scripts/check_api_contracts.py"],
    "error-hygiene": ["scripts/check_error_hygiene.py"],
    "health": ["scripts/check_health.py"],
    "evals": ["scripts/run_all_evals.py"],
    "eval-csv": ["scripts/export_eval_csv.py"],
    "frontend": ["scripts/check_frontend_integrity.py"],
    "fresh-clone": ["scripts/check_fresh_clone_experience.py"],
    "fresh-clone-local": ["scripts/check_fresh_clone_experience.py", "--source", str(ROOT)],
    "github-launch-setup": ["scripts/configure_github_launch.py"],
    "github-community": ["scripts/manage_community_issues.py"],
    "github-maintenance": ["scripts/maintain_github_state.py"],
    "github-readiness": ["scripts/check_github_readiness.py"],
    "governance": ["scripts/check_repository_governance.py"],
    "launch-assets": ["scripts/check_launch_assets.py"],
    "model-gateway-safety": ["scripts/check_model_gateway_safety.py"],
    "observability": ["scripts/check_observability_integrity.py"],
    "openai-live": ["scripts/check_openai_live_mode.py"],
    "otel-traces": ["scripts/export_traces_otel.py"],
    "postgres-migrations": ["scripts/check_postgres_migrations.py"],
    "postgres-runtime": ["scripts/check_project1_postgres_runtime.py"],
    "postgres-seed": ["scripts/generate_postgres_seed.py", "--check"],
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
    "visual-asset-diff": ["scripts/summarize_visual_asset_diff.py"],
    "workflow-security": ["scripts/check_workflow_security.py"],
}


def run_script(command: list[str]) -> int:
    return subprocess.run([sys.executable, "-B", *command], cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-platform developer entrypoint for the FDE AI Systems Reference repository.",
    )
    parser.add_argument(
        "command",
        choices=sorted(COMMANDS.keys()),
        help=(
            "start: run all demo servers; api-docs/architecture/assets/claims/community-issues/container-release/docker-runtime/dependency-surface/demo-presets/contracts/error-hygiene/health/evals/eval-csv/frontend/fresh-clone/fresh-clone-local/github-community/github-launch-setup/github-maintenance/github-readiness/governance/launch-assets/model-gateway-safety/observability/openai-live/otel-traces/postgres-migrations/postgres-runtime/postgres-seed/pr-policy/pr-triage/readiness-report/refresh-visual-assets/replay/replay-artifact/scenario-data/smoke/report/safety/quality/threat-model/ui-contracts/visual-assets/visual-asset-diff/workflow-security: run individual gates; "
            "visual-asset-diff: summarize changed visual assets without printing binary image contents; "
            "verify: start services if needed and run the full CI-quality gate."
        ),
    )
    args = parser.parse_args()
    return run_script(COMMANDS[args.command])


if __name__ == "__main__":
    raise SystemExit(main())
