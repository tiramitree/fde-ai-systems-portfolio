from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone

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
from .workflows import record_action_dispatch_checkpoint


MAX_OUTBOX_ATTEMPTS = 3
OUTBOX_LEASE_SECONDS = 300
APPROVAL_EXPIRES_DAYS = 2
APPROVAL_POLICY_VERSION = "approval_policy_v1"
DRY_RUN_PREVIEW_SCHEMA_VERSION = "dry_run_preview_v1"
SIDE_EFFECT_TOOLS = {"send_notice", "escalate_case"}
TOOL_REGISTRY_SCHEMA_VERSION = "tool_registry_v1"
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

TOOL_REGISTRY = [
    {
        "name": "search_recall_policy",
        "category": "read",
        "description": "Search recall policy evidence before proposing action.",
        "allowed_roles": ["investigator", "supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": False,
        "credential_scope": "policy:read",
        "idempotency_required": False,
        "audit_event": None,
        "raw_payload_returned": False,
    },
    {
        "name": "search_listings",
        "category": "read",
        "description": "Search marketplace listings and seller/product metadata.",
        "allowed_roles": ["investigator", "supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": False,
        "credential_scope": "listing:read",
        "idempotency_required": False,
        "audit_event": None,
        "raw_payload_returned": False,
    },
    {
        "name": "create_violation",
        "category": "internal_write",
        "description": "Open an internal violation record from grounded case evidence.",
        "allowed_roles": ["investigator", "supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": False,
        "credential_scope": "case:write",
        "idempotency_required": True,
        "audit_event": "violation_created",
        "raw_payload_returned": False,
    },
    {
        "name": "draft_seller_notice",
        "category": "draft",
        "description": "Prepare a seller notice draft without dispatching it.",
        "allowed_roles": ["investigator", "supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": False,
        "credential_scope": "notice:draft",
        "idempotency_required": False,
        "audit_event": None,
        "raw_payload_returned": False,
    },
    {
        "name": "schedule_followup",
        "category": "internal_write",
        "description": "Create an internal follow-up reminder for the case.",
        "allowed_roles": ["investigator", "supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": False,
        "credential_scope": "case:followup",
        "idempotency_required": True,
        "audit_event": "followup_scheduled",
        "raw_payload_returned": False,
    },
    {
        "name": "request_approval",
        "category": "governance_write",
        "description": "Create a supervisor approval request for a side-effect action.",
        "allowed_roles": ["investigator", "supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": True,
        "credential_scope": "approval:write",
        "idempotency_required": True,
        "audit_event": "approval_requested",
        "raw_payload_returned": False,
    },
    {
        "name": "send_notice",
        "category": "side_effect",
        "description": "Dispatch a seller notice through the governed outbox.",
        "allowed_roles": ["supervisor"],
        "side_effect": True,
        "approval_required": True,
        "dry_run_required": True,
        "credential_scope": "seller-notice:send",
        "idempotency_required": True,
        "audit_event": "notice_sent",
        "raw_payload_returned": False,
    },
    {
        "name": "escalate_case",
        "category": "side_effect",
        "description": "Escalate a case through the governed outbox.",
        "allowed_roles": ["supervisor"],
        "side_effect": True,
        "approval_required": True,
        "dry_run_required": True,
        "credential_scope": "case:escalate",
        "idempotency_required": True,
        "audit_event": "case_escalated",
        "raw_payload_returned": False,
    },
    {
        "name": "approve_action",
        "category": "governance_write",
        "description": "Approve a pending side-effect request and dispatch it idempotently.",
        "allowed_roles": ["supervisor"],
        "side_effect": False,
        "approval_required": False,
        "dry_run_required": False,
        "credential_scope": "approval:approve",
        "idempotency_required": True,
        "audit_event": "tool_action_executed",
        "raw_payload_returned": False,
    },
]


def list_tool_registry() -> list[dict]:
    return [dict(item) for item in sorted(TOOL_REGISTRY, key=lambda item: item["name"])]


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
        _ensure_approval_governance_fields(existing)
        _ensure_action_outbox(store, existing)
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
    _ensure_approval_governance_fields(approval)
    store.state["approval_requests"].append(approval)
    outbox_item = _ensure_action_outbox(store, approval)
    append_audit(store, user_id, "approval_requested", public_approval(approval))
    append_audit(store, user_id, "action_outbox_enqueued", outbox_item)
    return approval


def _stable_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _payload_summary(action_type: str, payload: dict) -> dict:
    if action_type == "send_notice":
        body = str(payload.get("body") or "")
        subject = str(payload.get("subject") or "")
        return {
            "case_id": payload.get("case_id"),
            "seller_id": payload.get("seller_id"),
            "listing_id": payload.get("listing_id"),
            "policy_id": payload.get("policy_id"),
            "dispatch_failure_mode": payload.get("dispatch_failure_mode"),
            "subject_sha256": hashlib.sha256(subject.encode("utf-8")).hexdigest(),
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "body_characters": len(body),
            "raw_body_returned": False,
        }
    if action_type == "escalate_case":
        reason = str(payload.get("reason") or "")
        return {
            "case_id": payload.get("case_id"),
            "reason_sha256": hashlib.sha256(reason.encode("utf-8")).hexdigest(),
            "reason_characters": len(reason),
            "raw_reason_returned": False,
        }
    return {"raw_payload_returned": False}


def _approval_expires_at(created_at: str | None = None) -> str:
    if created_at:
        try:
            start = datetime.fromisoformat(created_at)
        except ValueError:
            start = datetime.now(timezone.utc)
    else:
        start = datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return (start + timedelta(days=APPROVAL_EXPIRES_DAYS)).isoformat(timespec="seconds")


def _dry_run_preview(action_type: str, payload: dict) -> dict:
    summary = _payload_summary(action_type, payload)
    preview = {
        "schema_version": DRY_RUN_PREVIEW_SCHEMA_VERSION,
        "action_type": action_type,
        "tool_registry_version": TOOL_REGISTRY_SCHEMA_VERSION,
        "approval_policy": APPROVAL_POLICY_VERSION,
        "raw_payload_returned": False,
    }
    if action_type == "send_notice":
        preview.update(
            {
                "would_send_notice": True,
                "external_side_effect": "seller_notice_dispatch",
                "case_id": summary.get("case_id"),
                "seller_id": summary.get("seller_id"),
                "listing_id": summary.get("listing_id"),
                "policy_id": summary.get("policy_id"),
                "dispatch_failure_mode": summary.get("dispatch_failure_mode"),
                "subject_sha256": summary.get("subject_sha256"),
                "body_sha256": summary.get("body_sha256"),
                "body_characters": summary.get("body_characters"),
                "raw_body_returned": False,
            }
        )
        return preview
    if action_type == "escalate_case":
        preview.update(
            {
                "would_escalate_case": True,
                "external_side_effect": "case_status_escalation",
                "case_id": summary.get("case_id"),
                "reason_sha256": summary.get("reason_sha256"),
                "reason_characters": summary.get("reason_characters"),
                "raw_reason_returned": False,
            }
        )
        return preview
    preview["would_execute"] = False
    return preview


def _decision_summary(reason: str) -> dict:
    clean_reason = str(reason or "")
    return {
        "decision_reason_sha256": hashlib.sha256(clean_reason.encode("utf-8")).hexdigest(),
        "decision_reason_characters": len(clean_reason),
        "raw_decision_reason_returned": False,
    }


def _ensure_approval_governance_fields(approval: dict) -> dict:
    action_type = approval.get("action_type", "")
    payload = approval.get("payload") or {}
    created_at = approval.get("created_at")
    approval.setdefault("approval_policy", APPROVAL_POLICY_VERSION)
    approval.setdefault("tool_registry_version", TOOL_REGISTRY_SCHEMA_VERSION)
    approval.setdefault("owner_role", "supervisor")
    approval.setdefault("review_status", approval.get("status", "pending"))
    approval.setdefault("expires_at", _approval_expires_at(created_at))
    approval.setdefault("payload_sha256", _stable_hash(payload))
    approval.setdefault("payload_summary", _payload_summary(action_type, payload))
    approval.setdefault("dry_run_preview", _dry_run_preview(action_type, payload))
    approval.setdefault("raw_payload_returned", False)
    approval.setdefault("decision_reason_summary", None)
    approval.setdefault("raw_decision_reason_returned", False)
    return approval


def public_approval(approval: dict) -> dict:
    _ensure_approval_governance_fields(approval)
    public_fields = [
        "id",
        "created_at",
        "requested_by",
        "action_type",
        "reason",
        "status",
        "idempotency_key",
        "approval_policy",
        "tool_registry_version",
        "owner_role",
        "review_status",
        "expires_at",
        "payload_sha256",
        "payload_summary",
        "dry_run_preview",
        "raw_payload_returned",
        "approved_by",
        "approved_at",
        "rejected_by",
        "rejected_at",
        "expired_by",
        "expired_at",
        "decision_reason_summary",
        "raw_decision_reason_returned",
    ]
    return {key: approval.get(key) for key in public_fields if key in approval}


def public_action_response(response: dict) -> dict:
    public_response = dict(response)
    approval = public_response.get("approval")
    if isinstance(approval, dict):
        public_response["approval"] = public_approval(approval)
    notice = public_response.pop("notice", None)
    if isinstance(notice, dict):
        public_response["notice_ref"] = {
            "notice_id": notice.get("id"),
            "approval_id": notice.get("approval_id"),
            "case_id": notice.get("case_id"),
            "listing_id": notice.get("listing_id"),
            "seller_id": notice.get("seller_id"),
            "raw_body_returned": False,
        }
    return public_response


def _outbox_key(approval: dict) -> str:
    return f"outbox:{approval['idempotency_key']}"


def _outbox_for_approval(store: JsonStore, approval: dict) -> dict | None:
    key = _outbox_key(approval)
    return next(
        (
            item
            for item in store.state.setdefault("action_outbox", [])
            if item["idempotency_key"] == key
        ),
        None,
    )


def _ensure_action_outbox(store: JsonStore, approval: dict) -> dict:
    _ensure_approval_governance_fields(approval)
    existing = _outbox_for_approval(store, approval)
    if existing:
        existing.setdefault("approval_policy", approval.get("approval_policy"))
        existing.setdefault("tool_registry_version", approval.get("tool_registry_version"))
        existing.setdefault("approval_expires_at", approval.get("expires_at"))
        existing.setdefault("dry_run_preview", approval.get("dry_run_preview"))
        existing.setdefault("review_status", approval.get("review_status"))
        return existing

    item = {
        "id": f"outbox-{len(store.state.setdefault('action_outbox', [])) + 1:04d}",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "approval_id": approval["id"],
        "requested_by": approval["requested_by"],
        "action_type": approval["action_type"],
        "status": "awaiting_approval",
        "result": None,
        "approval_policy": approval["approval_policy"],
        "tool_registry_version": approval["tool_registry_version"],
        "approval_expires_at": approval["expires_at"],
        "review_status": approval["review_status"],
        "idempotency_key": _outbox_key(approval),
        "approval_idempotency_key": approval["idempotency_key"],
        "payload_sha256": _stable_hash(approval["payload"]),
        "payload_summary": _payload_summary(approval["action_type"], approval["payload"]),
        "dry_run_preview": approval["dry_run_preview"],
        "attempt_count": 0,
        "next_attempt_at": None,
        "last_error": None,
        "dead_lettered_at": None,
        "dead_letter_reason": None,
        "lease_id": None,
        "leased_by": None,
        "lease_acquired_at": None,
        "lease_expires_at": None,
        "lease_released_at": None,
        "lease_count": 0,
        "last_lease_id": None,
        "last_leased_by": None,
        "approved_by": None,
        "approved_at": None,
        "rejected_by": None,
        "rejected_at": None,
        "expired_by": None,
        "expired_at": None,
        "execution_id": None,
        "output_refs": {},
        "raw_payload_returned": False,
    }
    store.state["action_outbox"].append(item)
    return item


def _mark_outbox_dispatching(outbox_item: dict, approver_id: str) -> None:
    now = utc_now()
    outbox_item["status"] = "dispatching"
    outbox_item["updated_at"] = now
    outbox_item["approved_by"] = approver_id
    outbox_item["approved_at"] = outbox_item.get("approved_at") or now
    outbox_item["attempt_count"] = int(outbox_item.get("attempt_count") or 0) + 1
    outbox_item["last_error"] = None
    lease_count = int(outbox_item.get("lease_count") or 0) + 1
    lease_id = f"{outbox_item['id']}:lease:{lease_count:04d}"
    lease_expires_at = (datetime.now(timezone.utc) + timedelta(seconds=OUTBOX_LEASE_SECONDS)).isoformat(timespec="seconds")
    outbox_item["lease_id"] = lease_id
    outbox_item["leased_by"] = approver_id
    outbox_item["lease_acquired_at"] = now
    outbox_item["lease_expires_at"] = lease_expires_at
    outbox_item["lease_released_at"] = None
    outbox_item["lease_count"] = lease_count
    outbox_item["last_lease_id"] = lease_id
    outbox_item["last_leased_by"] = approver_id


def _release_outbox_lease(outbox_item: dict) -> None:
    outbox_item["lease_id"] = None
    outbox_item["leased_by"] = None
    outbox_item["lease_acquired_at"] = None
    outbox_item["lease_expires_at"] = None
    outbox_item["lease_released_at"] = utc_now()


def _simulated_dispatch_error(approval: dict, outbox_item: dict) -> dict | None:
    mode = approval.get("payload", {}).get("dispatch_failure_mode")
    attempt_count = int(outbox_item.get("attempt_count") or 0)
    if mode == "transient" and attempt_count == 1:
        return {
            "code": "simulated_transient_tool_outage",
            "message": "Dispatch failed before the side effect was applied.",
            "retryable": True,
        }
    if mode == "permanent":
        return {
            "code": "simulated_permanent_tool_outage",
            "message": "Dispatch failed before the side effect was applied.",
            "retryable": attempt_count < MAX_OUTBOX_ATTEMPTS,
        }
    return None


def _mark_outbox_failed(outbox_item: dict, error: dict) -> None:
    retryable = bool(error.get("retryable")) and int(outbox_item.get("attempt_count") or 0) < MAX_OUTBOX_ATTEMPTS
    outbox_item["updated_at"] = utc_now()
    outbox_item["status"] = "retryable_failure" if retryable else "dead_lettered"
    outbox_item["result"] = "dispatch_failed" if retryable else "dispatch_dead_lettered"
    outbox_item["last_error"] = {
        "code": error.get("code", "dispatch_failed"),
        "message": error.get("message", "Dispatch failed before the side effect was applied."),
        "retryable": retryable,
        "failed_at": utc_now(),
    }
    outbox_item["next_attempt_at"] = utc_now() if retryable else None
    if not retryable:
        outbox_item["dead_lettered_at"] = utc_now()
        outbox_item["dead_letter_reason"] = outbox_item["last_error"]["code"]
    _release_outbox_lease(outbox_item)


def _mark_outbox_succeeded(outbox_item: dict, execution: dict, result: str, output_refs: dict) -> None:
    outbox_item["status"] = "succeeded"
    outbox_item["updated_at"] = utc_now()
    outbox_item["result"] = result
    outbox_item["execution_id"] = execution["id"]
    outbox_item["executed_at"] = execution["executed_at"]
    outbox_item["output_refs"] = output_refs
    outbox_item["next_attempt_at"] = None
    outbox_item["last_error"] = None
    _release_outbox_lease(outbox_item)


def _record_action_run(
    store: JsonStore,
    approval: dict,
    approver_id: str,
    result: str,
    output_refs: dict,
) -> dict:
    action_type = approval["action_type"]
    execution_key = f"execute:{approval['idempotency_key']}"
    existing = next(
        (
            run
            for run in store.state.setdefault("action_runs", [])
            if run["idempotency_key"] == execution_key
        ),
        None,
    )
    if existing:
        return existing

    run = {
        "id": f"run-{len(store.state['action_runs']) + 1:04d}",
        "created_at": utc_now(),
        "executed_at": utc_now(),
        "approval_id": approval["id"],
        "requested_by": approval["requested_by"],
        "executed_by": approver_id,
        "action_type": action_type,
        "status": "succeeded",
        "result": result,
        "approval_policy": approval.get("approval_policy", APPROVAL_POLICY_VERSION),
        "tool_registry_version": approval.get("tool_registry_version", TOOL_REGISTRY_SCHEMA_VERSION),
        "idempotency_key": execution_key,
        "approval_idempotency_key": approval["idempotency_key"],
        "payload_sha256": _stable_hash(approval["payload"]),
        "payload_summary": _payload_summary(action_type, approval["payload"]),
        "dry_run_preview": approval.get("dry_run_preview", _dry_run_preview(action_type, approval["payload"])),
        "raw_payload_returned": False,
        "output_refs": output_refs,
    }
    store.state["action_runs"].append(run)
    append_audit(store, approver_id, "tool_action_executed", run)
    return run


def _execution_for_approval(store: JsonStore, approval: dict) -> dict | None:
    execution_key = f"execute:{approval['idempotency_key']}"
    return next(
        (
            run
            for run in store.state.setdefault("action_runs", [])
            if run["idempotency_key"] == execution_key
        ),
        None,
    )


def _approval_for_outbox(store: JsonStore, outbox_item: dict) -> dict | None:
    return next(
        (
            approval
            for approval in store.state.setdefault("approval_requests", [])
            if approval["id"] == outbox_item.get("approval_id")
        ),
        None,
    )


def _mark_approval_approved(approval: dict, approver_id: str) -> None:
    approval["status"] = "approved"
    approval["review_status"] = "approved"
    approval["approved_by"] = approver_id
    approval["approved_at"] = approval.get("approved_at") or utc_now()


def _mark_approval_rejected(approval: dict, reviewer_id: str, reason: str) -> None:
    approval["status"] = "rejected"
    approval["review_status"] = "rejected"
    approval["rejected_by"] = reviewer_id
    approval["rejected_at"] = approval.get("rejected_at") or utc_now()
    approval["decision_reason_summary"] = _decision_summary(reason)
    approval["raw_decision_reason_returned"] = False


def _mark_approval_expired(approval: dict, operator_id: str, reason: str) -> None:
    approval["status"] = "expired"
    approval["review_status"] = "expired"
    approval["expired_by"] = operator_id
    approval["expired_at"] = approval.get("expired_at") or utc_now()
    approval["decision_reason_summary"] = _decision_summary(reason)
    approval["raw_decision_reason_returned"] = False


def _mark_outbox_review_closed(outbox_item: dict, status: str, result: str, actor_id: str) -> None:
    now = utc_now()
    outbox_item["status"] = status
    outbox_item["result"] = result
    outbox_item["updated_at"] = now
    outbox_item["review_status"] = status.replace("approval_", "")
    outbox_item["next_attempt_at"] = None
    outbox_item["last_error"] = None
    outbox_item["lease_id"] = None
    outbox_item["leased_by"] = None
    outbox_item["lease_acquired_at"] = None
    outbox_item["lease_expires_at"] = None
    outbox_item["lease_released_at"] = outbox_item.get("lease_released_at") or now
    if status == "approval_rejected":
        outbox_item["rejected_by"] = actor_id
        outbox_item["rejected_at"] = now
    if status == "approval_expired":
        outbox_item["expired_by"] = actor_id
        outbox_item["expired_at"] = now


def _dispatch_approved_action(store: JsonStore, approval: dict, actor_id: str, outbox_item: dict) -> dict:
    _mark_outbox_dispatching(outbox_item, actor_id)
    simulated_error = _simulated_dispatch_error(approval, outbox_item)
    if simulated_error:
        _mark_outbox_failed(outbox_item, simulated_error)
        audit_action = "action_outbox_retryable_failure" if outbox_item["status"] == "retryable_failure" else "action_outbox_dead_lettered"
        append_audit(store, actor_id, audit_action, outbox_item)
        response = {
            "approval": approval,
            "result": outbox_item["result"],
            "execution": None,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], None)
        return response

    existing_execution = _execution_for_approval(store, approval)
    if existing_execution:
        _mark_outbox_succeeded(outbox_item, existing_execution, existing_execution["result"], existing_execution["output_refs"])
        response = {
            "approval": approval,
            "result": "already_executed",
            "execution": existing_execution,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], existing_execution)
        return response

    action_type = approval["action_type"]
    if action_type == "send_notice":
        notice = {
            "id": f"notice-{len(store.state['notices']) + 1:04d}",
            "created_at": utc_now(),
            "sent_by": actor_id,
            "approval_id": approval["id"],
            **approval["payload"],
        }
        store.state["notices"].append(notice)
        execution = _record_action_run(
            store,
            approval,
            actor_id,
            "notice_sent",
            {
                "notice_id": notice["id"],
                "case_id": notice["case_id"],
                "listing_id": notice["listing_id"],
                "seller_id": notice["seller_id"],
            },
        )
        _mark_outbox_succeeded(outbox_item, execution, "notice_sent", execution["output_refs"])
        append_audit(
            store,
            actor_id,
            "notice_sent",
            {
                "notice_id": notice["id"],
                "approval_id": approval["id"],
                "output_refs": execution["output_refs"],
                "raw_body_returned": False,
            },
        )
        append_audit(store, actor_id, "action_outbox_succeeded", outbox_item)
        response = {
            "approval": approval,
            "result": "notice_sent",
            "notice": notice,
            "execution": execution,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], execution)
        return response

    if action_type == "escalate_case":
        case_id = approval["payload"]["case_id"]
        case = get_case(store, case_id)
        if case:
            case["status"] = "escalated"
        execution = _record_action_run(
            store,
            approval,
            actor_id,
            "case_escalated",
            {
                "case_id": case_id,
                "case_status": case.get("status") if case else None,
            },
        )
        _mark_outbox_succeeded(outbox_item, execution, "case_escalated", execution["output_refs"])
        append_audit(
            store,
            actor_id,
            "case_escalated",
            {
                "approval_id": approval["id"],
                "output_refs": execution["output_refs"],
                "raw_reason_returned": False,
            },
        )
        append_audit(store, actor_id, "action_outbox_succeeded", outbox_item)
        response = {
            "approval": approval,
            "result": "case_escalated",
            "case": case,
            "execution": execution,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], execution)
        return response

    _mark_outbox_failed(
        outbox_item,
        {
            "code": "unsupported_action_type",
            "message": "Approval references an unsupported side-effect action.",
            "retryable": False,
        },
    )
    append_audit(store, actor_id, "action_outbox_dead_lettered", outbox_item)
    response = {
        "approval": approval,
        "result": "dispatch_dead_lettered",
        "execution": None,
        "outbox_item": outbox_item,
    }
    record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], None)
    return response


