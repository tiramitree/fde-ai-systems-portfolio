from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "secure-enterprise-knowledge-copilot"
SEED_PATH = PROJECT_ROOT / "data" / "seed_documents.json"
SRC_PATH = PROJECT_ROOT / "src"
OUTPUT_PATH = ROOT / "infra" / "postgres" / "seeds" / "001_project1_demo.sql"
UUID_NAMESPACE = uuid.UUID("9f83868a-75f0-4c18-9c6d-4e0ea87f0a41")

sys.path.insert(0, str(SRC_PATH))

from copilot.storage import build_seed_chunks, prepare_seed_document  # noqa: E402


def stable_uuid(kind: str, value: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, f"{kind}:{value}"))


def sql_literal(value: Any) -> str:
    if value is None:
        return "null"
    return "'" + str(value).replace("'", "''") + "'"


def text_array(values: list[str]) -> str:
    if not values:
        return "array[]::text[]"
    return "array[" + ", ".join(sql_literal(value) for value in values) + "]::text[]"


def jsonb_literal(payload: dict) -> str:
    text = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return f"{sql_literal(text)}::jsonb"


def vector_literal(values: list[float]) -> str:
    vector_text = "[" + ",".join(str(float(value)) for value in values) + "]"
    return f"{sql_literal(vector_text)}::vector"


def tenant_display_name(slug: str) -> str:
    return f"{slug.upper()} Demo Tenant"


def emit_tenants(seed: dict) -> list[str]:
    tenant_ids = sorted({user["tenant_id"] for user in seed["users"]} | {doc["tenant_id"] for doc in seed["documents"]})
    lines: list[str] = []
    for tenant_id in tenant_ids:
        tenant_uuid = stable_uuid("tenant", tenant_id)
        lines.append(
            "insert into tenants (id, slug, name)\n"
            f"values ({sql_literal(tenant_uuid)}::uuid, {sql_literal(tenant_id)}, {sql_literal(tenant_display_name(tenant_id))})\n"
            "on conflict (slug) do update set name = excluded.name;"
        )
    return lines


def emit_users(seed: dict) -> list[str]:
    lines: list[str] = []
    for user in sorted(seed["users"], key=lambda item: (item["tenant_id"], item["id"])):
        tenant_uuid = stable_uuid("tenant", user["tenant_id"])
        user_uuid = stable_uuid("user", f"{tenant_uuid}:{user['id']}")
        lines.append(
            "insert into users (id, tenant_id, external_user_id, display_name, role, group_ids)\n"
            "values ("
            f"{sql_literal(user_uuid)}::uuid, "
            f"{sql_literal(tenant_uuid)}::uuid, "
            f"{sql_literal(user['id'])}, "
            f"{sql_literal(user['name'])}, "
            f"{sql_literal(user['role'])}, "
            f"{text_array(user.get('group_ids', []))}"
            ")\n"
            "on conflict (tenant_id, external_user_id) do update set\n"
            "  display_name = excluded.display_name,\n"
            "  role = excluded.role,\n"
            "  group_ids = excluded.group_ids;"
        )
    return lines


