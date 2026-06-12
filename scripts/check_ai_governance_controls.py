from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "ai_governance_control_registry.json"
THREAT_MODEL = ROOT / "docs" / "threat_model.md"
INDUSTRIAL_PLAN = ROOT / "docs" / "industrial_true_production_gap_plan_2026_06_07.md"

REQUIRED_OWASP_CODES = {f"LLM{i:02d}" for i in range(1, 11)}
REQUIRED_NIST_FUNCTIONS = {"Govern", "Map", "Measure", "Manage"}
REQUIRED_THREATS = {f"T{i:02d}" for i in range(1, 14)}
REQUIRED_FRAMEWORKS = {"owasp-llm-top-10-2025", "nist-ai-rmf-genai-profile"}
PRIVATE_MARKERS = [
    "C:" + "/Users/",
    "C:" + "\\Users\\",
    "One" + "Drive/" + "xwe" + "chat_files",
    "wx" + "id_",
    "gh" + "o_",
    "s" + "k-" + "proj-",
    "s" + "k-" + "live-",
]


def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def command_names() -> set[str]:
    text = read_text("scripts/dev.py")
    return set(re.findall(r'^\s+"([^"]+)":\s+\["scripts/', text, flags=re.MULTILINE))


def load_registry() -> tuple[dict, list[str]]:
    if not REGISTRY.exists():
        return {}, ["missing docs/ai_governance_control_registry.json"]
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return {}, [f"invalid governance registry JSON: {exc}"]


def check_registry_shape(registry: dict) -> list[str]:
    failures: list[str] = []
    if registry.get("schema_version") != "ai-governance-control-registry-v1":
        failures.append("registry schema_version must be ai-governance-control-registry-v1")
    if registry.get("updated_at") != "2026-06-07":
        failures.append("registry updated_at must be 2026-06-07")
    if not registry.get("purpose"):
        failures.append("registry missing purpose")

    frameworks = registry.get("frameworks")
    if not isinstance(frameworks, list):
        return failures + ["registry frameworks must be a list"]
    framework_ids = {framework.get("id") for framework in frameworks if isinstance(framework, dict)}
    missing_frameworks = REQUIRED_FRAMEWORKS - framework_ids
    if missing_frameworks:
        failures.append(f"registry missing frameworks: {sorted(missing_frameworks)}")
    for framework in frameworks:
        if not isinstance(framework, dict):
            failures.append("registry framework entry must be an object")
            continue
        if not framework.get("source_url", "").startswith("https://"):
            failures.append(f"framework {framework.get('id')} missing https source_url")

    controls = registry.get("controls")
    if not isinstance(controls, list):
        failures.append("registry controls must be a list")
    elif len(controls) < 10:
        failures.append("registry must include at least 10 governance controls")
    return failures


