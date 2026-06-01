from __future__ import annotations

import re
import uuid

from .storage import (
    JsonStore,
    append_audit,
    get_case,
    get_listing,
    get_policy,
    get_product,
    get_seller,
    utc_now,
)


SIDE_EFFECT_TOOLS = {"send_notice", "escalate_case"}
TOOL_PERMISSIONS = {
    "investigator": {
        "search_recall_policy",
        "get_case",
        "search_listings",
        "create_violation",
        "draft_seller_notice",
        "request_approval",
        "schedule_followup",
    },
    "supervisor": {
        "search_recall_policy",
        "get_case",
        "search_listings",
        "create_violation",
        "draft_seller_notice",
        "request_approval",
        "schedule_followup",
        "send_notice",
        "escalate_case",
        "approve_action",
    },
}


def allowed(user: dict, tool_name: str) -> bool:
    return tool_name in TOOL_PERMISSIONS.get(user["role"], set())


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[a-z0-9_-]+", text) if len(token) > 1}


def search_recall_policy(store: JsonStore, query: str) -> list[dict]:
    query_tokens = tokenize(query)
    results = []
    for policy in store.state["policies"]:
        haystack = tokenize(policy["title"] + " " + policy["body"])
        score = len(query_tokens & haystack)
        if score > 0:
            result = dict(policy)
            result["score"] = score
            results.append(result)
    return sorted(results, key=lambda item: item["score"], reverse=True)


def search_listings(store: JsonStore, query: str) -> list[dict]:
    query_tokens = tokenize(query)
    results = []
    for listing in store.state["listings"]:
        product = get_product(store, listing["product_id"]) or {}
        seller = get_seller(store, listing["seller_id"]) or {}
        text = " ".join(
            [
                listing["id"],
                listing["status"],
                listing["url"],
                product.get("id", ""),
                product.get("name", ""),
                product.get("recall_id", ""),
                seller.get("id", ""),
                seller.get("name", ""),
            ]
        )
        score = len(query_tokens & tokenize(text))
        if score > 0:
            result = dict(listing)
            result["product"] = product
            result["seller"] = seller
            result["score"] = score
            results.append(result)
    return sorted(results, key=lambda item: item["score"], reverse=True)


def create_violation(store: JsonStore, case_id: str, listing_id: str, policy_id: str, user_id: str) -> dict:
    case = get_case(store, case_id)
    listing = get_listing(store, listing_id)
    policy = get_policy(store, policy_id)
    if not case or not listing or not policy:
        raise ValueError("case, listing, or policy not found")

    existing = next(
        (
            violation
            for violation in store.state["violations"]
            if violation["case_id"] == case_id and violation["listing_id"] == listing_id
        ),
        None,
    )
    if existing:
        return existing

    violation = {
        "id": f"vio-{len(store.state['violations']) + 1:04d}",
        "case_id": case_id,
        "listing_id": listing_id,
        "policy_id": policy_id,
        "status": "open",
        "created_at": utc_now(),
        "created_by": user_id,
        "reason": "Active marketplace listing for recalled product.",
    }
    store.state["violations"].append(violation)
    case["status"] = "violation_opened"
    append_audit(store, user_id, "violation_created", violation)
    return violation


def draft_seller_notice(store: JsonStore, case_id: str, listing_id: str, policy_id: str) -> dict:
    case = get_case(store, case_id)
    listing = get_listing(store, listing_id)
    product = get_product(store, listing["product_id"]) if listing else None
    seller = get_seller(store, listing["seller_id"]) if listing else None
    policy = get_policy(store, policy_id)
    if not case or not listing or not product or not seller or not policy:
        raise ValueError("cannot draft notice without case, listing, product, seller, and policy")

    body = (
        f"Seller {seller['name']}, our review found active listing {listing['id']} for "
        f"{product['name']} ({product['recall_id']}). Under {policy['title']}, active listings for recalled "
        "products must be removed and documented. Please remove the listing and provide confirmation."
    )
    return {
        "seller_id": seller["id"],
        "listing_id": listing["id"],
        "case_id": case["id"],
        "policy_id": policy["id"],
        "subject": f"Action required: recalled product listing {listing['id']}",
        "body": body,
    }


def request_approval(
    store: JsonStore,
    user_id: str,
    action_type: str,
    payload: dict,
    reason: str,
    idempotency_key: str,
) -> dict:
    existing = next(
        (
            approval
            for approval in store.state["approval_requests"]
            if approval["idempotency_key"] == idempotency_key
        ),
        None,
    )
    if existing:
        return existing

    approval = {
        "id": f"apr-{len(store.state['approval_requests']) + 1:04d}",
        "created_at": utc_now(),
        "requested_by": user_id,
        "action_type": action_type,
        "payload": payload,
        "reason": reason,
        "status": "pending",
        "idempotency_key": idempotency_key,
    }
    store.state["approval_requests"].append(approval)
    append_audit(store, user_id, "approval_requested", approval)
    return approval


def approve_action(store: JsonStore, approval_id: str, approver_id: str) -> dict:
    approval = next(
        (item for item in store.state["approval_requests"] if item["id"] == approval_id),
        None,
    )
    if not approval:
        raise ValueError(f"approval not found: {approval_id}")
    if approval["status"] != "pending":
        return {"approval": approval, "result": "already_processed"}

    action_type = approval["action_type"]
    if action_type == "send_notice":
        notice = {
            "id": f"notice-{len(store.state['notices']) + 1:04d}",
            "created_at": utc_now(),
            "sent_by": approver_id,
            "approval_id": approval_id,
            **approval["payload"],
        }
        store.state["notices"].append(notice)
        approval["status"] = "approved"
        approval["approved_by"] = approver_id
        approval["approved_at"] = utc_now()
        append_audit(store, approver_id, "notice_sent", notice)
        return {"approval": approval, "result": "notice_sent", "notice": notice}

    if action_type == "escalate_case":
        case_id = approval["payload"]["case_id"]
        case = get_case(store, case_id)
        if case:
            case["status"] = "escalated"
        approval["status"] = "approved"
        approval["approved_by"] = approver_id
        approval["approved_at"] = utc_now()
        append_audit(store, approver_id, "case_escalated", approval["payload"])
        return {"approval": approval, "result": "case_escalated", "case": case}

    raise ValueError(f"unsupported approval action: {action_type}")


def schedule_followup(store: JsonStore, user_id: str, case_id: str, days: int = 5) -> dict:
    existing = next(
        (item for item in store.state["followups"] if item["case_id"] == case_id and item["status"] == "scheduled"),
        None,
    )
    if existing:
        return existing
    followup = {
        "id": f"fup-{len(store.state['followups']) + 1:04d}",
        "case_id": case_id,
        "created_at": utc_now(),
        "created_by": user_id,
        "due_in_business_days": days,
        "status": "scheduled",
    }
    store.state["followups"].append(followup)
    append_audit(store, user_id, "followup_scheduled", followup)
    return followup


def direct_side_effect_blocked(tool_name: str, user: dict) -> dict:
    return {
        "tool": tool_name,
        "blocked": True,
        "reason": (
            f"{tool_name} is a side-effect action. User role {user['role']} cannot execute it directly; "
            "the agent must create an approval request."
        ),
    }