def approve_action(store: JsonStore, approval_id: str, approver_id: str) -> dict:
    approval = next(
        (item for item in store.state["approval_requests"] if item["id"] == approval_id),
        None,
    )
    if not approval:
        raise ValueError(f"approval not found: {approval_id}")
    _ensure_approval_governance_fields(approval)
    if approval["status"] != "pending":
        execution = _execution_for_approval(store, approval)
        outbox_item = _outbox_for_approval(store, approval)
        if execution:
            result = "already_processed"
        elif approval["status"] == "rejected":
            result = "approval_rejected"
        elif approval["status"] == "expired":
            result = "approval_expired"
        else:
            result = "dispatch_pending_retry"
        response = {
            "approval": approval,
            "result": result,
            "execution": execution,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], execution)
        return response

    outbox_item = _ensure_action_outbox(store, approval)
    _mark_approval_approved(approval, approver_id)
    return _dispatch_approved_action(store, approval, approver_id, outbox_item)


def reject_approval(store: JsonStore, approval_id: str, reviewer_id: str, reason: str = "") -> dict:
    approval = next(
        (item for item in store.state["approval_requests"] if item["id"] == approval_id),
        None,
    )
    if not approval:
        raise ValueError(f"approval not found: {approval_id}")
    _ensure_approval_governance_fields(approval)
    outbox_item = _ensure_action_outbox(store, approval)
    if approval["status"] != "pending":
        execution = _execution_for_approval(store, approval)
        result = f"approval_{approval['status']}" if approval["status"] in {"rejected", "expired"} else "already_processed"
        response = {"approval": approval, "result": result, "execution": execution, "outbox_item": outbox_item}
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], execution)
        return response

    _mark_approval_rejected(approval, reviewer_id, reason)
    _mark_outbox_review_closed(outbox_item, "approval_rejected", "approval_rejected", reviewer_id)
    append_audit(store, reviewer_id, "approval_rejected", public_approval(approval))
    append_audit(store, reviewer_id, "action_outbox_approval_rejected", outbox_item)
    response = {
        "approval": approval,
        "result": "approval_rejected",
        "execution": None,
        "outbox_item": outbox_item,
    }
    record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], None)
    return response


