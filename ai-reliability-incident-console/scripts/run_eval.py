from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from reliability_console.evals import run_evals_from_fresh_state


def main() -> int:
    result = run_evals_from_fresh_state()
    print(json.dumps(result, indent=2))
    return 0 if result["metrics"]["passed_cases"] == result["metrics"]["total_cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
