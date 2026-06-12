from __future__ import annotations

import time
import uuid

from .model_gateway import classify_intent_with_openai
from .storage import JsonStore, append_audit, append_trace, get_case, get_user, utc_now
from .tools import (
    approve_action,
    create_violation,
    direct_side_effect_blocked,
    draft_seller_notice,
    public_approval,
    request_approval,
    schedule_followup,
    search_listings,
    search_recall_policy,
)
from .workflows import record_agent_checkpoint, start_workflow_run


INJECTION_MARKERS = [
    "ignore policy",
    "bypass approval",
    "without approval",
    "do not log",
    "hide this",
    "override approval",
]


def classify_intent(message: str) -> tuple[str, str]:
    model_intent = classify_intent_with_openai(message)
    if model_intent:
        return model_intent, "openai"
    lower = message.lower()
    if "approve" in lower and "apr-" in lower:
        return "approve_action", "local"
    if "escalate" in lower:
        return "request_escalation", "local"
    if "send" in lower and "notice" in lower:
        return "request_notice_send", "local"
    if "listing" in lower or "seller" in lower or "recalled" in lower or "recall" in lower:
        return "investigate_listing", "local"
    return "general", "local"


def detect_injection(message: str) -> list[str]:
    lower = message.lower()
    return [marker for marker in INJECTION_MARKERS if marker in lower]


def _latency_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def _dispatch_failure_mode(message: str) -> str | None:
    lower = message.lower()
    if "permanent dispatch failure" in lower or "simulate permanent" in lower:
        return "permanent"
    if "transient dispatch failure" in lower or "simulate dispatch failure" in lower or "simulate outage" in lower:
        return "transient"
    return None


def _with_request_id(payload: dict, request_id: str) -> dict:
    if request_id:
        payload["request_id"] = request_id
    return payload


def _best_policy(policies: list[dict]) -> dict | None:
    return policies[0] if policies else None


def _best_recalled_active_listing(listings: list[dict]) -> dict | None:
    for listing in listings:
        product = listing.get("product", {})
        if listing["status"] == "active" and product.get("recall_status") == "active":
            return listing
    return None


