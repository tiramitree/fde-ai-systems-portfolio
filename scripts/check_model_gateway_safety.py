from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Gateway:
    name: str
    path: Path
    enable_function: str
    call_function: str
    provider_env: str
    local_default: str
    schema_markers: tuple[str, ...]


GATEWAYS = [
    Gateway(
        name="Secure Enterprise Knowledge Copilot",
        path=ROOT / "secure-enterprise-knowledge-copilot" / "src" / "copilot" / "model_gateway.py",
        enable_function="should_use_openai",
        call_function="generate_structured_answer",
        provider_env="COPILOT_MODEL_PROVIDER",
        local_default='os.getenv("COPILOT_MODEL_PROVIDER", "local")',
        schema_markers=('"answer"', '"confidence"', '"missing_evidence"', '"strict": True'),
    ),
    Gateway(
        name="Regulated Customer Operations Agent",
        path=ROOT / "regulated-customer-operations-agent" / "src" / "ops_agent" / "model_gateway.py",
        enable_function="should_use_openai_router",
        call_function="classify_intent_with_openai",
        provider_env="OPS_AGENT_MODEL_ROUTER",
        local_default='os.getenv("OPS_AGENT_MODEL_ROUTER", "local")',
        schema_markers=('"intent"', '"enum": INTENTS', '"strict": True'),
    ),
]

ALLOWED_OPENAI_KEY_REFERENCES = {
    ".env.example",
    "docker-compose.yml",
    "README.md",
    "PROJECT_CONTENT_INDEX.md",
    "docs/model_runtime_configuration.md",
    "docs/final_demo_runbook.md",
    "docs/final_completion_audit.md",
    "docs/completion_checklist.md",
    "docs/model_gateway_safety.md",
    "secure-enterprise-knowledge-copilot/README.md",
    "regulated-customer-operations-agent/README.md",
    "scripts/check_model_gateway_safety.py",
    "scripts/check_container_release.py",
    "scripts/check_pr_review_policy.py",
    "scripts/review_open_prs.py",
    "secure-enterprise-knowledge-copilot/src/copilot/model_gateway.py",
    "regulated-customer-operations-agent/src/ops_agent/model_gateway.py",
}

FORBIDDEN_GATEWAY_MARKERS = (
    "print(",
    "logging.",
    "subprocess.",
    "os.system",
    "eval(",
    "exec(",
    "pickle.",
)


def git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def top_level_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def function_returns_none_on_exception(function: ast.FunctionDef) -> bool:
    for node in ast.walk(function):
        if isinstance(node, ast.ExceptHandler):
            for statement in node.body:
                if isinstance(statement, ast.Return) and isinstance(statement.value, ast.Constant):
                    if statement.value.value is None:
                        return True
    return False


def function_has_raise_in_exception(function: ast.FunctionDef) -> bool:
    for node in ast.walk(function):
        if isinstance(node, ast.ExceptHandler):
            if any(isinstance(statement, ast.Raise) for statement in ast.walk(node)):
                return True
    return False


def function_names(tree: ast.Module) -> set[str]:
    return {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}


def check_gateway(gateway: Gateway) -> list[str]:
    failures: list[str] = []
    rel = gateway.path.relative_to(ROOT).as_posix()
    text = gateway.path.read_text(encoding="utf-8")
    tree = parse(gateway.path)
    functions = function_names(tree)

    if gateway.enable_function not in functions:
        failures.append(f"{rel}: missing {gateway.enable_function}")
    if gateway.call_function not in functions:
        failures.append(f"{rel}: missing {gateway.call_function}")

    expected_markers = [
        'OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"',
        gateway.local_default,
        f'os.getenv("{gateway.provider_env}", "local").lower() == "openai"',
        'bool(os.getenv("OPENAI_API_KEY"))',
        '"Authorization": f"Bearer {os.environ[\'OPENAI_API_KEY\']}"',
        '"Content-Type": "application/json"',
        "method=\"POST\"",
        "timeout=30",
        '"additionalProperties": False',
    ]
    for marker in expected_markers:
        if marker not in text:
            failures.append(f"{rel}: missing safety marker {marker}")

    for marker in gateway.schema_markers:
        if marker not in text:
            failures.append(f"{rel}: missing structured-output marker {marker}")

    for marker in FORBIDDEN_GATEWAY_MARKERS:
        if marker in text:
            failures.append(f"{rel}: forbidden gateway marker {marker}")

    call_function = top_level_function(tree, gateway.call_function)
    if call_function and not function_returns_none_on_exception(call_function):
        failures.append(f"{rel}: {gateway.call_function} must return None on API/parse errors")
    if call_function and function_has_raise_in_exception(call_function):
        failures.append(f"{rel}: {gateway.call_function} must not re-raise API/parse errors")

    return failures


def check_env_example() -> list[str]:
    failures: list[str] = []
    path = ROOT / ".env.example"
    text = path.read_text(encoding="utf-8")
    required = [
        "OPENAI_API_KEY=",
        "COPILOT_MODEL_PROVIDER=local",
        "OPS_AGENT_MODEL_ROUTER=local",
        "OPENAI_MODEL=gpt-5.2",
    ]
    for marker in required:
        if marker not in text:
            failures.append(f".env.example: missing {marker}")
    if re.search(r"OPENAI_API_KEY\s*=\s*\S+", text):
        failures.append(".env.example: OPENAI_API_KEY must remain blank")
    return failures


def check_docker_compose() -> list[str]:
    failures: list[str] = []
    text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    required = [
        "COPILOT_MODEL_PROVIDER: ${COPILOT_MODEL_PROVIDER:-local}",
        "OPS_AGENT_MODEL_ROUTER: ${OPS_AGENT_MODEL_ROUTER:-local}",
        "OPENAI_API_KEY: ${OPENAI_API_KEY:-}",
    ]
    for marker in required:
        if marker not in text:
            failures.append(f"docker-compose.yml: missing {marker}")
    return failures


def check_openai_key_references() -> list[str]:
    failures: list[str] = []
    for path in git_files():
        rel = path.relative_to(ROOT).as_posix()
        if "OPENAI_API_KEY" not in path.read_text(encoding="utf-8", errors="ignore"):
            continue
        if rel not in ALLOWED_OPENAI_KEY_REFERENCES:
            failures.append(f"{rel}: unexpected OPENAI_API_KEY reference")
    return failures


def main() -> int:
    failures: list[str] = []
    failures.extend(check_env_example())
    failures.extend(check_docker_compose())
    failures.extend(check_openai_key_references())
    for gateway in GATEWAYS:
        failures.extend(check_gateway(gateway))

    if failures:
        print("Model gateway safety check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Model gateway safety check passed: OpenAI mode is opt-in, key references are constrained, "
        "gateways use structured Responses API calls, and API failures fall back to local behavior."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
