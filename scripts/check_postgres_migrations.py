from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "infra" / "postgres" / "migrations"
CORE_MIGRATION = MIGRATIONS_DIR / "001_core.sql"
POSTGRES_ADAPTER = (
    ROOT / "secure-enterprise-knowledge-copilot" / "src" / "copilot" / "postgres_repositories.py"
)

REQUIRED_TABLES = [
    "tenants",
    "users",
    "documents",
    "document_chunks",
    "traces",
    "audit_events",
    "eval_runs",
    "eval_cases",
    "cases",
    "tool_actions",
    "approval_requests",
]

RLS_TABLES = [
    "users",
    "documents",
    "document_chunks",
    "traces",
    "audit_events",
    "eval_runs",
    "eval_cases",
    "cases",
    "tool_actions",
    "approval_requests",
]

REQUIRED_MARKERS = [
    "create extension if not exists vector",
    "embedding vector(1536)",
    "content_tsv tsvector generated always",
    "using hnsw (embedding vector_cosine_ops)",
    "using gin (content_tsv)",
    "source_hash text not null",
    "unique (tenant_id, external_doc_id, source_hash)",
    "idempotency_key text not null",
    "unique (tenant_id, idempotency_key)",
    "current_setting('app.tenant_id')::uuid",
    "current_setting('app.tenant_slug', true)",
    "current_setting('app.role')",
    "current_setting('app.user_id')::uuid",
    "current_setting('app.environment', true)",
    "authorized_documents_select",
    "authorized_chunks_select",
    "tenant_lookup_by_slug",
    "supervisor_approval_select",
    "eval_state_isolation_runs",
    "eval_state_isolation_cases",
]

FORBIDDEN_MARKERS = [
    "drop table",
    "drop schema",
    "disable row level security",
    "bypassrls",
]


def normalized_sql(path: Path) -> str:
    text = path.read_text(encoding="utf-8").lower()
    text = re.sub(r"--.*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def migration_files() -> list[Path]:
    if not MIGRATIONS_DIR.exists():
        return []
    return sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql"))


def check_version_order(files: list[Path]) -> list[str]:
    failures: list[str] = []
    expected = 1
    for path in files:
        prefix = path.name.split("_", 1)[0]
        if int(prefix) != expected:
            failures.append(f"{path.relative_to(ROOT).as_posix()}: expected migration prefix {expected:03d}")
        expected += 1
    return failures


def check_core_migration(sql: str) -> list[str]:
    failures: list[str] = []
    for table in REQUIRED_TABLES:
        if f"create table if not exists {table}" not in sql:
            failures.append(f"001_core.sql: missing table {table}")
    for table in RLS_TABLES:
        if f"alter table {table} enable row level security" not in sql:
            failures.append(f"001_core.sql: missing RLS enablement for {table}")
    for marker in REQUIRED_MARKERS:
        if marker.lower() not in sql:
            failures.append(f"001_core.sql: missing marker {marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in sql:
            failures.append(f"001_core.sql: forbidden marker {marker}")
    return failures


def check_docs() -> list[str]:
    design = ROOT / "docs" / "postgres_pgvector_adapter_design.md"
    index = ROOT / "PROJECT_CONTENT_INDEX.md"
    readme = ROOT / "README.md"
    failures: list[str] = []
    for rel, path, markers in [
        (
            "docs/postgres_pgvector_adapter_design.md",
            design,
            ["infra/postgres/migrations/001_core.sql", "python -B scripts/dev.py postgres-migrations"],
        ),
        (
            "PROJECT_CONTENT_INDEX.md",
            index,
            ["infra/postgres/migrations/001_core.sql", "scripts/check_postgres_migrations.py"],
        ),
        (
            "README.md",
            readme,
            ["python -B scripts/dev.py postgres-migrations"],
        ),
    ]:
        if not path.exists():
            failures.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel}: missing {marker!r}")
    return failures


def check_adapter_contract() -> list[str]:
    if not POSTGRES_ADAPTER.exists():
        return ["missing secure-enterprise-knowledge-copilot/src/copilot/postgres_repositories.py"]
    text = POSTGRES_ADAPTER.read_text(encoding="utf-8")
    required_markers = [
        "class PostgresKnowledgeRepository",
        "provider = \"postgres\"",
        "select set_config('app.tenant_id'",
        "select set_config('app.tenant_slug'",
        "select set_config('app.role'",
        "select set_config('app.user_id'",
        "select set_config('app.environment'",
        "def list_visible_documents",
        "def list_chunks",
        "def replace_document_with_chunks",
        "insert into documents",
        "insert into document_chunks",
        "insert into traces",
        "insert into audit_events",
        "insert into eval_runs",
        "insert into eval_cases",
        "load_scenario_snapshot",
    ]
    return [
        f"postgres_repositories.py: missing adapter marker {marker}"
        for marker in required_markers
        if marker not in text
    ]


def main() -> int:
    failures: list[str] = []
    files = migration_files()
    if not files:
        failures.append("missing versioned PostgreSQL migrations under infra/postgres/migrations")
    if not CORE_MIGRATION.exists():
        failures.append("missing infra/postgres/migrations/001_core.sql")
    failures.extend(check_version_order(files))
    if CORE_MIGRATION.exists():
        failures.extend(check_core_migration(normalized_sql(CORE_MIGRATION)))
    failures.extend(check_adapter_contract())
    failures.extend(check_docs())

    if failures:
        print("PostgreSQL migration check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PostgreSQL migration check passed: core schema, pgvector indexes, RLS policies, eval isolation, idempotent action keys, and the Project 1 adapter contract are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
