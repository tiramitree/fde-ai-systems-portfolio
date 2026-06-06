from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTGRES_COMPOSE = ROOT / "docker-compose.postgres.yml"
ROLE_INIT = ROOT / "infra" / "postgres" / "init" / "000_project1_runtime_roles.sql"
GRANTS_INIT = ROOT / "infra" / "postgres" / "init" / "003_project1_runtime_grants.sql"
MIGRATION = ROOT / "infra" / "postgres" / "migrations" / "001_core.sql"
SEED = ROOT / "infra" / "postgres" / "seeds" / "001_project1_demo.sql"
README = ROOT / "README.md"
POSTGRES_DESIGN = ROOT / "docs" / "postgres_pgvector_adapter_design.md"
CONTAINER_DOC = ROOT / "docs" / "container_release_hygiene.md"
DOCKER_RUNTIME_DOC = ROOT / "docs" / "docker_runtime_evidence_checklist.md"
PRODUCTION_NOTES = ROOT / "docs" / "production_upgrade_notes.md"
INDEX = ROOT / "PROJECT_CONTENT_INDEX.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def require_file(path: Path, failures: list[str]) -> bool:
    if not path.exists():
        failures.append(f"missing {path.relative_to(ROOT).as_posix()}")
        return False
    return True


def require_contains(path: Path, markers: list[str], failures: list[str]) -> None:
    if not require_file(path, failures):
        return
    body = text(path)
    rel = path.relative_to(ROOT).as_posix()
    for marker in markers:
        if marker not in body:
            failures.append(f"{rel}: missing `{marker}`")


def require_absent(path: Path, markers: list[str], failures: list[str]) -> None:
    if not path.exists():
        return
    body = text(path)
    rel = path.relative_to(ROOT).as_posix()
    for marker in markers:
        if marker in body:
            failures.append(f"{rel}: forbidden marker `{marker}`")


def check_compose(failures: list[str]) -> None:
    require_contains(
        POSTGRES_COMPOSE,
        [
            "name: fde-ai-systems-postgres",
            "project1-postgres:",
            "image: pgvector/pgvector:0.8.1-pg17-trixie@sha256:cab20e476214dfd8f2456b8bacd502fb2f8dfc3d899808ab92fdf6355c0889a8",
            "POSTGRES_DB: fde_portfolio",
            "POSTGRES_USER: fde_migrator",
            "POSTGRES_PASSWORD: fde_migrator_demo_password",
            '"${COPILOT_POSTGRES_PORT:-55432}:5432"',
            "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}",
            "project1_runtime_roles",
            "target: /docker-entrypoint-initdb.d/000_project1_runtime_roles.sql",
            "project1_core_migration",
            "target: /docker-entrypoint-initdb.d/001_core.sql",
            "project1_demo_seed",
            "target: /docker-entrypoint-initdb.d/002_project1_demo_seed.sql",
            "project1_runtime_grants",
            "target: /docker-entrypoint-initdb.d/003_project1_runtime_grants.sql",
            "file: ./infra/postgres/init/000_project1_runtime_roles.sql",
            "file: ./infra/postgres/migrations/001_core.sql",
            "file: ./infra/postgres/seeds/001_project1_demo.sql",
            "file: ./infra/postgres/init/003_project1_runtime_grants.sql",
        ],
        failures,
    )
    require_absent(
        POSTGRES_COMPOSE,
        [
            "latest",
            "privileged:",
            "network_mode: host",
            "/var/run/docker.sock",
            "env_file:",
            "COPILOT_POSTGRES_DSN:",
            "OPENAI_API" + "_KEY:",
        ],
        failures,
    )


def check_role_files(failures: list[str]) -> None:
    require_contains(
        ROLE_INIT,
        [
            "create role fde_app login password 'fde_app_demo_password'",
            "alter role fde_app with login password 'fde_app_demo_password'",
            "alter role fde_app set row_security = on",
        ],
        failures,
    )
    require_contains(
        GRANTS_INIT,
        [
            "grant connect on database fde_portfolio to fde_app",
            "grant usage on schema public to fde_app",
            "grant select, insert, update, delete on all tables in schema public to fde_app",
            "grant usage, select on all sequences in schema public to fde_app",
        ],
        failures,
    )
    require_absent(ROLE_INIT, ["bypassrls", "superuser"], failures)
    require_absent(GRANTS_INIT, ["bypassrls", "superuser"], failures)


def check_supporting_artifacts(failures: list[str]) -> None:
    require_file(MIGRATION, failures)
    require_file(SEED, failures)
    doc_markers = [
        "docker-compose.postgres.yml",
        "python -B scripts/dev.py postgres-compose",
        "COPILOT_POSTGRES_DSN",
        "fde_app",
        "fde_app_demo_password",
        "55432",
    ]
    for path in [README, POSTGRES_DESIGN, CONTAINER_DOC, DOCKER_RUNTIME_DOC, PRODUCTION_NOTES, INDEX]:
        require_contains(path, doc_markers, failures)


def main() -> int:
    failures: list[str] = []
    check_compose(failures)
    check_role_files(failures)
    check_supporting_artifacts(failures)
    if failures:
        print("PostgreSQL compose check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PostgreSQL compose check passed: pgvector compose image, init order, role separation, seed wiring, healthcheck, and docs are aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
