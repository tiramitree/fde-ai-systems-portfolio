from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    severity: str
    location: str
    reason: str


HIGH_IMPACT_PATHS = (
    ".github/workflows/",
    "scripts/public_safety_scan.py",
    "scripts/quality_gate.py",
    "scripts/ci_quality_gate.py",
    "scripts/dev.py",
    "scripts/configure_github_launch.py",
    "secure-enterprise-knowledge-copilot/src/copilot/security.py",
    "secure-enterprise-knowledge-copilot/src/copilot/retrieval.py",
    "secure-enterprise-knowledge-copilot/src/copilot/answering.py",
    "regulated-customer-operations-agent/src/ops_agent/tools.py",
    "regulated-customer-operations-agent/src/ops_agent/agent.py",
)

MEDIUM_IMPACT_PATHS = (
    "requirements",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "Dockerfile",
    "docker-compose",
    ".dockerignore",
    ".gitignore",
    "eval_cases.json",
    "evals.py",
    "model_gateway.py",
)

BINARY_OR_EXECUTABLE_SUFFIXES = (
    ".exe",
    ".dll",
    ".dylib",
    ".so",
    ".ps1",
    ".bat",
    ".cmd",
    ".msi",
)

HIGH_RISK_PATTERNS = {
    "credential or token marker": [
        "github_" + r"pat_",
        r"gh[pousr]_",
        r"BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY",
        r"OPENAI_API_KEY",
        r"AWS_SECRET_ACCESS_KEY",
        "s" + r"k-[A-Za-z0-9_-]{10,}",
    ],
    "private local path or personal artifact": [
        r"C:\\Users",
        r"/Users/[^/\s]+/",
        "One" + "Drive",
        "x" + "wechat",
        "wx" + "id_",
        "CV_" + "Runze",
    ],
    "command execution or shell escape": [
        r"\bsubprocess\.",
        r"\bos\.system\(",
        r"\bStart-Process\b",
        r"\bInvoke-Expression\b",
        r"\bcmd\s*/c\b",
        r"\bpowershell\s+-",
    ],
    "destructive filesystem operation": [
        r"\bshutil\.rmtree\(",
        r"\bos\.remove\(",
        r"\bos\.unlink\(",
        r"\bRemove-Item\b",
        r"\brm\s+-rf\b",
    ],
    "dynamic code execution": [
        r"\beval\(",
        r"\bexec\(",
        r"\bcompile\(",
        r"\bpickle\.loads?\(",
        r"\bbase64\.b64decode\(",
    ],
    "new outbound network behavior": [
        r"\burllib\.request\.urlopen\(",
        r"\brequests\.",
        r"\bsocket\.",
        r"\bfetch\(",
        r"\bInvoke-WebRequest\b",
        r"\bcurl\s+",
    ],
}

MEDIUM_RISK_PATTERNS = {
    "environment variable access": [
        r"\bos\.environ\b",
        r"\bos\.getenv\(",
        r"\bprocess\.env\b",
    ],
    "dependency installation or package manager call": [
        r"\bpip\s+install\b",
        r"\bnpm\s+install\b",
        r"\buv\s+add\b",
        r"\bpoetry\s+add\b",
    ],
    "external URL introduced": [
        r"https?://",
    ],
}


