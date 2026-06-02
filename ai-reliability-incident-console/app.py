from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from reliability_console.api import ApiError, ReliabilityApi
from reliability_console.storage import init_state


WEB_DIR = ROOT / "web"
API = ReliabilityApi()


class Handler(BaseHTTPRequestHandler):
    server_version = "AIReliabilityIncidentConsole/0.1"

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/"):
                self.send_json(API.get(parsed.path, API.parse_query(parsed.query)))
            else:
                self.serve_static(parsed.path)
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except Exception:
            self.send_json({"error": "Internal server error"}, 500)

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            body = json.loads(raw or "{}")
            self.send_json(API.post(parsed.path, body))
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON body"}, 400)
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except Exception:
            self.send_json({"error": "Internal server error"}, 500)

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
        if content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(data)

    def send_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'",
        )

    def log_message(self, fmt: str, *args) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8780)
    parser.add_argument("--reset", action="store_true", help="Recreate runtime state from seed data.")
    args = parser.parse_args()

    init_state(reset=args.reset)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AI Reliability Incident Console running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
