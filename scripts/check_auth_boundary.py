from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require_text(text: str, phrase: str, label: str, failures: list[str]) -> None:
    if phrase not in text:
        failures.append(f"{label}: missing {phrase!r}")


def check_shared_helper(failures: list[str]) -> None:
    path = ROOT / "local_auth_tokens.py"
    if not path.exists():
        failures.append("missing local_auth_tokens.py")
        return
    text = path.read_text(encoding="utf-8")
    for phrase in [
        'LOCAL_AUTH_POLICY = "local_signed_demo_token_v1"',
        'GLOBAL_AUTH_SECRET_ENV = "FDE_DEMO_AUTH_SECRET"',
        "DEFAULT_LOCAL_AUTH_SECRET",
        "not-for-production",
        "def issue_demo_token(",
        "def verify_demo_token(",
        "def bearer_token_from_header(",
        "hmac.compare_digest",
        '"aud": LOCAL_AUTH_AUDIENCE',
        '"tenant_id": _tenant_id(user)',
    ]:
        require_text(text, phrase, "local_auth_tokens.py", failures)


def check_app_headers(failures: list[str]) -> None:
    for rel_path in [
        "secure-enterprise-knowledge-copilot/app.py",
        "regulated-customer-operations-agent/app.py",
        "ai-reliability-incident-console/app.py",
    ]:
        text = read(rel_path)
        require_text(text, "REPO_ROOT = ROOT.parent", rel_path, failures)
        require_text(text, "headers_with_request_context", rel_path, failures)
        require_text(text, 'GOVERNOR.check("GET", parsed.path, self.headers, self.client_address)', rel_path, failures)
        require_text(text, 'GOVERNOR.check("POST", parsed.path, self.headers, self.client_address)', rel_path, failures)
        require_text(text, "headers = headers_with_request_context(self.headers, self._request_context)", rel_path, failures)
        require_text(text, "API.get(parsed.path, API.parse_query(parsed.query), headers)", rel_path, failures)
        require_text(text, "API.post(parsed.path, body, headers)", rel_path, failures)


def check_project_api_auth(failures: list[str]) -> None:
    expectations = {
        "secure-enterprise-knowledge-copilot/src/copilot/auth_tokens.py": [
            "from local_auth_tokens import",
            'LOCAL_AUTH_ISSUER = "secure-enterprise-knowledge-copilot"',
            'LOCAL_AUTH_SECRET_ENV = "COPILOT_DEMO_AUTH_SECRET"',
            "def issue_demo_token(",
            "def verify_demo_token(",
        ],
        "secure-enterprise-knowledge-copilot/src/copilot/api.py": [
            'if path == "/api/auth/demo-token":',
            "bearer_token_from_header",
            "Request user_id does not match authenticated subject.",
            "Authenticated context no longer matches the user record.",
        ],
        "regulated-customer-operations-agent/src/ops_agent/api.py": [
            "from local_auth_tokens import",
            'auth_secret_env = "OPS_AGENT_DEMO_AUTH_SECRET"',
            'if path == "/api/auth/demo-token":',
            "issue_demo_token(user, issuer=self.app_name, secret_env=self.auth_secret_env)",
            "def _resolve_user_id(",
            "Request identity does not match authenticated subject.",
            "Authenticated context no longer matches the user record.",
        ],
        "ai-reliability-incident-console/src/reliability_console/api.py": [
            "from local_auth_tokens import",
            'auth_secret_env = "RELIABILITY_CONSOLE_DEMO_AUTH_SECRET"',
            'if path == "/api/auth/demo-token":',
            "issue_demo_token(user, issuer=self.app_name, secret_env=self.auth_secret_env)",
            "def _resolve_user_id(",
            "Request identity does not match authenticated subject.",
            "Authenticated context no longer matches the user record.",
        ],
    }
    for rel_path, phrases in expectations.items():
        text = read(rel_path)
        for phrase in phrases:
            require_text(text, phrase, rel_path, failures)


def check_contracts_and_docs(failures: list[str]) -> None:
    contracts = read("scripts/check_api_contracts.py")
    for phrase in [
        "P1 local signed demo auth token contract",
        "P2 local signed demo auth token contract",
        "P2 supervisor demo auth token contract",
        "P3 local signed demo auth token contract",
        "P2 bearer auth resolves agent subject",
        "P2 bearer auth rejects identity mismatch",
        "P3 bearer auth rejects identity mismatch",
        "Authorization",
        "local_signed_demo_token_v1",
        "authenticated subject",
    ]:
        require_text(contracts, phrase, "scripts/check_api_contracts.py", failures)

    api_docs = read("docs/api_contracts.md")
    for phrase in [
        "local_auth_tokens.py",
        "Authorization: Bearer <token>",
        "Project 2 and Project 3 use the same identity boundary",
        "FDE_DEMO_AUTH_SECRET",
        "COPILOT_DEMO_AUTH_SECRET",
        "OPS_AGENT_DEMO_AUTH_SECRET",
        "RELIABILITY_CONSOLE_DEMO_AUTH_SECRET",
        "it is not a production SSO replacement",
    ]:
        require_text(api_docs, phrase, "docs/api_contracts.md", failures)

    evidence = read("docs/portfolio_evidence_matrix.md")
    require_text(evidence, "All services expose a local signed identity boundary.", "docs/portfolio_evidence_matrix.md", failures)
    require_text(evidence, "python -B scripts/dev.py auth-boundary", "docs/portfolio_evidence_matrix.md", failures)

    for rel_path in ["README.md", "PROJECT_CONTENT_INDEX.md"]:
        require_text(read(rel_path), "local_auth_tokens.py", rel_path, failures)


def check_no_overclaim(failures: list[str]) -> None:
    public_text = "\n".join(
        [
            read("README.md"),
            read("docs/api_contracts.md"),
            read("docs/portfolio_evidence_matrix.md"),
            read("docs/production_upgrade_notes.md"),
        ]
    ).lower()
    forbidden = [
        "production sso replacement",
        "production-ready sso",
        "production-ready authentication",
        "real oidc is implemented",
    ]
    for phrase in forbidden:
        if phrase in public_text and f"not a {phrase}" not in public_text:
            failures.append(f"public auth docs overclaim: {phrase!r}")


def main() -> int:
    failures: list[str] = []
    check_shared_helper(failures)
    check_app_headers(failures)
    check_project_api_auth(failures)
    check_contracts_and_docs(failures)
    check_no_overclaim(failures)

    if failures:
        print("Auth boundary check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Auth boundary check passed: shared local bearer-token helper, service header plumbing, "
        "runtime auth contracts, and public docs stay aligned without production SSO overclaims."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
