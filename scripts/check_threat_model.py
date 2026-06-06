from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THREAT_MODEL = ROOT / "docs" / "threat_model.md"


THREATS = {
    "T01": {
        "phrases": ["Unauthorized document disclosure", "tenant and role", "before retrieval scoring"],
        "files": [
            "secure-enterprise-knowledge-copilot/src/copilot/retrieval.py",
            "secure-enterprise-knowledge-copilot/src/copilot/retrieval_scoring.py",
            "secure-enterprise-knowledge-copilot/src/copilot/answering.py",
            "secure-enterprise-knowledge-copilot/data/eval_cases.json",
            "scripts/check_observability_integrity.py",
        ],
        "commands": ["evals", "smoke", "observability"],
    },
    "T02": {
        "phrases": ["prompt injection", "rejected before retrieval", "removed from evidence"],
        "files": [
            "secure-enterprise-knowledge-copilot/src/copilot/security.py",
            "secure-enterprise-knowledge-copilot/src/copilot/answering.py",
            "secure-enterprise-knowledge-copilot/data/eval_cases.json",
        ],
        "commands": ["evals", "smoke", "observability"],
    },
    "T03": {
        "phrases": ["Unsupported or fabricated answers", "abstains", "citation requirements", "retrieval evals"],
        "files": [
            "secure-enterprise-knowledge-copilot/src/copilot/answering.py",
            "secure-enterprise-knowledge-copilot/src/copilot/retrieval_scoring.py",
            "secure-enterprise-knowledge-copilot/src/copilot/evals.py",
            "scripts/check_claim_consistency.py",
        ],
        "commands": ["evals", "claims"],
    },
    "T04": {
        "phrases": ["External side effect without approval", "blocks direct side-effect tools"],
        "files": [
            "regulated-customer-operations-agent/src/ops_agent/tools.py",
            "regulated-customer-operations-agent/src/ops_agent/agent.py",
            "regulated-customer-operations-agent/data/eval_cases.json",
        ],
        "commands": ["evals", "smoke", "observability"],
    },
    "T05": {
        "phrases": ["Approval bypass or non-supervisor approval", "supervisor-only"],
        "files": [
            "regulated-customer-operations-agent/src/ops_agent/api.py",
            "regulated-customer-operations-agent/src/ops_agent/tools.py",
            "scripts/check_api_contracts.py",
        ],
        "commands": ["evals", "contracts", "observability"],
    },
    "T06": {
        "phrases": ["Duplicate side-effect execution", "idempotency keys", "already-processed"],
        "files": [
            "regulated-customer-operations-agent/src/ops_agent/tools.py",
            "scripts/smoke_test_demo_flows.py",
            "scripts/check_observability_integrity.py",
        ],
        "commands": ["smoke", "observability"],
    },
    "T07": {
        "phrases": ["Secret, private path, or internal exception leakage", "generic JSON errors"],
        "files": [
            "scripts/public_safety_scan.py",
            "scripts/check_error_hygiene.py",
            ".gitignore",
            "SECURITY.md",
        ],
        "commands": ["safety", "error-hygiene"],
    },
    "T08": {
        "phrases": ["Public PR or CI workflow abuse", "read-only permissions", "CODEOWNERS"],
        "files": [
            ".github/workflows/ci.yml",
            ".github/CODEOWNERS",
            "scripts/check_workflow_security.py",
            "scripts/check_repository_governance.py",
            "scripts/review_open_prs.py",
        ],
        "commands": ["workflow-security", "governance", "pr-triage"],
    },
    "T09": {
        "phrases": ["Dependency or supply-chain drift", "digest-pinned", "Dependabot"],
        "files": [
            "scripts/check_dependency_surface.py",
            ".github/dependabot.yml",
            "docs/supply_chain_security.md",
        ],
        "commands": ["dependency-surface"],
    },
    "T10": {
        "phrases": ["Optional model gateway", "opt-in", "fall back locally"],
        "files": [
            "scripts/check_model_gateway_safety.py",
            "secure-enterprise-knowledge-copilot/src/copilot/model_gateway.py",
            "regulated-customer-operations-agent/src/ops_agent/model_gateway.py",
            ".env.example",
        ],
        "commands": ["model-gateway-safety"],
    },
    "T11": {
        "phrases": ["Trace, audit, approval, or release-decision evidence", "persisted trace IDs", "release decisions"],
        "files": [
            "scripts/check_observability_integrity.py",
            "scripts/export_traces_otel.py",
            "docs/observability_integrity.md",
            "docs/otel_trace_export.md",
        ],
        "commands": ["observability", "otel-traces"],
    },
    "T12": {
        "phrases": ["Browser/static route surprises", "content types", "traversal blocking"],
        "files": [
            "scripts/check_runtime_ui_contracts.py",
            "secure-enterprise-knowledge-copilot/app.py",
            "regulated-customer-operations-agent/app.py",
            "docs/runtime_ui_contracts.md",
        ],
        "commands": ["ui-contracts"],
    },
    "T13": {
        "phrases": ["Unauthorized or poisoned document ingestion", "admin-only ingestion", "parser metadata", "source_hash"],
        "files": [
            "secure-enterprise-knowledge-copilot/src/copilot/ingestion.py",
            "secure-enterprise-knowledge-copilot/src/copilot/github_connector.py",
            "secure-enterprise-knowledge-copilot/src/copilot/source_parsing.py",
            "scripts/check_api_contracts.py",
            "docs/api_contracts.md",
        ],
        "commands": ["contracts", "api-docs"],
    },
}


