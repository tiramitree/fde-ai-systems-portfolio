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

from copilot.answering import generate_answer
from copilot.evals import latest_eval_run, run_evals
from copilot.storage import (
    connect,
    init_db,
    list_audit_events,
    list_traces,
    list_users,
    list_visible_documents,
    get_user,
)


WEB_DIR = ROOT / "web"


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class Handler(BaseHTTPRequestHandler):
    server_version = "SecureEnterpriseCopilot/0.1"

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
            if parsed.path == "/api/query":
                with connect() as conn:
                    result = generate_answer(conn, body.get("user_id", ""), body.get("question", ""))
                    self.send_json(result)
                return
            if parsed.path == "/api/eval/run":
                with connect() as conn:
                    result = run_evals(conn)
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
        with connect() as conn:
            if path == "/api/health":
                self.send_json({"status": "ok", "app": "secure-enterprise-knowledge-copilot"})
                return
            if path == "/api/users":
                self.send_json({"users": list_users(conn)})
                return
            if path == "/api/documents":
                user_id = query.get("user_id", ["alice"])[0]
                user = get_user(conn, user_id)
                if not user:
                    raise ApiError(404, f"Unknown user_id: {user_id}")
                self.send_json({"documents": list_visible_documents(conn, user)})
                return
            if path == "/api/traces":
                limit = int(query.get("limit", ["25"])[0])
                self.send_json({"traces": list_traces(conn, limit=limit)})
                return
            if path == "/api/audit":
                limit = int(query.get("limit", ["50"])[0])
                self.send_json({"events": list_audit_events(conn, limit=limit)})
                return
            if path == "/api/eval/latest":
                self.send_json({"eval_run": latest_eval_run(conn)})
                return
        raise ApiError(404, f"Unknown endpoint: {path}")

    def serve_static(self, path: str) -> None:
        if path in ("", "/"):
            file_path = WEB_DIR / "index.html"
        else:
            requested = path.lstrip("/")
            file_path = (WEB_DIR / requested).resolve()
            if WEB_DIR.resolve() not in file_path.parents and file_path != WEB_DIR.resolve():
                raise ApiError(403, "Forbidden")
        if not file_path.exists() or not file_path.is_file():
            raise ApiError(404, "Not found")

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
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
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--reset", action="store_true", help="Recreate the SQLite database from seed data.")
    args = parser.parse_args()

    init_db(reset=args.reset)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Secure Enterprise Knowledge Copilot running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()

