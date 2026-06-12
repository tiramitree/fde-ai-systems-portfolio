LOCAL_AUTH_ISSUER = "secure-enterprise-knowledge-copilot"
LOCAL_AUTH_SECRET_ENV = "COPILOT_DEMO_AUTH_SECRET"

from local_auth_tokens import (
    LOCAL_AUTH_POLICY,
    LOCAL_AUTH_TTL_SECONDS,
    AuthTokenError,
    bearer_token_from_header,
    issue_demo_token as _issue_demo_token,
    public_claims as _public_claims,
    verify_demo_token as _verify_demo_token,
)


def public_claims(user: dict, now: int | None = None) -> dict:
    return _public_claims(user, issuer=LOCAL_AUTH_ISSUER, now=now)


def issue_demo_token(user: dict, now: int | None = None) -> str:
    return _issue_demo_token(user, issuer=LOCAL_AUTH_ISSUER, secret_env=LOCAL_AUTH_SECRET_ENV, now=now)


def verify_demo_token(token: str, now: int | None = None) -> dict:
    return _verify_demo_token(token, issuer=LOCAL_AUTH_ISSUER, secret_env=LOCAL_AUTH_SECRET_ENV, now=now)
