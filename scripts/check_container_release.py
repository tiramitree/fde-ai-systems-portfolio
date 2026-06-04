from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.yml"
DOCKER_RUNTIME_EVIDENCE_CHECKLIST = ROOT / "docs" / "docker_runtime_evidence_checklist.md"
DOCKER_RUNTIME_FAILURE_EXAMPLES = ROOT / "docs" / "docker_runtime_failure_examples.md"

PROJECTS = [
    {
        "name": "secure-enterprise-knowledge-copilot",
        "path": "secure-enterprise-knowledge-copilot",
        "port": "8765",
        "env_markers": ["COPILOT_MODEL_PROVIDER: ${COPILOT_MODEL_PROVIDER:-local}"],
    },
    {
        "name": "regulated-customer-operations-agent",
        "path": "regulated-customer-operations-agent",
        "port": "8770",
        "env_markers": ["OPS_AGENT_MODEL_ROUTER: ${OPS_AGENT_MODEL_ROUTER:-local}"],
    },
    {
        "name": "ai-reliability-incident-console",
        "path": "ai-reliability-incident-console",
        "port": "8780",
        "env_markers": [],
    },
]

REQUIRED_DOCKERIGNORE_PATTERNS = {
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.log",
    "data/runtime_state.json",
    "data/eval_runtime_state.json",
    "data/runtime_state.tmp",
    "data/*.sqlite",
    "data/*.sqlite-journal",
    "data/write-test.txt",
    ".env",
    ".venv/",
    "venv/",
}

FORBIDDEN_CONTAINER_MARKERS = (
    "OPENAI_API_KEY=",
    "ARG OPENAI_API_KEY",
    "ENV OPENAI_API_KEY",
    "COPY .env",
    "ADD .env",
    "privileged:",
    "network_mode: host",
    "/var/run/docker.sock",
    "env_file:",
    "volumes:",
)


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def dockerignore_patterns(path: Path) -> set[str]:
    patterns = set()
    for raw_line in normalized_text(path).splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            patterns.add(line)
    return patterns


def require_contains(text: str, needle: str, location: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"{location}: missing `{needle}`")


def check_dockerfile(project: dict[str, str]) -> list[str]:
    failures: list[str] = []
    dockerfile = ROOT / project["path"] / "Dockerfile"
    rel = dockerfile.relative_to(ROOT).as_posix()
    if not dockerfile.exists():
        return [f"missing {rel}"]

    text = normalized_text(dockerfile)
    require_contains(text, "FROM python:3.12-slim@sha256:", rel, failures)
    require_contains(text, "ENV PYTHONDONTWRITEBYTECODE=1", rel, failures)
    require_contains(text, "ENV PYTHONUNBUFFERED=1", rel, failures)
    require_contains(text, "WORKDIR /app", rel, failures)
    require_contains(text, "COPY . /app", rel, failures)
    require_contains(text, f"EXPOSE {project['port']}", rel, failures)
    require_contains(
        text,
        f'CMD ["python", "-B", "app.py", "--reset", "--host", "0.0.0.0", "--port", "{project["port"]}"]',
        rel,
        failures,
    )

    lowered = text.lower()
    risky_markers = ("pip install", "curl ", "wget ", "apt-get", "apk add")
    for marker in risky_markers:
        if marker in lowered:
            failures.append(f"{rel}: image build includes package/bootstrap marker `{marker.strip()}`")

    for marker in FORBIDDEN_CONTAINER_MARKERS:
        if marker in text:
            failures.append(f"{rel}: forbidden secret/host marker `{marker}`")
    return failures


def check_dockerignore(project: dict[str, str]) -> list[str]:
    failures: list[str] = []
    ignore_file = ROOT / project["path"] / ".dockerignore"
    rel = ignore_file.relative_to(ROOT).as_posix()
    if not ignore_file.exists():
        return [f"missing {rel}"]

    patterns = dockerignore_patterns(ignore_file)
    missing = sorted(REQUIRED_DOCKERIGNORE_PATTERNS - patterns)
    for pattern in missing:
        failures.append(f"{rel}: missing build-context ignore pattern `{pattern}`")
    return failures


