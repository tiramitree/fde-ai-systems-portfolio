from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_1_PORT = 8866
DEFAULT_PROJECT_2_PORT = 8871
DEFAULT_PROJECT_3_PORT = 8878


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def request_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def reserve_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def services(project_1_port: int, project_2_port: int, project_3_port: int) -> list[dict]:
    return [
        {
            "name": "secure-enterprise-knowledge-copilot",
            "path": ROOT / "secure-enterprise-knowledge-copilot",
            "port": project_1_port,
            "health": f"http://127.0.0.1:{project_1_port}/api/health",
        },
        {
            "name": "regulated-customer-operations-agent",
            "path": ROOT / "regulated-customer-operations-agent",
            "port": project_2_port,
            "health": f"http://127.0.0.1:{project_2_port}/api/health",
        },
        {
            "name": "ai-reliability-incident-console",
            "path": ROOT / "ai-reliability-incident-console",
            "port": project_3_port,
            "health": f"http://127.0.0.1:{project_3_port}/api/health",
        },
    ]


def healthy(url: str) -> bool:
    try:
        status, payload = get_json(url)
        return status == 200 and payload.get("status") == "ok"
    except Exception:
        return False


def wait_for_health(url: str, seconds: int = 15) -> bool:
    for _ in range(seconds):
        if healthy(url):
            return True
        time.sleep(1)
    return False


def start_service(service: dict) -> subprocess.Popen:
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


def get_json(url: str) -> tuple[int, dict]:
    return request_json("GET", url)


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    return request_json("POST", url, payload)


