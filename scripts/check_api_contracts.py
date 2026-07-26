from __future__ import annotations

import argparse
import base64
import json
import socket
import subprocess
import sys
import tempfile
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


def request_json(
    method: str,
    url: str,
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request_headers = {"Content-Type": "application/json", **(headers or {})}
    request = urllib.request.Request(
        url,
        data=data,
        headers=request_headers,
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


def service_state_path(state_root: Path, service: dict) -> Path:
    return state_root / f"{service['name']}-runtime_state.json"


def start_service(service: dict, state_root: Path) -> subprocess.Popen:
    print(f"Starting {service['name']} on port {service['port']}")
    return subprocess.Popen(
        [
            sys.executable,
            "-B",
            "app.py",
            "--reset",
            "--state-path",
            str(service_state_path(state_root, service)),
            "--port",
            str(service["port"]),
        ],
        cwd=service["path"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def get_json(url: str, headers: dict[str, str] | None = None) -> tuple[int, dict]:
    return request_json("GET", url, headers=headers)


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None) -> tuple[int, dict]:
    return request_json("POST", url, payload, headers=headers)


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


def valid_evidence_spans(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, dict)
            and isinstance(item.get("text"), str)
            and bool(item["text"].strip())
            and valid_source_span(item.get("source_span"))
            for item in value
        )
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


def readiness_contract(base_url: str, label: str, expected_app: str, expected_checks: set[str]) -> Check:
    status, readiness = get_json(f"{base_url}/api/ready")
    checks = readiness.get("checks")
    actual_checks = set(checks.keys()) if isinstance(checks, dict) else set()
    return check(
        status == 200
        and readiness.get("status") == "ready"
        and readiness.get("app") == expected_app
        and readiness.get("ready") is True
        and expected_checks.issubset(actual_checks),
        f"{label} readiness contract",
        f"status={status}; checks={sorted(actual_checks)}",
    )


def project_1_contracts(base_url: str) -> list[Check]:
    checks: list[Check] = []

    status, health = get_json(f"{base_url}/api/health")
    checks.append(check(status == 200 and health == {"status": "ok", "app": "secure-enterprise-knowledge-copilot"}, "P1 health contract", json.dumps(health)))
    checks.append(
        readiness_contract(
            base_url,
            "P1",
            "secure-enterprise-knowledge-copilot",
            {"storage", "seed_data", "eval_state", "scenario_snapshot", "users", "scenario_files"},
        )
    )

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P1 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str, "tenant_id": str})
        checks.append(check(ok, "P1 user shape contract", detail))
        riley = next((user for user in users["users"] if user.get("id") == "riley"), {})
        checks.append(
            check(
                riley.get("role") == "employee"
                and "engineering-oncall" in riley.get("group_ids", [])
                and "group:engineering-oncall" in riley.get("source_principals", []),
                "P1 user identity group contract",
                f"riley_groups={riley.get('group_ids')}; principals={riley.get('source_principals')}",
            )
        )

    status, demo_token = post_json(f"{base_url}/api/auth/demo-token", {"user_id": "riley"})
    riley_bearer = {"Authorization": f"Bearer {demo_token.get('token', '')}"}
    checks.append(
        check(
            status == 200
            and demo_token.get("token_type") == "Bearer"
            and demo_token.get("auth_policy") == "local_signed_demo_token_v1"
            and demo_token.get("auth_context", {}).get("user_id") == "riley"
            and "engineering-oncall" in demo_token.get("auth_context", {}).get("group_ids", []),
            "P1 local signed demo auth token contract",
            f"status={status}; policy={demo_token.get('auth_policy')}; subject={demo_token.get('auth_context', {}).get('user_id')}",
        )
    )
    status, token_documents = get_json(f"{base_url}/api/documents", headers=riley_bearer)
    checks.append(
        check(
            status == 200
            and any(doc.get("id") == "engineering-oncall-escalation-2026" for doc in token_documents.get("documents", [])),
            "P1 bearer auth resolves document visibility",
            f"status={status}; documents={len(token_documents.get('documents', []))}",
        )
    )
    status, token_group_answer = post_json(
        f"{base_url}/api/query",
        {"question": "How quickly must Sev2 pages be acknowledged by the primary on-call engineer?"},
        headers=riley_bearer,
    )
    checks.append(
        check(
            status == 200
            and token_group_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == "engineering-oncall-escalation-2026"
                for citation in token_group_answer.get("citations", [])
            ),
            "P1 bearer auth can query group-scoped evidence",
            f"status={status}; trace={token_group_answer.get('trace_id')}; citations={len(token_group_answer.get('citations', []))}",
        )
    )
    status, token_mismatch = get_json(f"{base_url}/api/documents?user_id=alice", headers=riley_bearer)
    checks.append(
        check(
            status == 403 and "authenticated subject" in token_mismatch.get("error", ""),
            "P1 bearer auth rejects user_id mismatch",
            f"status={status}; error={token_mismatch.get('error')}",
        )
    )

    status, documents = get_json(f"{base_url}/api/documents?user_id=alice")
    checks.append(check(status == 200 and isinstance(documents.get("documents"), list), "P1 visible documents contract", f"documents={len(documents.get('documents', []))}"))
    if documents.get("documents"):
        ok, detail = expect_types(
            documents["documents"][0],
            {"id": str, "tenant_id": str, "title": str, "classification": str, "allowed_roles": list},
        )
        checks.append(check(ok and "body" not in documents["documents"][0], "P1 document shape hides body", detail))
    status, riley_documents = get_json(f"{base_url}/api/documents?user_id=riley")
    checks.append(
        check(
            status == 200
            and any(doc.get("id") == "engineering-oncall-escalation-2026" for doc in riley_documents.get("documents", []))
            and not any(doc.get("id") == "engineering-oncall-escalation-2026" for doc in documents.get("documents", [])),
            "P1 source group visibility differs within same role",
            f"alice_docs={len(documents.get('documents', []))}; riley_docs={len(riley_documents.get('documents', []))}",
        )
    )

    status, riley_oncall_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "riley",
            "question": "How quickly must Sev2 pages be acknowledged by the primary on-call engineer?",
        },
    )
    checks.append(
        check(
            status == 200
            and riley_oncall_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == "engineering-oncall-escalation-2026"
                for citation in riley_oncall_answer.get("citations", [])
            ),
            "P1 source group member can retrieve group-scoped evidence",
            f"trace={riley_oncall_answer.get('trace_id')}; citations={len(riley_oncall_answer.get('citations', []))}",
        )
    )

    status, alice_oncall_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "How quickly must Sev2 pages be acknowledged by the primary on-call engineer?",
        },
    )
    checks.append(
        check(
            status == 200
            and alice_oncall_answer.get("abstain_reason") == "no_accessible_grounded_evidence"
            and alice_oncall_answer.get("permission_blocked_count", 0) >= 1
            and not any(
                citation.get("doc_id") == "engineering-oncall-escalation-2026"
                for citation in alice_oncall_answer.get("citations", [])
            ),
            "P1 source group non-member is denied group-scoped evidence",
            f"blocked={alice_oncall_answer.get('permission_blocked_count')}; trace={alice_oncall_answer.get('trace_id')}",
        )
    )

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

    status, forbidden_preview = post_json(f"{base_url}/api/documents/parse-preview", forbidden_payload)
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_preview.get("error", ""),
            "P1 parse preview rejects non-admin users",
            json.dumps(forbidden_preview),
        )
    )

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
    status, parse_preview = post_json(f"{base_url}/api/documents/parse-preview", ingest_payload)
    preview = parse_preview.get("preview", {})
    preview_parser = preview.get("parser", {})
    preview_quality = preview_parser.get("quality", {})
    preview_scan = preview.get("source_scan", {})
    preview_chunks = preview.get("chunks", [])
    checks.append(
        check(
            status == 200
            and preview.get("raw_body_returned") is False
            and preview.get("would_index") is True
            and len(preview.get("source_hash", "")) == 64
            and preview_parser.get("contract_version") == "source_parser_contract_v1"
            and preview_parser.get("quality_schema_version") == "source_parser_quality_v1"
            and preview_parser.get("name") == "markdown-v1"
            and preview_quality.get("schema_version") == "source_parser_quality_v1"
            and preview_quality.get("parser_name") == "markdown-v1"
            and preview_quality.get("normalized_character_count") == preview_parser.get("normalized_characters")
            and preview_scan.get("schema_version") == "source_scan_v1"
            and preview_scan.get("raw_matches_returned") is False
            and preview.get("chunk_count", 0) >= 1
            and preview.get("chunk_source_span_unit") == "normalized_text"
            and isinstance(preview_chunks, list)
            and preview_chunks
            and valid_source_span(preview_chunks[0].get("source_span")),
            "P1 parse preview contract",
            f"status={status}; parser={preview_parser.get('name')}; chunks={preview.get('chunk_count')}; raw_body_returned={preview.get('raw_body_returned')}",
        )
    )

    status, ingestion = post_json(f"{base_url}/api/documents/ingest", ingest_payload)
    ingested_doc = ingestion.get("document", {})
    parser = ingestion.get("ingestion", {}).get("parser", {})
    ingestion_metadata = ingestion.get("ingestion", {})
    ingestion_scan = ingestion_metadata.get("source_scan", {})
    checks.append(
        check(
            status == 200
            and isinstance(ingested_doc, dict)
            and "body" not in ingested_doc
            and ingestion.get("chunk_count", 0) >= 1
            and len(ingestion_metadata.get("source_hash", "")) == 64
            and ingestion_scan.get("schema_version") == "source_scan_v1"
            and ingestion_scan.get("raw_matches_returned") is False
            and ingestion_metadata.get("chunk_source_span_unit") == "normalized_text"
            and ingestion_metadata.get("chunk_source_span_count") == ingestion.get("chunk_count"),
            "P1 admin ingestion contract",
            f"status={status}; doc={ingested_doc.get('id')}; chunks={ingestion.get('chunk_count')}; span_unit={ingestion_metadata.get('chunk_source_span_unit')}",
        )
    )
    checks.append(
        check(
            isinstance(parser, dict)
            and parser.get("contract_version") == "source_parser_contract_v1"
            and parser.get("quality_schema_version") == "source_parser_quality_v1"
            and parser.get("name") == "markdown-v1"
            and isinstance(parser.get("normalized_characters"), int)
            and parser.get("normalized_characters", 0) >= 20
            and isinstance(parser.get("metadata"), dict)
            and parser.get("quality", {}).get("schema_version") == "source_parser_quality_v1"
            and parser.get("quality", {}).get("normalized_character_count") == parser.get("normalized_characters")
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
            and csv_parser.get("metadata", {}).get("has_header") is True
            and csv_parser.get("quality", {}).get("csv_data_row_count") == 2,
            "P1 CSV ingestion parser contract",
            f"status={status}; parser={csv_parser.get('name')}; metadata={csv_parser.get('metadata')}",
        )
    )

    file_text = (
        "Benefits Open Enrollment Notice 2026\n\n"
        "Employees may enroll in the wellness stipend during the source-file intake pilot window "
        "from June 10 through June 20. The People Operations team requires citation evidence "
        "before the answer path mentions the stipend window."
    )
    file_ingest_payload = {
        "user_id": "avery",
        "replace": True,
        "document": {
            "title": "Benefits Open Enrollment Notice 2026",
            "file": {
                "filename": "benefits-open-enrollment-2026.md",
                "content_base64": base64.b64encode(file_text.encode("utf-8")).decode("ascii"),
            },
            "classification": "internal",
            "allowed_roles": ["employee", "manager", "admin"],
            "version": "2026.06",
            "updated_at": "2026-06-06",
        },
    }
    status, file_ingestion = post_json(f"{base_url}/api/documents/ingest", file_ingest_payload)
    file_doc = file_ingestion.get("document", {})
    file_source = file_ingestion.get("ingestion", {}).get("source", {}).get("file", {})
    file_parser = file_ingestion.get("ingestion", {}).get("parser", {})
    checks.append(
        check(
            status == 200
            and file_doc.get("source_connector") == "file-upload"
            and file_doc.get("source_url") == "uploaded://acme/benefits-open-enrollment-2026.md"
            and file_doc.get("source_file", {}).get("file_name") == "benefits-open-enrollment-2026.md"
            and file_source.get("file_size_bytes") == len(file_text.encode("utf-8"))
            and file_source.get("file_content_encoding") == "base64"
            and file_parser.get("name") == "markdown-v1",
            "P1 file-like ingestion contract",
            f"status={status}; doc={file_doc.get('id')}; source={file_doc.get('source_url')}; file={file_source}",
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
            and isinstance(sync_metadata.get("source_scan_review_required_count"), int)
            and isinstance(sync_metadata.get("source_scan_finding_counts"), dict)
            and len(synced_documents) == 3
            and all("body" not in doc for doc in synced_documents)
            and all(doc.get("source_scan", {}).get("schema_version") == "source_scan_v1" for doc in synced_documents)
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

    group_acl_sync_payload = {
        "user_id": "avery",
        "replace": True,
        "connector": {
            "name": "local-drive-groups-demo",
            "cursor": "2026-06-06T01:15:00Z",
            "acl_source": "fixture-group-acl-v1",
            "acl_snapshot": {
                "version": "fixture-group-acl-v1",
                "documents": {
                    "drive-doc-oncall-source-groups-2026": {
                        "allowed_roles": ["admin"],
                        "allowed_groups": ["engineering-oncall"],
                        "permission_id": "drive-acl-engineering-oncall-group-v1",
                        "principal_count": 1,
                    },
                },
            },
        },
        "documents": [
            {
                "id": "source-group-oncall-rotation-2026",
                "external_id": "drive-doc-oncall-source-groups-2026",
                "title": "Source Group On-Call Rotation 2026",
                "body": (
                    "Source Group On-Call Rotation 2026\n\n"
                    "The connector group ACL demo says engineering-oncall members can view rotation handoff notes. "
                    "Primary engineers must update the handoff checklist before leaving the rotation."
                ),
                "classification": "internal",
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
        ],
    }
    status, group_acl_sync = post_json(f"{base_url}/api/sources/sync", group_acl_sync_payload)
    group_acl_doc = group_acl_sync.get("documents", [{}])[0] if group_acl_sync.get("documents") else {}
    checks.append(
        check(
            status == 200
            and group_acl_doc.get("allowed_roles") == ["admin"]
            and group_acl_doc.get("allowed_groups") == ["engineering-oncall"]
            and group_acl_doc.get("source_acl_principals") == ["group:engineering-oncall"]
            and group_acl_doc.get("source_acl_principal_count") == 1,
            "P1 source sync applies connector group ACL snapshot",
            f"status={status}; groups={group_acl_doc.get('allowed_groups')}; principals={group_acl_doc.get('source_acl_principals')}",
        )
    )

    status, group_acl_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "riley",
            "question": "What are rotation handoff notes?",
        },
    )
    checks.append(
        check(
            status == 200
            and group_acl_answer.get("abstain_reason") is None
            and any(citation.get("doc_id") == "source-group-oncall-rotation-2026" for citation in group_acl_answer.get("citations", [])),
            "P1 connector group ACL evidence is retrievable by group member",
            f"trace={group_acl_answer.get('trace_id')}; citations={len(group_acl_answer.get('citations', []))}",
        )
    )

    status, group_acl_denied = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What are rotation handoff notes?",
        },
    )
    checks.append(
        check(
            status == 200
            and group_acl_denied.get("abstain_reason") == "no_accessible_grounded_evidence"
            and group_acl_denied.get("permission_blocked_count", 0) >= 1
            and not any(citation.get("doc_id") == "source-group-oncall-rotation-2026" for citation in group_acl_denied.get("citations", [])),
            "P1 connector group ACL non-member is denied retrieved evidence",
            f"blocked={group_acl_denied.get('permission_blocked_count')}; trace={group_acl_denied.get('trace_id')}",
        )
    )

    prune_sync_payload = {
        "user_id": "avery",
        "replace": True,
        "prune_missing": True,
        "connector": {
            "name": "prune-demo",
            "cursor": "2026-06-06T01:30:00Z",
            "acl_source": "fixture-acl-prune-v1",
            "acl_snapshot": {
                "version": "fixture-acl-prune-v1",
                "documents": {
                    "prune-demo-active-2026": {
                        "allowed_roles": ["employee", "manager", "admin"],
                        "permission_id": "prune-demo-active-v1",
                        "principal_count": 3,
                    },
                    "prune-demo-stale-2026": {
                        "allowed_roles": ["employee", "manager", "admin"],
                        "permission_id": "prune-demo-stale-v1",
                        "principal_count": 3,
                    },
                },
            },
        },
        "documents": [
            {
                "id": "prune-demo-active-2026",
                "external_id": "prune-demo-active-2026",
                "title": "Prune Demo Active Source 2026",
                "body": "Prune Demo Active Source 2026\n\nThe active prune source says current connector records stay searchable after a full sync.",
                "classification": "internal",
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
            {
                "id": "prune-demo-stale-2026",
                "external_id": "prune-demo-stale-2026",
                "title": "Prune Demo Stale Source 2026",
                "body": "Prune Demo Stale Source 2026\n\nThe obsolete prune archive says the zebra quasar exception should disappear after pruning.",
                "classification": "internal",
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
        ],
    }
    status, prune_seed = post_json(f"{base_url}/api/sources/sync", prune_sync_payload)
    checks.append(
        check(
            status == 200
            and prune_seed.get("sync", {}).get("connector") == "prune-demo"
            and prune_seed.get("sync", {}).get("prune_missing") is True
            and prune_seed.get("sync", {}).get("pruned_count") == 0,
            "P1 source sync can run a full prune-safe snapshot",
            f"status={status}; pruned={prune_seed.get('sync', {}).get('pruned_count')}",
        )
    )

    prune_followup_payload = {
        **prune_sync_payload,
        "connector": {
            **prune_sync_payload["connector"],
            "cursor": "2026-06-06T01:45:00Z",
            "acl_snapshot": {
                "version": "fixture-acl-prune-v2",
                "documents": {
                    "prune-demo-active-2026": {
                        "allowed_roles": ["employee", "manager", "admin"],
                        "permission_id": "prune-demo-active-v2",
                        "principal_count": 3,
                    },
                },
            },
        },
        "documents": [prune_sync_payload["documents"][0]],
    }
    status, prune_followup = post_json(f"{base_url}/api/sources/sync", prune_followup_payload)
    prune_metadata = prune_followup.get("sync", {})
    checks.append(
        check(
            status == 200
            and prune_metadata.get("prune_missing") is True
            and prune_metadata.get("pruned_count") == 1
            and prune_metadata.get("pruned_doc_ids") == ["prune-demo-stale-2026"],
            "P1 source sync prunes missing connector documents",
            f"pruned={prune_metadata.get('pruned_doc_ids')}",
        )
    )

    status, documents_after_prune = get_json(f"{base_url}/api/documents?user_id=alice")
    checks.append(
        check(
            status == 200
            and any(doc.get("id") == "prune-demo-active-2026" for doc in documents_after_prune.get("documents", []))
            and not any(doc.get("id") == "prune-demo-stale-2026" for doc in documents_after_prune.get("documents", [])),
            "P1 pruned source disappears from visible documents",
            f"documents={len(documents_after_prune.get('documents', []))}",
        )
    )

    status, pruned_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What does the obsolete prune archive say about the zebra quasar exception?",
        },
    )
    checks.append(
        check(
            status == 200
            and not any(citation.get("doc_id") == "prune-demo-stale-2026" for citation in pruned_answer.get("citations", []))
            and not any(item.get("doc_id") == "prune-demo-stale-2026" for item in pruned_answer.get("retrieved", [])),
            "P1 pruned source is no longer retrievable",
            f"trace={pruned_answer.get('trace_id')}; citations={len(pruned_answer.get('citations', []))}",
        )
    )

    job_sync_payload = {
        "user_id": "avery",
        "replace": True,
        "connector": {
            "name": "local-drive-demo",
            "cursor": "2026-06-06T02:00:00Z",
            "acl_source": "fixture-acl-job-v1",
            "acl_snapshot": {
                "version": "fixture-acl-job-v1",
                "documents": {
                    "drive-doc-job-source-readiness-2026": {
                        "allowed_roles": ["employee", "manager", "admin"],
                        "permission_id": "drive-acl-job-source-readiness-v1",
                        "principal_count": 3,
                    },
                },
            },
        },
        "documents": [
            {
                "id": "job-source-readiness-2026",
                "external_id": "drive-doc-job-source-readiness-2026",
                "title": "Ingestion Job Readiness 2026",
                "body": (
                    "Ingestion Job Readiness 2026\n\n"
                    "Durable ingestion jobs must record queued, running, succeeded, and dead-lettered states. "
                    "Operators use idempotency keys to avoid duplicate connector sync execution."
                ),
                "classification": "internal",
                "source_mime": "text/markdown",
                "updated_at": "2026-06-06",
            },
        ],
    }
    ingestion_job_payload = {
        "user_id": "avery",
        "type": "source_sync",
        "idempotency_key": "contract-source-sync-job-v1",
        "payload": job_sync_payload,
    }
    status, forbidden_job = post_json(
        f"{base_url}/api/ingestion/jobs",
        {**ingestion_job_payload, "user_id": "alice"},
    )
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_job.get("error", ""),
            "P1 ingestion job rejects non-admin users",
            json.dumps(forbidden_job),
        )
    )

    status, ingestion_job = post_json(f"{base_url}/api/ingestion/jobs", ingestion_job_payload)
    job = ingestion_job.get("job", {})
    job_result = ingestion_job.get("result", {}).get("sync", {})
    checks.append(
        check(
            status == 200
            and job.get("status") == "succeeded"
            and job.get("type") == "source_sync"
            and job.get("attempts") == 1
            and job.get("idempotency_key") == "contract-source-sync-job-v1"
            and job.get("input", {}).get("document_count") == 1
            and "body" not in job.get("input", {}).get("documents", [{}])[0]
            and len(job.get("input", {}).get("documents", [{}])[0].get("body_sha256", "")) == 64
            and job_result.get("document_count") == 1
            and job_result.get("chunk_count", 0) >= 1,
            "P1 ingestion job succeeds with sanitized input summary",
            f"job={job.get('id')}; status={job.get('status')}; chunks={job_result.get('chunk_count')}",
        )
    )

    status, replayed_job = post_json(f"{base_url}/api/ingestion/jobs", ingestion_job_payload)
    checks.append(
        check(
            status == 200
            and replayed_job.get("idempotency_replayed") is True
            and replayed_job.get("job", {}).get("id") == job.get("id")
            and replayed_job.get("job", {}).get("status") == "succeeded",
            "P1 ingestion job idempotency replays existing job",
            f"job={replayed_job.get('job', {}).get('id')}; replay={replayed_job.get('idempotency_replayed')}",
        )
    )

    status, forbidden_jobs_list = get_json(f"{base_url}/api/ingestion/jobs?user_id=alice")
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_jobs_list.get("error", ""),
            "P1 ingestion job list rejects non-admin users",
            json.dumps(forbidden_jobs_list),
        )
    )

    failed_job_payload = {
        "user_id": "avery",
        "type": "source_sync",
        "idempotency_key": "contract-source-sync-job-missing-acl-v1",
        "payload": {
            "user_id": "avery",
            "replace": True,
            "connector": {
                "name": "local-drive-demo",
                "cursor": "2026-06-06T03:00:00Z",
                "acl_source": "fixture-acl-missing",
                "acl_snapshot": {
                    "version": "fixture-acl-missing",
                    "documents": {
                        "drive-doc-unrelated-source-2026": {
                            "allowed_roles": ["employee", "manager", "admin"],
                            "permission_id": "drive-acl-unrelated-source-v1",
                            "principal_count": 3,
                        },
                    },
                },
            },
            "documents": [
                {
                    "id": "dead-letter-source-2026",
                    "external_id": "drive-doc-dead-letter-source-2026",
                    "title": "Dead Letter Source 2026",
                    "body": (
                        "Dead Letter Source 2026\n\n"
                        "This source should never become searchable until the connector provides a matching ACL record."
                    ),
                    "classification": "internal",
                    "source_mime": "text/markdown",
                    "updated_at": "2026-06-06",
                },
            ],
        },
    }
    status, failed_job = post_json(f"{base_url}/api/ingestion/jobs", failed_job_payload)
    failed_job_record = failed_job.get("job", {})
    checks.append(
        check(
            status == 200
            and failed_job_record.get("status") == "dead_lettered"
            and failed_job_record.get("error", {}).get("retryable") is True
            and "source ACL snapshot" in failed_job_record.get("error", {}).get("message", ""),
            "P1 ingestion job dead-letters failed source sync",
            f"job={failed_job_record.get('id')}; error={failed_job_record.get('error', {}).get('status')}",
        )
    )

    retry_payload = {
        "user_id": "avery",
        "type": "source_sync",
        "idempotency_key": "contract-source-sync-job-retry-v1",
        "retry_of_job_id": failed_job_record.get("id"),
        "payload": {
            **failed_job_payload["payload"],
            "connector": {
                "name": "local-drive-demo",
                "cursor": "2026-06-06T03:05:00Z",
                "acl_source": "fixture-acl-retry",
                "acl_snapshot": {
                    "version": "fixture-acl-retry",
                    "documents": {
                        "drive-doc-dead-letter-source-2026": {
                            "allowed_roles": ["employee", "manager", "admin"],
                            "permission_id": "drive-acl-dead-letter-source-v1",
                            "principal_count": 3,
                        },
                    },
                },
            },
        },
    }
    status, retry_job = post_json(f"{base_url}/api/ingestion/jobs", retry_payload)
    retry_job_record = retry_job.get("job", {})
    checks.append(
        check(
            status == 200
            and retry_job_record.get("status") == "succeeded"
            and retry_job_record.get("retry_of_job_id") == failed_job_record.get("id")
            and retry_job_record.get("result", {}).get("doc_ids") == ["dead-letter-source-2026"],
            "P1 ingestion job retry can recover a dead-letter",
            f"job={retry_job_record.get('id')}; retry_of={retry_job_record.get('retry_of_job_id')}",
        )
    )

    status, jobs_list = get_json(f"{base_url}/api/ingestion/jobs?user_id=avery&limit=10")
    jobs = jobs_list.get("jobs", [])
    serialized_jobs = json.dumps(jobs)
    checks.append(
        check(
            status == 200
            and isinstance(jobs, list)
            and any(item.get("id") == job.get("id") for item in jobs)
            and any(item.get("id") == failed_job_record.get("id") and item.get("status") == "dead_lettered" for item in jobs)
            and any(item.get("retry_of_job_id") == failed_job_record.get("id") for item in jobs)
            and "Durable ingestion jobs must record queued" not in serialized_jobs,
            "P1 ingestion jobs list exposes status without raw bodies",
            f"jobs={len(jobs)}",
        )
    )

    github_payload = {
        "user_id": "avery",
        "mode": "fixture",
        "owner": "tiramitree",
        "repo": "fde-ai-systems-portfolio",
        "cursor": "2026-06-06T04:00:00Z",
        "idempotency_key": "contract-github-connector-sync-v1",
        "records": [
            {
                "kind": "issue",
                "number": 5,
                "title": "CSV export for eval summaries",
                "body": (
                    "GitHub connector fixture records that eval summary exports must include pass_rate, "
                    "failed_cases, and trace_id columns before review."
                ),
                "state": "open",
                "html_url": "https://github.com/tiramitree/fde-ai-systems-portfolio/issues/5",
                "updated_at": "2026-06-06T04:00:00Z",
                "labels": [{"name": "evals"}, {"name": "export"}],
                "user": {"login": "contributor-fixture"},
                "allowed_roles": ["employee", "manager", "admin"],
            },
            {
                "kind": "pull",
                "number": 7,
                "title": "Add GitHub connector runbook",
                "body": (
                    "GitHub pull request runbook says connector syncs need cursor checkpoints, "
                    "source URLs, and permission snapshots."
                ),
                "state": "open",
                "html_url": "https://github.com/tiramitree/fde-ai-systems-portfolio/pull/7",
                "updated_at": "2026-06-06T04:05:00Z",
                "labels": ["connector", "runbook"],
                "user": {"login": "reviewer-fixture"},
                "allowed_roles": ["manager", "admin"],
            },
        ],
    }
    status, forbidden_github = post_json(
        f"{base_url}/api/connectors/github/sync",
        {**github_payload, "user_id": "alice"},
    )
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_github.get("error", ""),
            "P1 GitHub connector rejects non-admin users",
            json.dumps(forbidden_github),
        )
    )

    status, github_sync = post_json(f"{base_url}/api/connectors/github/sync", github_payload)
    github_meta = github_sync.get("github", {})
    github_job = github_sync.get("job", {})
    github_result = github_sync.get("result", {})
    github_docs = github_result.get("documents", [])
    checks.append(
        check(
            status == 200
            and github_meta.get("owner") == "tiramitree"
            and github_meta.get("repo") == "fde-ai-systems-portfolio"
            and github_meta.get("mode") == "fixture"
            and github_meta.get("record_count") == 2
            and github_job.get("status") == "succeeded"
            and github_job.get("input", {}).get("connector") == "github"
            and github_result.get("sync", {}).get("connector") == "github"
            and github_result.get("sync", {}).get("document_count") == 2
            and len(github_docs) == 2
            and all("body" not in item for item in github_docs)
            and any(
                item.get("id") == "github-tiramitree-fde-ai-systems-portfolio-issue-5"
                and item.get("source_connector") == "github"
                and item.get("external_id") == "github:tiramitree/fde-ai-systems-portfolio:issue:5"
                and item.get("source_url") == "https://github.com/tiramitree/fde-ai-systems-portfolio/issues/5"
                and item.get("allowed_roles_source") == "connector_acl_snapshot"
                for item in github_docs
            ),
            "P1 GitHub connector syncs issues and PRs through ingestion jobs",
            f"job={github_job.get('id')}; docs={len(github_docs)}",
        )
    )

    status, replayed_github_sync = post_json(f"{base_url}/api/connectors/github/sync", github_payload)
    checks.append(
        check(
            status == 200
            and replayed_github_sync.get("idempotency_replayed") is True
            and replayed_github_sync.get("job", {}).get("id") == github_job.get("id"),
            "P1 GitHub connector idempotency replays existing sync",
            f"job={replayed_github_sync.get('job', {}).get('id')}; replay={replayed_github_sync.get('idempotency_replayed')}",
        )
    )

    status, github_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What columns must eval summary exports include before review?",
        },
    )
    checks.append(
        check(
            status == 200
            and github_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == "github-tiramitree-fde-ai-systems-portfolio-issue-5"
                and valid_source_span(citation.get("source_span"))
                for citation in github_answer.get("citations", [])
            ),
            "P1 GitHub connector content is retrievable with citation",
            f"trace={github_answer.get('trace_id')}; citations={len(github_answer.get('citations', []))}",
        )
    )

    status, github_jobs_list = get_json(f"{base_url}/api/ingestion/jobs?user_id=avery&limit=20")
    github_jobs = github_jobs_list.get("jobs", [])
    serialized_github_jobs = json.dumps(github_jobs)
    checks.append(
        check(
            status == 200
            and any(item.get("id") == github_job.get("id") and item.get("status") == "succeeded" for item in github_jobs)
            and "eval summary exports must include" not in serialized_github_jobs,
            "P1 GitHub connector job list hides raw GitHub bodies",
            f"jobs={len(github_jobs)}",
        )
    )

    source_bundle_payload = {
        "user_id": "avery",
        "bundle": "operations-handbook",
        "cursor": "2026-06-07T00:00:00Z",
        "idempotency_key": "contract-source-bundle-sync-v1",
        "prune_missing": True,
    }
    status, forbidden_bundle_catalog = get_json(
        f"{base_url}/api/connectors/source-bundle/catalog?user_id=alice&bundle=operations-handbook"
    )
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_bundle_catalog.get("error", ""),
            "P1 source bundle catalog rejects non-admin users",
            json.dumps(forbidden_bundle_catalog),
        )
    )
    status, traversal_bundle_catalog = get_json(
        f"{base_url}/api/connectors/source-bundle/catalog?user_id=avery&bundle=../seed_documents"
    )
    checks.append(
        check(
            status == 400 and "unsupported characters" in traversal_bundle_catalog.get("error", ""),
            "P1 source bundle catalog rejects path traversal bundle names",
            json.dumps(traversal_bundle_catalog),
        )
    )
    status, source_bundle_catalog = get_json(
        f"{base_url}/api/connectors/source-bundle/catalog?user_id=avery&bundle=operations-handbook"
    )
    catalog = source_bundle_catalog.get("catalog", {})
    catalog_bundles = catalog.get("bundles", [])
    catalog_bundle = catalog_bundles[0] if catalog_bundles else {}
    catalog_documents = catalog_bundle.get("documents", [])
    serialized_source_bundle_catalog = json.dumps(source_bundle_catalog)
    checks.append(
        check(
            status == 200
            and catalog.get("catalog_version") == "source_bundle_catalog_v1"
            and catalog.get("bundle_count") == 1
            and catalog.get("raw_bodies_returned") is False
            and catalog_bundle.get("bundle") == "operations-handbook"
            and catalog_bundle.get("connector") == "source-bundle"
            and catalog_bundle.get("document_count") == 3
            and isinstance(catalog_bundle.get("manifest_sha256"), str)
            and len(catalog_bundle.get("manifest_sha256", "")) == 64
            and len(catalog_documents) == 3
            and all("body" not in item for item in catalog_documents)
            and any(
                item.get("id") == "source-bundle-operations-handbook-incident-escalation"
                and item.get("source_mime") == "text/markdown"
                and item.get("principal_count") == 3
                and isinstance(item.get("body_sha256"), str)
                and len(item.get("body_sha256", "")) == 64
                for item in catalog_documents
            )
            and "Sev2 incidents from the source bundle" not in serialized_source_bundle_catalog,
            "P1 source bundle catalog previews manifests without raw bodies",
            f"bundles={len(catalog_bundles)}; docs={len(catalog_documents)}",
        )
    )
    status, forbidden_bundle = post_json(
        f"{base_url}/api/connectors/source-bundle/sync",
        {**source_bundle_payload, "user_id": "alice"},
    )
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_bundle.get("error", ""),
            "P1 source bundle connector rejects non-admin users",
            json.dumps(forbidden_bundle),
        )
    )
    status, traversal_bundle = post_json(
        f"{base_url}/api/connectors/source-bundle/sync",
        {**source_bundle_payload, "bundle": "../seed_documents"},
    )
    checks.append(
        check(
            status == 400 and "unsupported characters" in traversal_bundle.get("error", ""),
            "P1 source bundle connector rejects path traversal bundle names",
            json.dumps(traversal_bundle),
        )
    )
    status, source_bundle_sync = post_json(f"{base_url}/api/connectors/source-bundle/sync", source_bundle_payload)
    source_bundle_meta = source_bundle_sync.get("source_bundle", {})
    source_bundle_job = source_bundle_sync.get("job", {})
    source_bundle_result = source_bundle_sync.get("result", {})
    source_bundle_docs = source_bundle_result.get("documents", [])
    serialized_source_bundle = json.dumps(source_bundle_sync)
    checks.append(
        check(
            status == 200
            and source_bundle_meta.get("bundle") == "operations-handbook"
            and source_bundle_meta.get("connector") == "source-bundle"
            and source_bundle_meta.get("document_count") == 3
            and isinstance(source_bundle_meta.get("manifest_sha256"), str)
            and len(source_bundle_meta.get("manifest_sha256", "")) == 64
            and source_bundle_job.get("status") == "succeeded"
            and source_bundle_result.get("sync", {}).get("connector") == "source-bundle"
            and source_bundle_result.get("sync", {}).get("document_count") == 3
            and len(source_bundle_docs) == 3
            and all("body" not in item for item in source_bundle_docs)
            and any(
                item.get("id") == "source-bundle-operations-handbook-incident-escalation"
                and item.get("source_connector") == "source-bundle"
                and item.get("external_id") == "source-bundle:operations-handbook:incident-escalation.md"
                and item.get("source_url") == "source-bundle://operations-handbook/incident-escalation.md"
                and item.get("allowed_roles_source") == "connector_acl_snapshot"
                and "engineering-oncall" in item.get("allowed_groups", [])
                for item in source_bundle_docs
            )
            and "Sev2 incidents from the source bundle" not in serialized_source_bundle,
            "P1 source bundle connector syncs checked-in files through ingestion jobs",
            f"job={source_bundle_job.get('id')}; docs={len(source_bundle_docs)}",
        )
    )
    status, replayed_source_bundle_sync = post_json(
        f"{base_url}/api/connectors/source-bundle/sync",
        source_bundle_payload,
    )
    checks.append(
        check(
            status == 200
            and replayed_source_bundle_sync.get("idempotency_replayed") is True
            and replayed_source_bundle_sync.get("job", {}).get("id") == source_bundle_job.get("id"),
            "P1 source bundle connector idempotency replays existing sync",
            f"job={replayed_source_bundle_sync.get('job', {}).get('id')}; replay={replayed_source_bundle_sync.get('idempotency_replayed')}",
        )
    )
    status, source_bundle_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "riley",
            "question": "What must Sev2 incidents from the source bundle include before escalation?",
        },
    )
    checks.append(
        check(
            status == 200
            and source_bundle_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == "source-bundle-operations-handbook-incident-escalation"
                and valid_source_span(citation.get("source_span"))
                for citation in source_bundle_answer.get("citations", [])
            ),
            "P1 source bundle content is retrievable by source group with citation",
            f"trace={source_bundle_answer.get('trace_id')}; citations={len(source_bundle_answer.get('citations', []))}",
        )
    )

    status, forbidden_connector_status = get_json(f"{base_url}/api/connectors/status?user_id=alice")
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_connector_status.get("error", ""),
            "P1 connector status rejects non-admin users",
            json.dumps(forbidden_connector_status),
        )
    )

    status, connector_status = get_json(f"{base_url}/api/connectors/status?user_id=avery&limit=20")
    connectors = connector_status.get("connectors", [])
    github_status = next((item for item in connectors if item.get("connector") == "github"), {})
    local_status = next((item for item in connectors if item.get("connector") == "local-drive-demo"), {})
    source_bundle_status = next((item for item in connectors if item.get("connector") == "source-bundle"), {})
    serialized_connector_status = json.dumps(connector_status)
    checks.append(
        check(
            status == 200
            and connector_status.get("status_source") == "ingestion_jobs+indexed_documents"
            and connector_status.get("connector_count") >= 3
            and github_status.get("health") == "healthy"
            and github_status.get("latest_job_id") == github_job.get("id")
            and github_status.get("latest_cursor") == "2026-06-06T04:00:00Z"
            and github_status.get("document_count") == 2
            and github_status.get("chunk_count", 0) >= 2
            and github_status.get("indexed_document_count") == 2
            and github_status.get("active_document_count") == 2
            and github_status.get("filtered_document_count") == 0
            and github_status.get("index_matches_latest_job") is True
            and github_status.get("index_health") == "indexed"
            and github_status.get("parser_warning_count") == 0
            and any(str(source).startswith("github:") for source in github_status.get("acl_sources", []))
            and source_bundle_status.get("health") == "healthy"
            and source_bundle_status.get("latest_job_id") == source_bundle_job.get("id")
            and source_bundle_status.get("latest_cursor") == "2026-06-07T00:00:00Z"
            and source_bundle_status.get("document_count") == 3
            and source_bundle_status.get("chunk_count", 0) >= 3
            and source_bundle_status.get("indexed_document_count") == 3
            and source_bundle_status.get("active_document_count") == 3
            and source_bundle_status.get("source_lifecycle_counts", {}).get("active") == 3
            and "source-bundle:operations-handbook:v1" in source_bundle_status.get("source_acl_versions", [])
            and local_status.get("health") == "recovered"
            and local_status.get("latest_job_status") == "succeeded"
            and local_status.get("latest_cursor") == "2026-06-06T03:05:00Z"
            and local_status.get("dead_letter_count", 0) >= 1
            and local_status.get("success_count", 0) >= 1
            and local_status.get("indexed_document_count", 0) >= local_status.get("document_count", 0)
            and local_status.get("active_document_count", 0) >= 1
            and local_status.get("index_health") == "indexed"
            and "eval summary exports must include" not in serialized_connector_status
            and "Sev2 incidents from the source bundle" not in serialized_connector_status
            and "Durable ingestion jobs must record queued" not in serialized_connector_status,
            "P1 connector status summarizes job and indexed-source health without raw bodies",
            f"connectors={len(connectors)}; github={github_status.get('health')}; source_bundle={source_bundle_status.get('health')}; local={local_status.get('health')}",
        )
    )

    status, forbidden_source_quality = get_json(f"{base_url}/api/sources/quality?user_id=alice")
    checks.append(
        check(
            status == 403 and "Only admin users" in forbidden_source_quality.get("error", ""),
            "P1 source quality rejects non-admin users",
            json.dumps(forbidden_source_quality),
        )
    )

    status, source_quality_payload = get_json(f"{base_url}/api/sources/quality?user_id=avery&limit=30")
    source_quality = source_quality_payload.get("source_quality", {})
    quality_docs = source_quality.get("documents", [])
    ingested_quality_doc = next((item for item in quality_docs if item.get("id") == ingested_doc.get("id")), {})
    serialized_source_quality = json.dumps(source_quality_payload)
    checks.append(
        check(
            status == 200
            and source_quality.get("schema_version") == "source_quality_report_v1"
            and source_quality.get("actor_user_id") == "avery"
            and source_quality.get("document_count", 0) >= len(quality_docs)
            and source_quality.get("active_document_count", 0) >= 1
            and isinstance(source_quality.get("attention_required_count"), int)
            and source_quality.get("raw_bodies_returned") is False
            and source_quality.get("parser_quality_schema_counts", {}).get("source_parser_quality_v1", 0) >= 1
            and source_quality.get("source_scan_schema_counts", {}).get("source_scan_v1", 0) >= 1
            and isinstance(source_quality.get("source_scan_review_required_count"), int)
            and isinstance(source_quality.get("source_scan_finding_counts"), dict)
            and isinstance(quality_docs, list)
            and quality_docs
            and ingested_quality_doc.get("parser_quality_schema") == "source_parser_quality_v1"
            and ingested_quality_doc.get("source_scan_schema") == "source_scan_v1"
            and ingested_quality_doc.get("source_scan_status") in {"passed", "review_required"}
            and isinstance(ingested_quality_doc.get("source_scan_finding_categories"), list)
            and ingested_quality_doc.get("normalized_non_empty_line_count", 0) >= 1
            and isinstance(ingested_quality_doc.get("risk_flags"), list)
            and "Employee Travel Expense Policy 2026\n\nEmployees" not in serialized_source_quality
            and "eval summary exports must include" not in serialized_source_quality
            and "Sev2 incidents from the source bundle" not in serialized_source_quality,
            "P1 source quality summarizes parser, source scan, ACL, lifecycle, and risk flags without raw bodies",
            f"docs={source_quality.get('document_count')}; attention={source_quality.get('attention_required_count')}; schemas={source_quality.get('parser_quality_schema_counts')}; scans={source_quality.get('source_scan_schema_counts')}",
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

    status, file_answer = post_json(
        f"{base_url}/api/query",
        {
            "user_id": "alice",
            "question": "What are the wellness stipend enrollment dates from the source-file intake pilot?",
        },
    )
    checks.append(
        check(
            status == 200
            and file_answer.get("abstain_reason") is None
            and any(
                citation.get("doc_id") == file_doc.get("id")
                for citation in file_answer.get("citations", [])
            ),
            "P1 file-like ingested document is retrievable with citation",
            f"trace={file_answer.get('trace_id')}; doc={file_doc.get('id')}",
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
    status, source_sync_audit = get_json(f"{base_url}/api/audit?limit=80")
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
    status, ingestion_job_audit = get_json(f"{base_url}/api/audit?limit=80")
    checks.append(
        check(
            status == 200
            and any(
                event.get("action") == "ingestion_job_completed"
                and event.get("details", {}).get("job_id") == job.get("id")
                for event in ingestion_job_audit.get("events", [])
            )
            and any(
                event.get("action") == "ingestion_job_dead_lettered"
                and event.get("details", {}).get("job_id") == failed_job_record.get("id")
                for event in ingestion_job_audit.get("events", [])
            ),
            "P1 ingestion jobs write completion and dead-letter audit events",
            f"events={len(ingestion_job_audit.get('events', []))}",
        )
    )
    status, github_connector_audit = get_json(f"{base_url}/api/audit?limit=80")
    checks.append(
        check(
            status == 200
            and any(
                event.get("action") == "github_connector_synced"
                and event.get("details", {}).get("owner") == "tiramitree"
                and event.get("details", {}).get("repo") == "fde-ai-systems-portfolio"
                and event.get("details", {}).get("job_id") == github_job.get("id")
                for event in github_connector_audit.get("events", [])
            ),
            "P1 GitHub connector writes audit event",
            f"events={len(github_connector_audit.get('events', []))}",
        )
    )
    status, source_bundle_audit = get_json(f"{base_url}/api/audit?limit=100")
    checks.append(
        check(
            status == 200
            and any(
                event.get("action") == "source_bundle_synced"
                and event.get("details", {}).get("bundle") == "operations-handbook"
                and event.get("details", {}).get("connector") == "source-bundle"
                and event.get("details", {}).get("job_id") == source_bundle_job.get("id")
                and event.get("details", {}).get("job_status") == "succeeded"
                for event in source_bundle_audit.get("events", [])
            ),
            "P1 source bundle connector writes audit event",
            f"events={len(source_bundle_audit.get('events', []))}",
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
            and profile.get("permission_filter") == "tenant_identity_before_scoring"
            and profile.get("source_lifecycle_policy") == "active_sources_only"
            and isinstance(profile.get("stale_filtered_count"), int)
            and profile.get("stale_filtered_count", 0) >= 1
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
            and isinstance(citations[0].get("evidence_excerpt"), str)
            and bool(citations[0]["evidence_excerpt"].strip())
            and valid_evidence_spans(citations[0].get("evidence_spans"))
            and "hr-remote-work-2025-superseded" not in {item.get("doc_id") for item in retrieved}
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
    checks.append(
        readiness_contract(
            base_url,
            "P2",
            "regulated-customer-operations-agent",
            {"storage", "seed_data", "eval_state", "scenario_snapshot", "users", "cases", "approvals", "scenario_files"},
        )
    )

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P2 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str})
        checks.append(check(ok, "P2 user shape contract", detail))

    status, ivy_token = post_json(f"{base_url}/api/auth/demo-token", {"user_id": "ivy"})
    ivy_bearer = {"Authorization": f"Bearer {ivy_token.get('token', '')}"}
    checks.append(
        check(
            status == 200
            and ivy_token.get("token_type") == "Bearer"
            and ivy_token.get("auth_policy") == "local_signed_demo_token_v1"
            and ivy_token.get("auth_context", {}).get("user_id") == "ivy"
            and ivy_token.get("auth_context", {}).get("role") == "investigator",
            "P2 local signed demo auth token contract",
            f"status={status}; policy={ivy_token.get('auth_policy')}; subject={ivy_token.get('auth_context', {}).get('user_id')}",
        )
    )
    status, sam_token = post_json(f"{base_url}/api/auth/demo-token", {"user_id": "sam"})
    sam_bearer = {"Authorization": f"Bearer {sam_token.get('token', '')}"}
    checks.append(
        check(
            status == 200
            and sam_token.get("auth_context", {}).get("user_id") == "sam"
            and sam_token.get("auth_context", {}).get("role") == "supervisor",
            "P2 supervisor demo auth token contract",
            f"status={status}; subject={sam_token.get('auth_context', {}).get('user_id')}",
        )
    )
    status, token_general = post_json(
        f"{base_url}/api/agent",
        {"message": "What time is it?"},
        headers=ivy_bearer,
    )
    checks.append(
        check(
            status == 200
            and token_general.get("intent") == "general"
            and token_general.get("approvals") == []
            and isinstance(token_general.get("trace_id"), str),
            "P2 bearer auth resolves agent subject",
            f"status={status}; trace={token_general.get('trace_id')}",
        )
    )
    status, token_mismatch = post_json(
        f"{base_url}/api/agent",
        {"user_id": "sam", "message": "What can you do?"},
        headers=ivy_bearer,
    )
    checks.append(
        check(
            status == 403 and "authenticated subject" in token_mismatch.get("error", ""),
            "P2 bearer auth rejects identity mismatch",
            f"status={status}; error={token_mismatch.get('error')}",
        )
    )

    status, cases = get_json(f"{base_url}/api/cases")
    checks.append(check(status == 200 and isinstance(cases.get("cases"), list) and cases["cases"], "P2 cases list contract", f"cases={len(cases.get('cases', []))}"))
    if cases.get("cases"):
        ok, detail = expect_types(cases["cases"][0], {"id": str, "seller_id": str, "product_id": str, "status": str})
        checks.append(check(ok, "P2 case shape contract", detail))

    status, tool_registry = get_json(f"{base_url}/api/tool-registry")
    tools = tool_registry.get("tools", [])
    send_notice_tool = next((tool for tool in tools if tool.get("name") == "send_notice"), {})
    checks.append(
        check(
            status == 200
            and tool_registry.get("schema_version") == "tool_registry_v1"
            and isinstance(tools, list)
            and len(tools) >= 8
            and send_notice_tool.get("side_effect") is True
            and send_notice_tool.get("approval_required") is True
            and send_notice_tool.get("dry_run_required") is True
            and send_notice_tool.get("raw_payload_returned") is False
            and "supervisor" in send_notice_tool.get("allowed_roles", []),
            "P2 tool registry exposes governed side-effect tools",
            f"tools={len(tools)}; send_notice={send_notice_tool.get('credential_scope')}",
        )
    )

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
        "latency_ms",
        "workflow_run",
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
            "latency_ms": (int, float),
            "workflow_run": dict,
        },
    )
    checks.append(check(status == 200 and has_keys(investigation, agent_keys) and ok, "P2 agent response contract", detail))
    checks.append(check(investigation.get("model_router") == "local", "P2 default router source contract", f"model_router={investigation.get('model_router')}"))
    approval_id = investigation["approvals"][0]["id"] if investigation.get("approvals") else ""
    checks.append(check(bool(approval_id) and investigation.get("blocked_actions"), "P2 approval plus blocked-side-effect contract", f"approval={approval_id}"))
    approval_preview = investigation["approvals"][0] if investigation.get("approvals") else {}
    serialized_investigation = json.dumps(investigation)
    checks.append(
        check(
            approval_preview.get("approval_policy") == "approval_policy_v1"
            and approval_preview.get("tool_registry_version") == "tool_registry_v1"
            and approval_preview.get("owner_role") == "supervisor"
            and approval_preview.get("review_status") == "pending"
            and approval_preview.get("raw_payload_returned") is False
            and "payload" not in approval_preview
            and len(approval_preview.get("payload_sha256", "")) == 64
            and approval_preview.get("dry_run_preview", {}).get("schema_version") == "dry_run_preview_v1"
            and approval_preview.get("dry_run_preview", {}).get("raw_body_returned") is False
            and "Seller Market Blue" not in serialized_investigation
            and "Please remove the listing" not in serialized_investigation,
            "P2 agent response exposes sanitized approval dry-run preview",
            f"approval={approval_id}; expires={approval_preview.get('expires_at')}",
        )
    )
    workflow_run = investigation.get("workflow_run", {})
    checks.append(
        check(
            workflow_run.get("schema_version") == "workflow_run_v1"
            and workflow_run.get("status") == "waiting_for_approval"
            and workflow_run.get("stage") == "approval_requested"
            and workflow_run.get("trace_id") == investigation.get("trace_id")
            and approval_id in workflow_run.get("approval_ids", [])
            and workflow_run.get("raw_message_returned") is False
            and len(workflow_run.get("message_sha256", "")) == 64,
            "P2 agent workflow checkpoint waits on approval",
            f"workflow={workflow_run.get('id')}; status={workflow_run.get('status')}; approvals={workflow_run.get('approval_ids')}",
        )
    )

    status, pending_outbox = get_json(f"{base_url}/api/action-outbox?limit=5")
    pending_outbox_items = pending_outbox.get("action_outbox", [])
    pending_outbox_item = next((item for item in pending_outbox_items if item.get("approval_id") == approval_id), {})
    serialized_pending_outbox = json.dumps(pending_outbox)
    checks.append(
        check(
            status == 200
            and pending_outbox_item.get("status") == "awaiting_approval"
            and pending_outbox_item.get("action_type") == "send_notice"
            and pending_outbox_item.get("attempt_count") == 0
            and pending_outbox_item.get("lease_count") == 0
            and pending_outbox_item.get("lease_id") is None
            and pending_outbox_item.get("last_leased_by") is None
            and pending_outbox_item.get("raw_payload_returned") is False
            and pending_outbox_item.get("approval_policy") == "approval_policy_v1"
            and pending_outbox_item.get("tool_registry_version") == "tool_registry_v1"
            and pending_outbox_item.get("approval_expires_at") == approval_preview.get("expires_at")
            and pending_outbox_item.get("dry_run_preview", {}).get("schema_version") == "dry_run_preview_v1"
            and pending_outbox_item.get("dry_run_preview", {}).get("raw_body_returned") is False
            and len(pending_outbox_item.get("payload_sha256", "")) == 64
            and "Seller Market Blue" not in serialized_pending_outbox
            and "Please remove the listing" not in serialized_pending_outbox,
            "P2 approval request enqueues sanitized action outbox item",
            f"outbox={pending_outbox_item.get('id')}; approval={approval_id}",
        )
    )
    status, pending_workflows = get_json(f"{base_url}/api/workflow-runs?limit=5")
    pending_workflow_items = pending_workflows.get("workflow_runs", [])
    pending_workflow = next((item for item in pending_workflow_items if approval_id in item.get("approval_ids", [])), {})
    serialized_pending_workflows = json.dumps(pending_workflows)
    checks.append(
        check(
            status == 200
            and pending_workflow.get("status") == "waiting_for_approval"
            and pending_workflow.get("stage") == "approval_requested"
            and pending_outbox_item.get("id") in pending_workflow.get("outbox_ids", [])
            and pending_workflow.get("raw_message_returned") is False
            and "Seller Market Blue" not in serialized_pending_workflows
            and "Please remove the listing" not in serialized_pending_workflows,
            "P2 workflow run ledger exposes sanitized approval checkpoint",
            f"workflow={pending_workflow.get('id')}; outbox={pending_outbox_item.get('id')}",
        )
    )

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
        },
        headers=sam_bearer,
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
    execution = approval.get("execution", {})
    outbox_item = approval.get("outbox_item", {})
    checks.append(
        check(
            isinstance(execution, dict)
            and execution.get("approval_id") == approval_id
            and execution.get("action_type") == "send_notice"
            and execution.get("status") == "succeeded"
            and execution.get("result") == "notice_sent"
            and isinstance(execution.get("payload_sha256"), str)
            and len(execution.get("payload_sha256", "")) == 64
            and execution.get("payload_summary", {}).get("raw_body_returned") is False,
            "P2 supervisor approval writes side-effect execution receipt",
            f"execution={execution.get('id')}; result={execution.get('result')}",
        )
    )
    checks.append(
        check(
            isinstance(outbox_item, dict)
            and outbox_item.get("approval_id") == approval_id
            and outbox_item.get("status") == "succeeded"
            and outbox_item.get("execution_id") == execution.get("id")
            and outbox_item.get("attempt_count") == 1
            and outbox_item.get("lease_count") == 1
            and outbox_item.get("last_leased_by") == "sam"
            and str(outbox_item.get("last_lease_id", "")).startswith(f"{outbox_item.get('id')}:lease:")
            and outbox_item.get("lease_id") is None
            and outbox_item.get("leased_by") is None
            and outbox_item.get("lease_released_at")
            and outbox_item.get("raw_payload_returned") is False
            and outbox_item.get("payload_summary", {}).get("raw_body_returned") is False,
            "P2 supervisor approval drains outbox item into execution receipt",
            f"outbox={outbox_item.get('id')}; execution={execution.get('id')}",
        )
    )
    status, approved_workflows = get_json(f"{base_url}/api/workflow-runs?limit=5")
    approved_workflow = next((item for item in approved_workflows.get("workflow_runs", []) if approval_id in item.get("approval_ids", [])), {})
    checks.append(
        check(
            status == 200
            and approved_workflow.get("status") == "succeeded"
            and approved_workflow.get("stage") == "side_effect_executed"
            and execution.get("id") in approved_workflow.get("action_run_ids", [])
            and outbox_item.get("id") in approved_workflow.get("outbox_ids", [])
            and approved_workflow.get("waiting_on") is None,
            "P2 workflow checkpoint records approved side-effect execution",
            f"workflow={approved_workflow.get('id')}; execution={execution.get('id')}",
        )
    )
    status, replayed_approval = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": approval_id,
            "approver_id": "sam",
        },
    )
    checks.append(
        check(
            status == 200
            and replayed_approval.get("result") == "already_processed"
            and replayed_approval.get("execution", {}).get("id") == execution.get("id"),
            "P2 approval execution is idempotent",
            f"execution={replayed_approval.get('execution', {}).get('id')}; result={replayed_approval.get('result')}",
        )
    )
    status, approvals = get_json(f"{base_url}/api/approvals")
    checks.append(check(status == 200 and isinstance(approvals.get("approvals"), list), "P2 approvals list contract", f"approvals={len(approvals.get('approvals', []))}"))
    approval_list_item = next((item for item in approvals.get("approvals", []) if item.get("id") == approval_id), {})
    serialized_approvals = json.dumps(approvals)
    checks.append(
        check(
            approval_list_item.get("status") == "approved"
            and approval_list_item.get("approved_by") == "sam"
            and "payload" not in approval_list_item
            and approval_list_item.get("raw_payload_returned") is False
            and approval_list_item.get("payload_summary", {}).get("raw_body_returned") is False
            and approval_list_item.get("dry_run_preview", {}).get("raw_body_returned") is False
            and "Seller Market Blue" not in serialized_approvals
            and "Please remove the listing" not in serialized_approvals,
            "P2 approvals endpoint exposes sanitized governance records",
            f"approval={approval_list_item.get('id')}; status={approval_list_item.get('status')}",
        )
    )

    status, action_runs = get_json(f"{base_url}/api/action-runs?limit=5")
    serialized_action_runs = json.dumps(action_runs)
    checks.append(
        check(
            status == 200
            and isinstance(action_runs.get("action_runs"), list)
            and any(run.get("id") == execution.get("id") for run in action_runs.get("action_runs", []))
            and "Seller Market Blue" not in serialized_action_runs
            and "Please remove the listing" not in serialized_action_runs,
            "P2 action run ledger exposes execution receipts without raw notice bodies",
            f"runs={len(action_runs.get('action_runs', []))}; execution={execution.get('id')}",
        )
    )
    status, final_outbox = get_json(f"{base_url}/api/action-outbox?limit=5")
    final_outbox_items = final_outbox.get("action_outbox", [])
    final_outbox_item = next((item for item in final_outbox_items if item.get("approval_id") == approval_id), {})
    serialized_final_outbox = json.dumps(final_outbox)
    checks.append(
        check(
            status == 200
            and isinstance(final_outbox_items, list)
            and final_outbox_item.get("status") == "succeeded"
            and final_outbox_item.get("execution_id") == execution.get("id")
            and final_outbox_item.get("result") == "notice_sent"
            and "Seller Market Blue" not in serialized_final_outbox
            and "Please remove the listing" not in serialized_final_outbox,
            "P2 action outbox ledger exposes dispatch state without raw notice bodies",
            f"outbox={final_outbox_item.get('id')}; status={final_outbox_item.get('status')}",
        )
    )

    status, reject_case = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Escalate the Market Blue recalled product case.",
        },
    )
    reject_approval_id = reject_case["approvals"][0]["id"] if reject_case.get("approvals") else ""
    status, forbidden_reject = post_json(
        f"{base_url}/api/approval/reject",
        {
            "approval_id": reject_approval_id,
            "reviewer_id": "ivy",
            "reason": "operator should not be able to reject this action",
        },
    )
    checks.append(check(status == 403 and isinstance(forbidden_reject.get("error"), str), "P2 non-supervisor rejection error contract", json.dumps(forbidden_reject)))
    status, rejected = post_json(
        f"{base_url}/api/approval/reject",
        {
            "approval_id": reject_approval_id,
            "reviewer_id": "sam",
            "reason": "supervisor rejected controlled demo escalation",
        },
    )
    rejected_approval = rejected.get("approval", {})
    rejected_outbox = rejected.get("outbox_item", {})
    checks.append(
        check(
            status == 200
            and rejected.get("result") == "approval_rejected"
            and rejected.get("execution") is None
            and rejected_approval.get("status") == "rejected"
            and rejected_approval.get("review_status") == "rejected"
            and rejected_approval.get("rejected_by") == "sam"
            and rejected_approval.get("decision_reason_summary", {}).get("raw_decision_reason_returned") is False
            and "payload" not in rejected_approval
            and rejected_outbox.get("status") == "approval_rejected"
            and rejected_outbox.get("result") == "approval_rejected"
            and rejected_outbox.get("attempt_count") == 0,
            "P2 supervisor rejection closes approval without dispatch",
            f"approval={reject_approval_id}; outbox={rejected_outbox.get('id')}",
        )
    )
    status, rejected_workflows = get_json(f"{base_url}/api/workflow-runs?limit=10")
    rejected_workflow = next((item for item in rejected_workflows.get("workflow_runs", []) if reject_approval_id in item.get("approval_ids", [])), {})
    checks.append(
        check(
            status == 200
            and rejected_workflow.get("status") == "approval_rejected"
            and rejected_workflow.get("stage") == "approval_rejected"
            and rejected_outbox.get("id") in rejected_workflow.get("outbox_ids", [])
            and rejected_workflow.get("waiting_on") is None,
            "P2 workflow checkpoint records approval rejection",
            f"workflow={rejected_workflow.get('id')}; status={rejected_workflow.get('status')}",
        )
    )

    status, expire_case = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1002",
            "message": "Send the seller notice for Market Blue RX-900.",
        },
    )
    expire_approval_id = expire_case["approvals"][0]["id"] if expire_case.get("approvals") else ""
    status, expired = post_json(
        f"{base_url}/api/approval/expire",
        {
            "approval_id": expire_approval_id,
            "operator_id": "sam",
            "reason": "approval window expired in controlled demo",
        },
    )
    expired_approval = expired.get("approval", {})
    expired_outbox = expired.get("outbox_item", {})
    checks.append(
        check(
            status == 200
            and expired.get("result") == "approval_expired"
            and expired.get("execution") is None
            and expired_approval.get("status") == "expired"
            and expired_approval.get("review_status") == "expired"
            and expired_approval.get("expired_by") == "sam"
            and expired_approval.get("decision_reason_summary", {}).get("raw_decision_reason_returned") is False
            and expired_outbox.get("status") == "approval_expired"
            and expired_outbox.get("result") == "approval_expired"
            and expired_outbox.get("attempt_count") == 0,
            "P2 supervisor expiry closes approval without dispatch",
            f"approval={expire_approval_id}; outbox={expired_outbox.get('id')}",
        )
    )

    status, transient_case = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Send notice for Market Blue recalled product and simulate transient dispatch failure.",
        },
    )
    transient_approval_id = transient_case["approvals"][0]["id"] if transient_case.get("approvals") else ""
    status, transient_failure = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": transient_approval_id,
            "approver_id": "sam",
        },
    )
    transient_outbox = transient_failure.get("outbox_item", {})
    checks.append(
        check(
            status == 200
            and transient_failure.get("result") == "dispatch_failed"
            and transient_failure.get("execution") is None
            and transient_outbox.get("status") == "retryable_failure"
            and transient_outbox.get("attempt_count") == 1
            and transient_outbox.get("lease_count") == 1
            and transient_outbox.get("last_leased_by") == "sam"
            and transient_outbox.get("lease_id") is None
            and transient_outbox.get("lease_released_at")
            and transient_outbox.get("last_error", {}).get("retryable") is True
            and transient_outbox.get("last_error", {}).get("code") == "simulated_transient_tool_outage"
            and transient_outbox.get("next_attempt_at"),
            "P2 action outbox records retryable dispatch failure without side effect",
            f"outbox={transient_outbox.get('id')}; status={transient_outbox.get('status')}",
        )
    )
    transient_workflow = transient_case.get("workflow_run", {})
    status, failed_workflows = get_json(f"{base_url}/api/workflow-runs?limit=10")
    failed_workflow = next((item for item in failed_workflows.get("workflow_runs", []) if item.get("id") == transient_workflow.get("id")), {})
    checks.append(
        check(
            status == 200
            and failed_workflow.get("status") == "dispatch_retryable_failure"
            and failed_workflow.get("stage") == "waiting_for_retry"
            and transient_outbox.get("id") in failed_workflow.get("retryable_outbox_ids", [])
            and failed_workflow.get("waiting_on", {}).get("operator_action") == "retry_dispatch",
            "P2 workflow checkpoint records retryable dispatch failure",
            f"workflow={failed_workflow.get('id')}; retryable={failed_workflow.get('retryable_outbox_ids')}",
        )
    )

    status, transient_retry = post_json(
        f"{base_url}/api/action-outbox/retry",
        {
            "outbox_id": transient_outbox.get("id"),
            "operator_id": "sam",
        },
    )
    retry_outbox = transient_retry.get("outbox_item", {})
    retry_execution = transient_retry.get("execution", {})
    checks.append(
        check(
            status == 200
            and transient_retry.get("result") == "notice_sent"
            and isinstance(retry_execution, dict)
            and retry_execution.get("approval_id") == transient_approval_id
            and retry_outbox.get("status") == "succeeded"
            and retry_outbox.get("attempt_count") == 2
            and retry_outbox.get("lease_count") == 2
            and retry_outbox.get("last_leased_by") == "sam"
            and retry_outbox.get("lease_id") is None
            and retry_outbox.get("lease_released_at")
            and retry_outbox.get("last_error") is None
            and retry_outbox.get("execution_id") == retry_execution.get("id"),
            "P2 action outbox retry recovers a transient dispatch failure idempotently",
            f"outbox={retry_outbox.get('id')}; execution={retry_execution.get('id')}",
        )
    )
    status, retried_workflows = get_json(f"{base_url}/api/workflow-runs?limit=10")
    retried_workflow = next((item for item in retried_workflows.get("workflow_runs", []) if item.get("id") == transient_workflow.get("id")), {})
    checks.append(
        check(
            status == 200
            and retried_workflow.get("status") == "succeeded"
            and retried_workflow.get("stage") == "side_effect_executed"
            and retry_execution.get("id") in retried_workflow.get("action_run_ids", [])
            and not retried_workflow.get("retryable_outbox_ids")
            and retried_workflow.get("waiting_on") is None,
            "P2 workflow checkpoint records retry recovery",
            f"workflow={retried_workflow.get('id')}; execution={retry_execution.get('id')}",
        )
    )

    status, forbidden_retry = post_json(
        f"{base_url}/api/action-outbox/retry",
        {
            "outbox_id": transient_outbox.get("id"),
            "operator_id": "ivy",
        },
    )
    checks.append(check(status == 403 and isinstance(forbidden_retry.get("error"), str), "P2 non-supervisor outbox retry error contract", json.dumps(forbidden_retry)))

    status, permanent_case = post_json(
        f"{base_url}/api/agent",
        {
            "user_id": "ivy",
            "case_id": "case-1001",
            "message": "Send notice for Market Blue recalled product and simulate permanent dispatch failure.",
        },
    )
    permanent_approval_id = permanent_case["approvals"][0]["id"] if permanent_case.get("approvals") else ""
    status, permanent_first = post_json(
        f"{base_url}/api/approval/approve",
        {
            "approval_id": permanent_approval_id,
            "approver_id": "sam",
        },
    )
    permanent_outbox_id = permanent_first.get("outbox_item", {}).get("id")
    post_json(
        f"{base_url}/api/action-outbox/retry",
        {
            "outbox_id": permanent_outbox_id,
            "operator_id": "sam",
        },
    )
    status, permanent_dead_letter = post_json(
        f"{base_url}/api/action-outbox/retry",
        {
            "outbox_id": permanent_outbox_id,
            "operator_id": "sam",
        },
    )
    dead_letter_outbox = permanent_dead_letter.get("outbox_item", {})
    checks.append(
        check(
            status == 200
            and permanent_dead_letter.get("result") == "dispatch_dead_lettered"
            and permanent_dead_letter.get("execution") is None
            and dead_letter_outbox.get("status") == "dead_lettered"
            and dead_letter_outbox.get("attempt_count") == 3
            and dead_letter_outbox.get("lease_count") == 3
            and dead_letter_outbox.get("last_leased_by") == "sam"
            and dead_letter_outbox.get("lease_id") is None
            and dead_letter_outbox.get("lease_released_at")
            and dead_letter_outbox.get("last_error", {}).get("retryable") is False
            and dead_letter_outbox.get("dead_lettered_at")
            and dead_letter_outbox.get("dead_letter_reason") == "simulated_permanent_tool_outage",
            "P2 action outbox dead-letters repeated dispatch failures without side effect",
            f"outbox={dead_letter_outbox.get('id')}; status={dead_letter_outbox.get('status')}",
        )
    )
    permanent_workflow = permanent_case.get("workflow_run", {})
    status, dead_letter_workflows = get_json(f"{base_url}/api/workflow-runs?limit=10")
    dead_letter_workflow = next((item for item in dead_letter_workflows.get("workflow_runs", []) if item.get("id") == permanent_workflow.get("id")), {})
    checks.append(
        check(
            status == 200
            and dead_letter_workflow.get("status") == "dispatch_dead_lettered"
            and dead_letter_workflow.get("stage") == "dead_lettered"
            and dead_letter_outbox.get("id") in dead_letter_workflow.get("dead_lettered_outbox_ids", []),
            "P2 workflow checkpoint records dead-lettered dispatch",
            f"workflow={dead_letter_workflow.get('id')}; dead_lettered={dead_letter_workflow.get('dead_lettered_outbox_ids')}",
        )
    )

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
    checks.append(
        readiness_contract(
            base_url,
            "P3",
            "ai-reliability-incident-console",
            {
                "storage",
                "seed_data",
                "eval_state",
                "scenario_snapshot",
                "users",
                "releases",
                "incidents",
                "runbooks",
                "scenario_files",
            },
        )
    )

    status, users = get_json(f"{base_url}/api/users")
    checks.append(check(status == 200 and isinstance(users.get("users"), list) and users["users"], "P3 users list contract", f"users={len(users.get('users', []))}"))
    if users.get("users"):
        ok, detail = expect_types(users["users"][0], {"id": str, "name": str, "role": str})
        checks.append(check(ok, "P3 user shape contract", detail))

    status, maya_token = post_json(f"{base_url}/api/auth/demo-token", {"user_id": "maya"})
    maya_bearer = {"Authorization": f"Bearer {maya_token.get('token', '')}"}
    checks.append(
        check(
            status == 200
            and maya_token.get("token_type") == "Bearer"
            and maya_token.get("auth_policy") == "local_signed_demo_token_v1"
            and maya_token.get("auth_context", {}).get("user_id") == "maya"
            and maya_token.get("auth_context", {}).get("role") == "reliability_lead",
            "P3 local signed demo auth token contract",
            f"status={status}; policy={maya_token.get('auth_policy')}; subject={maya_token.get('auth_context', {}).get('user_id')}",
        )
    )
    status, triage_mismatch = post_json(
        f"{base_url}/api/triage",
        {
            "user_id": "nolan",
            "release_id": "rel-2026-06-01",
            "incident_id": "inc-2026-014",
        },
        headers=maya_bearer,
    )
    checks.append(
        check(
            status == 403 and "authenticated subject" in triage_mismatch.get("error", ""),
            "P3 bearer auth rejects identity mismatch",
            f"status={status}; error={triage_mismatch.get('error')}",
        )
    )

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
            "release_id": "rel-2026-06-01",
            "incident_id": "inc-2026-014",
        },
        headers=maya_bearer,
    )
    triage_keys = {"trace_id", "release", "incident", "decision", "failed_evals", "remediation_steps", "evidence", "latency_ms"}
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
            "latency_ms": (int, float),
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
        with tempfile.TemporaryDirectory(prefix="fde-api-contracts-") as temp_dir:
            state_root = Path(temp_dir)
            try:
                for service in service_list:
                    started.append(start_service(service, state_root))
                for service in service_list:
                    if not wait_for_health(service["health"]):
                        print(f"Service did not become healthy: {service['name']}", file=sys.stderr)
                        return 1

                checks.extend(project_1_contracts(project_1_url))
                checks.extend(project_2_contracts(project_2_url))
                checks.extend(project_3_contracts(project_3_url))
            finally:
                for process in started:
                    process.terminate()
                for process in started:
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        print(f"API contract check failed with exception: {exc}", file=sys.stderr)
        return 1

    for item in checks:
        status = "PASS" if item.passed else "FAIL"
        print(f"[{status}] {item.name}: {item.detail}")

    passed = sum(1 for item in checks if item.passed)
    total = len(checks)
    print(f"\nAPI contract checks: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
