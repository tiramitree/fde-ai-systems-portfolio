from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / "scripts" / "review_open_prs.py"
RUNBOOK = ROOT / "docs" / "pr_review_runbook.md"
POLICY = ROOT / "docs" / "maintainer_review_policy.md"
DOCS_ONLY_EXAMPLES = ROOT / "docs" / "docs_only_pr_review_examples.md"
TEMPLATE = ROOT / ".github" / "pull_request_template.md"


REQUIRED_HIGH_IMPACT_PATHS = [
    ".github/workflows/",
    "scripts/public_safety_scan.py",
    "scripts/quality_gate.py",
    "scripts/ci_quality_gate.py",
    "scripts/dev.py",
    "scripts/configure_github_launch.py",
    "scripts/maintain_github_state.py",
    "scripts/community_issue_pack.py",
    "scripts/check_community_issue_pack.py",
    "scripts/manage_community_issues.py",
    "scripts/check_launch_assets.py",
    "secure-enterprise-knowledge-copilot/src/copilot/security.py",
    "secure-enterprise-knowledge-copilot/src/copilot/retrieval.py",
    "secure-enterprise-knowledge-copilot/src/copilot/answering.py",
    "regulated-customer-operations-agent/src/ops_agent/tools.py",
    "regulated-customer-operations-agent/src/ops_agent/agent.py",
]

REQUIRED_MEDIUM_IMPACT_PATHS = [
    "requirements",
    "pyproject.toml",
    "package.json",
    "Dockerfile",
    "docker-compose",
    ".gitignore",
    "eval_cases.json",
    "model_gateway.py",
]

REQUIRED_BINARY_SUFFIXES = [
    ".exe",
    ".dll",
    ".so",
    ".ps1",
    ".bat",
    ".cmd",
    ".msi",
]

REQUIRED_HIGH_RISK_REASONS = [
    "credential or token marker",
    "private local path or personal artifact",
    "command execution or shell escape",
    "destructive filesystem operation",
    "dynamic code execution",
    "new outbound network behavior",
]

REQUIRED_MEDIUM_RISK_REASONS = [
    "environment variable access",
    "dependency installation or package manager call",
    "external URL introduced",
]

REQUIRED_PATTERN_FRAGMENTS = [
    "OPENAI_API_KEY",
    "PRIVATE KEY",
    "subprocess",
    "os.system",
    "Start-Process",
    "Invoke-Expression",
    "Remove-Item",
    "rm",
    "eval",
    "exec",
    "pickle",
    "base64",
    "urlopen",
    "requests",
    "socket",
    "fetch",
    "Invoke-WebRequest",
    "curl",
    "pip",
    "npm",
    "process",
]

REQUIRED_RUNBOOK_PHRASES = [
    "Read the diff before running code",
    "python -B scripts/dev.py pr-triage",
    "python -B scripts/dev.py governance",
    "python -B scripts/dev.py workflow-security",
    "python -B scripts/dev.py safety",
    "python -B scripts/dev.py verify",
    "python -B scripts/review_open_prs.py --strict",
    "python -B scripts/maintain_github_state.py",
    "gh auth login",
    "workflow changes",
    "dependency changes",
    "outbound network calls",
    "binary files",
]

REQUIRED_POLICY_PHRASES = [
    "ask for secrets",
    "unrelated links",
    "obfuscated code",
    "weaken permission checks",
    "approval gates",
    "Run triage before running contributor code",
    "Confirm GitHub Actions is green",
]

REQUIRED_TEMPLATE_PHRASES = [
    "Permission checks are preserved",
    "Approval gates are preserved",
    "No secrets",
    "Dependency surface is intentional",
    "Eval or CI failures are not hidden",
    "No required OpenAI API dependency",
    "New risky behavior has eval coverage",
]

REQUIRED_DOCS_ONLY_EXAMPLE_PHRASES = [
    "Useful Docs PR Example",
    "Low-Signal Docs PR Example",
    "Unsafe Docs PR Example",
    "Claim Check",
    "Link And Artifact Check",
    "Issue-Pack Drift Check",
    "Docs-Only Merge Bar",
    "Do not run contributor commands",
    "generated runtime artifacts",
    "private paths",
    "external-account requirements",
    "paid-service requirements",
    "real customer data",
    "python -B scripts/dev.py community-issues",
    "python -B scripts/dev.py pr-policy",
    "python -B scripts/dev.py safety",
    "python -B scripts/dev.py quality",
]


def read(rel_path: Path) -> str:
    return rel_path.read_text(encoding="utf-8")