def has_keys(payload: dict, keys: set[str]) -> bool:
    return keys.issubset(payload.keys())


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def valid_source_span(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required_ints = ("start_char", "end_char", "start_line", "end_line")
    if value.get("text_unit") != "normalized_text":
        return False
    if not all(isinstance(value.get(key), int) for key in required_ints):
        return False
    return (
        int(value["start_char"]) <= int(value["end_char"])
        and int(value["start_line"]) <= int(value["end_line"])
    )


def check(condition: bool, name: str, detail: str) -> Check:
    return Check(name=name, passed=condition, detail=detail)


def expect_types(payload: dict, expected: dict[str, type | tuple[type, ...]]) -> tuple[bool, str]:
    failures = []
    for key, expected_type in expected.items():
        if key not in payload:
            failures.append(f"missing {key}")
            continue
        if not isinstance(payload[key], expected_type):
            failures.append(f"{key}={type_name(payload[key])}")
    return not failures, ", ".join(failures) or "ok"


def scenario_contract(base_url: str, label: str, expected_app: str) -> list[Check]:
    checks: list[Check] = []
    status, payload = get_json(f"{base_url}/api/scenario")
    scenario = payload.get("scenario")
    checks.append(
        check(
            status == 200 and isinstance(scenario, dict),
            f"{label} scenario endpoint contract",
            f"status={status}; keys={sorted(scenario.keys()) if isinstance(scenario, dict) else []}",
        )
    )
    if isinstance(scenario, dict):
        ok, detail = expect_types(
            scenario,
            {
                "app": str,
                "draft_mode": str,
                "write_policy": str,
                "files": list,
            },
        )
        checks.append(
            check(
                ok
                and scenario.get("app") == expected_app
                and scenario.get("draft_mode") == "browser_local_storage"
                and scenario.get("write_policy") == "read_only_seed_snapshot",
                f"{label} scenario metadata contract",
                detail,
            )
        )
        files = scenario.get("files", [])
        checks.append(check(isinstance(files, list) and len(files) == 2, f"{label} scenario file list contract", f"files={len(files) if isinstance(files, list) else 0}"))
        if files:
            ok, detail = expect_types(files[0], {"path": str, "kind": str, "record_count": int, "content": (dict, list)})
            checks.append(check(ok and files[0]["path"].startswith("data/"), f"{label} scenario file shape contract", detail))
    return checks


def project_1_contracts(base_url: str) -> list[Check]:
    checks: list[Check] = []

    status, health = get_json(f"{base_url}/api/health")
    checks.append(check(status == 200 and health == {"status": "ok", "app": "secure-enterprise-knowledge-copilot"}, "P1 health contract", json.dumps(health)))

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P1 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str, "tenant_id": str})
        checks.append(check(ok, "P1 user shape contract", detail))

    status, documents = get_json(f"{base_url}/api/documents?user_id=alice")
    checks.append(check(status == 200 and isinstance(documents.get("documents"), list), "P1 visible documents contract", f"documents={len(documents.get('documents', []))}"))
    if documents.get("documents"):
        ok, detail = expect_types(
            documents["documents"][0],
            {"id": str, "tenant_id": str, "title": str, "classification": str, "allowed_roles": list},
        )
        checks.append(check(ok and "body" not in documents["documents"][0], "P1 document shape hides body", detail))

    forbidden_payload = {
        "user_id": "alice",
        "document": {
            "title": "Employee Travel Expense Policy 2026",
            "body": "Employees must submit travel expense receipts within five business days after each approved trip.",
            "classification": "internal",
            "allowed_roles": ["employee", "manager", "admin"],
            "source_url": "ingested://acme/travel-expense-policy-2026",
        },
    }
    status, forbidden = post_json(f"{base_url}/api/documents/ingest", forbidden_payload)
    checks.append(check(status == 403 and "Only admin users" in forbidden.get("error", ""), "P1 ingestion rejects non-admin users", json.dumps(forbidden)))

    ingest_payload = {
        "user_id": "avery",
        "replace": True,
        "document": {
            "title": "Employee Travel Expense Policy 2026",
            "body": (
                "Employee Travel Expense Policy 2026\n\n"
                "Employees must submit travel expense receipts within five business days after each approved trip. "
                "Expense reports must include the trip purpose, manager approval, and original receipt evidence."
            ),
            "classification": "internal",
            "allowed_roles": ["employee", "manager", "admin"],
            "source_url": "ingested://acme/travel-expense-policy-2026",
            "source_mime": "text/markdown",
            "version": "2026.06",
            "updated_at": "2026-06-06",
        },
    }
    status, ingestion = post_json(f"{base_url}/api/documents/ingest", ingest_payload)
    ingested_doc = ingestion.get("document", {})
    parser = ingestion.get("ingestion", {}).get("parser", {})
    ingestion_metadata = ingestion.get("ingestion", {})
    checks.append(
        check(
            status == 200
            and isinstance(ingested_doc, dict)
            and "body" not in ingested_doc
            and ingestion.get("chunk_count", 0) >= 1
            and len(ingestion_metadata.get("source_hash", "")) == 64
            and ingestion_metadata.get("chunk_source_span_unit") == "normalized_text"
            and ingestion_metadata.get("chunk_source_span_count") == ingestion.get("chunk_count"),
            "P1 admin ingestion contract",
            f"status={status}; doc={ingested_doc.get('id')}; chunks={ingestion.get('chunk_count')}; span_unit={ingestion_metadata.get('chunk_source_span_unit')}",
        )
    )
    checks.append(
        check(
            isinstance(parser, dict)
            and parser.get("name") == "markdown-v1"
            and isinstance(parser.get("normalized_characters"), int)
            and parser.get("normalized_characters", 0) >= 20
            and isinstance(parser.get("metadata"), dict)
            and isinstance(parser.get("warnings"), list),
            "P1 ingestion parser metadata contract",
            f"parser={parser.get('name')}; chars={parser.get('normalized_characters')}",
        )
    )
    embedding = ingestion.get("ingestion", {}).get("embedding", {})
    checks.append(
        check(
            isinstance(embedding, dict)
            and embedding.get("model") == "local-hashing-v1"
            and embedding.get("dimensions") == 1536
            and embedding.get("chunk_embedding_count") == ingestion.get("chunk_count"),
            "P1 ingestion embedding metadata contract",
            f"model={embedding.get('model')}; dimensions={embedding.get('dimensions')}; chunks={embedding.get('chunk_embedding_count')}",
        )
    )

    csv_ingest_payload = {
        "user_id": "avery",
        "replace": True,
        "document": {
            "title": "Operations Vendor Contacts 2026",
            "body": (
                "vendor,owner,status\n"
                "Northwind Logistics,Avery Stone,approved\n"
                "Contoso Facilities,Morgan Lee,review required"
            ),
            "classification": "internal",
            "allowed_roles": ["employee", "manager", "admin"],
            "source_url": "ingested://acme/operations-vendor-contacts-2026",
            "source_mime": "text/csv",
            "version": "2026.06",
            "updated_at": "2026-06-06",
        },
    }
    status, csv_ingestion = post_json(f"{base_url}/api/documents/ingest", csv_ingest_payload)
    csv_parser = csv_ingestion.get("ingestion", {}).get("parser", {})
    checks.append(
        check(
            status == 200
            and csv_parser.get("name") == "csv-v1"
            and csv_parser.get("metadata", {}).get("row_count") == 2
            and csv_parser.get("metadata", {}).get("column_count") == 3
            and csv_parser.get("metadata", {}).get("has_header") is True,
            "P1 CSV ingestion parser contract",
            f"status={status}; parser={csv_parser.get('name')}; metadata={csv_parser.get('metadata')}",
        )
    )

    source_sync_payload = {
        "user_id": "avery",
        "replace": True,
        "connector": {
            "name": "local-drive-demo",
            "cursor": "2026-06-06T00:00:00Z",
            "acl_source": "fixture-acl-v1",
            "acl_snapshot": {
                "version": "fixture-acl-v1",
                "documents": {
                    "drive-doc-source-sync-playbook-2026": {
                        "allowed_roles": ["employee", "manager", "admin"],
                        "permission_id": "drive-acl-source-sync-playbook-v1",
                        "principal_count": 3,
                    },
                    "drive-json-finance-retention-controls-2026": {
                        "allowed_roles": ["manager", "admin"],
                        "permission_id": "drive-acl-finance-controls-v1",
                        "principal_count": 2,
                    },
                    "drive-doc-acl-drift-playbook-2026": {
                        "allowed_roles": ["manager", "admin"],
                        "permission_id": "drive-acl-drift-playbook-v1",
                        "principal_count": 2,
                    },
                },
            },
        },
        "documents": [
            {
                "id": "source-sync-playbook-2026",
                "external_id": "drive-doc-source-sync-playbook-2026",
                "title": "Source Sync Playbook 2026",
                "body": (
                    "Source Sync Playbook 2026\n\n"
                    "After each connector sync, administrators must review parser warnings, ACL source mappings, "
                    "and trace-to-eval candidates before promoting new knowledge into the trusted answer path."
                ),
                "classification": "internal",
                "allowed_roles": ["employee", "manager", "admin"],
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
            {
                "id": "finance-retention-control-notes-2026",
                "external_id": "drive-json-finance-retention-controls-2026",
                "title": "Finance Retention Control Notes 2026",
                "body": json.dumps(
                    {
                        "policy": "Finance Retention Control Notes 2026",
                        "owner": "Finance Operations",
                        "summary": (
                            "Confidential retention controls require manager review, audit linkage, "
                            "and approval evidence before wider access."
                        ),
                    }
                ),
                "classification": "confidential",
                "allowed_roles": ["manager", "admin"],
                "source_mime": "application/json",
                "updated_at": "2026-06-06",
            },
            {
                "id": "acl-drift-playbook-2026",
                "external_id": "drive-doc-acl-drift-playbook-2026",
                "title": "ACL Drift Playbook 2026",
                "body": (
                    "ACL Drift Playbook 2026\n\n"
                    "Delta rehearsal compares source ACL snapshots before updating searchable access. "
                    "Administrators should confirm added roles, removed roles, and affected document IDs."
                ),
                "classification": "internal",
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
        ],
    }
    forbidden_sync_payload = {**source_sync_payload, "user_id": "alice"}
    status, forbidden_sync = post_json(f"{base_url}/api/sources/sync", forbidden_sync_payload)
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_sync.get("error", ""),
            "P1 source sync rejects non-admin users",
            json.dumps(forbidden_sync),
        )
    )

    status, source_sync = post_json(f"{base_url}/api/sources/sync", source_sync_payload)
    sync_metadata = source_sync.get("sync", {})
    synced_documents = source_sync.get("documents", [])
    checks.append(
        check(
            status == 200
            and sync_metadata.get("connector") == "local-drive-demo"
            and sync_metadata.get("cursor") == "2026-06-06T00:00:00Z"
            and sync_metadata.get("acl_source") == "fixture-acl-v1"
            and sync_metadata.get("acl_snapshot_version") == "fixture-acl-v1"
            and sync_metadata.get("document_count") == 3
            and sync_metadata.get("chunk_count", 0) >= 3
            and len(synced_documents) == 3
            and all("body" not in doc for doc in synced_documents)
            and synced_documents[0].get("source_connector") == "local-drive-demo"
            and synced_documents[0].get("external_id") == "drive-doc-source-sync-playbook-2026"
            and synced_documents[0].get("acl_source") == "fixture-acl-v1"
            and synced_documents[0].get("sync_cursor") == "2026-06-06T00:00:00Z",
            "P1 source sync batch contract",
            f"status={status}; connector={sync_metadata.get('connector')}; docs={sync_metadata.get('document_count')}; chunks={sync_metadata.get('chunk_count')}",
        )
    )
    drift_doc = next((doc for doc in synced_documents if doc.get("id") == "acl-drift-playbook-2026"), {})
    checks.append(
        check(
            status == 200
            and drift_doc.get("allowed_roles") == ["manager", "admin"]
            and drift_doc.get("allowed_roles_source") == "connector_acl_snapshot"
            and drift_doc.get("source_acl_version") == "fixture-acl-v1"
            and drift_doc.get("source_acl_permission_id") == "drive-acl-drift-playbook-v1"
            and drift_doc.get("source_acl_principal_count") == 2,
            "P1 source sync applies connector ACL snapshot",
            f"roles={drift_doc.get('allowed_roles')}; acl_version={drift_doc.get('source_acl_version')}",
        )
    )

    status, synced_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What must administrators review after each connector sync?",
        },
    )
    checks.append(
        check(
            status == 200
            and synced_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == "source-sync-playbook-2026"
                and valid_source_span(citation.get("source_span"))
                for citation in synced_answer.get("citations", [])
            ),
            "P1 synced source is retrievable with citation",
            f"trace={synced_answer.get('trace_id')}; citations={len(synced_answer.get('citations', []))}",
        )
    )

    status, alice_documents_before_drift = get_json(f"{base_url}/api/documents?user_id=alice")
    checks.append(
        check(
            status == 200
            and not any(
                doc.get("id") == "acl-drift-playbook-2026"
                for doc in alice_documents_before_drift.get("documents", [])
            ),
            "P1 source ACL snapshot hides unsynced role",
            f"documents={len(alice_documents_before_drift.get('documents', []))}",
        )
    )

    drift_sync_payload = {
        "user_id": "avery",
        "replace": True,
        "connector": {
            "name": "local-drive-demo",
            "cursor": "2026-06-06T01:00:00Z",
            "acl_source": "fixture-acl-v2",
            "acl_snapshot": {
                "version": "fixture-acl-v2",
                "documents": {
                    "drive-doc-acl-drift-playbook-2026": {
                        "allowed_roles": ["employee", "manager", "admin"],
                        "permission_id": "drive-acl-drift-playbook-v2",
                        "principal_count": 3,
                    },
                },
            },
        },
        "documents": [
            {
                "id": "acl-drift-playbook-2026",
                "external_id": "drive-doc-acl-drift-playbook-2026",
                "title": "ACL Drift Playbook 2026",
                "body": (
                    "ACL Drift Playbook 2026\n\n"
                    "Delta rehearsal compares source ACL snapshots before updating searchable access. "
                    "Administrators should confirm added roles, removed roles, and affected document IDs."
                ),
                "classification": "internal",
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
        ],
    }
    status, drift_sync = post_json(f"{base_url}/api/sources/sync", drift_sync_payload)
    drift_sync_metadata = drift_sync.get("sync", {})
    drift_document = drift_sync.get("documents", [{}])[0] if drift_sync.get("documents") else {}
    checks.append(
        check(
            status == 200
            and drift_sync_metadata.get("acl_snapshot_version") == "fixture-acl-v2"
            and drift_sync_metadata.get("acl_drift_count") == 1
            and drift_sync_metadata.get("acl_drift_doc_ids") == ["acl-drift-playbook-2026"]
            and drift_document.get("allowed_roles") == ["employee", "manager", "admin"]
            and drift_document.get("source_acl_permission_id") == "drive-acl-drift-playbook-v2",
            "P1 source ACL drift is detected on resync",
            f"drift={drift_sync_metadata.get('acl_drift_count')}; docs={drift_sync_metadata.get('acl_drift_doc_ids')}",
        )
    )

    status, drift_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What does delta rehearsal compare before updating searchable access?",
        },
    )
    checks.append(
        check(
            status == 200
            and drift_answer.get("abstain_reason") is None
            and any(citation.get("doc_id") == "acl-drift-playbook-2026" for citation in drift_answer.get("citations", [])),
            "P1 source ACL drift changes retrieval visibility",
            f"trace={drift_answer.get('trace_id')}; citations={len(drift_answer.get('citations', []))}",
        )
    )

    status, documents_after_ingest = get_json(f"{base_url}/api/documents?user_id=alice")
    checks.append(
        check(
            status == 200
            and any(doc.get("id") == ingested_doc.get("id") and "body" not in doc for doc in documents_after_ingest.get("documents", [])),
            "P1 ingested document appears without body",
            f"documents={len(documents_after_ingest.get('documents', []))}",
        )
    )

    status, ingested_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "When must employees submit travel expense receipts?",
        },
    )
    checks.append(
        check(
            status == 200
            and ingested_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == ingested_doc.get("id")
                and valid_source_span(citation.get("source_span"))
                for citation in ingested_answer.get("citations", [])
            ),
            "P1 ingested document is retrievable with citation",
            f"trace={ingested_answer.get('trace_id')}; doc={ingested_doc.get('id')}",
        )
    )

    status, audit = get_json(f"{base_url}/api/audit?limit=50")
    checks.append(
        check(
            status == 200
            and any(
                event.get("action") == "document_ingested"
                and event.get("details", {}).get("doc_id") == ingested_doc.get("id")
                for event in audit.get("events", [])
            ),
            "P1 ingestion writes audit event",
            f"events={len(audit.get('events', []))}",
        )
    )
    status, source_sync_audit = get_json(f"{base_url}/api/audit?limit=20")
    checks.append(
        check(
            status == 200
            and any(
                event.get("action") == "source_sync_completed"
                and event.get("details", {}).get("connector") == "local-drive-demo"
                and event.get("details", {}).get("document_count") == 1
                and event.get("details", {}).get("acl_drift_count") == 1
                for event in source_sync_audit.get("events", [])
            ),
            "P1 source sync writes ACL drift audit event",
            f"events={len(source_sync_audit.get('events', []))}",
        )
    )

    status, query = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "How many days per week can employees work remotely?",
        },
    )
    query_keys = {
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
        "retrieval_profile",
        "permission_blocked_count",
        "latency_ms",
    }
    ok, detail = expect_types(
        query,
        {
            "trace_id": str,
            "answer": str,
            "citations": list,
            "confidence": (int, float),
            "missing_evidence": list,
            "security_events": list,
            "retrieved": list,
            "retrieval_profile": dict,
            "permission_blocked_count": int,
            "latency_ms": (int, float),
        },
    )
    checks.append(check(status == 200 and has_keys(query, query_keys) and ok, "P1 query response contract", detail))
    retrieved = query.get("retrieved", [])
    citations = query.get("citations", [])
    profile = query.get("retrieval_profile", {})
    checks.append(
        check(
            isinstance(profile, dict)
            and profile.get("name") == "local-hybrid-v1"
            and "bm25_like" in profile.get("score_components", [])
            and "vector" in profile.get("score_components", [])
            and profile.get("embedding_model") == "local-hashing-v1"
            and profile.get("embedding_dimensions") == 1536
            and profile.get("permission_filter") == "tenant_role_before_scoring"
            and profile.get("candidate_strategy") == "local_full_scan"
            and isinstance(profile.get("candidate_source_count"), int)
            and profile.get("reranker") == "local-evidence-reranker-v1"
            and "query_overlap" in profile.get("rerank_features", [])
            and isinstance(retrieved, list)
            and bool(retrieved)
            and isinstance(retrieved[0].get("score_breakdown"), dict)
            and isinstance(retrieved[0].get("rerank_breakdown"), dict)
            and isinstance(retrieved[0].get("rerank_score"), (int, float))
            and "semantic" in retrieved[0]["score_breakdown"]
            and "vector" in retrieved[0]["score_breakdown"]
            and "base_score" in retrieved[0]["rerank_breakdown"]
            and "security_penalty" in retrieved[0]["rerank_breakdown"]
            and retrieved[0].get("embedding_model") == "local-hashing-v1"
            and retrieved[0].get("embedding_dimensions") == 1536
            and valid_source_span(retrieved[0].get("source_span"))
            and bool(citations)
            and valid_source_span(citations[0].get("source_span"))
            and "embedding" not in retrieved[0],
            "P1 retrieval profile and score-breakdown contract",
            f"profile={profile.get('name')}; top_doc={retrieved[0].get('doc_id') if retrieved else None}",
        )
    )

    status, blocked = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What is the finance retention plan?",
        },
    )
    checks.append(
        check(
            status == 200
            and isinstance(blocked.get("abstain_reason"), str)
            and blocked.get("permission_blocked_count", 0) >= 1
            and isinstance(blocked.get("citations"), list)
            and not blocked["citations"],
            "P1 unauthorized query abstention contract",
            f"reason={blocked.get('abstain_reason')}; blocked={blocked.get('permission_blocked_count')}",
        )
    )

    status, error = get_json(f"{base_url}/api/documents?user_id=missing-user")
    checks.append(check(status == 404 and isinstance(error.get("error"), str), "P1 API error contract", json.dumps(error)))

    status, traces = get_json(f"{base_url}/api/traces?limit=2")
    checks.append(check(status == 200 and isinstance(traces.get("traces"), list) and len(traces["traces"]) <= 2, "P1 traces list contract", f"traces={len(traces.get('traces', []))}"))
    if traces.get("traces"):
        ok, detail = expect_types(traces["traces"][0], {"id": str, "created_at": str, "user_id": str, "question": str, "payload": dict})
        checks.append(check(ok, "P1 trace shape contract", detail))

    checks.extend(scenario_contract(base_url, "P1", "secure-enterprise-knowledge-copilot"))
    return checks


