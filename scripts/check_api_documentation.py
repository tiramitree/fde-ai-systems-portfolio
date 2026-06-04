from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "api_contracts.md"

PROJECTS = {
    "Secure Enterprise Knowledge Copilot": {
        "source": ROOT / "secure-enterprise-knowledge-copilot" / "src" / "copilot" / "api.py",
        "get": {
            "/api/health",
            "/api/users",
            "/api/documents",
            "/api/traces",
            "/api/audit",
            "/api/eval/latest",
            "/api/scenario",
        },
        "post": {
            "/api/query",
            "/api/eval/run",
        },
        "fields": {
            "trace_id",
            "user",
            "question",
            "answer",
            "citations",
            "confidence",
            "missing_evidence",
            "abstain_reason",
            "security_events",
            "model_provider",
            "openai_gateway_enabled",
            "retrieved",
            "permission_blocked_count",
            "latency_ms",
            "draft_mode",
            "write_policy",
            "record_count",
            "body is never returned",
        },
    },
    "Regulated Customer Operations Agent": {
        "source": ROOT / "regulated-customer-operations-agent" / "src" / "ops_agent" / "api.py",
        "get": {
            "/api/health",
            "/api/users",
            "/api/cases",
            "/api/approvals",
            "/api/traces",
            "/api/audit",
            "/api/eval/latest",
            "/api/scenario",
        },
        "post": {
            "/api/agent",
            "/api/approval/approve",
            "/api/eval/run",
        },
        "fields": {
            "trace_id",
            "intent",
            "response",
            "tool_calls",
            "approvals",
            "blocked_actions",
            "cited_policies",
            "outputs",
            "case",
            "model_router",
            "draft_mode",
            "write_policy",
            "record_count",
            "Supervisor-only approval execution",
            "non-supervisors receive `403`",
        },
    },
    "AI Reliability Incident Console": {
        "source": ROOT / "ai-reliability-incident-console" / "src" / "reliability_console" / "api.py",
        "get": {
            "/api/health",
            "/api/users",
            "/api/releases",
            "/api/incidents",
            "/api/eval-runs",
            "/api/runbooks",
            "/api/traces",
            "/api/audit",
            "/api/eval/latest",
            "/api/scenario",
        },
        "post": {
            "/api/triage",
            "/api/eval/run",
        },
        "fields": {
            "trace_id",
            "release",
            "incident",
            "decision",
            "failed_evals",
            "remediation_steps",
            "evidence",
            "release_blocked",
            "recommendation",
            "draft_mode",
            "write_policy",
            "record_count",
            "unsafe rollout incidents return `block_release`",
            "latency-only incidents can return `monitor`",
        },
    },
}

CROSS_REFERENCES = {
    "README.md": ["docs/api_contracts.md", "python -B scripts/dev.py api-docs"],
    "PROJECT_CONTENT_INDEX.md": ["docs/api_contracts.md", "scripts/check_api_documentation.py"],
    "docs/portfolio_evidence_matrix.md": ["python -B scripts/dev.py api-docs"],
}


def function_routes(source: Path, method_name: str) -> set[str]:
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    routes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != method_name:
            continue
        for nested in ast.walk(node):
            if not isinstance(nested, ast.Compare):
                continue
            if not isinstance(nested.left, ast.Name) or nested.left.id != "path":
                continue
            for comparator in nested.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    routes.add(comparator.value)
    return routes


def require_text(text: str, phrase: str, label: str) -> list[str]:
    return [] if phrase in text else [f"{label} missing: {phrase}"]


def check_project(name: str, config: dict, doc_text: str) -> list[str]:
    failures: list[str] = []
    source = config["source"]
    if not source.exists():
        return [f"missing API source for {name}: {source.relative_to(ROOT)}"]

    for method in ("get", "post"):
        actual = function_routes(source, method)
        expected = config[method]
        missing_source = sorted(expected - actual)
        extra_source = sorted(actual - expected)
        for route in missing_source:
            failures.append(f"{source.relative_to(ROOT)} missing {method.upper()} route: {route}")
        for route in extra_source:
            failures.append(f"{source.relative_to(ROOT)} has undocumented expected-set route: {method.upper()} {route}")
        for route in expected:
            marker = f"| {method.upper()} | `{route}"
            if marker not in doc_text:
                failures.append(f"docs/api_contracts.md missing route row: {method.upper()} {route}")

    failures.extend(require_text(doc_text, name, "docs/api_contracts.md"))
    for field in config["fields"]:
        failures.extend(require_text(doc_text, field, "docs/api_contracts.md"))
    return failures


def check_cross_references() -> list[str]:
    failures: list[str] = []
    for rel_path, phrases in CROSS_REFERENCES.items():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path} missing API docs reference: {phrase}")
    return failures


def main() -> int:
    failures: list[str] = []
    if not DOC.exists():
        failures.append("missing docs/api_contracts.md")
        doc_text = ""
    else:
        doc_text = DOC.read_text(encoding="utf-8")

    if doc_text:
        required_phrases = [
            "python -B scripts/dev.py contracts",
            "python -B scripts/dev.py api-docs",
            "Responses are JSON.",
            '{"error": "message"}',
            "permissions and side effects are enforced before the JSON response",
        ]
        for phrase in required_phrases:
            failures.extend(require_text(doc_text, phrase, "docs/api_contracts.md"))
        for name, config in PROJECTS.items():
            failures.extend(check_project(name, config, doc_text))

    failures.extend(check_cross_references())

    if failures:
        print("API documentation check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("API documentation check passed: source routes, public docs, and evidence references are aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
