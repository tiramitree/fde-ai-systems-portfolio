from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRESETS_PATH = ROOT / "docs" / "demo_state_presets.json"

PROJECTS = {
    "secure-enterprise-knowledge-copilot": {
        "seed": ROOT / "secure-enterprise-knowledge-copilot" / "data" / "seed_documents.json",
        "evals": ROOT / "secure-enterprise-knowledge-copilot" / "data" / "eval_cases.json",
        "users_key": "users",
        "step_endpoints": {"/api/query"},
    },
    "regulated-customer-operations-agent": {
        "seed": ROOT / "regulated-customer-operations-agent" / "data" / "seed_state.json",
        "evals": ROOT / "regulated-customer-operations-agent" / "data" / "eval_cases.json",
        "users_key": "users",
        "step_endpoints": {"/api/agent", "/api/approval/approve"},
    },
    "ai-reliability-incident-console": {
        "seed": ROOT / "ai-reliability-incident-console" / "data" / "seed_state.json",
        "evals": ROOT / "ai-reliability-incident-console" / "data" / "eval_cases.json",
        "users_key": "users",
        "step_endpoints": {"/api/triage"},
    },
}

FORBIDDEN_TEXT_MARKERS = (
    "C:/",
    "C:\\",
    "One" + "Drive",
    "x" + "wechat",
    "wx" + "id_",
    "117" + "58",
    "s" + "k-",
    "github_" + "pat_",
    "BEGIN " + "PRIVATE KEY",
)

