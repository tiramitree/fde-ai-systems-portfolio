from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_traces_otel import (  # noqa: E402
    INSTRUMENTATION_SCOPE,
    endpoint_with_traces_path,
    merged_otlp_headers,
    parse_otlp_headers,
    resolve_otlp_traces_url,
    send_otlp_http_json,
)


class CaptureHandler(BaseHTTPRequestHandler):
    captured: list[dict[str, Any]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.__class__.captured.append(
            {
                "path": self.path,
                "headers": dict(self.headers.items()),
                "body": body,
            }
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"partialSuccess":{}}')

    def log_message(self, format: str, *args: object) -> None:
        return


def check(condition: bool, name: str, detail: str) -> bool:
    prefix = "[PASS]" if condition else "[FAIL]"
    print(f"{prefix} {name}: {detail}")
    return condition


def sample_payload() -> dict[str, Any]:
    return {
        "resourceSpans": [
            {
                "resource": {"attributes": []},
                "scopeSpans": [
                    {
                        "scope": {"name": INSTRUMENTATION_SCOPE, "version": "test"},
                        "spans": [
                            {
                                "traceId": "0" * 32,
                                "spanId": "1" * 16,
                                "name": "collector.handoff.check",
                                "kind": 1,
                                "startTimeUnixNano": "1",
                                "endTimeUnixNano": "2",
                                "attributes": [],
                                "events": [],
                                "status": {"code": 1},
                            }
                        ],
                    }
                ],
            }
        ]
    }


def run_local_handoff() -> list[bool]:
    CaptureHandler.captured = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = int(server.server_address[1])
        status, response = send_otlp_http_json(
            sample_payload(),
            resolve_otlp_traces_url(f"http://127.0.0.1:{port}", None),
            {"x-handoff-check": "local"},
            timeout=5,
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    captured = CaptureHandler.captured[0] if CaptureHandler.captured else {}
    headers = captured.get("headers", {})
    body = captured.get("body", b"")
    try:
        parsed_body = json.loads(body.decode("utf-8"))
    except Exception:
        parsed_body = {}

    return [
        check(status == 200 and "partialSuccess" in response, "local collector response", f"status={status}"),
        check(captured.get("path") == "/v1/traces", "OTLP traces path", str(captured.get("path"))),
        check(headers.get("Content-Type") == "application/json", "OTLP JSON content type", headers.get("Content-Type", "")),
        check(
            str(headers.get("User-Agent", "")).startswith(INSTRUMENTATION_SCOPE),
            "exporter user agent",
            headers.get("User-Agent", ""),
        ),
        check(headers.get("X-Handoff-Check") == "local", "custom header handoff", headers.get("X-Handoff-Check", "")),
        check(bool(parsed_body.get("resourceSpans")), "resourceSpans payload", f"groups={len(parsed_body.get('resourceSpans', []))}"),
    ]


def main() -> int:
    checks = [
        check(
            endpoint_with_traces_path("http://collector:4318") == "http://collector:4318/v1/traces",
            "base endpoint appends traces path",
            endpoint_with_traces_path("http://collector:4318"),
        ),
        check(
            resolve_otlp_traces_url("http://collector:4318/base", None)
            == "http://collector:4318/base/v1/traces",
            "base endpoint preserves base path",
            resolve_otlp_traces_url("http://collector:4318/base", None),
        ),
        check(
            resolve_otlp_traces_url("http://collector:4318", "http://collector:4318/custom/traces")
            == "http://collector:4318/custom/traces",
            "signal endpoint is used as-is",
            resolve_otlp_traces_url("http://collector:4318", "http://collector:4318/custom/traces"),
        ),
        check(
            parse_otlp_headers("x-one=1,x-two=two") == {"x-one": "1", "x-two": "two"},
            "OTLP header parser",
            "two headers",
        ),
    ]

    old_env = {
        "OTEL_EXPORTER_OTLP_HEADERS": os.environ.get("OTEL_EXPORTER_OTLP_HEADERS"),
        "OTEL_EXPORTER_OTLP_TRACES_HEADERS": os.environ.get("OTEL_EXPORTER_OTLP_TRACES_HEADERS"),
    }
    try:
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = "x-env=base"
        os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = "x-env=trace,x-trace=1"
        checks.append(
            check(
                merged_otlp_headers(["x-cli=1"]) == {"x-env": "trace", "x-trace": "1", "x-cli": "1"},
                "OTLP header precedence",
                "trace-specific and CLI headers override base headers",
            )
        )
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    checks.extend(run_local_handoff())

    passed = sum(1 for item in checks if item)
    print(f"\nOpenTelemetry collector handoff checks: {passed}/{len(checks)} passed")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