def process_message(store: JsonStore, user_id: str, message: str, case_id: str | None = None, request_id: str = "") -> dict:
    start = time.perf_counter()
    user = get_user(store, user_id)
    if not user:
        raise ValueError(f"unknown user_id: {user_id}")

    trace_id = str(uuid.uuid4())
    intent, model_router = classify_intent(message)
    workflow_run = start_workflow_run(store, user_id, trace_id, message, intent, case_id, model_router)
    injection_hits = detect_injection(message)
    tool_calls = []
    approvals = []
    outputs = []
    blocked_actions = []
    cited_policies = []

    if injection_hits:
        blocked = {
            "reason": "instruction_attempt_to_bypass_governance",
            "markers": injection_hits,
        }
        append_audit(store, user_id, "unsafe_instruction_blocked", _with_request_id({**blocked, "trace_id": trace_id}, request_id))
        response = (
            "I cannot bypass approval, logging, or policy controls. I can investigate the case and create an "
            "approval request for any external side-effect action."
        )
        result = _with_request_id(
            {
                "trace_id": trace_id,
                "intent": intent,
                "response": response,
                "tool_calls": [],
                "approvals": [],
                "blocked_actions": [blocked],
                "cited_policies": [],
                "case": get_case(store, case_id) if case_id else None,
                "model_router": model_router,
            },
            request_id,
        )
        result["latency_ms"] = _latency_ms(start)
        result["workflow_run"] = record_agent_checkpoint(store, workflow_run["id"], result)
        append_trace(
            store,
            _with_request_id(
                {
                    "id": trace_id,
                    "created_at": utc_now(),
                    "user_id": user_id,
                    "message": message,
                    "intent": intent,
                    "result": result,
                },
                request_id,
            ),
        )
        return result

    if intent == "approve_action":
        approval_id = next((token.strip(".,") for token in message.split() if token.startswith("apr-")), "")
        if user["role"] != "supervisor":
            blocked_actions.append(
                {
                    "tool": "approve_action",
                    "blocked": True,
                    "reason": "Only supervisors can approve side-effect actions.",
                }
            )
            response = "Only a supervisor can approve side-effect actions."
        else:
            approval_result = approve_action(store, approval_id, user_id)
            tool_calls.append({"tool": "approve_action", "approval_id": approval_id, "result": approval_result["result"]})
            response = f"Approved {approval_id}; result: {approval_result['result']}."
        result = _with_request_id(
            {
                "trace_id": trace_id,
                "intent": intent,
                "response": response,
                "tool_calls": tool_calls,
                "approvals": approvals,
                "blocked_actions": blocked_actions,
                "cited_policies": cited_policies,
                "case": get_case(store, case_id) if case_id else None,
                "model_router": model_router,
            },
            request_id,
        )
        result["latency_ms"] = _latency_ms(start)
        result["workflow_run"] = record_agent_checkpoint(store, workflow_run["id"], result)
        append_trace(
            store,
            _with_request_id(
                {
                    "id": trace_id,
                    "created_at": utc_now(),
                    "user_id": user_id,
                    "message": message,
                    "intent": intent,
                    "result": result,
                },
                request_id,
            ),
        )
        return result

    policies = search_recall_policy(store, message + " recall compliance seller listing notice escalation")
    policy = _best_policy(policies)
    if policy:
        cited_policies.append({"id": policy["id"], "title": policy["title"], "version": policy["version"]})
    tool_calls.append({"tool": "search_recall_policy", "result_count": len(policies)})

    listings = search_listings(store, message)
    tool_calls.append({"tool": "search_listings", "result_count": len(listings)})
    listing = _best_recalled_active_listing(listings)

    if not case_id and listing:
        case_id = next(
            (
                case["id"]
                for case in store.state["cases"]
                if case["seller_id"] == listing["seller_id"] and case["product_id"] == listing["product_id"]
            ),
            None,
        )
    case = get_case(store, case_id) if case_id else None

    if not listing or not policy or not case:
        response = (
            "I could not find enough case, policy, and active recalled-listing evidence to take action. "
            "Please provide a case ID, seller, product, or listing URL."
        )
    else:
        violation = create_violation(store, case["id"], listing["id"], policy["id"], user_id)
        tool_calls.append({"tool": "create_violation", "violation_id": violation["id"]})
        notice = draft_seller_notice(store, case["id"], listing["id"], policy["id"])
        tool_calls.append({"tool": "draft_seller_notice", "listing_id": listing["id"]})
        followup = schedule_followup(store, user_id, case["id"])
        tool_calls.append({"tool": "schedule_followup", "followup_id": followup["id"]})

        if intent == "request_escalation":
            blocked = direct_side_effect_blocked("escalate_case", user)
            blocked_actions.append(blocked)
            approval = request_approval(
                store,
                user_id,
                "escalate_case",
                {"case_id": case["id"], "reason": "Potential recalled-product listing requires escalation."},
                "Escalation changes case status and requires supervisor approval.",
                f"escalate:{case['id']}",
            )
            approvals.append(public_approval(approval))
            response = (
                f"I opened violation {violation['id']} and created escalation approval {approval['id']}. "
                "The case will not be escalated until a supervisor approves it."
            )
        else:
            blocked = direct_side_effect_blocked("send_notice", user)
            blocked_actions.append(blocked)
            dispatch_failure_mode = _dispatch_failure_mode(message)
            notice_payload = dict(notice)
            idempotency_key = f"send_notice:{case['id']}:{listing['id']}"
            if dispatch_failure_mode:
                notice_payload["dispatch_failure_mode"] = dispatch_failure_mode
                idempotency_key = f"{idempotency_key}:dispatch-{dispatch_failure_mode}"
            approval = request_approval(
                store,
                user_id,
                "send_notice",
                notice_payload,
                "Sending seller notice is an external side-effect action.",
                idempotency_key,
            )
            public_request = public_approval(approval)
            approvals.append(public_request)
            response = (
                f"I found active recalled listing {listing['id']} for {listing['product']['name']}, "
                f"opened violation {violation['id']}, drafted the seller notice, scheduled follow-up "
                f"{followup['id']}, and created approval request {approval['id']} before sending."
            )
            outputs.append({"draft_notice_preview": public_request["dry_run_preview"]})

    result = _with_request_id(
        {
            "trace_id": trace_id,
            "intent": intent,
            "response": response,
            "tool_calls": tool_calls,
            "approvals": approvals,
            "blocked_actions": blocked_actions,
            "cited_policies": cited_policies,
            "outputs": outputs,
            "case": case,
            "model_router": model_router,
        },
        request_id,
    )
    result["latency_ms"] = _latency_ms(start)
    result["workflow_run"] = record_agent_checkpoint(store, workflow_run["id"], result)
    append_trace(
        store,
        _with_request_id(
            {
                "id": trace_id,
                "created_at": utc_now(),
                "user_id": user_id,
                "message": message,
                "intent": intent,
                "result": result,
            },
            request_id,
        ),
    )
    append_audit(store, user_id, "agent_message_processed", _with_request_id({"trace_id": trace_id, "intent": intent}, request_id))
    return result
