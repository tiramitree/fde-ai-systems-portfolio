from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ops_agent.agent import process_message
from ops_agent.evals import run_evals
from ops_agent.storage import (
    connect,
    get_user,
    init_state,
    latest_eval_run,
    list_approvals,
    list_audit,
    list_cases,
    list_traces,
    list_users,
)
from ops_agent.tools import approve_action


WEB_DIR = ROOT / "web"


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class Handler(BaseHTTPRequestHandler):
    server_version = "RegulatedCustomerOpsAgent/0.1"

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/"):
                self.handle_api_get(parsed.path, parse_qs(parsed.query))
            else:
                self.serve_static(parsed.path)
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            body = json.loads(raw or "{}")
            with connect() as store:
                if parsed.path == "/api/agent":
                    result = process_message(
                        store,
                        body.get("user_id", ""),
                        body.get("message", ""),
                        body.get("case_id"),
                    )
                    self.send_json(result)
                    return
                if parsed.path == "/api/approval/approve":
                    approver_id = body.get("approver_id", "")
                    user = get_user(store, approver_id)
                    if not user or user["role"] != "supervisor":
                        raise ApiError(403, "Only supervisors can approve actions.")
                    result = approve_action(store, body.get("approval_id", ""), approver_id)
                    self.send_json(result)
                    return
                if parsed.path == "/api/eval/run":
                    init_state(reset=True)
                    store.load()
                    result = run_evals(store)
                    self.send_json(result)
                    return
            raise ApiError(404, f"Unknown endpoint: {parsed.path}")
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON body"}, 400)
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def handle_api_get(self, path: str, query: dict[str, list[str]]) -> None:
        with connect() as store:
            if path == "/api/health":
                self.send_json({"status": "ok", "app": "regulated-customer-operations-agent"})
                return
            if path == "/api/users":
                self.send_json({"users": list_users(store)})
                return
            if path == "/api/cases":
                self.send_json({"cases": list_cases(store)})
                return
            if path == "/api/approvals":
                self.send_json({"approvals": list_approvals(store)})
                return
            if path == "/api/traces":
                self.send_json({"traces": list_traces(store, int(query.get("limit", ["25"])[0]))})
                return
            if path == "/api/audit":
                self.send_json({"events": list_audit(store, int(query.get("limit", ["50"])[0]))})
                return
            if path == "/api/eval/latest":
                self.send_json({"eval_run": latest_eval_run(store)})
                return
        raise ApiError(404, f"Unknown endpoint: {path}")

    def serve_static(self, path: str) -> None:
        file_path = WEB_DIR / "index.html" if path in ("", "/") else (WEB_DIR / path.lstrip("/")).resolve()
        if WEB_DIR.resolve() not in file_path.parents and file_path != WEB_DIR.resolve():
            raise ApiError(403, "Forbidden")
        if not file_path.exists() or not file_path.is_file():
            raise ApiError(404, "Not found")
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    init_state(reset=args.reset)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Regulated Customer Operations Agent running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()