SUPPORTING_DOCS = [
    "SECURITY.md",
    "docs/adr_0002_model_is_not_security_boundary.md",
    "docs/model_gateway_safety.md",
    "docs/workflow_security.md",
    "docs/supply_chain_security.md",
    "docs/observability_integrity.md",
    "docs/runtime_ui_contracts.md",
    "secure-enterprise-knowledge-copilot/docs/threat_model.md",
    "regulated-customer-operations-agent/docs/threat_model.md",
]


SOURCE_MARKERS = {
    "secure-enterprise-knowledge-copilot/src/copilot/retrieval.py": ["tenant_id", "allowed_roles", "_allowed"],
    "secure-enterprise-knowledge-copilot/src/copilot/retrieval_scoring.py": ["local-hybrid-v1", "score_chunk", "semantic_family"],
    "secure-enterprise-knowledge-copilot/src/copilot/answering.py": ["abstain_reason", "insert_trace", "insert_audit"],
    "secure-enterprise-knowledge-copilot/src/copilot/security.py": ["INJECTION_PATTERNS", "detect_prompt_injection"],
    "secure-enterprise-knowledge-copilot/src/copilot/ingestion.py": ["Only admin users", "source_hash", "document_ingested", "source_sync_completed", "acl_role_drift"],
    "secure-enterprise-knowledge-copilot/src/copilot/github_connector.py": ["Only admin users", "github_connector_synced", "GITHUB_CONNECTOR_TOKEN", "source_payload_sha256"],
    "secure-enterprise-knowledge-copilot/src/copilot/ingestion_jobs.py": ["idempotency_key", "dead_lettered", "ingestion_job_completed", "ingestion_job_dead_lettered"],
    "secure-enterprise-knowledge-copilot/src/copilot/source_parsing.py": ["parse_source_content", "ParsedSource", "parser_name"],
    "regulated-customer-operations-agent/src/ops_agent/tools.py": [
        "direct_side_effect_blocked",
        "request_approval",
        "approve_action",
        "idempotency_key",
    ],
    ".github/workflows/ci.yml": ["permissions:", "contents: read", "persist-credentials: false"],
    "SECURITY.md": ["Permission checks happen before model generation", "Side-effect actions require"],
}


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def command_names() -> set[str]:
    text = read("scripts/dev.py")
    return set(re.findall(r'^\s+"([^"]+)":\s+\["scripts/', text, flags=re.MULTILINE))


def check_threat_model_doc() -> list[str]:
    failures: list[str] = []
    if not THREAT_MODEL.exists():
        return ["missing docs/threat_model.md"]

    text = THREAT_MODEL.read_text(encoding="utf-8")
    required_global_phrases = [
        "The model is not the security boundary",
        "## Assets",
        "## Threat Matrix",
        "## Trust Boundaries",
        "## Production Controls To Add",
        "## Technical Review Framing",
    ]
    for phrase in required_global_phrases:
        if phrase not in text:
            failures.append(f"docs/threat_model.md missing phrase: {phrase}")

    for threat_id, config in THREATS.items():
        if threat_id not in text:
            failures.append(f"docs/threat_model.md missing threat id: {threat_id}")
        for phrase in config["phrases"]:
            if phrase not in text:
                failures.append(f"docs/threat_model.md missing {threat_id} phrase: {phrase}")
        for command in config["commands"]:
            expected = f"python -B scripts/dev.py {command}"
            if expected not in text:
                failures.append(f"docs/threat_model.md missing {threat_id} evidence command: {expected}")
    return failures


def check_supporting_files() -> list[str]:
    failures: list[str] = []
    rel_paths = set(SUPPORTING_DOCS)
    for config in THREATS.values():
        rel_paths.update(config["files"])

    for rel_path in sorted(rel_paths):
        if not (ROOT / rel_path).exists():
            failures.append(f"missing threat-model evidence file: {rel_path}")
    return failures


def check_dev_commands() -> list[str]:
    failures: list[str] = []
    available = command_names()
    required = {command for config in THREATS.values() for command in config["commands"]}
    required.add("threat-model")
    for command in sorted(required):
        if command not in available:
            failures.append(f"scripts/dev.py missing threat-model command: {command}")
    return failures


def check_source_markers() -> list[str]:
    failures: list[str] = []
    for rel_path, markers in SOURCE_MARKERS.items():
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"missing marker source: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel_path} missing marker: {marker}")
    return failures


def check_public_docs_reference_root_model() -> list[str]:
    failures: list[str] = []
    references = {
        "README.md": ["docs/threat_model.md", "Threat Model"],
        "PROJECT_CONTENT_INDEX.md": ["docs/threat_model.md"],
        "SECURITY.md": ["docs/threat_model.md"],
        "docs/portfolio_evidence_matrix.md": ["docs/threat_model.md", "python -B scripts/dev.py threat-model"],
    }
    for rel_path, phrases in references.items():
        text = read(rel_path)
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path} missing threat-model reference: {phrase}")
    return failures


def main() -> int:
    failures: list[str] = []
    failures.extend(check_threat_model_doc())
    failures.extend(check_supporting_files())
    failures.extend(check_dev_commands())
    failures.extend(check_source_markers())
    failures.extend(check_public_docs_reference_root_model())

    if failures:
        print("Threat model check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Threat model check passed: {len(THREATS)} threats mapped to controls, files, and evidence commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