def project_2_contracts(base_url: str) -> list[Check]:
    checks: list[Check] = []

    status, health = get_json(f"{base_url}/api/health")
    checks.append(check(status == 200 and health == {"status": "ok", "app": "regulated-customer-operations-agent"}, "P2 health contract", json.dumps(health)))

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P2 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str})
        checks.append(check(ok, "P2 user shape contract", detail))

    status, cases = get_json(f"{base_url}/api/cases")
    checks.append(check(status == 200 and isinstance(cases.get("cases"), list) and cases["cases"], "P2 cases list contract", f"cases={len(cases.get('cases', []))}"))
    if cases.get("cases"):
        ok, detail = expect_types(cases["cases"][0], {"id": str, "seller_id": str, "product_id": str, "status": str})
        checks.append(check(ok, "P2 case shape contract", detail))

    status, investigation = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Check whether Market Blue still has an active listing for the recalled RX-900 product.",
        },
    )
    agent_keys = {
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
    }
    ok, detail = expect_types(
        investigation,
        {
            "trace_id": str,
            "intent": str,
            "response": str,
            "tool_calls": list,
            "approvals": list,
            "blocked_actions": list,
            "cited_policies": list,
        },
    )
    checks.append(check(status == 200 and has_keys(investigation, agent_keys) and ok, "P2 agent response contract", detail))
    checks.append(check(investigation.get("model_router") == "local", "P2 default router source contract", f"model_router={investigation.get('model_router')}"))
    approval_id = investigation["approvals"][0]["id"] if investigation.get("approvals") else ""
    checks.append(check(bool(approval_id) and investigation.get("blocked_actions"), "P2 approval plus blocked-side-effect contract", f"approval={approval_id}"))

    status, forbidden = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": approval_id,
            "approver_id": "ivy",
        },
    )
    checks.append(check(status == 403 and isinstance(forbidden.get("error"), str), "P2 non-supervisor approval error contract", json.dumps(forbidden)))

    status, approval = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": approval_id,
            "approver_id": "sam",
        },
    )
    checks.append(
        check(
            status == 200
            and approval.get("result") in {"notice_sent", "already_processed"}
            and isinstance(approval.get("approval"), dict),
            "P2 supervisor approval contract",
            f"approval={approval_id}; result={approval.get('result')}",
        )
    )

    status, approvals = get_json(f"{base_url}/api/approvals")
    checks.append(check(status == 200 and isinstance(approvals.get("approvals"), list), "P2 approvals list contract", f"approvals={len(approvals.get('approvals', []))}"))

    status, traces = get_json(f"{base_url}/api/traces?limit=2")
    checks.append(check(status == 200 and isinstance(traces.get("traces"), list) and len(traces["traces"]) <= 2, "P2 traces list contract", f"traces={len(traces.get('traces', []))}"))
    if traces.get("traces"):
        ok, detail = expect_types(traces["traces"][0], {"id": str, "created_at": str, "user_id": str, "message": str, "intent": str, "result": dict})
        checks.append(check(ok, "P2 trace shape contract", detail))

    checks.extend(scenario_contract(base_url, "P2", "regulated-customer-operations-agent"))
    return checks


