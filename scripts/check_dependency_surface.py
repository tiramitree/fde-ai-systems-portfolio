from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
SUPPLY_CHAIN_DOC = ROOT / "docs" / "supply_chain_security.md"
GITHUB_SETTINGS_DOC = ROOT / "docs" / "github_repository_settings.md"
DEPENDABOT_SECRET_SCANNING_DOC = ROOT / "docs" / "dependabot_secret_scanning_verification_examples.md"
STALE_DEPENDABOT_ALERT_EVIDENCE_DOC = ROOT / "docs" / "stale_dependabot_alert_evidence_examples.md"

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
    failures = [f".github/dependabot.yml: missing {item}" for item in required if item not in text]
    if text.count('dependency-name: "python"') < 3:
        failures.append('.github/dependabot.yml: missing Python Docker ignore rules for all service images')
    if text.count('version-update:semver-minor') < 3:
        failures.append('.github/dependabot.yml: missing Docker semver-minor ignore rules for all service images')
    if text.count('version-update:semver-major') < 3:
        failures.append('.github/dependabot.yml: missing Docker semver-major ignore rules for all service images')
    return failures


def check_policy_docs() -> list[str]:
    failures: list[str] = []
    expected_files = [
        ("docs/supply_chain_security.md", SUPPLY_CHAIN_DOC),
        ("docs/github_repository_settings.md", GITHUB_SETTINGS_DOC),
        ("docs/dependabot_secret_scanning_verification_examples.md", DEPENDABOT_SECRET_SCANNING_DOC),
        ("docs/stale_dependabot_alert_evidence_examples.md", STALE_DEPENDABOT_ALERT_EVIDENCE_DOC),
    ]
    for rel_path, path in expected_files:
        if not path.exists():
            failures.append(f"missing {rel_path}")

    if failures:
        return failures

    supply_chain = SUPPLY_CHAIN_DOC.read_text(encoding="utf-8")
    github_settings = GITHUB_SETTINGS_DOC.read_text(encoding="utf-8")
    verification = DEPENDABOT_SECRET_SCANNING_DOC.read_text(encoding="utf-8")
    stale_evidence = STALE_DEPENDABOT_ALERT_EVIDENCE_DOC.read_text(encoding="utf-8")
    expectations = [
        ("docs/supply_chain_security.md", supply_chain, "docs/dependabot_secret_scanning_verification_examples.md"),
        ("docs/supply_chain_security.md", supply_chain, "docs/stale_dependabot_alert_evidence_examples.md"),
        ("docs/github_repository_settings.md", github_settings, "docs/dependabot_secret_scanning_verification_examples.md"),
        ("docs/dependabot_secret_scanning_verification_examples.md", verification, ".github/dependabot.yml"),
        ("docs/dependabot_secret_scanning_verification_examples.md", verification, "docs/stale_dependabot_alert_evidence_examples.md"),
        ("docs/dependabot_secret_scanning_verification_examples.md", verification, "python -B scripts/dev.py dependency-surface"),
        ("docs/dependabot_secret_scanning_verification_examples.md", verification, "Do not claim Dependabot or secret-scanning setup is complete until public/account-level evidence confirms it"),
        ("docs/stale_dependabot_alert_evidence_examples.md", stale_evidence, "python -B scripts/dev.py dependency-surface"),
        ("docs/stale_dependabot_alert_evidence_examples.md", stale_evidence, "Do not claim Dependabot or secret-scanning alert evidence is current until GitHub readiness or authenticated evidence confirms it"),
    ]
    for rel_path, text, phrase in expectations:
        if phrase not in text:
            failures.append(f"{rel_path}: missing {phrase!r}")
    return failures


def main() -> int:
    files = tracked_files()
    failures: list[str] = []
    failures.extend(check_dependency_manifests(files))
    failures.extend(check_python_imports(files))
    failures.extend(check_frontend_remote_dependencies(files))
    failures.extend(check_dockerfiles(files))
    failures.extend(check_dependabot())
    failures.extend(check_policy_docs())

    if failures:
        print("Dependency surface check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Dependency surface check passed: stdlib-only Python, first-party frontend assets, pinned Docker bases, and Dependabot coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