REQUIRED_PRESET_IDS = {
    "p1-finance-access",
    "p2-case-1001-approval",
    "p3-unsafe-canary-release",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def row_ids(rows: list[dict[str, Any]], source: str, failures: list[str]) -> set[str]:
    ids: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            failures.append(f"{source}: row missing string id")
            continue
        if row_id in ids:
            failures.append(f"{source}: duplicate id {row_id}")
        ids.add(row_id)
    return ids


def check_text_safety(payload: Any, failures: list[str]) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    for marker in FORBIDDEN_TEXT_MARKERS:
        if marker in text:
            failures.append(f"demo_state_presets.json: forbidden text marker {marker!r}")


def index_project_data(project: str, failures: list[str]) -> dict[str, set[str]]:
    config = PROJECTS[project]
    seed = read_json(config["seed"])
    evals = read_json(config["evals"])
    ids: dict[str, set[str]] = {
        "users": row_ids(seed.get("users", []), f"{project} users", failures),
        "eval_cases": row_ids(evals, f"{project} eval cases", failures),
    }
    if project == "secure-enterprise-knowledge-copilot":
        ids["documents"] = row_ids(seed.get("documents", []), "P1 documents", failures)
    elif project == "regulated-customer-operations-agent":
        ids["cases"] = row_ids(seed.get("cases", []), "P2 cases", failures)
        ids["policies"] = row_ids(seed.get("policies", []), "P2 policies", failures)
    elif project == "ai-reliability-incident-console":
        ids["releases"] = row_ids(seed.get("releases", []), "P3 releases", failures)
        ids["incidents"] = row_ids(seed.get("incidents", []), "P3 incidents", failures)
        eval_run_case_ids: set[str] = set()
        for run in seed.get("eval_runs", []):
            eval_run_case_ids.update(row_ids(run.get("cases", []), f"P3 eval run {run.get('id')} cases", failures))
        ids["eval_run_cases"] = eval_run_case_ids
    return ids


def validate_refs(preset: dict[str, Any], ids_by_type: dict[str, set[str]], failures: list[str]) -> None:
    preset_id = preset.get("id", "<missing>")
    seed_refs = preset.get("seed_refs", {})
    require(isinstance(seed_refs, dict), failures, f"{preset_id}: seed_refs must be an object")
    for ref_type, values in seed_refs.items():
        require(ref_type in ids_by_type, failures, f"{preset_id}: unsupported seed ref type {ref_type}")
        require(isinstance(values, list) and values, failures, f"{preset_id}: {ref_type} refs must be a non-empty list")
        known = ids_by_type.get(ref_type, set())
        for value in values if isinstance(values, list) else []:
            require(value in known, failures, f"{preset_id}: {ref_type} references missing id {value}")


def validate_steps(preset: dict[str, Any], ids_by_type: dict[str, set[str]], failures: list[str]) -> None:
    preset_id = preset.get("id", "<missing>")
    project = preset.get("project", "")
    allowed_endpoints = PROJECTS.get(project, {}).get("step_endpoints", set())
    steps = preset.get("steps", [])
    require(isinstance(steps, list) and steps, failures, f"{preset_id}: steps must be a non-empty list")
    for step in steps if isinstance(steps, list) else []:
        label = step.get("label", "<missing>")
        require(step.get("method") == "POST", failures, f"{preset_id}/{label}: only POST steps are supported")
        require(step.get("endpoint") in allowed_endpoints, failures, f"{preset_id}/{label}: unexpected endpoint {step.get('endpoint')}")
        payload = step.get("payload", {})
        expected = step.get("expected", {})
        require(isinstance(payload, dict), failures, f"{preset_id}/{label}: payload must be an object")
        require(isinstance(expected, dict) and expected, failures, f"{preset_id}/{label}: expected must be a non-empty object")
        user_id = payload.get("user_id") or payload.get("approver_id")
        if user_id:
            require(user_id in ids_by_type["users"], failures, f"{preset_id}/{label}: unknown user {user_id}")
        if "case_id" in payload:
            require(payload["case_id"] in ids_by_type.get("cases", set()), failures, f"{preset_id}/{label}: unknown case {payload['case_id']}")
        if "release_id" in payload:
            require(payload["release_id"] in ids_by_type.get("releases", set()), failures, f"{preset_id}/{label}: unknown release {payload['release_id']}")
        if "incident_id" in payload:
            require(payload["incident_id"] in ids_by_type.get("incidents", set()), failures, f"{preset_id}/{label}: unknown incident {payload['incident_id']}")
        for doc_id in expected.get("must_cite_doc_ids", []) + expected.get("forbidden_doc_ids", []):
            require(doc_id in ids_by_type.get("documents", set()), failures, f"{preset_id}/{label}: unknown document {doc_id}")
        for policy_id in expected.get("must_cite_policy_ids", []):
            require(policy_id in ids_by_type.get("policies", set()), failures, f"{preset_id}/{label}: unknown policy {policy_id}")
        for eval_case_id in expected.get("must_link_eval_case_ids", []):
            require(eval_case_id in ids_by_type.get("eval_run_cases", set()), failures, f"{preset_id}/{label}: unknown eval run case {eval_case_id}")


def validate_canonical_coverage(presets: list[dict[str, Any]], failures: list[str]) -> None:
    by_id = {preset.get("id"): preset for preset in presets}
    require(REQUIRED_PRESET_IDS <= set(by_id), failures, "demo presets must cover all canonical project paths")

    p1_refs = by_id.get("p1-finance-access", {}).get("seed_refs", {})
    require({"alice", "morgan"} <= set(p1_refs.get("users", [])), failures, "p1-finance-access must cover Alice and Morgan")
    require("finance-retention-plan-2026" in p1_refs.get("documents", []), failures, "p1-finance-access must reference the finance document")

    p2_refs = by_id.get("p2-case-1001-approval", {}).get("seed_refs", {})
    require({"ivy", "sam"} <= set(p2_refs.get("users", [])), failures, "p2-case-1001-approval must cover Ivy and Sam")
    require("case-1001" in p2_refs.get("cases", []), failures, "p2-case-1001-approval must reference case-1001")

    p3_refs = by_id.get("p3-unsafe-canary-release", {}).get("seed_refs", {})
    require("maya" in p3_refs.get("users", []), failures, "p3-unsafe-canary-release must cover Maya")
    require("rel-2026-06-01" in p3_refs.get("releases", []), failures, "p3-unsafe-canary-release must reference rel-2026-06-01")
    require("inc-2026-014" in p3_refs.get("incidents", []), failures, "p3-unsafe-canary-release must reference inc-2026-014")
    require(
        {"rel-eval-003-employee-finance-abstain", "rel-eval-004-citation-required"} <= set(p3_refs.get("eval_run_cases", [])),
        failures,
        "p3-unsafe-canary-release must reference the failed eval evidence",
    )


def main() -> int:
    failures: list[str] = []
    require(PRESETS_PATH.exists(), failures, "missing docs/demo_state_presets.json")
    if failures:
        print("Demo state presets check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    payload = read_json(PRESETS_PATH)
    check_text_safety(payload, failures)
    require(payload.get("schema_version") == "1.0", failures, "schema_version must be 1.0")
    verify_commands = payload.get("verify_commands", [])
    for command in ("python -B scripts/dev.py demo-presets", "python -B scripts/dev.py replay", "python -B scripts/dev.py smoke"):
        require(command in verify_commands, failures, f"verify_commands must include {command}")

    presets = payload.get("presets", [])
    require(isinstance(presets, list) and presets, failures, "presets must be a non-empty list")
    preset_ids = row_ids(presets if isinstance(presets, list) else [], "demo presets", failures)
    require(len(preset_ids) == len(presets), failures, "preset ids must be unique")
    validate_canonical_coverage(presets if isinstance(presets, list) else [], failures)

    indexed: dict[str, dict[str, set[str]]] = {}
    for preset in presets if isinstance(presets, list) else []:
        preset_id = preset.get("id", "<missing>")
        project = preset.get("project")
        require(project in PROJECTS, failures, f"{preset_id}: unknown project {project}")
        require(str(preset.get("local_url", "")).startswith("http://127.0.0.1:"), failures, f"{preset_id}: local_url must be loopback")
        require("--reset" in str(preset.get("reset_command", "")), failures, f"{preset_id}: reset_command must include --reset")
        require("python -B scripts/dev.py demo-presets" in preset.get("evidence_commands", []), failures, f"{preset_id}: evidence commands must include demo-presets")
        for rel_path in preset.get("state_sources", []):
            require((ROOT / rel_path).exists(), failures, f"{preset_id}: missing state source {rel_path}")
        if project in PROJECTS:
            indexed.setdefault(project, index_project_data(project, failures))
            validate_refs(preset, indexed[project], failures)
            validate_steps(preset, indexed[project], failures)

    if failures:
        print("Demo state presets check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Demo state presets check passed: 3 canonical reset presets reference valid seed and eval data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