def check_controls(registry: dict) -> list[str]:
    failures: list[str] = []
    controls = registry.get("controls") or []
    if not isinstance(controls, list):
        return ["registry controls must be a list"]

    available_commands = command_names()
    seen_ids: set[str] = set()
    covered_owasp: set[str] = set()
    covered_nist: set[str] = set()
    covered_threats: set[str] = set()

    for control in controls:
        if not isinstance(control, dict):
            failures.append("control entry must be an object")
            continue

        control_id = control.get("id")
        if not isinstance(control_id, str) or not re.fullmatch(r"GOV-\d{2}", control_id):
            failures.append(f"control has invalid id: {control_id!r}")
            control_id = "UNKNOWN"
        elif control_id in seen_ids:
            failures.append(f"duplicate control id: {control_id}")
        seen_ids.add(control_id)

        for field in [
            "title",
            "status",
            "owner_role",
            "risk_families",
            "repo_controls",
            "remaining_production_gap",
        ]:
            if not control.get(field):
                failures.append(f"{control_id} missing {field}")

        threat_ids = control.get("threat_ids") or []
        owasp_entries = control.get("owasp_llm_2025") or []
        nist_functions = control.get("nist_ai_rmf_functions") or []
        evidence_files = control.get("evidence_files") or []
        evidence_commands = control.get("evidence_commands") or []

        if not isinstance(threat_ids, list) or not threat_ids:
            failures.append(f"{control_id} missing threat_ids")
        if not isinstance(owasp_entries, list) or not owasp_entries:
            failures.append(f"{control_id} missing owasp_llm_2025")
        if not isinstance(nist_functions, list) or not nist_functions:
            failures.append(f"{control_id} missing nist_ai_rmf_functions")
        if not isinstance(evidence_files, list) or not evidence_files:
            failures.append(f"{control_id} missing evidence_files")
        if not isinstance(evidence_commands, list) or not evidence_commands:
            failures.append(f"{control_id} missing evidence_commands")

        for threat_id in threat_ids:
            if not re.fullmatch(r"T\d{2}", str(threat_id)):
                failures.append(f"{control_id} invalid threat id: {threat_id}")
            covered_threats.add(str(threat_id))

        for entry in owasp_entries:
            match = re.match(r"(LLM\d{2})\b", str(entry))
            if not match:
                failures.append(f"{control_id} invalid OWASP entry: {entry}")
                continue
            covered_owasp.add(match.group(1))

        for function in nist_functions:
            function_text = str(function)
            covered_nist.add(function_text)
            if function_text not in REQUIRED_NIST_FUNCTIONS:
                failures.append(f"{control_id} invalid NIST function: {function_text}")

        if "docs/threat_model.md" not in evidence_files and control_id in {"GOV-01", "GOV-02"}:
            failures.append(f"{control_id} must include docs/threat_model.md as evidence")

        for rel_path in evidence_files:
            rel = Path(str(rel_path))
            path = ROOT / rel
            if rel.is_absolute() or ".." in rel.parts:
                failures.append(f"{control_id} evidence file must be repo-relative: {rel_path}")
            elif not path.exists():
                failures.append(f"{control_id} missing evidence file: {rel_path}")

        for command in evidence_commands:
            prefix = "python -B scripts/dev.py "
            if not str(command).startswith(prefix):
                failures.append(f"{control_id} invalid evidence command prefix: {command}")
                continue
            name = str(command)[len(prefix) :].split()[0]
            if name not in available_commands:
                failures.append(f"{control_id} evidence command not in scripts/dev.py: {name}")

    missing_owasp = REQUIRED_OWASP_CODES - covered_owasp
    if missing_owasp:
        failures.append(f"registry missing OWASP risk coverage: {sorted(missing_owasp)}")

    missing_nist = REQUIRED_NIST_FUNCTIONS - covered_nist
    if missing_nist:
        failures.append(f"registry missing NIST function coverage: {sorted(missing_nist)}")

    missing_threats = REQUIRED_THREATS - covered_threats
    if missing_threats:
        failures.append(f"registry missing threat coverage: {sorted(missing_threats)}")

    return failures


def check_public_safe_text() -> list[str]:
    failures: list[str] = []
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
    for marker in PRIVATE_MARKERS:
        if marker in text:
            failures.append(f"registry contains private marker: {marker}")
    return failures


def check_docs_reference_registry() -> list[str]:
    failures: list[str] = []
    references = {
        "docs/threat_model.md": [
            "docs/ai_governance_control_registry.json",
            "python -B scripts/dev.py governance-controls",
            "OWASP Top 10 for LLM Applications",
            "NIST AI RMF",
        ],
        "docs/portfolio_evidence_matrix.md": [
            "docs/ai_governance_control_registry.json",
            "python -B scripts/dev.py governance-controls",
        ],
        "docs/industrial_true_production_gap_plan_2026_06_07.md": [
            "Production-minded reference implementation, not production software.",
            "docs/ai_governance_control_registry.json",
            "OWASP LLM Top 10",
            "NIST AI RMF",
        ],
        "PROJECT_CONTENT_INDEX.md": [
            "docs/ai_governance_control_registry.json",
            "scripts/check_ai_governance_controls.py",
            "python -B scripts/dev.py governance-controls",
        ],
    }
    for rel_path, phrases in references.items():
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"missing governance reference file: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path} missing governance reference: {phrase}")

    if not INDUSTRIAL_PLAN.exists():
        failures.append("missing docs/industrial_true_production_gap_plan_2026_06_07.md")
    if not THREAT_MODEL.exists():
        failures.append("missing docs/threat_model.md")
    return failures


def main() -> int:
    registry, failures = load_registry()
    if registry:
        failures.extend(check_registry_shape(registry))
        failures.extend(check_controls(registry))
        failures.extend(check_public_safe_text())
    failures.extend(check_docs_reference_registry())

    if failures:
        print("AI governance control registry check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("AI governance control registry check passed.")
    print("Mapped 10 controls across OWASP LLM Top 10, NIST AI RMF, and T01-T13 threat coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
