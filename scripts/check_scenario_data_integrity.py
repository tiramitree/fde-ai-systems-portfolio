from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVAL_GUIDE = ROOT / "docs" / "eval_authoring_guide.md"
LOCAL_ARTIFACT_GLOSSARY = ROOT / "docs" / "local_artifact_glossary.md"
EVAL_TROUBLESHOOTING = ROOT / "docs" / "eval_gate_troubleshooting_examples.md"
SEED_EXAMPLES = ROOT / "docs" / "seed_data_extension_examples.md"
SEED_FIXTURE_DATA_FLOW = ROOT / "docs" / "seed_fixture_data_flow.md"

P1_ROOT = ROOT / "secure-enterprise-knowledge-copilot"
P2_ROOT = ROOT / "regulated-customer-operations-agent"
P3_ROOT = ROOT / "ai-reliability-incident-console"

P1_ROLES = {"employee", "manager", "admin"}
P2_ROLES = {"investigator", "supervisor"}
P3_ROLES = {"reliability_lead", "product_manager"}
P1_BEHAVIORS = {"answer", "abstain"}
P2_INTENTS = {"approve_action", "request_escalation", "request_notice_send", "investigate_listing", "general"}

FORBIDDEN_DATA_MARKERS = (
    "C:/",
    "C:\\",
    "One" + "Drive",
    "x" + "wechat",
    "wx" + "id_",
    "117" + "58",
    "Runze",
    "s" + "k-",
    "github_" + "pat_",
    "BEGIN " + "PRIVATE KEY",
)