def emit_documents_and_chunks(seed: dict) -> list[str]:
    lines: list[str] = []
    prepared_documents = [prepare_seed_document(doc) for doc in seed["documents"]]
    for doc in sorted(prepared_documents, key=lambda item: (item["tenant_id"], item["id"])):
        tenant_uuid = stable_uuid("tenant", doc["tenant_id"])
        doc_uuid = stable_uuid("document", f"{tenant_uuid}:{doc['id']}")
        document_metadata = {
            "allowed_groups": doc.get("allowed_groups", []),
            "source_acl_principals": doc.get("source_acl_principals", []),
            "source_acl_version": doc.get("source_acl_version", ""),
            "source_acl_permission_id": doc.get("source_acl_permission_id", ""),
            "source_acl_principal_count": doc.get("source_acl_principal_count", 0),
            "source_lifecycle_state": doc.get("source_lifecycle_state", "active"),
            "superseded_by": doc.get("superseded_by", ""),
            "parser_name": doc["parser_name"],
            "parser_contract_version": doc["parser_contract_version"],
            "parser_metadata": doc["parser_metadata"],
            "parser_warnings": doc["parser_warnings"],
            "parser_warning_count": doc["parser_warning_count"],
            "source_scan": doc["source_scan"],
            "source_connector": doc["source_connector"],
            "external_id": doc["external_id"],
            "acl_source": doc["acl_source"],
            "sync_cursor": doc["sync_cursor"],
            "allowed_roles_source": doc["allowed_roles_source"],
        }
        lines.append(
            "insert into documents (\n"
            "  id, tenant_id, external_doc_id, title, source_uri, source_mime,\n"
            "  source_hash, sensitivity, allowed_roles, version, updated_at, metadata\n"
            ")\n"
            "values ("
            f"{sql_literal(doc_uuid)}::uuid, "
            f"{sql_literal(tenant_uuid)}::uuid, "
            f"{sql_literal(doc['id'])}, "
            f"{sql_literal(doc['title'])}, "
            f"{sql_literal(doc['source_url'])}, "
            f"{sql_literal(doc['source_mime'])}, "
            f"{sql_literal(doc['source_hash'])}, "
            f"{sql_literal(doc['classification'])}, "
            f"{text_array(doc['allowed_roles'])}, "
            f"{sql_literal(doc['version'])}, "
            f"{sql_literal(doc['updated_at'])}::timestamptz, "
            f"{jsonb_literal(document_metadata)}"
            ")\n"
            "on conflict (id) do update set\n"
            "  title = excluded.title,\n"
            "  source_uri = excluded.source_uri,\n"
            "  source_mime = excluded.source_mime,\n"
            "  source_hash = excluded.source_hash,\n"
            "  sensitivity = excluded.sensitivity,\n"
            "  allowed_roles = excluded.allowed_roles,\n"
            "  version = excluded.version,\n"
            "  updated_at = excluded.updated_at,\n"
            "  metadata = excluded.metadata;"
        )
        lines.append(f"delete from document_chunks where document_id = {sql_literal(doc_uuid)}::uuid;")
        for chunk in build_seed_chunks(doc):
            index = int(chunk["chunk_index"])
            external_chunk_id = chunk["id"]
            chunk_uuid = stable_uuid("chunk", f"{doc_uuid}:{external_chunk_id}")
            metadata = {
                "external_chunk_id": external_chunk_id,
                "allowed_groups": chunk.get("allowed_groups", []),
                "source_acl_principals": chunk.get("source_acl_principals", []),
                "source_acl_version": chunk.get("source_acl_version", ""),
                "source_acl_permission_id": chunk.get("source_acl_permission_id", ""),
                "source_acl_principal_count": chunk.get("source_acl_principal_count", 0),
                "source_lifecycle_state": chunk.get("source_lifecycle_state", "active"),
                "superseded_by": chunk.get("superseded_by", ""),
                "source_mime": chunk["source_mime"],
                "source_hash": chunk["source_hash"],
                "parser_name": chunk["parser_name"],
                "parser_contract_version": chunk["parser_contract_version"],
                "parser_metadata": chunk["parser_metadata"],
                "parser_warnings": chunk["parser_warnings"],
                "parser_warning_count": chunk["parser_warning_count"],
                "source_scan": chunk["source_scan"],
                "source_connector": chunk["source_connector"],
                "external_id": chunk["external_id"],
                "acl_source": chunk["acl_source"],
                "sync_cursor": chunk["sync_cursor"],
                "allowed_roles_source": chunk["allowed_roles_source"],
                "updated_at": chunk["updated_at"],
                "source_span": chunk["source_span"],
                "chunk_source_span_unit": chunk["chunk_source_span_unit"],
                "embedding_model": chunk["embedding_model"],
                "embedding_dimensions": chunk["embedding_dimensions"],
                "embedding_norm": chunk["embedding_norm"],
            }
            lines.append(
                "insert into document_chunks (\n"
                "  id, tenant_id, document_id, chunk_index, content, embedding, metadata\n"
                ")\n"
                "values ("
                f"{sql_literal(chunk_uuid)}::uuid, "
                f"{sql_literal(tenant_uuid)}::uuid, "
                f"{sql_literal(doc_uuid)}::uuid, "
                f"{index}, "
                f"{sql_literal(chunk['text'])}, "
                f"{vector_literal(chunk['embedding'])}, "
                f"{jsonb_literal(metadata)}"
                ");"
            )
    return lines


def generate_sql() -> str:
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    sections = [
        "-- 001_project1_demo.sql",
        "-- Deterministic Project 1 demo seed for the PostgreSQL/pgvector production path.",
        "-- Generated from secure-enterprise-knowledge-copilot/data/seed_documents.json.",
        "-- Run after infra/postgres/migrations/001_core.sql as a migration-owner or seed role.",
        "",
        "begin;",
        "",
        *emit_tenants(seed),
        "",
        *emit_users(seed),
        "",
        *emit_documents_and_chunks(seed),
        "",
        "commit;",
        "",
    ]
    return "\n".join(sections)


def check_output(expected: str) -> int:
    if not OUTPUT_PATH.exists():
        print(f"Missing {OUTPUT_PATH.relative_to(ROOT).as_posix()}")
        return 1
    actual = OUTPUT_PATH.read_text(encoding="utf-8")
    if actual != expected:
        print(f"{OUTPUT_PATH.relative_to(ROOT).as_posix()} is stale. Run:")
        print("python -B scripts/generate_postgres_seed.py --write")
        return 1
    print("PostgreSQL seed artifact check passed: Project 1 demo seed SQL matches seed_documents.json.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or check deterministic Project 1 PostgreSQL seed SQL.")
    parser.add_argument("--write", action="store_true", help="Write infra/postgres/seeds/001_project1_demo.sql")
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in SQL is stale")
    args = parser.parse_args()

    sql = generate_sql()
    if args.write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(sql, encoding="utf-8")
        print(f"Wrote {OUTPUT_PATH.relative_to(ROOT).as_posix()}")
        return 0
    if args.check:
        return check_output(sql)
    print(sql)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