def literal_assignment(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    raise ValueError(f"missing assignment: {name}")


def flatten(value) -> list[str]:
    items: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            items.append(str(key))
            items.extend(flatten(nested))
    elif isinstance(value, (list, tuple, set)):
        for nested in value:
            items.extend(flatten(nested))
    else:
        items.append(str(value))
    return items


def require_contains(haystack: str, needles: list[str], label: str) -> list[str]:
    return [f"{label} missing phrase: {needle}" for needle in needles if needle not in haystack]


def check_triage_script() -> list[str]:
    failures: list[str] = []
    if not TRIAGE.exists():
        return ["missing scripts/review_open_prs.py"]

    text = read(TRIAGE)
    normalized_text = text.lower().replace("\\", "")
    tree = ast.parse(text)
    high_paths = list(literal_assignment(tree, "HIGH_IMPACT_PATHS"))
    medium_paths = list(literal_assignment(tree, "MEDIUM_IMPACT_PATHS"))
    suffixes = list(literal_assignment(tree, "BINARY_OR_EXECUTABLE_SUFFIXES"))
    for path in REQUIRED_HIGH_IMPACT_PATHS:
        if path not in high_paths:
            failures.append(f"HIGH_IMPACT_PATHS missing: {path}")
    for path in REQUIRED_MEDIUM_IMPACT_PATHS:
        if path not in medium_paths:
            failures.append(f"MEDIUM_IMPACT_PATHS missing: {path}")
    for suffix in REQUIRED_BINARY_SUFFIXES:
        if suffix not in suffixes:
            failures.append(f"BINARY_OR_EXECUTABLE_SUFFIXES missing: {suffix}")
    for reason in REQUIRED_HIGH_RISK_REASONS:
        if reason not in text:
            failures.append(f"HIGH_RISK_PATTERNS missing reason: {reason}")
    for reason in REQUIRED_MEDIUM_RISK_REASONS:
        if reason not in text:
            failures.append(f"MEDIUM_RISK_PATTERNS missing reason: {reason}")
    for fragment in REQUIRED_PATTERN_FRAGMENTS:
        lowered = fragment.lower()
        if lowered not in text.lower() and lowered not in normalized_text:
            failures.append(f"risk patterns missing marker fragment: {fragment}")

    required_code_phrases = [
        "scrape_open_pr_numbers",
        "manual review required before running code",
        "read the diff before running it",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py verify",
        "Strict mode failed",
    ]
    failures.extend(require_contains(text, required_code_phrases, "scripts/review_open_prs.py"))
    return failures


def check_docs() -> list[str]:
    failures: list[str] = []
    for path in (RUNBOOK, POLICY, DOCS_ONLY_EXAMPLES, TEMPLATE):
        if not path.exists():
            failures.append(f"missing PR review policy file: {path.relative_to(ROOT)}")

    if RUNBOOK.exists():
        failures.extend(require_contains(read(RUNBOOK), REQUIRED_RUNBOOK_PHRASES, "docs/pr_review_runbook.md"))
    if POLICY.exists():
        failures.extend(require_contains(read(POLICY), REQUIRED_POLICY_PHRASES, "docs/maintainer_review_policy.md"))
    if DOCS_ONLY_EXAMPLES.exists():
        failures.extend(
            require_contains(
                read(DOCS_ONLY_EXAMPLES),
                REQUIRED_DOCS_ONLY_EXAMPLE_PHRASES,
                "docs/docs_only_pr_review_examples.md",
            )
        )
    if TEMPLATE.exists():
        failures.extend(require_contains(read(TEMPLATE), REQUIRED_TEMPLATE_PHRASES, ".github/pull_request_template.md"))
    return failures


def check_cross_references() -> list[str]:
    failures: list[str] = []
    references = {
        "README.md": ["docs/pr_review_security.md", "docs/docs_only_pr_review_examples.md", "python -B scripts/dev.py pr-policy"],
        "PROJECT_CONTENT_INDEX.md": ["docs/pr_review_security.md", "docs/docs_only_pr_review_examples.md", "scripts/check_pr_review_policy.py"],
        "docs/threat_model.md": ["python -B scripts/dev.py pr-policy"],
        "docs/portfolio_evidence_matrix.md": ["python -B scripts/dev.py pr-policy"],
    }
    for rel_path, phrases in references.items():
        text = read(ROOT / rel_path)
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path} missing PR-policy reference: {phrase}")
    return failures


def main() -> int:
    failures: list[str] = []
    failures.extend(check_triage_script())
    failures.extend(check_docs())
    failures.extend(check_cross_references())

    if failures:
        print("PR review policy check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PR review policy check passed: triage heuristics, runbook, policy, docs-only examples, and template remain safety-focused.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
