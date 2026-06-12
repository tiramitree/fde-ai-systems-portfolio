import { byId, clear, element, renderList, tag } from "./dom.js";
import { traceHash } from "./traceLinks.js";

export function populateUserSelect(users, selectedUser) {
  const select = byId("userSelect");
  clear(select);
  users.forEach((user) => {
    const option = element("option", { textContent: `${user.name} (${user.role})` });
    option.value = user.id;
    select.append(option);
  });
  select.value = selectedUser;
}

export function populateCaseSelect(cases, selectedCase) {
  const select = byId("caseSelect");
  clear(select);
  cases.forEach((caseItem) => {
    const option = element("option", { textContent: caseItem.id });
    option.value = caseItem.id;
    select.append(option);
  });
  select.value = selectedCase;
}

export function renderCaseSummary(cases, selectedCase) {
  const caseItem = cases.find((item) => item.id === selectedCase);
  const container = byId("caseSummary");
  clear(container);
  if (!caseItem) {
    container.textContent = "No case loaded.";
    return;
  }
  container.append(
    element("strong", { textContent: caseItem.id }),
    element("br"),
    document.createTextNode(caseItem.summary),
    element("br"),
    tag(caseItem.status)
  );
}

export function renderDecision(data) {
  const decision = byId("decision");
  clear(decision);
  const policyTags = data.cited_policies.map((policy) => tag(policy.id));
  decision.append(
    element("p", { textContent: data.response }),
    element("p", {}, [tag(data.intent), ...policyTags])
  );

  if (data.approvals.length) {
    decision.append(
      element("p", {}, [tag(`approval ${data.approvals[0].id}`), tag(data.approvals[0].status)])
    );
  }
  if (data.blocked_actions.length) {
    decision.append(
      element("p", {}, [
        tag("blocked side effect", "warn"),
        document.createTextNode(` ${data.blocked_actions[0].reason || "blocked"}`),
      ])
    );
  }

  byId("trace").textContent = JSON.stringify(
    {
      trace_id: data.trace_id,
      intent: data.intent,
      tool_calls: data.tool_calls,
      approvals: data.approvals,
      blocked_actions: data.blocked_actions,
      outputs: data.outputs,
      workflow_run: data.workflow_run,
    },
    null,
    2
  );
}

export function renderToolRegistry(tools) {
  renderList(
    byId("toolRegistry"),
    tools,
    (tool) => {
      const children = [
        element("strong", { textContent: tool.name }),
        element("span", { textContent: tool.category }),
        element("br"),
        tag(tool.allowed_roles.join("/")),
      ];
      if (tool.side_effect) {
        children.push(tag("side effect", "warn"));
      }
      if (tool.approval_required) {
        children.push(tag("approval"));
      }
      if (tool.dry_run_required) {
        children.push(tag("dry-run"));
      }
      return element("div", { className: "item" }, children);
    },
    "No tools registered."
  );
}

export function renderApprovals(approvals, onApprove, onReject) {
  renderList(
    byId("approvals"),
    approvals,
    (approval) => {
      const preview = approval.dry_run_preview || {};
      const children = [
        element("strong", { textContent: `${approval.id} ${approval.action_type}` }),
        element("span", { textContent: approval.reason }),
        element("br"),
        tag(approval.status),
        tag(approval.requested_by),
        tag(approval.owner_role || "supervisor"),
        tag(`expires ${approval.expires_at || "unknown"}`),
      ];
      if (preview.body_sha256) {
        children.push(tag(`body ${preview.body_sha256.slice(0, 8)}`));
      }
      if (preview.reason_sha256) {
        children.push(tag(`reason ${preview.reason_sha256.slice(0, 8)}`));
      }
      if (approval.decision_reason_summary?.decision_reason_sha256) {
        children.push(tag(`decision ${approval.decision_reason_summary.decision_reason_sha256.slice(0, 8)}`));
      }
      if (approval.status === "pending") {
        const approveButton = element("button", { textContent: "Approve as supervisor" });
        approveButton.addEventListener("click", () => onApprove(approval.id));
        children.push(approveButton);
        if (onReject) {
          const rejectButton = element("button", { textContent: "Reject" });
          rejectButton.addEventListener("click", () => onReject(approval.id));
          children.push(rejectButton);
        }
      }
      return element("div", { className: "item" }, children);
    },
    "No approvals."
  );
}

