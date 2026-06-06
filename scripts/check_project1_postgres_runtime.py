from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPILOT_ROOT = ROOT / "secure-enterprise-knowledge-copilot"
REPOSITORIES = COPILOT_ROOT / "src" / "copilot" / "repositories.py"
POSTGRES_REPOSITORIES = COPILOT_ROOT / "src" / "copilot" / "postgres_repositories.py"
APP = COPILOT_ROOT / "app.py"
ENV_EXAMPLE = ROOT / ".env.example"
README = ROOT / "README.md"
PRODUCTION_NOTES = ROOT / "docs" / "production_upgrade_notes.md"
POSTGRES_DESIGN = ROOT / "docs" / "postgres_pgvector_adapter_design.md"
INDEX = ROOT / "PROJECT_CONTENT_INDEX.md"


def require_text(path: Path, markers: list[str], label: str | None = None) -> list[str]:
    if not path.exists():
        return [f"missing {label or path.relative_to(ROOT).as_posix()}"]
    text = path.read_text(encoding="utf-8")
    rel = label or path.relative_to(ROOT).as_posix()
    return [f"{rel}: missing {marker!r}" for marker in markers if marker not in text]


def check_static_contract() -> list[str]:
    failures: list[str] = []
    failures.extend(
        require_text(
            REPOSITORIES,
            [
                "def repository_provider",
                'os.getenv("COPILOT_REPOSITORY", "json")',
                "def postgres_dsn",
                'os.getenv("COPILOT_POSTGRES_DSN"',
                "def postgres_pool_enabled",
                'os.getenv("COPILOT_POSTGRES_POOL", "0")',
            "class PostgresRepositorySession",
            "connect_psycopg",
            'importlib.import_module("psycopg")',
            'importlib.import_module("psycopg_pool")',
            "class PooledPostgresConnection",
            "count_potentially_blocked_chunks",
            'if provider == "postgres"',
            "PostgresKnowledgeRepository(self._connection, self.tenant_slug)",
            "COPILOT_REPOSITORY=postgres requires COPILOT_POSTGRES_DSN",
            ],
        )
    )
    failures.extend(
        require_text(
            POSTGRES_REPOSITORIES,
            [
                "class PostgresKnowledgeRepository",
                "def rollback",
                "def close",
                "select set_config('app.tenant_id'",
                "select set_config('app.tenant_slug'",
                "def list_retrieval_candidates",
                "postgres_hybrid_sql_v1",
                "websearch_to_tsquery",
                "embedding <=> %s::vector",
                "def count_potentially_blocked_chunks",
                "select project1_denied_relevant_chunk_count",
            ],
        )
    )
    failures.extend(
        require_text(
            APP,
            [
                'os.getenv("COPILOT_REPOSITORY", "json")',
                'if repository_provider == "json"',
                "Ignoring --reset because COPILOT_REPOSITORY=",
            ],
        )
    )
    failures.extend(
        require_text(
            ENV_EXAMPLE,
            [
                "COPILOT_REPOSITORY=json",
                "COPILOT_TENANT_SLUG=acme",
                "COPILOT_POSTGRES_DSN=",
                "COPILOT_POSTGRES_POOL=0",
            ],
        )
    )
    doc_markers = [
        "python -B scripts/dev.py postgres-runtime",
        "COPILOT_REPOSITORY=postgres",
        "COPILOT_POSTGRES_DSN",
        "COPILOT_POSTGRES_POOL",
    ]
    for path in [README, PRODUCTION_NOTES, POSTGRES_DESIGN, INDEX]:
        failures.extend(require_text(path, doc_markers))
    return failures


def check_live_runtime() -> list[str]:
    sys.path.insert(0, str(COPILOT_ROOT / "src"))
    from copilot.repositories import PostgresRepositorySession, postgres_dsn
    from copilot.retrieval import tokenize

    failures: list[str] = []
    if not postgres_dsn():
        return ["live Postgres runtime check requires COPILOT_POSTGRES_DSN"]

    try:
        with PostgresRepositorySession() as repo:
            users = {user["id"]: user for user in repo.list_users()}
            for required_user in ["alice", "morgan", "avery"]:
                if required_user not in users:
                    failures.append(f"Postgres runtime missing seeded user {required_user}")
            alice = repo.get_user("alice")
            morgan = repo.get_user("morgan")
            if not alice or not morgan:
                return failures or ["Postgres runtime could not load seeded Alice/Morgan users"]

            alice_docs = {doc["id"] for doc in repo.list_visible_documents(alice)}
            if "finance-retention-plan-2026" in alice_docs:
                failures.append("RLS violation: Alice can see finance-retention-plan-2026 in visible documents")
            if "hr-remote-work-2026" not in alice_docs:
                failures.append("RLS setup error: Alice cannot see expected internal HR document")

            alice_chunks = {chunk["doc_id"] for chunk in repo.list_chunks(alice["tenant_id"])}
            if "finance-retention-plan-2026" in alice_chunks:
                failures.append("RLS violation: Alice can read finance-retention-plan-2026 chunks")

            finance_tokens = tokenize("What is the finance retention plan?")
            alice_candidates = repo.list_retrieval_candidates(
                alice,
                "How many days per week can employees work remotely?",
                tokenize("How many days per week can employees work remotely?"),
                [0.0] * 1536,
                10,
            )
            if alice_candidates.get("candidate_strategy") != "postgres_hybrid_sql_v1":
                failures.append("Postgres runtime retrieval candidates should use postgres_hybrid_sql_v1")
            if "hr-remote-work-2026" not in {chunk["doc_id"] for chunk in alice_candidates.get("chunks", [])}:
                failures.append("Postgres hybrid candidates missed the expected HR remote-work document")

            alice_blocked = repo.count_potentially_blocked_chunks(alice, finance_tokens)
            if alice_blocked < 1:
                failures.append("Denied-evidence count failed: Alice finance query should report at least one blocked chunk")

            morgan_docs = {doc["id"] for doc in repo.list_visible_documents(morgan)}
            if "finance-retention-plan-2026" not in morgan_docs:
                failures.append("RLS setup error: Morgan cannot see finance-retention-plan-2026")
            morgan_blocked = repo.count_potentially_blocked_chunks(morgan, finance_tokens)
            if morgan_blocked != 0:
                failures.append("Denied-evidence count failed: Morgan finance query should not report blocked finance chunks")

            repo.list_traces(limit=1)
            repo.list_audit_events(limit=1)
    except Exception as exc:
        failures.append(f"live Postgres runtime check failed: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Project 1 PostgreSQL runtime wiring.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use COPILOT_POSTGRES_DSN to verify a real PostgreSQL/pgvector runtime with seeded data.",
    )
    args = parser.parse_args()

    failures = check_static_contract()
    if args.live:
        failures.extend(check_live_runtime())

    if failures:
        print("Project 1 PostgreSQL runtime check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    if args.live:
        print("Project 1 PostgreSQL runtime check passed: live tenant, RLS, denied-evidence count, trace, and audit queries succeeded.")
    else:
        print("Project 1 PostgreSQL runtime check passed: runtime provider switch, optional pool wiring, reset guard, and docs are aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
