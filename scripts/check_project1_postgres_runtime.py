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

    failures: list[str] = []
    if not postgres_dsn():
        return ["live Postgres runtime check requires COPILOT_POSTGRES_DSN"]

    try:
        with PostgresRepositorySession() as repo:
            users = repo.list_users()
            if not users:
                failures.append("Postgres runtime returned no users; apply migration and seed first")
            else:
                user = repo.get_user(users[0]["id"])
                if not user:
                    failures.append("Postgres runtime could not reload the first listed user")
                else:
                    repo.list_visible_documents(user)
                    repo.list_chunks(user["tenant_id"])
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
        print("Project 1 PostgreSQL runtime check passed: live tenant, user, document, chunk, trace, and audit queries succeeded.")
    else:
        print("Project 1 PostgreSQL runtime check passed: runtime provider switch, optional pool wiring, reset guard, and docs are aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