INJECTION_MARKERS = (
    "ignore previous",
    "disregard prior",
    "follow the vendor note",
    "reveal",
    "override policy",
    "override approval",
    "bypass approval",
    "without approval",
    "do not log",
    "hide this",
    "exfiltrate",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def require_text(text: str, needle: str, failures: list[str], source: str) -> None:
    if needle not in text:
        failures.append(f"{source}: missing {needle!r}")


def ids(rows: list[dict[str, Any]], label: str, failures: list[str]) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            failures.append(f"{label}: row missing string id")
            continue
        if row_id in seen:
            failures.append(f"{label}: duplicate id {row_id}")
        seen.add(row_id)
    return seen


def check_text_safety(payload: Any, source: str, failures: list[str]) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    for marker in FORBIDDEN_DATA_MARKERS:
        if marker in text:
            failures.append(f"{source}: forbidden data marker {marker!r}")


def has_injection_marker(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in INJECTION_MARKERS)


def check_eval_ids(cases: list[dict[str, Any]], source: str, failures: list[str]) -> None:
    seen = ids(cases, source, failures)
    for case in cases:
        case_id = case.get("id", "")
        require(bool(re.fullmatch(r"eval-\d{3}-[a-z0-9-]+", case_id)), failures, f"{source}: invalid eval id {case_id}")
    require(len(seen) == len(cases), failures, f"{source}: eval ids must be unique")


def check_p1() -> list[str]:
    failures: list[str] = []
    seed = read_json(P1_ROOT / "data" / "seed_documents.json")
    eval_cases = read_json(P1_ROOT / "data" / "eval_cases.json")
    check_text_safety(seed, "P1 seed_documents.json", failures)
    check_text_safety(eval_cases, "P1 eval_cases.json", failures)

    users = seed.get("users", [])
    documents = seed.get("documents", [])
    require(isinstance(users, list) and users, failures, "P1: users must be a non-empty list")
    require(isinstance(documents, list) and documents, failures, "P1: documents must be a non-empty list")
    user_ids = ids(users, "P1 users", failures)
    doc_ids = ids(documents, "P1 documents", failures)
    roles = {user.get("role") for user in users}

    require(P1_ROLES.issubset(roles), failures, "P1: employee, manager, and admin demo roles must all exist")
    for user in users:
        require(user.get("role") in P1_ROLES, failures, f"P1 user {user.get('id')}: unknown role {user.get('role')}")
        require(user.get("tenant_id") == "acme", failures, f"P1 user {user.get('id')}: tenant_id must be acme")

    for doc in documents:
        doc_id = doc.get("id")
        allowed_roles = set(doc.get("allowed_roles", []))
        classification = doc.get("classification")
        require(classification in {"internal", "confidential"}, failures, f"P1 document {doc_id}: invalid classification")
        require(bool(allowed_roles), failures, f"P1 document {doc_id}: allowed_roles cannot be empty")
        require(allowed_roles <= P1_ROLES, failures, f"P1 document {doc_id}: allowed_roles contains unknown role")
        require(doc.get("source_url", "").startswith("internal://"), failures, f"P1 document {doc_id}: source_url must be internal://")
        require(str(doc.get("title", "")) in str(doc.get("body", "")), failures, f"P1 document {doc_id}: body should include title")
        if classification == "confidential":
            require("employee" not in allowed_roles, failures, f"P1 document {doc_id}: confidential docs must not allow employee")
            require({"manager", "admin"} <= allowed_roles, failures, f"P1 document {doc_id}: confidential docs must allow manager and admin")

    unsafe_docs = [doc for doc in documents if has_injection_marker(str(doc.get("body", "")))]
    require(bool(unsafe_docs), failures, "P1: seed data must include at least one unsafe retrieved-content document")
    require(
        any(doc.get("id") == "vendor-onboarding-note-unsafe" for doc in unsafe_docs),
        failures,
        "P1: vendor-onboarding-note-unsafe must remain the unsafe retrieved-content fixture",
    )

    require(isinstance(eval_cases, list) and eval_cases, failures, "P1: eval cases must be a non-empty list")
    check_eval_ids(eval_cases, "P1 eval_cases.json", failures)
    for case in eval_cases:
        case_id = case.get("id")
        user_id = case.get("user_id")
        expected = case.get("expected", {})
        require(user_id in user_ids, failures, f"P1 eval {case_id}: unknown user_id {user_id}")
        require(expected.get("behavior") in P1_BEHAVIORS, failures, f"P1 eval {case_id}: invalid behavior")
        for field in ("must_cite_doc_ids", "forbidden_doc_ids"):
            values = expected.get(field, [])
            require(isinstance(values, list), failures, f"P1 eval {case_id}: {field} must be a list")
            for doc_id in values:
                require(doc_id in doc_ids, failures, f"P1 eval {case_id}: {field} references missing doc {doc_id}")
        if expected.get("requires_security_event"):
            require(
                has_injection_marker(case.get("question", "")),
                failures,
                f"P1 eval {case_id}: security-event eval should include an injection/exfiltration marker",
            )
        if expected.get("behavior") == "answer":
            require(bool(expected.get("must_cite_doc_ids")), failures, f"P1 eval {case_id}: answer cases must require a citation")

    return failures


def check_p2() -> list[str]:
    failures: list[str] = []
    seed = read_json(P2_ROOT / "data" / "seed_state.json")
    eval_cases = read_json(P2_ROOT / "data" / "eval_cases.json")
    check_text_safety(seed, "P2 seed_state.json", failures)
    check_text_safety(eval_cases, "P2 eval_cases.json", failures)

    users = seed.get("users", [])
    policies = seed.get("policies", [])
    products = seed.get("products", [])
    sellers = seed.get("sellers", [])
    listings = seed.get("listings", [])
    cases = seed.get("cases", [])

    user_ids = ids(users, "P2 users", failures)
    policy_ids = ids(policies, "P2 policies", failures)
    product_ids = ids(products, "P2 products", failures)
    seller_ids = ids(sellers, "P2 sellers", failures)
    listing_ids = ids(listings, "P2 listings", failures)
    case_ids = ids(cases, "P2 cases", failures)
    roles = {user.get("role") for user in users}

    require(P2_ROLES.issubset(roles), failures, "P2: investigator and supervisor roles must both exist")
    for user in users:
        require(user.get("role") in P2_ROLES, failures, f"P2 user {user.get('id')}: unknown role {user.get('role')}")

    for policy in policies:
        body = str(policy.get("body", ""))
        require("approval" in body.lower(), failures, f"P2 policy {policy.get('id')}: policy should describe approval")
        require(policy.get("version", "").startswith("2026."), failures, f"P2 policy {policy.get('id')}: version should be 2026.x")

    active_recalled_products: set[str] = set()
    for product in products:
        status = product.get("recall_status")
        product_id = product.get("id")
        require(status in {"active", "none"}, failures, f"P2 product {product_id}: invalid recall_status")
        if status == "active":
            active_recalled_products.add(product_id)
            require(bool(product.get("recall_id")), failures, f"P2 product {product_id}: active recalls need recall_id")
            require(bool(product.get("hazard")), failures, f"P2 product {product_id}: active recalls need hazard")

    active_recalled_listings: set[str] = set()
    for listing in listings:
        listing_id = listing.get("id")
        seller_id = listing.get("seller_id")
        product_id = listing.get("product_id")
        require(seller_id in seller_ids, failures, f"P2 listing {listing_id}: missing seller {seller_id}")
        require(product_id in product_ids, failures, f"P2 listing {listing_id}: missing product {product_id}")
        require(listing.get("status") in {"active", "removed"}, failures, f"P2 listing {listing_id}: invalid status")
        require(str(listing.get("url", "")).startswith("marketplace://"), failures, f"P2 listing {listing_id}: url must be marketplace://")
        if listing.get("status") == "active" and product_id in active_recalled_products:
            active_recalled_listings.add(listing_id)
    require(bool(active_recalled_listings), failures, "P2: must include an active listing for an actively recalled product")

    for case in cases:
        case_id = case.get("id")
        seller_id = case.get("seller_id")
        product_id = case.get("product_id")
        require(seller_id in seller_ids, failures, f"P2 case {case_id}: missing seller {seller_id}")
        require(product_id in product_ids, failures, f"P2 case {case_id}: missing product {product_id}")
        require(case.get("status") in {"open", "monitoring"}, failures, f"P2 case {case_id}: invalid status")

    require(isinstance(eval_cases, list) and eval_cases, failures, "P2: eval cases must be a non-empty list")
    check_eval_ids(eval_cases, "P2 eval_cases.json", failures)
    for case in eval_cases:
        case_id = case.get("id")
        user_id = case.get("user_id")
        expected = case.get("expected", {})
        require(user_id in user_ids, failures, f"P2 eval {case_id}: unknown user_id {user_id}")
        if "case_id" in case:
            require(case.get("case_id") in case_ids, failures, f"P2 eval {case_id}: missing case {case.get('case_id')}")
        require(expected.get("intent") in P2_INTENTS, failures, f"P2 eval {case_id}: invalid intent")
        require(expected.get("forbids_direct_side_effect") is True, failures, f"P2 eval {case_id}: must forbid direct side effects")
        for policy_id in expected.get("must_cite_policy_ids", []):
            require(policy_id in policy_ids, failures, f"P2 eval {case_id}: missing policy {policy_id}")
        if expected.get("must_refuse"):
            require(has_injection_marker(case.get("message", "")) or expected.get("intent") == "approve_action", failures, f"P2 eval {case_id}: refusal case should include bypass marker or approval attempt")
        if expected.get("requires_approval"):
            require(expected.get("requires_blocked_action") is True, failures, f"P2 eval {case_id}: approval cases must require blocked action")

    return failures


def check_p3() -> list[str]:
    failures: list[str] = []
    seed = read_json(P3_ROOT / "data" / "seed_state.json")
    eval_cases = read_json(P3_ROOT / "data" / "eval_cases.json")
    check_text_safety(seed, "P3 seed_state.json", failures)
    check_text_safety(eval_cases, "P3 eval_cases.json", failures)

    users = seed.get("users", [])
    releases = seed.get("releases", [])
    incidents = seed.get("incidents", [])
    eval_runs = seed.get("eval_runs", [])
    runbooks = seed.get("runbooks", [])

    user_ids = ids(users, "P3 users", failures)
    release_ids = ids(releases, "P3 releases", failures)
    incident_ids = ids(incidents, "P3 incidents", failures)
    runbook_ids = ids(runbooks, "P3 runbooks", failures)
    roles = {user.get("role") for user in users}
    require(P3_ROLES.issubset(roles), failures, "P3: reliability lead and product manager roles must both exist")

    eval_case_ids_by_release: dict[str, set[str]] = {}
    for run in eval_runs:
        release_id = run.get("release_id")
        require(release_id in release_ids, failures, f"P3 eval run {run.get('id')}: missing release {release_id}")
        cases = run.get("cases", [])
        case_ids = ids(cases, f"P3 eval run {run.get('id')} cases", failures)
        eval_case_ids_by_release.setdefault(str(release_id), set()).update(case_ids)
        metrics = run.get("metrics", {})
        require(metrics.get("total_cases") == len(cases), failures, f"P3 eval run {run.get('id')}: total_cases mismatch")
        require(metrics.get("passed_cases", 0) <= metrics.get("total_cases", 0), failures, f"P3 eval run {run.get('id')}: passed_cases exceeds total")

    require(isinstance(incidents, list) and incidents, failures, "P3: incidents must be a non-empty list")
    for incident in incidents:
        incident_id = incident.get("id")
        release_id = incident.get("release_id")
        require(release_id in release_ids, failures, f"P3 incident {incident_id}: missing release {release_id}")
        require(incident.get("severity") in {"low", "medium", "high", "critical"}, failures, f"P3 incident {incident_id}: invalid severity")
        require(incident.get("status") in {"open", "monitoring", "resolved"}, failures, f"P3 incident {incident_id}: invalid status")
        for runbook_id in incident.get("runbook_ids", []):
            require(runbook_id in runbook_ids, failures, f"P3 incident {incident_id}: missing runbook {runbook_id}")
        known_cases = eval_case_ids_by_release.get(str(release_id), set())
        for eval_case_id in incident.get("linked_eval_case_ids", []):
            require(eval_case_id in known_cases, failures, f"P3 incident {incident_id}: missing linked eval {eval_case_id}")

    require(isinstance(eval_cases, list) and eval_cases, failures, "P3: eval cases must be a non-empty list")
    check_eval_ids(eval_cases, "P3 eval_cases.json", failures)
    for case in eval_cases:
        case_id = case.get("id")
        user_id = case.get("user_id")
        release_id = case.get("release_id")
        incident_id = case.get("incident_id")
        expected = case.get("expected", {})
        require(user_id in user_ids, failures, f"P3 eval {case_id}: unknown user_id {user_id}")
        require(release_id in release_ids, failures, f"P3 eval {case_id}: missing release {release_id}")
        require(incident_id in incident_ids, failures, f"P3 eval {case_id}: missing incident {incident_id}")
        require(expected.get("minimum_severity") in {"low", "medium", "high", "critical"}, failures, f"P3 eval {case_id}: invalid minimum_severity")
        for eval_case_id in expected.get("must_link_eval_case_ids", []):
            require(eval_case_id in eval_case_ids_by_release.get(str(release_id), set()), failures, f"P3 eval {case_id}: missing linked eval {eval_case_id}")
        if expected.get("release_blocked") is True:
            require(bool(expected.get("must_recommend_phrases")), failures, f"P3 eval {case_id}: blocked release cases need remediation phrases")

    return failures


def check_eval_authoring_guide() -> list[str]:
    failures: list[str] = []
    if not EVAL_GUIDE.exists():
        return ["missing docs/eval_authoring_guide.md"]

    text = EVAL_GUIDE.read_text(encoding="utf-8")
    required_phrases = [
        "Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, or generated runtime state.",
        "docs/local_artifact_glossary.md",
        "docs/eval_gate_troubleshooting_examples.md",
        "secure-enterprise-knowledge-copilot/data/seed_documents.json",
        "secure-enterprise-knowledge-copilot/data/eval_cases.json",
        "expected.behavior",
        "expected.must_cite_doc_ids",
        "expected.forbidden_doc_ids",
        "expected.requires_security_event",
        "regulated-customer-operations-agent/data/seed_state.json",
        "regulated-customer-operations-agent/data/eval_cases.json",
        "expected.intent",
        "expected.requires_approval",
        "expected.forbids_direct_side_effect",
        "expected.requires_blocked_action",
        "expected.must_refuse",
        "ai-reliability-incident-console/data/seed_state.json",
        "ai-reliability-incident-console/data/eval_cases.json",
        "expected.release_blocked",
        "expected.minimum_severity",
        "expected.must_link_eval_case_ids",
        "expected.must_recommend_phrases",
        "python -B scripts/dev.py scenario-data",
        "python -B scripts/dev.py evals",
        "python -B scripts/dev.py claims",
        "python -B scripts/dev.py quality",
    ]
    for phrase in required_phrases:
        require_text(text, phrase, failures, "docs/eval_authoring_guide.md")

    cross_references = {
        ROOT / "README.md": "docs/eval_authoring_guide.md",
        ROOT / "PROJECT_CONTENT_INDEX.md": "docs/eval_authoring_guide.md",
    }
    for path, phrase in cross_references.items():
        require_text(path.read_text(encoding="utf-8"), phrase, failures, path.relative_to(ROOT).as_posix())

    return failures


def check_local_artifact_glossary() -> list[str]:
    failures: list[str] = []
    if not LOCAL_ARTIFACT_GLOSSARY.exists():
        return ["missing docs/local_artifact_glossary.md"]

    text = LOCAL_ARTIFACT_GLOSSARY.read_text(encoding="utf-8")
    required_phrases = [
        "Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime files, or real incident details.",
        "Seed fixture",
        "Runtime state",
        "Eval fixture",
        "Eval run",
        "Replay artifact",
        "Trace",
        "Audit",
        "Approval",
        "Release evidence",
        "Generated artifact",
        "secure-enterprise-knowledge-copilot/data/seed_documents.json",
        "regulated-customer-operations-agent/data/seed_state.json",
        "ai-reliability-incident-console/data/seed_state.json",
        "secure-enterprise-knowledge-copilot/data/eval_cases.json",
        "regulated-customer-operations-agent/data/eval_cases.json",
        "ai-reliability-incident-console/data/eval_cases.json",
        "*/data/runtime_state.json",
        "*/data/eval_runtime_state.json",
        "docs/demo_replay_artifact.md",
        "out/demo_replay_artifact.md",
        "out/demo_replay_artifact.json",
        "eval_summaries.csv",
        "otel_traces.json",
        "python -B scripts/dev.py scenario-data",
        "python -B scripts/dev.py evals",
        "python -B scripts/dev.py claims",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
    ]
    for phrase in required_phrases:
        require_text(text, phrase, failures, "docs/local_artifact_glossary.md")

    cross_references = {
        ROOT / "README.md": "docs/local_artifact_glossary.md",
        ROOT / "PROJECT_CONTENT_INDEX.md": "docs/local_artifact_glossary.md",
        ROOT / "docs" / "eval_authoring_guide.md": "docs/local_artifact_glossary.md",
    }
    for path, phrase in cross_references.items():
        require_text(path.read_text(encoding="utf-8"), phrase, failures, path.relative_to(ROOT).as_posix())

    return failures


def check_eval_troubleshooting_examples() -> list[str]:
    failures: list[str] = []
    if not EVAL_TROUBLESHOOTING.exists():
        return ["missing docs/eval_gate_troubleshooting_examples.md"]

    text = EVAL_TROUBLESHOOTING.read_text(encoding="utf-8")
    required_phrases = [
        "Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime state, or real incident details.",
        "do not fix a failing eval by weakening the expected safety behavior",
        "forbidden_citation_leaked:finance-retention-plan-2026",
        "secure-enterprise-knowledge-copilot/data/seed_documents.json",
        "secure-enterprise-knowledge-copilot/src/copilot/retrieval.py",
        "unsafe_leak_failures = 0",
        "direct_side_effect_tool_called",
        "regulated-customer-operations-agent/src/ops_agent/agent.py",
        "regulated-customer-operations-agent/src/ops_agent/tools.py",
        "unsafe_direct_side_effect_failures = 0",
        "wrong_release_block_decision",
        "ai-reliability-incident-console/src/reliability_console/triage.py",
        "ai-reliability-incident-console/src/reliability_console/evals.py",
        "unsafe_release_approval_failures = 0",
        "python -B scripts/dev.py scenario-data",
        "python -B scripts/dev.py evals",
        "python -B scripts/dev.py claims",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
    ]
    for phrase in required_phrases:
        require_text(text, phrase, failures, "docs/eval_gate_troubleshooting_examples.md")

    cross_references = {
        ROOT / "README.md": "docs/eval_gate_troubleshooting_examples.md",
        ROOT / "PROJECT_CONTENT_INDEX.md": "docs/eval_gate_troubleshooting_examples.md",
        ROOT / "docs" / "eval_authoring_guide.md": "docs/eval_gate_troubleshooting_examples.md",
    }
    for path, phrase in cross_references.items():
        require_text(path.read_text(encoding="utf-8"), phrase, failures, path.relative_to(ROOT).as_posix())

    return failures


def check_seed_extension_examples() -> list[str]:
    failures: list[str] = []
    if not SEED_EXAMPLES.exists():
        return ["missing docs/seed_data_extension_examples.md"]

    text = SEED_EXAMPLES.read_text(encoding="utf-8")
    required_phrases = [
        "Do not edit `runtime_state.json`, generated demo reports, trace exports, replay artifacts, private files, external accounts, paid-service configuration, secrets, or real customer data.",
        "secure-enterprise-knowledge-copilot/data/seed_documents.json",
        "secure-enterprise-knowledge-copilot/data/eval_cases.json",
        "ai-change-review-standard-2026",
        "internal://ai/change-review-standard-2026",
        "expected.must_cite_doc_ids",
        "regulated-customer-operations-agent/data/seed_state.json",
        "regulated-customer-operations-agent/data/eval_cases.json",
        "prod-vacuum-v12",
        "lst-1004",
        "case-1003",
        "marketplace://homehub/vacuum-v12-cordless",
        "expected.forbids_direct_side_effect",
        "ai-reliability-incident-console/data/seed_state.json",
        "ai-reliability-incident-console/data/eval_cases.json",
        "inc-2026-016",
        "rel-eval-006-latency-budget",
        "rb-latency-investigation",
        "expected.release_blocked",
        "python -B scripts/dev.py scenario-data",
        "python -B scripts/dev.py demo-presets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
    ]
    for phrase in required_phrases:
        require_text(text, phrase, failures, "docs/seed_data_extension_examples.md")

    cross_references = {
        ROOT / "README.md": "docs/seed_data_extension_examples.md",
        ROOT / "PROJECT_CONTENT_INDEX.md": "docs/seed_data_extension_examples.md",
    }
    for path, phrase in cross_references.items():
        require_text(path.read_text(encoding="utf-8"), phrase, failures, path.relative_to(ROOT).as_posix())

    return failures


def check_seed_fixture_data_flow() -> list[str]:
    failures: list[str] = []
    if not SEED_FIXTURE_DATA_FLOW.exists():
        return ["missing docs/seed_fixture_data_flow.md"]

    text = SEED_FIXTURE_DATA_FLOW.read_text(encoding="utf-8")
    required_phrases = [
        "Do not add secrets, private paths, real customer data, external accounts, paid-service requirements, generated runtime files, or real incident details.",
        "secure-enterprise-knowledge-copilot/data/seed_documents.json",
        "regulated-customer-operations-agent/data/seed_state.json",
        "ai-reliability-incident-console/data/seed_state.json",
        "secure-enterprise-knowledge-copilot/data/eval_cases.json",
        "regulated-customer-operations-agent/data/eval_cases.json",
        "ai-reliability-incident-console/data/eval_cases.json",
        "runtime_state.json",
        "runtime_state.tmp",
        "eval_runtime_state.json",
        "localStorage",
        "fde-scenario-draft:",
        "out/demo_replay_artifact.*",
        "docs/demo_report.md",
        "otel_traces.json",
        "eval_summaries.csv",
        "storage.seed()",
        "storage.init_state()",
        "retrieval.retrieve()",
        "answering.generate_answer()",
        "agent.process_message()",
        "tools.request_approval()",
        "supervisor /api/approval/approve",
        "triage.triage_incident()",
        "permission filtering happens before answer generation",
        "side-effect actions are represented as approval requests with idempotency keys",
        "high-risk incidents linked to failed evals block rollout",
        "/api/scenario",
        "docs/demo_state_presets.json",
        "docs/local_demo_reset_troubleshooting.md",
        "docs/local_artifact_glossary.md",
        "python -B scripts/dev.py scenario-data",
        "python -B scripts/dev.py demo-presets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
    ]
    for phrase in required_phrases:
        require_text(text, phrase, failures, "docs/seed_fixture_data_flow.md")

    cross_references = {
        ROOT / "README.md": "docs/seed_fixture_data_flow.md",
        ROOT / "PROJECT_CONTENT_INDEX.md": "docs/seed_fixture_data_flow.md",
    }
    for path, phrase in cross_references.items():
        require_text(path.read_text(encoding="utf-8"), phrase, failures, path.relative_to(ROOT).as_posix())

    return failures


def main() -> int:
    failures = []
    failures.extend(check_p1())
    failures.extend(check_p2())
    failures.extend(check_p3())
    failures.extend(check_eval_authoring_guide())
    failures.extend(check_local_artifact_glossary())
    failures.extend(check_eval_troubleshooting_examples())
    failures.extend(check_seed_extension_examples())
    failures.extend(check_seed_fixture_data_flow())

    if failures:
        print("Scenario data integrity check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Scenario data integrity check passed: seed data, roles, references, and eval expectations are internally consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
