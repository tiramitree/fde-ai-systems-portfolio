from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_trace_eval_candidates import build_payload, collect_candidates, write_artifacts  # noqa: E402


REQUIRED_PROJECTS = {
    "secure-enterprise-knowledge-copilot",
    "regulated-customer-operations-agent",
    "ai-reliability-incident-console",
}
REQUIRED_CATEGORIES = {
    "p1_permission_abstain",
    "p1_prompt_injection_abstain",
    "p1_grounded_citation_answer",
    "p2_side_effect_requires_approval",
    "p2_governance_bypass_refusal",
    "p3_release_block_from_failed_eval",
    "p3_monitor_only_eval_signal",
}
PRIVATE_MARKERS = [
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\b" + "g" + r"ho_[A-Za-z0-9_]+\b"),
    re.compile(r"\b" + "s" + r"k-[A-Za-z0-9_-]+\b"),
    re.compile("One" + "Drive", re.IGNORECASE),
    re.compile("wx" + "id_", re.IGNORECASE),
]


def check(condition: bool, name: str, detail: str) -> bool:
    prefix = "[PASS]" if condition else "[FAIL]"
    print(f"{prefix} {name}: {detail}")
    return condition


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def has_private_marker(value: Any) -> bool:
    text = json_text(value)
    return any(pattern.search(text) for pattern in PRIVATE_MARKERS)


def valid_candidate(candidate: dict[str, Any]) -> bool:
    suggested = candidate.get("suggested_eval", {})
    evidence = candidate.get("evidence", {})
    if candidate.get("review_status") != "needs_human_review":
        return False
    if not all(candidate.get(key) for key in ("id", "project", "category", "risk", "reason", "source_trace_id")):
        return False
    if not suggested.get("id") or not suggested.get("expected"):
        return False
    if not isinstance(evidence, dict) or not evidence:
        return False
    if has_private_marker(candidate):
        return False
    return True


def main() -> int:
    candidates = collect_candidates()
    payload = build_payload(candidates)
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        write_artifacts(out_dir, payload)
        json_payload = json.loads((out_dir / "trace_eval_candidates.json").read_text(encoding="utf-8"))
        md_text = (out_dir / "trace_eval_candidates.md").read_text(encoding="utf-8")

    projects = set(payload["summary"]["projects"])
    categories = set(payload["summary"]["categories"])
    checks = [
        check(bool(candidates), "candidates generated", f"count={len(candidates)}"),
        check(REQUIRED_PROJECTS.issubset(projects), "project coverage", ", ".join(sorted(projects))),
        check(REQUIRED_CATEGORIES.issubset(categories), "category coverage", ", ".join(sorted(categories))),
        check(json_payload["summary"] == payload["summary"], "JSON artifact summary", json_text(json_payload["summary"])),
        check("Trace-To-Eval Candidates" in md_text, "Markdown artifact title", "found"),
        check(
            all(valid_candidate(item) for item in candidates),
            "candidate shape and safety",
            f"valid={sum(1 for item in candidates if valid_candidate(item))}/{len(candidates)}",
        ),
        check(
            all(item["id"].startswith("trace-eval-") for item in candidates),
            "candidate ids are review-only",
            "trace-eval-*",
        ),
        check(
            all("source_trace_id" in item and item["source_trace_id"] for item in candidates),
            "trace linkage",
            f"linked={sum(1 for item in candidates if item.get('source_trace_id'))}/{len(candidates)}",
        ),
    ]

    p1_permission = [item for item in candidates if item["category"] == "p1_permission_abstain"]
    p1_injection = [item for item in candidates if item["category"] == "p1_prompt_injection_abstain"]
    p2_bypass = [item for item in candidates if item["category"] == "p2_governance_bypass_refusal"]
    p3_block = [item for item in candidates if item["category"] == "p3_release_block_from_failed_eval"]
    checks.extend(
        [
            check(
                all(
                    item["suggested_eval"]["expected"].get("retrieval", {}).get("min_permission_blocked_count") == 1
                    for item in p1_permission
                ),
                "P1 permission candidates preserve denied-count invariant",
                f"count={len(p1_permission)}",
            ),
            check(
                all(item["suggested_eval"]["expected"].get("requires_security_event") is True for item in p1_injection),
                "P1 injection candidates require security events",
                f"count={len(p1_injection)}",
            ),
            check(
                all(item["suggested_eval"]["expected"].get("must_refuse") is True for item in p2_bypass),
                "P2 bypass candidates require refusal",
                f"count={len(p2_bypass)}",
            ),
            check(
                all(item["suggested_eval"]["expected"].get("release_blocked") is True for item in p3_block),
                "P3 release-block candidates require rollout block",
                f"count={len(p3_block)}",
            ),
        ]
    )

    passed = sum(1 for item in checks if item)
    print(f"\nTrace-to-eval checks: {passed}/{len(checks)} passed")
    if not all(checks):
        print("Run python -B scripts/dev.py replay or observability before this gate if no candidates were generated.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