def git_output(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        capture_output=True,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def repo_from_remote(remote: str) -> str | None:
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def get_repo() -> str:
    code, remote = git_output(["remote", "get-url", "origin"])
    if code != 0:
        raise RuntimeError("origin remote is not configured")
    repo = repo_from_remote(remote)
    if not repo:
        raise RuntimeError(f"origin is not a GitHub repository: {remote}")
    return repo


def api_get(path: str) -> tuple[int, Any, str]:
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "fde-portfolio-pr-triage",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8")), ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, None, body or str(exc)
    except urllib.error.URLError as exc:
        return 0, None, str(exc.reason)


def api_pages(path: str) -> tuple[int, list[dict[str, Any]], str]:
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        separator = "&" if "?" in path else "?"
        status, data, error = api_get(f"{path}{separator}per_page=100&page={page}")
        if status != 200 or not isinstance(data, list):
            return status, rows, error
        rows.extend(item for item in data if isinstance(item, dict))
        if len(data) < 100:
            return status, rows, ""
        page += 1


def added_lines(patch: str | None) -> str:
    if not patch:
        return ""
    lines = []
    for line in patch.splitlines():
        if line.startswith("+++") or not line.startswith("+"):
            continue
        lines.append(line[1:])
    return "\n".join(lines)


def find_patterns(text: str, patterns: dict[str, list[str]], severity: str, location: str) -> list[Finding]:
    findings: list[Finding] = []
    for reason, regexes in patterns.items():
        for regex in regexes:
            if re.search(regex, text, re.IGNORECASE):
                findings.append(Finding(severity, location, reason))
                break
    return findings


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[Finding] = []
    for finding in findings:
        key = (finding.severity, finding.location, finding.reason)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique


def scan_file(file_info: dict[str, Any]) -> list[Finding]:
    filename = str(file_info.get("filename", ""))
    patch = file_info.get("patch")
    status = str(file_info.get("status", ""))
    findings: list[Finding] = []

    if any(filename.startswith(path) for path in HIGH_IMPACT_PATHS):
        findings.append(Finding("HIGH", filename, "high-impact safety, CI, or governance file changed"))
    elif any(marker in filename for marker in MEDIUM_IMPACT_PATHS):
        findings.append(Finding("MEDIUM", filename, "dependency, runtime, eval, or environment-adjacent file changed"))

    if filename.endswith(BINARY_OR_EXECUTABLE_SUFFIXES):
        findings.append(Finding("HIGH", filename, "binary or executable file introduced or changed"))

    if status == "removed":
        findings.append(Finding("MEDIUM", filename, "file removed; check for deleted tests, docs, or safeguards"))

    if patch is None:
        findings.append(Finding("MEDIUM", filename, "patch omitted by GitHub API; inspect file manually before running code"))
        return findings

    added = added_lines(patch)
    findings.extend(find_patterns(added, HIGH_RISK_PATTERNS, "HIGH", filename))
    findings.extend(find_patterns(added, MEDIUM_RISK_PATTERNS, "MEDIUM", filename))
    return dedupe_findings(findings)


def recommendation(findings: list[Finding], pr: dict[str, Any]) -> str:
    if pr.get("draft"):
        return "wait: PR is draft"
    severities = {finding.severity for finding in findings}
    if "HIGH" in severities:
        return "manual review required before running code"
    if "MEDIUM" in severities:
        return "review carefully, then run safety and verify gates"
    return "low-risk shape; still review diff and run gates before merge"


def summarize_pr(repo: str, pr: dict[str, Any]) -> tuple[list[str], bool]:
    number = int(pr.get("number", 0))
    title = str(pr.get("title", ""))
    user = pr.get("user") or {}
    author = str(user.get("login", "unknown"))
    url = str(pr.get("html_url", ""))
    draft = bool(pr.get("draft"))

    status, files, error = api_pages(f"/repos/{repo}/pulls/{number}/files")
    if status != 200:
        return [f"[FAIL] PR #{number} files could not be fetched: {error or status}"], True

    findings = dedupe_findings([finding for file_info in files for finding in scan_file(file_info)])
    high_risk = any(finding.severity == "HIGH" for finding in findings)
    additions = sum(int(file_info.get("additions") or 0) for file_info in files)
    deletions = sum(int(file_info.get("deletions") or 0) for file_info in files)

    lines = [
        f"PR #{number}: {title}",
        f"- author: {author}",
        f"- url: {url}",
        f"- draft: {str(draft).lower()}",
        f"- changed files: {len(files)}, additions: {additions}, deletions: {deletions}",
        f"- recommendation: {recommendation(findings, pr)}",
    ]
    if findings:
        lines.append("- findings:")
        for finding in sorted(findings, key=lambda item: (item.severity != "HIGH", item.location, item.reason)):
            lines.append(f"  - [{finding.severity}] {finding.location}: {finding.reason}")
    else:
        lines.append("- findings: none from automated static triage")

    lines.extend(
        [
            "- required before merge:",
            "  - read the diff before running it",
            "  - python -B scripts/dev.py safety",
            "  - python -B scripts/dev.py verify",
            "  - confirm GitHub Actions is green",
        ]
    )
    return lines, high_risk


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report open public PRs and flag risky changes before review or merge.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when high-risk findings are present.")
    parser.add_argument("--pr", type=int, help="Inspect one PR number instead of every open PR.")
    args = parser.parse_args()

    repo = get_repo()
    if args.pr:
        status, pr, error = api_get(f"/repos/{repo}/pulls/{args.pr}")
        if status != 200 or not isinstance(pr, dict):
            print(f"PR #{args.pr} could not be fetched: {error or status}")
            return 1
        prs = [pr]
    else:
        query = urllib.parse.urlencode({"state": "open", "sort": "updated", "direction": "desc"})
        status, prs, error = api_pages(f"/repos/{repo}/pulls?{query}")
        if status != 200:
            print(f"Open PRs could not be fetched: {error or status}")
            return 1

    print(f"Repository: {repo}")
    if not prs:
        print("Open PRs: 0")
        print("No external PRs are awaiting review.")
        return 0

    print(f"Open PRs inspected: {len(prs)}")
    any_high_risk = False
    for pr in prs:
        lines, high_risk = summarize_pr(repo, pr)
        any_high_risk = any_high_risk or high_risk
        print()
        print("\n".join(lines))

    if args.strict and any_high_risk:
        print()
        print("Strict mode failed: high-risk PR findings require manual review.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
