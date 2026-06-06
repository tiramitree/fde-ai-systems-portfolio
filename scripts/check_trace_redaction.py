from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_trace_eval_candidates import project_1_candidates  # noqa: E402
from export_traces_otel import REDACTION_POLICY, copilot_span, resource_span  # noqa: E402
from trace_redaction import redact_text  # noqa: E402


def check(condition: bool, name: str, detail: str) -> bool:
    prefix = "[PASS]" if condition else "[FAIL]"
    print(f"{prefix} {name}: {detail}")
    return condition


def raw_sensitive_values() -> dict[str, str]:
    return {
        "email": "alex" + "@example.com",
        "secret_assignment": "token=" + "demo-secret-value-123",
        "api_key": "api_key:" + "demo-key-value-456",
        "provider_key": "s" + "k-" + "demoRedactionKey123456",
        "github_key": "g" + "ho_" + "demoRedactionToken123456",
        "path": "C:" + "\\Users\\alex\\secrets\\notes.txt",
        "sync_path": "One" + "Drive" + "\\private\\source.md",
        "private_id": "wx" + "id_" + "private123",
        "ssn": "123-45-6789",
        "phone": "+1 415 555 0199",
    }


def contains_any_raw(value: Any, raw_values: dict[str, str]) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return any(raw in text for raw in raw_values.values())


def sample_copilot_trace(raw_values: dict[str, str]) -> dict[str, Any]:
    question = (
        f"Can you use {raw_values['email']} and {raw_values['secret_assignment']} "
        f"from {raw_values['path']}?"
    )
    return {
        "id": "trace-redaction-demo-001",
        "created_at": "2026-06-07T00:00:00+00:00",
        "user_id": raw_values["email"],
        "question": question,
        "payload": {
            "retrieval": {
                "permission_blocked_count": 0,
                "query_tokens": ["contact", raw_values["email"]],
                "hits": [{"doc_id": "public-demo-doc"}],
                "profile": {
                    "source_lifecycle_policy": "active_sources_only",
                    "stale_filtered_count": 0,
                },
            },
            "output": {
                "model_provider": "local",
                "abstain_reason": None,
                "security_events": [],
                "citations": [
                    {
                        "doc_id": "public-demo-doc",
                        "chunk_id": "public-demo-doc::chunk-1",
                        "title": "Demo Source",
                        "score": 1.0,
                        "source_span": {"text_unit": "normalized_text", "start_line": 1, "end_line": 1},
                        "evidence_excerpt": (
                            f"Call {raw_values['phone']} with {raw_values['api_key']} "
                            f"and {raw_values['sync_path']}"
                        ),
                        "evidence_spans": [
                            {
                                "text": f"Use {raw_values['ssn']} and {raw_values['private_id']}.",
                                "source_span": {"text_unit": "normalized_text", "start_line": 1, "end_line": 1},
                            }
                        ],
                    }
                ],
            },
        },
    }


def main() -> int:
    raw_values = raw_sensitive_values()
    sample_text = " ".join(raw_values.values())
    redacted_text = redact_text(sample_text)

    trace = sample_copilot_trace(raw_values)
    span = copilot_span("secure-enterprise-knowledge-copilot", trace)
    payload = {"resourceSpans": [resource_span({"name": "secure-enterprise-knowledge-copilot"}, [span])]}
    candidates = project_1_candidates({"traces": [trace], "audit_events": []})

    checks = [
        check(not contains_any_raw(redacted_text, raw_values), "text redaction", "raw markers removed"),
        check("[REDACTED_EMAIL]" in redacted_text, "email placeholder", "present"),
        check("[REDACTED_SECRET]" in redacted_text, "secret placeholder", "present"),
        check("[REDACTED_PATH]" in redacted_text, "path placeholder", "present"),
        check(not contains_any_raw(payload, raw_values), "OTel payload redaction", "raw markers removed"),
        check(REDACTION_POLICY in json.dumps(payload, sort_keys=True), "OTel redaction policy", REDACTION_POLICY),
        check(bool(candidates), "trace-to-eval candidate generated", f"count={len(candidates)}"),
        check(not contains_any_raw(candidates, raw_values), "trace-to-eval redaction", "raw markers removed"),
    ]

    passed = sum(1 for item in checks if item)
    print(f"\nTrace redaction checks: {passed}/{len(checks)} passed")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