def project_3_contracts(base_url: str) -> list[Check]:
    checks: list[Check] = []

    status, health = get_json(f"{base_url}/api/health")
    checks.append(check(status == 200 and health == {"status": "ok", "app": "ai-reliability-incident-console"}, "P3 health contract", json.dumps(health)))

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P3 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str})
        checks.append(check(ok, "P3 user shape contract", detail))

    status, releases = get_json(f"{base_url}/api/releases")
    checks.append(check(status == 200 and isinstance(releases.get("releases"), list) and releases["releases"], "P3 releases list contract", f"releases={len(releases.get('releases', []))}"))
    if releases.get("releases"):
        ok, detail = expect_types(
            releases["releases"][0],
            {"id": str, "name": str, "created_at": str, "status": str, "owner": str, "change_summary": str, "traffic_percent": int},
        )
        checks.append(check(ok, "P3 release shape contract", detail))

    status, incidents = get_json(f"{base_url}/api/incidents")
    checks.append(check(status == 200 and isinstance(incidents.get("incidents"), list) and incidents["incidents"], "P3 incidents list contract", f"incidents={len(incidents.get('incidents', []))}"))
    if incidents.get("incidents"):
        ok, detail = expect_types(
            incidents["incidents"][0],
            {
                "id": str,
                "release_id": str,
                "opened_at": str,
                "status": str,
                "severity": str,
                "category": str,
                "title": str,
                "summary": str,
                "signals": list,
                "linked_eval_case_ids": list,
                "runbook_ids": list,
            },
        )
        checks.append(check(ok, "P3 incident shape contract", detail))

    status, runbooks = get_json(f"{base_url}/api/runbooks")
    checks.append(check(status == 200 and isinstance(runbooks.get("runbooks"), list) and runbooks["runbooks"], "P3 runbooks list contract", f"runbooks={len(runbooks.get('runbooks', []))}"))
    if runbooks.get("runbooks"):
        ok, detail = expect_types(runbooks["runbooks"][0], {"id": str, "title": str, "steps": list})
        checks.append(check(ok, "P3 runbook shape contract", detail))

    status, eval_runs = get_json(f"{base_url}/api/eval-runs")
    checks.append(check(status == 200 and isinstance(eval_runs.get("eval_runs"), list) and eval_runs["eval_runs"], "P3 eval-runs list contract", f"eval_runs={len(eval_runs.get('eval_runs', []))}"))

    status, latest_eval = get_json(f"{base_url}/api/eval/latest")
    eval_run = latest_eval.get("eval_run")
    ok = isinstance(eval_run, dict) and isinstance(eval_run.get("metrics"), dict) and isinstance(eval_run.get("cases"), list)
    checks.append(check(status == 200 and ok, "P3 latest eval shape contract", f"cases={len(eval_run.get('cases', [])) if isinstance(eval_run, dict) else 0}"))

    status, unsafe = post_json(
        f"{base_url}/api/triage",
        {
            "user_id": "maya",
            "release_id": "rel-2026-06-01",
            "incident_id": "inc-2026-014",
        },
    )
    triage_keys = {"trace_id", "release", "incident", "decision", "failed_evals", "remediation_steps", "evidence"}
    ok, detail = expect_types(
        unsafe,
        {
            "trace_id": str,
            "release": dict,
            "incident": dict,
            "decision": dict,
            "failed_evals": list,
            "remediation_steps": list,
            "evidence": dict,
        },
    )
    checks.append(check(status == 200 and has_keys(unsafe, triage_keys) and ok, "P3 triage response contract", detail))
    decision = unsafe.get("decision", {})
    checks.append(
        check(
            isinstance(decision, dict)
            and decision.get("recommendation") == "block_release"
            and decision.get("release_blocked") is True
            and decision.get("severity") == "critical",
            "P3 unsafe rollout block contract",
            f"recommendation={decision.get('recommendation')}; blocked={decision.get('release_blocked')}",
        )
    )
    evidence = unsafe.get("evidence", {})
    checks.append(
        check(
            bool(unsafe.get("failed_evals"))
            and isinstance(evidence, dict)
            and isinstance(evidence.get("linked_eval_case_ids"), list)
            and evidence["linked_eval_case_ids"],
            "P3 failed eval evidence contract",
            f"failed_evals={len(unsafe.get('failed_evals', []))}; linked={len(evidence.get('linked_eval_case_ids', [])) if isinstance(evidence, dict) else 0}",
        )
    )

    status, latency = post_json(
        f"{base_url}/api/triage",
        {
            "user_id": "maya",
            "release_id": "rel-2026-06-01",
            "incident_id": "inc-2026-015",
        },
    )
    latency_decision = latency.get("decision", {})
    checks.append(
        check(
            status == 200
            and isinstance(latency_decision, dict)
            and latency_decision.get("recommendation") == "monitor"
            and latency_decision.get("release_blocked") is False,
            "P3 latency monitor contract",
            f"recommendation={latency_decision.get('recommendation')}; blocked={latency_decision.get('release_blocked')}",
        )
    )

    status, error = post_json(
        f"{base_url}/api/triage",
        {
            "user_id": "missing-user",
            "release_id": "rel-2026-06-01",
            "incident_id": "inc-2026-014",
        },
    )
    checks.append(check(status == 404 and isinstance(error.get("error"), str), "P3 triage error contract", json.dumps(error)))

    status, traces = get_json(f"{base_url}/api/traces?limit=3")
    checks.append(check(status == 200 and isinstance(traces.get("traces"), list) and len(traces["traces"]) <= 3, "P3 traces list contract", f"traces={len(traces.get('traces', []))}"))
    if traces.get("traces"):
        ok, detail = expect_types(traces["traces"][0], {"id": str, "created_at": str, "user_id": str, "release_id": str, "incident_id": str, "result": dict})
        checks.append(check(ok, "P3 trace shape contract", detail))

    status, audit = get_json(f"{base_url}/api/audit?limit=3")
    checks.append(check(status == 200 and isinstance(audit.get("events"), list), "P3 audit list contract", f"events={len(audit.get('events', []))}"))
    if audit.get("events"):
        ok, detail = expect_types(audit["events"][0], {"id": int, "created_at": str, "user_id": str, "action": str, "details": dict})
        checks.append(check(ok, "P3 audit shape contract", detail))

    checks.extend(scenario_contract(base_url, "P3", "ai-reliability-incident-console"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start isolated demo services and verify stable API response contracts.",
    )
    parser.add_argument("--project1-port", type=int, default=DEFAULT_PROJECT_1_PORT)
    parser.add_argument("--project2-port", type=int, default=DEFAULT_PROJECT_2_PORT)
    parser.add_argument("--project3-port", type=int, default=DEFAULT_PROJECT_3_PORT)
    args = parser.parse_args()

    project_1_port = reserve_port(args.project1_port)
    project_2_port = reserve_port(args.project2_port)
    project_3_port = reserve_port(args.project3_port)
    project_1_url = f"http://127.0.0.1:{project_1_port}"
    project_2_url = f"http://127.0.0.1:{project_2_port}"
    project_3_url = f"http://127.0.0.1:{project_3_port}"
    service_list = services(project_1_port, project_2_port, project_3_port)

    checks: list[Check] = []
    started: list[subprocess.Popen] = []
    try:
        for service in service_list:
            started.append(start_service(service))
        for service in service_list:
            if not wait_for_health(service["health"]):
                print(f"Service did not become healthy: {service['name']}", file=sys.stderr)
                return 1

        checks.extend(project_1_contracts(project_1_url))
        checks.extend(project_2_contracts(project_2_url))
        checks.extend(project_3_contracts(project_3_url))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        print(f"API contract check failed with exception: {exc}", file=sys.stderr)
        return 1
    finally:
        for process in started:
            process.terminate()
        for process in started:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    for item in checks:
        status = "PASS" if item.passed else "FAIL"
        print(f"[{status}] {item.name}: {item.detail}")

    passed = sum(1 for item in checks if item.passed)
    total = len(checks)
    print(f"\nAPI contract checks: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
