from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPENDABOT = ROOT / ".github" / "dependabot.yml"

FORBIDDEN_DEPENDENCY_FILES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "uv.lock",
    "environment.yml",
    "environment.yaml",
    "conda.yml",
}

WEB_REMOTE_MARKERS = (
    "https://",
    "http://",
    "cdn.",
    "unpkg.com",
    "jsdelivr.net",
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]


def local_import_roots(files: list[Path]) -> set[str]:
    roots = {"copilot", "ops_agent", "reliability_console"}
    for path in files:
        if path.suffix == ".py":
            roots.add(path.stem)
    return roots


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue
            if node.module:
                roots.add(node.module.split(".", 1)[0])
    return roots


def check_python_imports(files: list[Path]) -> list[str]:
    failures: list[str] = []
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    allowed = stdlib | {"__future__"} | local_import_roots(files)
    for path in files:
        if path.suffix != ".py":
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            imports = imported_roots(path)
        except SyntaxError as exc:
            failures.append(f"{rel}: syntax error while checking imports: {exc}")
            continue
        external = sorted(root for root in imports if root not in allowed)
        if external:
            failures.append(f"{rel}: external Python import(s) not documented or allowed: {', '.join(external)}")
    return failures


def check_dependency_manifests(files: list[Path]) -> list[str]:
    failures: list[str] = []
    for path in files:
        if path.name in FORBIDDEN_DEPENDENCY_FILES:
            rel = path.relative_to(ROOT).as_posix()
            failures.append(f"{rel}: dependency manifest present; update the supply-chain policy before adding packages")
    return failures


def check_frontend_remote_dependencies(files: list[Path]) -> list[str]:
    failures: list[str] = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if "/web/" not in rel or path.suffix not in {".html", ".js", ".css"}:
            continue
        text = path.read_text(encoding="utf-8")
        matches = sorted(marker for marker in WEB_REMOTE_MARKERS if marker in text)
        if matches:
            failures.append(f"{rel}: remote frontend dependency marker(s): {', '.join(matches)}")
    return failures


def check_dockerfiles(files: list[Path]) -> list[str]:
    failures: list[str] = []
    dockerfiles = [path for path in files if path.name == "Dockerfile"]
    for path in dockerfiles:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        from_lines = [line.strip() for line in text.splitlines() if line.strip().upper().startswith("FROM ")]
        if not from_lines:
            failures.append(f"{rel}: missing FROM line")
            continue
        for line in from_lines:
            if "@sha256:" not in line:
                failures.append(f"{rel}: Docker base image must be digest-pinned: {line}")
        lower = text.lower()
        risky_markers = ["pip install", "curl |", "wget "]
        matches = [marker for marker in risky_markers if marker in lower]
        if matches:
            failures.append(f"{rel}: risky package/bootstrap marker(s): {', '.join(matches)}")
    return failures


def check_dependabot() -> list[str]:
    if not DEPENDABOT.exists():
        return ["missing .github/dependabot.yml"]
    text = DEPENDABOT.read_text(encoding="utf-8")
    required = [
        'package-ecosystem: "github-actions"',
        'package-ecosystem: "docker"',
        'directory: "/secure-enterprise-knowledge-copilot"',
        'directory: "/regulated-customer-operations-agent"',
        'directory: "/ai-reliability-incident-console"',
        'interval: "weekly"',
    ]
    return [f".github/dependabot.yml: missing {item}" for item in required if item not in text]


def main() -> int:
    files = tracked_files()
    failures: list[str] = []
    failures.extend(check_dependency_manifests(files))
    failures.extend(check_python_imports(files))
    failures.extend(check_frontend_remote_dependencies(files))
    failures.extend(check_dockerfiles(files))
    failures.extend(check_dependabot())

    if failures:
        print("Dependency surface check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Dependency surface check passed: stdlib-only Python, first-party frontend assets, pinned Docker bases, and Dependabot coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
