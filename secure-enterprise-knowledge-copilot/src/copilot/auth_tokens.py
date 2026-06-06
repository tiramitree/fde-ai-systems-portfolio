from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any


LOCAL_AUTH_POLICY = "local_signed_demo_token_v1"
LOCAL_AUTH_ISSUER = "secure-enterprise-knowledge-copilot"
LOCAL_AUTH_AUDIENCE = "local-demo"
LOCAL_AUTH_TTL_SECONDS = 3600
LOCAL_AUTH_SECRET_ENV = "COPILOT_DEMO_AUTH_SECRET"
DEFAULT_LOCAL_AUTH_SECRET = "local-demo-token-signing-key-not-for-production"


class AuthTokenError(ValueError):
    pass


def _secret() -> bytes:
    return os.getenv(LOCAL_AUTH_SECRET_ENV, DEFAULT_LOCAL_AUTH_SECRET).encode("utf-8")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))
    except Exception as exc:
        raise AuthTokenError("Malformed bearer token.") from exc


def _sign(signing_input: str) -> str:
    digest = hmac.new(_secret(), signing_input.encode("ascii"), hashlib.sha256).digest()
    return _b64url(digest)


def public_claims(user: dict[str, Any], now: int | None = None) -> dict[str, Any]:
    issued_at = int(time.time() if now is None else now)
    return {
        "iss": LOCAL_AUTH_ISSUER,
        "aud": LOCAL_AUTH_AUDIENCE,
        "sub": str(user.get("id", "")),
        "tenant_id": str(user.get("tenant_id", "")),
        "role": str(user.get("role", "")),
        "group_ids": list(user.get("group_ids", [])),
        "policy": LOCAL_AUTH_POLICY,
        "iat": issued_at,
        "exp": issued_at + LOCAL_AUTH_TTL_SECONDS,
    }


def issue_demo_token(user: dict[str, Any], now: int | None = None) -> str:
    header = {"alg": "HS256", "typ": "JWT", "policy": LOCAL_AUTH_POLICY}
    payload = public_claims(user, now=now)
    signing_input = ".".join(
        [
            _b64url(json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")),
            _b64url(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")),
        ]
    )
    return f"{signing_input}.{_sign(signing_input)}"


def verify_demo_token(token: str, now: int | None = None) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthTokenError("Malformed bearer token.")
    signing_input = ".".join(parts[:2])
    expected = _sign(signing_input)
    if not hmac.compare_digest(expected, parts[2]):
        raise AuthTokenError("Invalid bearer token signature.")

    try:
        header = json.loads(_b64url_decode(parts[0]).decode("utf-8"))
        payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AuthTokenError("Malformed bearer token payload.") from exc
    if header.get("alg") != "HS256" or header.get("policy") != LOCAL_AUTH_POLICY:
        raise AuthTokenError("Unsupported bearer token header.")
    if payload.get("iss") != LOCAL_AUTH_ISSUER or payload.get("aud") != LOCAL_AUTH_AUDIENCE:
        raise AuthTokenError("Unsupported bearer token audience.")
    expires_at = int(payload.get("exp", 0) or 0)
    current = int(time.time() if now is None else now)
    if expires_at < current:
        raise AuthTokenError("Expired bearer token.")
    if not str(payload.get("sub", "")).strip():
        raise AuthTokenError("Bearer token is missing a subject.")
    return payload


def bearer_token_from_header(value: str) -> str:
    prefix = "Bearer "
    if not value.startswith(prefix):
        raise AuthTokenError("Authorization header must use Bearer auth.")
    token = value[len(prefix) :].strip()
    if not token:
        raise AuthTokenError("Bearer token is empty.")
    return token