def expire_approval(store: JsonStore, approval_id: str, operator_id: str, reason: str = "approval_window_expired") -> dict:
    approval = next(
        (item for item in store.state["approval_requests"] if item["id"] == approval_id),
        None,
    )
    if not approval:
        raise ValueError(f"approval not found: {approval_id}")
    _ensure_approval_governance_fields(approval)
    outbox_item = _ensure_action_outbox(store, approval)
    if approval["status"] != "pending":
        execution = _execution_for_approval(store, approval)
        result = f"approval_{approval['status']}" if approval["status"] in {"rejected", "expired"} else "already_processed"
        response = {"approval": approval, "result": result, "execution": execution, "outbox_item": outbox_item}
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], execution)
        return response

    _mark_approval_expired(approval, operator_id, reason)
    _mark_outbox_review_closed(outbox_item, "approval_expired", "approval_expired", operator_id)
    append_audit(store, operator_id, "approval_expired", public_approval(approval))
    append_audit(store, operator_id, "action_outbox_approval_expired", outbox_item)
    response = {
        "approval": approval,
        "result": "approval_expired",
        "execution": None,
        "outbox_item": outbox_item,
    }
    record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], None)
    return response


def retry_action_outbox(store: JsonStore, outbox_id: str, operator_id: str) -> dict:
    outbox_item = next(
        (item for item in store.state.setdefault("action_outbox", []) if item["id"] == outbox_id),
        None,
    )
    if not outbox_item:
        raise ValueError(f"action outbox item not found: {outbox_id}")
    approval = _approval_for_outbox(store, outbox_item)
    if not approval:
        raise ValueError(f"approval not found for outbox item: {outbox_id}")
    if outbox_item["status"] == "succeeded":
        execution = _execution_for_approval(store, approval)
        response = {
            "approval": approval,
            "result": "already_succeeded",
            "execution": execution,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], execution)
        return response
    if outbox_item["status"] == "dead_lettered":
        response = {
            "approval": approval,
            "result": "dead_lettered",
            "execution": None,
            "outbox_item": outbox_item,
        }
        record_action_dispatch_checkpoint(store, approval, outbox_item, response["result"], None)
        return response
    if outbox_item["status"] != "retryable_failure":
        raise ValueError(f"action outbox item is not retryable: {outbox_id}")
    return _dispatch_approved_action(store, approval, operator_id, outbox_item)


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
