from __future__ import annotations

import json
import sys
from urllib.request import urlopen


URLS = [
    "http://127.0.0.1:8765/api/health",
    "http://127.0.0.1:8770/api/health",
]


def main() -> int:
    failed = False
    for url in URLS:
        try:
            with urlopen(url, timeout=5) as response:
                body = json.loads(response.read().decode("utf-8"))
                print(f"{url}: {body['status']} ({body['app']})")
        except Exception as exc:
            failed = True
            print(f"{url}: failed - {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