export function renderActionOutbox(actionOutbox, onRetry) {
  renderList(
    byId("actionOutbox"),
    actionOutbox,
    (item) => {
      const children = [
        element("strong", { textContent: `${item.id} ${item.action_type}` }),
        element("span", { textContent: `attempts ${item.attempt_count} / leases ${item.lease_count || 0}` }),
        element("br"),
        tag(item.status, item.status === "succeeded" ? "" : "warn"),
        tag(item.approval_id),
        tag(String(item.payload_sha256 || "").slice(0, 8)),
      ];
      if (item.last_leased_by) {
        children.push(tag(`worker ${item.last_leased_by}`));
      }
      if (item.last_error?.code) {
        children.push(element("br"));
        children.push(tag(item.last_error.code, "warn"));
      }
      if (item.next_attempt_at) {
        children.push(tag(`next ${item.next_attempt_at}`));
      }
      if (item.status === "retryable_failure" && onRetry) {
        const button = element("button", { textContent: "Retry dispatch" });
        button.addEventListener("click", () => onRetry(item.id));
        children.push(button);
      }
      return element("div", { className: "item" }, children);
    },
    "No action outbox items."
  );
}

export function renderWorkflowRuns(workflowRuns) {
  renderList(
    byId("workflowRuns"),
    workflowRuns,
    (run) => {
      const children = [
        element("strong", { textContent: `${run.id} ${run.intent}` }),
        element("span", { textContent: run.stage }),
        element("br"),
        tag(run.status, run.status === "succeeded" || run.status === "completed" ? "" : "warn"),
        tag(run.user_id),
        tag(String(run.message_sha256 || "").slice(0, 8)),
      ];
      if (run.approval_ids?.length) {
        children.push(tag(`approval ${run.approval_ids[0]}`));
      }
      if (run.outbox_ids?.length) {
        children.push(tag(`outbox ${run.outbox_ids[0]}`));
      }
      if (run.retryable_outbox_ids?.length) {
        children.push(tag("retry needed", "warn"));
      }
      if (run.dead_lettered_outbox_ids?.length) {
        children.push(tag("dead letter", "warn"));
      }
      return element("div", { className: "item" }, children);
    },
    "No workflow runs."
  );
}

export function renderActionRuns(actionRuns) {
  renderList(
    byId("actionRuns"),
    actionRuns,
    (run) =>
      element("div", { className: "item" }, [
        element("strong", { textContent: `${run.id} ${run.action_type}` }),
        element("span", { textContent: `${run.result} by ${run.executed_by}` }),
        element("br"),
        tag(run.status),
        tag(run.approval_id),
        tag(String(run.payload_sha256 || "").slice(0, 8)),
      ]),
    "No action runs."
  );
}

export function renderAudit(events) {
  renderList(
    byId("audit"),
    events,
    (event) =>
      element("div", { className: "item" }, [
        element("strong", { textContent: event.action }),
        element("span", { textContent: event.created_at }),
        element("br"),
        tag(event.user_id),
      ]),
    "No audit events."
  );
}

export function renderTraces(traces, selectedTraceId = "") {
  renderList(
    byId("traces"),
    traces,
    (trace) =>
      element("a", {
        className: ["item", "traceLink", trace.id === selectedTraceId ? "selectedTrace" : ""].filter(Boolean).join(" "),
        dataset: { traceId: trace.id },
        href: traceHash(trace.id),
      }, [
        element("strong", { textContent: trace.intent }),
        element("span", { textContent: trace.message }),
        element("br"),
        tag(trace.id.slice(0, 8)),
      ]),
    "No traces."
  );
}
