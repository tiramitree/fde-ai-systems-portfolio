from __future__ import annotations

import os
import re
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Mapping

from local_http_limits import parse_content_length


REQUEST_ID_HEADER = "X-Request-ID"
RATE_LIMIT_ENABLED_ENV = "FDE_RATE_LIMIT_ENABLED"
RATE_LIMIT_REQUESTS_ENV = "FDE_RATE_LIMIT_REQUESTS_PER_WINDOW"
RATE_LIMIT_BUDGET_ENV = "FDE_RATE_LIMIT_BUDGET_PER_WINDOW"
RATE_LIMIT_WINDOW_SECONDS_ENV = "FDE_RATE_LIMIT_WINDOW_SECONDS"

DEFAULT_RATE_LIMIT_REQUESTS = 120
DEFAULT_RATE_LIMIT_BUDGET = 1_200
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,79}$")


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    request_limit: int
    requests_remaining: int
    budget_limit: int
    budget_remaining: int
    window_seconds: int
    retry_after_seconds: int = 0

    def response_headers(self) -> dict[str, str]:
        headers = {
            REQUEST_ID_HEADER: self.request_id,
            "X-RateLimit-Limit": str(self.request_limit),
            "X-RateLimit-Remaining": str(max(0, self.requests_remaining)),
            "X-RateLimit-Window-Seconds": str(self.window_seconds),
            "X-RateLimit-Budget-Limit": str(self.budget_limit),
            "X-RateLimit-Budget-Remaining": str(max(0, self.budget_remaining)),
        }
        if self.retry_after_seconds:
            headers["Retry-After"] = str(self.retry_after_seconds)
        return headers


class RequestGovernanceError(Exception):
    status = 400
    message = "Request rejected."

    def __init__(self, context: RequestContext, message: str | None = None) -> None:
        self.context = context
        self.message = message or self.message
        super().__init__(self.message)


class RateLimitExceeded(RequestGovernanceError):
    status = 429
    message = "Rate limit exceeded."


@dataclass
class _Bucket:
    window_started_at: float
    request_count: int = 0
    budget_used: int = 0


class LocalRequestGovernor:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._buckets: dict[str, _Bucket] = {}

    def check(
        self,
        method: str,
        path: str,
        headers: Mapping[str, Any],
        client_address: tuple[str, int] | None,
    ) -> RequestContext:
        request_id = safe_request_id(_header(headers, REQUEST_ID_HEADER))
        limit = _positive_int_env(RATE_LIMIT_REQUESTS_ENV, DEFAULT_RATE_LIMIT_REQUESTS)
        budget_limit = _positive_int_env(RATE_LIMIT_BUDGET_ENV, DEFAULT_RATE_LIMIT_BUDGET)
        window_seconds = _positive_int_env(RATE_LIMIT_WINDOW_SECONDS_ENV, DEFAULT_RATE_LIMIT_WINDOW_SECONDS)
        content_length = parse_content_length(_header(headers, "Content-Length"))
        cost = request_cost(method, path, content_length)

        if not _rate_limit_enabled():
            return RequestContext(
                request_id=request_id,
                request_limit=limit,
                requests_remaining=limit,
                budget_limit=budget_limit,
                budget_remaining=budget_limit,
                window_seconds=window_seconds,
            )

        now = time.monotonic()
        key = self._bucket_key(client_address, method, path)
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None or now - bucket.window_started_at >= window_seconds:
                bucket = _Bucket(window_started_at=now)
                self._buckets[key] = bucket

            retry_after = max(1, int(window_seconds - (now - bucket.window_started_at)))
            would_exceed_requests = bucket.request_count + 1 > limit
            would_exceed_budget = bucket.budget_used + cost > budget_limit
            if would_exceed_requests or would_exceed_budget:
                context = RequestContext(
                    request_id=request_id,
                    request_limit=limit,
                    requests_remaining=max(0, limit - bucket.request_count),
                    budget_limit=budget_limit,
                    budget_remaining=max(0, budget_limit - bucket.budget_used),
                    window_seconds=window_seconds,
                    retry_after_seconds=retry_after,
                )
                raise RateLimitExceeded(context)

            bucket.request_count += 1
            bucket.budget_used += cost
            return RequestContext(
                request_id=request_id,
                request_limit=limit,
                requests_remaining=max(0, limit - bucket.request_count),
                budget_limit=budget_limit,
                budget_remaining=max(0, budget_limit - bucket.budget_used),
                window_seconds=window_seconds,
            )

    @staticmethod
    def _bucket_key(client_address: tuple[str, int] | None, method: str, path: str) -> str:
        client = client_address[0] if client_address else "unknown-client"
        return f"{client}:{method.upper()}:{path}"


class GovernedHeaders:
    def __init__(self, source: Mapping[str, Any], context: RequestContext) -> None:
        self._source = source
        self._request_id = context.request_id

    def get(self, key: str, default: Any = "") -> Any:
        if key.lower() == REQUEST_ID_HEADER.lower():
            return self._request_id
        getter = getattr(self._source, "get", None)
        if callable(getter):
            return getter(key, default)
        return default


def headers_with_request_context(headers: Mapping[str, Any], context: RequestContext | None) -> Mapping[str, Any]:
    if context is None:
        return headers
    return GovernedHeaders(headers, context)


def safe_request_id(value: str) -> str:
    candidate = str(value or "").strip()
    if candidate and _REQUEST_ID_RE.match(candidate):
        return candidate
    return str(uuid.uuid4())


def request_cost(method: str, path: str, content_length: int) -> int:
    method_upper = method.upper()
    cost = 1
    if method_upper == "POST":
        cost += 1
    if path in {"/api/query", "/api/agent", "/api/triage"}:
        cost += 8
    elif path == "/api/eval/run":
        cost += 12
    elif path.endswith("/sync") or path in {"/api/documents/ingest", "/api/ingestion/jobs"}:
        cost += 18
    if content_length > 0:
        cost += (content_length - 1) // 4096
    return max(1, cost)


def _header(headers: Mapping[str, Any], key: str) -> str:
    getter = getattr(headers, "get", None)
    if callable(getter):
        return str(getter(key, "") or "")
    return ""


def _positive_int_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _rate_limit_enabled() -> bool:
    raw = os.getenv(RATE_LIMIT_ENABLED_ENV, "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}
