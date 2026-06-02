from __future__ import annotations

import uuid

from .storage import (
    JsonStore,
    append_audit,
    append_trace,
    append_triage_decision,
    get_eval_run,
    get_incident,
    get_release,
    get_user,
    utc_now,
)


HIGH_RISK_SIGNALS = {
    "unauthorized_answer",
    "missing_citation",
    "prompt_injection_bypass",
    "side_effect_without_approval",
}


def failed_eval_cases(eval_run: dict | None, incident: dict) -> list[dict]:
    if not eval_run:
        return []
    signal_ids = set(incident.get("linked_eval_case_ids", []))
    rows = [case for case in eval_run.get("cases", []) if not case.get("passed")]
    if signal_ids:
        matched = [case for case in rows if case.get("id") in signal_ids]
        if matched:
            return matched
    return rows


def severity_rank(severity: str) -> int:
    return {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(severity, 0)


def root_cause_for(incident: dict, failures: list[dict]) -> str:
    categories = {incident.get("category", "")}
    categories.update(str(case.get("category", "")) for case in failures)
    if "unauthorized_answer" in categories:
        return "permission filtering or evidence gating regressed before answer generation"
    if "missing_citation" in categories:
        return "answer construction drifted away from citation-required response shape"
    if "prompt_injection_bypass" in categories:
        return "unsafe retrieved or user instruction was not rejected before model-facing work"
    if "side_effect_without_approval" in categories:
        return "tool authorization boundary failed to hold side effects behind approval"
    return "release behavior drifted from the eval contract and needs owner review"


def remediation_steps(incident: dict, failures: list[dict], release_blocked: bool) -> list[str]:
    steps = [
        "open the linked traces and compare failing eval inputs against the release diff",
        "rerun the targeted eval slice before changing user-visible copy",
    ]
    categories = {incident.get("category", "")}
    categories.update(str(case.get("category", "")) for case in failures)
    if release_blocked:
        steps.insert(0, "pause or roll back the canary release before widening traffic")
    if "unauthorized_answer" in categories:
        steps.append("inspect retrieval filters and confirm unauthorized evidence never reaches generation")
    if "missing_citation" in categories:
        steps.append("restore citation-required answer schema and reject unsupported answers")
    if "prompt_injection_bypass" in categories:
        steps.append("add a red-team eval for the bypass phrase and block unsafe retrieved text")
    if "side_effect_without_approval" in categories:
        steps.append("move side-effect execution behind deterministic approval checks")
    steps.append("attach the new passing eval run to the release notes before resuming rollout")
    return steps


def triage_incident(store: JsonStore, user_id: str, release_id: str, incident_id: str) -> dict:
    user = get_user(store, user_id)
    if not user:
        raise ValueError(f"Unknown user_id: {user_id}")
    release = get_release(store, release_id)
    if not release:
        raise ValueError(f"Unknown release_id: {release_id}")
    incident = get_incident(store, incident_id)
    if not incident:
        raise ValueError(f"Unknown incident_id: {incident_id}")
    if incident.get("release_id") != release_id:
        raise ValueError(f"Incident {incident_id} is not linked to release {release_id}")

    eval_run = get_eval_run(store, release_id)
    failures = failed_eval_cases(eval_run, incident)
    high_risk = incident.get("category") in HIGH_RISK_SIGNALS or any(
        failure.get("category") in HIGH_RISK_SIGNALS for failure in failures
    )
    release_blocked = incident.get("status") == "open" and (
        severity_rank(incident.get("severity", "")) >= 3 or high_risk or bool(failures)
    )
    severity = "critical" if high_risk and severity_rank(incident.get("severity", "")) >= 3 else incident.get("severity", "medium")
    recommendation = "block_release" if release_blocked else "monitor"
    trace_id = str(uuid.uuid4())
    decision = {
        "trace_id": trace_id,
        "created_at": utc_now(),
        "user_id": user_id,
        "release_id": release_id,
        "incident_id": incident_id,
        "severity": severity,
        "recommendation": recommendation,
        "release_blocked": release_blocked,
        "root_cause": root_cause_for(incident, failures),
        "confidence": 0.91 if failures else 0.72,
    }
    response = {
        "trace_id": trace_id,
        "release": release,
        "incident": incident,
        "decision": decision,
        "failed_evals": failures,
        "remediation_steps": remediation_steps(incident, failures, release_blocked),
        "evidence": {
            "eval_run_id": eval_run.get("id") if eval_run else None,
            "linked_eval_case_ids": [case["id"] for case in failures],
            "runbook_ids": incident.get("runbook_ids", []),
            "signals": incident.get("signals", []),
        },
    }
    append_triage_decision(store, decision)
    append_trace(
        store,
        {
            "id": trace_id,
            "created_at": decision["created_at"],
            "user_id": user_id,
            "release_id": release_id,
            "incident_id": incident_id,
            "result": {
                "recommendation": recommendation,
                "release_blocked": release_blocked,
                "failed_eval_count": len(failures),
            },
        },
    )
    append_audit(
        store,
        user_id,
        "incident_triaged",
        {
            "trace_id": trace_id,
            "release_id": release_id,
            "incident_id": incident_id,
            "recommendation": recommendation,
        },
    )
    return response
