from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
INTENTS = ["approve_action", "request_escalation", "request_notice_send", "investigate_listing", "general"]


def should_use_openai_router() -> bool:
    return os.getenv("OPS_AGENT_MODEL_ROUTER", "local").lower() == "openai" and bool(os.getenv("OPENAI_API_KEY"))


def _extract_output_text(response: dict) -> str:
    if response.get("output_text"):
        return response["output_text"]
    parts = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text") or content.get("output_text")
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def classify_intent_with_openai(message: str) -> str | None:
    """Optional OpenAI router. Deterministic governance checks remain outside the model."""
    if not should_use_openai_router():
        return None

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"intent": {"type": "string", "enum": INTENTS}},
        "required": ["intent"],
    }
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-5.5"),
        "input": [
            {
                "role": "system",
                "content": (
                    "Classify the customer-operations request into exactly one intent. "
                    "Do not decide approvals or execute tools."
                ),
            },
            {"role": "user", "content": message},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "ops_agent_intent",
                "strict": True,
                "schema": schema,
            }
        },
    }
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = json.loads(response.read().decode("utf-8"))
        parsed = json.loads(_extract_output_text(raw))
        intent = parsed.get("intent")
        return intent if intent in INTENTS else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError):
        return None

