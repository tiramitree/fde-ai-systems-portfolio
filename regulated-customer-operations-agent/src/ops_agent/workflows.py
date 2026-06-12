from __future__ import annotations

import hashlib
from typing import Any

from .storage import JsonStore, utc_now


WORKFLOW_RUN_SCHEMA_VERSION = "workflow_run_v1"


def _message_sha256(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _outbox_ids_for_approvals(store: JsonStore, approval_ids: list[str]) -> list[str]:
    return _unique(
        [
            item.get("id", "")
            for item in store.state.setdefault("action_outbox", [])
            if item.get("approval_id") in approval_ids
        ]
    )


def start_workflow_run(
    store: JsonStore,
    user_id: str,
    trace_id: str,
    message: str,
    intent: str,
    case_id: str | None,
    model_router: str,
) -> dict[str, Any]:
    workflow_run = {
        "id": f"wf-{len(store.state.setdefault('workflow_runs', [])) + 1:04d}",
        "schema_version": WORKFLOW_RUN_SCHEMA_VERSION,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "user_id": user_id,
        "trace_id": trace_id,
        "case_id": case_id,
        "intent": intent,
        "model_router": model_router,
        "status": "running",
        "stage": "intent_classified",
        "message_sha256": _message_sha256(message),
        "message_characters": len(message),
        "raw_message_returned": False,
        "tool_call_count": 0,
        "approval_ids": [],
        "outbox_ids": [],
        "action_run_ids": [],
        "blocked_action_count": 0,
        "cited_policy_ids": [],
        "waiting_on": None,
        "retryable_outbox_ids": [],
        "dead_lettered_outbox_ids": [],
        "last_result": None,
    }
    store.state["workflow_runs"].append(workflow_run)
    return workflow_run


def get_workflow_run(store: JsonStore, workflow_run_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in store.state.setdefault("workflow_runs", []) if item.get("id") == workflow_run_id),
        None,
    )


def list_workflow_runs(store: JsonStore, limit: int = 25) -> list[dict[str, Any]]:
    runs = sorted(
        store.state.setdefault("workflow_runs", []),
        key=lambda item: item.get("updated_at", item.get("created_at", "")),
        reverse=True,
    )
    return runs[: max(1, min(int(limit), 100))]


def _update_run(workflow_run: dict[str, Any], **changes: Any) -> dict[str, Any]:
    workflow_run.update(changes)
    workflow_run["updated_at"] = utc_now()
    return workflow_run


def record_agent_checkpoint(store: JsonStore, workflow_run_id: str, result: dict[str, Any]) -> dict[str, Any] | None:
    workflow_run = get_workflow_run(store, workflow_run_id)
    if not workflow_run:
        return None

    approval_ids = _unique([approval.get("id", "") for approval in result.get("approvals", [])])
    outbox_ids = _outbox_ids_for_approvals(store, approval_ids)
    blocked_count = len(result.get("blocked_actions", []))
    cited_policy_ids = _unique([policy.get("id", "") for policy in result.get("cited_policies", [])])

    if approval_ids:
        status = "waiting_for_approval"
        stage = "approval_requested"
        waiting_on = {"approval_ids": approval_ids, "outbox_ids": outbox_ids}
        last_result = "approval_required"
    elif blocked_count:
        status = "blocked"
        stage = "governance_refused"
        waiting_on = None
        last_result = "blocked"
    else:
        status = "completed"
        stage = "response_returned"
        waiting_on = None
        last_result = "completed_without_side_effect"

    return _update_run(
        workflow_run,
        status=status,
        stage=stage,
        case_id=result.get("case", {}).get("id") if isinstance(result.get("case"), dict) else workflow_run.get("case_id"),
        tool_call_count=len(result.get("tool_calls", [])),
        approval_ids=approval_ids,
        outbox_ids=outbox_ids,
        blocked_action_count=blocked_count,
        cited_policy_ids=cited_policy_ids,
        waiting_on=waiting_on,
        last_result=last_result,
    )


def _runs_for_refs(store: JsonStore, approval_id: str | None = None, outbox_id: str | None = None) -> list[dict[str, Any]]:
    runs = []
    for workflow_run in store.state.setdefault("workflow_runs", []):
        if approval_id and approval_id in workflow_run.get("approval_ids", []):
            runs.append(workflow_run)
            continue
        if outbox_id and outbox_id in workflow_run.get("outbox_ids", []):
            runs.append(workflow_run)
    return runs


def record_action_dispatch_checkpoint(
    store: JsonStore,
    approval: dict[str, Any],
    outbox_item: dict[str, Any] | None,
    result: str,
    execution: dict[str, Any] | None = None,
) -> None:
    approval_id = approval.get("id")
    outbox_id = outbox_item.get("id") if outbox_item else None
    workflow_runs = _runs_for_refs(store, approval_id=approval_id, outbox_id=outbox_id)
    if not workflow_runs:
        return

    outbox_status = outbox_item.get("status") if outbox_item else None
    if outbox_status == "succeeded":
        status = "succeeded"
        stage = "side_effect_executed"
    elif outbox_status == "retryable_failure":
        status = "dispatch_retryable_failure"
        stage = "waiting_for_retry"
    elif outbox_status == "dead_lettered":
        status = "dispatch_dead_lettered"
        stage = "dead_lettered"
    elif outbox_status == "approval_rejected":
        status = "approval_rejected"
        stage = "approval_rejected"
    elif outbox_status == "approval_expired":
        status = "approval_expired"
        stage = "approval_expired"
    else:
        status = "dispatch_pending"
        stage = "approval_processed"

    for workflow_run in workflow_runs:
        approval_ids = _unique([*workflow_run.get("approval_ids", []), approval_id or ""])
        outbox_ids = _unique([*workflow_run.get("outbox_ids", []), outbox_id or ""])
        action_run_ids = _unique(
            [
                *workflow_run.get("action_run_ids", []),
                execution.get("id", "") if execution else "",
            ]
        )
        retryable_ids = _unique(
            [
                outbox.get("id", "")
                for outbox in store.state.setdefault("action_outbox", [])
                if outbox.get("id") in outbox_ids and outbox.get("status") == "retryable_failure"
            ]
        )
        dead_lettered_ids = _unique(
            [
                outbox.get("id", "")
                for outbox in store.state.setdefault("action_outbox", [])
                if outbox.get("id") in outbox_ids and outbox.get("status") == "dead_lettered"
            ]
        )
        waiting_on = None
        if status == "dispatch_retryable_failure":
            waiting_on = {"outbox_ids": retryable_ids, "operator_action": "retry_dispatch"}
        elif status == "dispatch_pending":
            waiting_on = {"approval_ids": approval_ids, "outbox_ids": outbox_ids}
        elif status == "approval_rejected":
            waiting_on = None
        elif status == "approval_expired":
            waiting_on = None

        _update_run(
            workflow_run,
            status=status,
            stage=stage,
            approval_ids=approval_ids,
            outbox_ids=outbox_ids,
            action_run_ids=action_run_ids,
            retryable_outbox_ids=retryable_ids,
            dead_lettered_outbox_ids=dead_lettered_ids,
            waiting_on=waiting_on,
            last_result=result,
        )
