from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"

ALLOWED_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/upload-artifact",
}

APPROVED_ACTION_REFS = {
    "actions/checkout": {"v6"},
    "actions/setup-python": {"v6"},
    "actions/upload-artifact": {"v7"},
}

FORBIDDEN_TEXT_PATTERNS = {
    "dangerous pull_request_target trigger": r"\bpull_request_target\s*:",
    "workflow_run trigger can chain privileged workflows": r"\bworkflow_run\s*:",
    "write-all token permission": r"\bpermissions\s*:\s*write-all\b",
    "explicit write token permission": (
        r"\b(actions|checks|contents|deployments|discussions|id-token|issues|packages|pages|"
        r"pull-requests|repository-projects|security-events|statuses)\s*:\s*write\b"
    ),
    "secret context referenced from workflow": r"\bsecrets\.",
    "curl or wget piped into shell": r"\b(curl|wget)\b[^\n|]*\|",
    "PowerShell expression execution": r"\b(Invoke-Expression|iex)\b",
    "encoded PowerShell command": r"\bpowershell(?:\.exe)?\s+-(?:enc|encodedcommand)\b",
    "GitHub CLI authentication inside CI": r"\bgh\s+auth\b",
    "CI job pushes to git": r"\bgit\s+push\b",
    "destructive root-like removal": r"\brm\s+-rf\s+[/~*$]",
}

USES_RE = re.compile(r"^\s*uses\s*:\s*(?P<action>[^\s#]+)", re.MULTILINE)


def workflow_files() -> list[Path]:
    if not WORKFLOW_DIR.exists():
        return []
    return sorted(
        path
        for path in WORKFLOW_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )


def check_permissions(text: str, rel_path: str) -> list[str]:
    failures: list[str] = []
    if "permissions:" not in text:
        failures.append(f"{rel_path}: workflow must declare least-privilege permissions")
    if not re.search(r"^\s{2}contents\s*:\s*read\s*$", text, re.MULTILINE):
        failures.append(f"{rel_path}: workflow token must be limited to contents: read")
    return failures


def check_forbidden_text(text: str, rel_path: str) -> list[str]:
    failures: list[str] = []
    for reason, pattern in FORBIDDEN_TEXT_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            failures.append(f"{rel_path}: {reason}")
    return failures


def check_actions(text: str, rel_path: str) -> list[str]:
    failures: list[str] = []
    for match in USES_RE.finditer(text):
        raw = match.group("action").strip().strip('"').strip("'")
        if "@" not in raw:
            failures.append(f"{rel_path}: action is not version-pinned: {raw}")
            continue
        action, version = raw.split("@", 1)
        if action not in ALLOWED_ACTIONS:
            failures.append(f"{rel_path}: unapproved third-party action: {action}")
        if not version:
            failures.append(f"{rel_path}: action has empty version: {raw}")
            continue
        approved_versions = APPROVED_ACTION_REFS.get(action)
        if approved_versions is not None and version not in approved_versions:
            expected = ", ".join(sorted(approved_versions))
            failures.append(f"{rel_path}: action {action} must use approved ref(s) {expected}, got {version}")
    return failures


def check_checkout_hardening(text: str, rel_path: str) -> list[str]:
    failures: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "uses:" not in line or "actions/checkout@" not in line:
            continue
        window = "\n".join(lines[index : index + 8])
        if not re.search(r"\bpersist-credentials\s*:\s*false\b", window, re.IGNORECASE):
            failures.append(f"{rel_path}: actions/checkout must set persist-credentials: false")
    return failures


def check_pull_request_coverage(text: str, rel_path: str) -> list[str]:
    if re.search(r"^\s{2}pull_request\s*:\s*$|^\s{2}pull_request\s*$", text, re.MULTILINE):
        return []
    if re.search(r"^\s*pull_request\s*:\s*$|^\s*pull_request\s*$", text, re.MULTILINE):
        return []
    return [f"{rel_path}: workflow should run on pull_request for external contribution checks"]


def main() -> int:
    failures: list[str] = []
    files = workflow_files()
    if not files:
        failures.append(".github/workflows: no workflow files found")

    for path in files:
        rel_path = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        failures.extend(check_permissions(text, rel_path))
        failures.extend(check_forbidden_text(text, rel_path))
        failures.extend(check_actions(text, rel_path))
        failures.extend(check_checkout_hardening(text, rel_path))
        failures.extend(check_pull_request_coverage(text, rel_path))

    if failures:
        print("Workflow security check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Workflow security check passed: workflows use read-only tokens, safe PR triggers, approved actions, and hardened checkout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