def check_compose() -> list[str]:
    failures: list[str] = []
    if not COMPOSE.exists():
        return ["missing docker-compose.yml"]

    text = normalized_text(COMPOSE)
    rel = COMPOSE.relative_to(ROOT).as_posix()
    require_contains(text, "services:", rel, failures)
    require_contains(text, "OPENAI_MODEL: ${OPENAI_MODEL:-gpt-5.2}", rel, failures)
    require_contains(text, "OPENAI_API_KEY: ${OPENAI_API_KEY:-}", rel, failures)

    for project in PROJECTS:
        name = project["name"]
        port = project["port"]
        path = project["path"]
        require_contains(text, f"  {name}:\n", rel, failures)
        require_contains(text, f"      context: ./{path}", rel, failures)
        for env_marker in project["env_markers"]:
            require_contains(text, f"      {env_marker}", rel, failures)
        require_contains(text, f'      - "{port}:{port}"', rel, failures)
        require_contains(
            text,
            f'    command: ["python", "-B", "app.py", "--reset", "--host", "0.0.0.0", "--port", "{port}"]',
            rel,
            failures,
        )
        require_contains(
            text,
            f"urllib.request.urlopen('http://127.0.0.1:{port}/api/health', timeout=3)",
            rel,
            failures,
        )

    for marker in FORBIDDEN_CONTAINER_MARKERS:
        if marker in text and marker != "OPENAI_API_KEY=":
            failures.append(f"{rel}: forbidden secret/host marker `{marker}`")
    return failures


def check_runtime_evidence_checklist() -> list[str]:
    failures: list[str] = []
    if not DOCKER_RUNTIME_EVIDENCE_CHECKLIST.exists():
        return ["missing docs/docker_runtime_evidence_checklist.md"]

    text = normalized_text(DOCKER_RUNTIME_EVIDENCE_CHECKLIST)
    required = [
        "python -B scripts/dev.py container-release",
        "python -B scripts/dev.py docker-runtime",
        "static config evidence",
        "runtime evidence only on a Docker-enabled machine",
        "Docker CLI version output",
        "Docker Compose version output",
        "Smoke tests: 13/13 passed",
        "Docker runtime check passed",
        "Do not claim Docker runtime verification until",
        "Do not commit generated container logs",
    ]
    for marker in required:
        require_contains(text, marker, "docs/docker_runtime_evidence_checklist.md", failures)
    return failures


def check_runtime_failure_examples() -> list[str]:
    failures: list[str] = []
    if not DOCKER_RUNTIME_FAILURE_EXAMPLES.exists():
        return ["missing docs/docker_runtime_failure_examples.md"]

    text = normalized_text(DOCKER_RUNTIME_FAILURE_EXAMPLES)
    required = [
        "python -B scripts/dev.py container-release",
        "python -B scripts/dev.py docker-runtime",
        "`python -B scripts/dev.py quality` must not require Docker",
        "Missing Docker Daemon",
        "Compose Command Mismatch",
        "Unhealthy Service",
        "Stale Generated Logs",
        "Port Conflicts",
        "Do not claim Docker runtime proof",
        "Do not commit generated container logs",
    ]
    for marker in required:
        require_contains(text, marker, "docs/docker_runtime_failure_examples.md", failures)
    return failures


def main() -> int:
    failures: list[str] = []
    failures.extend(check_compose())
    failures.extend(check_runtime_evidence_checklist())
    failures.extend(check_runtime_failure_examples())
    for project in PROJECTS:
        failures.extend(check_dockerfile(project))
        failures.extend(check_dockerignore(project))

    if failures:
        print("Container release check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Container release check passed: compose, Dockerfiles, health checks, ports, commands, "
        "and build-context ignores are aligned."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
