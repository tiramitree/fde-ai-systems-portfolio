import { byId, clear, element, renderList, tag } from "./dom.js";

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
    },
    null,
    2
  );
}

export function renderApprovals(approvals, onApprove) {
  renderList(
    byId("approvals"),
    approvals,
    (approval) => {
      const children = [
        element("strong", { textContent: `${approval.id} ${approval.action_type}` }),
        element("span", { textContent: approval.reason }),
        element("br"),
        tag(approval.status),
        tag(approval.requested_by),
      ];
      if (approval.status === "pending") {
        const button = element("button", { textContent: "Approve as supervisor" });
        button.addEventListener("click", () => onApprove(approval.id));
        children.push(button);
      }
      return element("div", { className: "item" }, children);
    },
    "No approvals."
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

export function renderTraces(traces) {
  renderList(
    byId("traces"),
    traces,
    (trace) =>
      element("div", { className: "item" }, [
        element("strong", { textContent: trace.intent }),
        element("span", { textContent: trace.message }),
        element("br"),
        tag(trace.id.slice(0, 8)),
      ]),
    "No traces."
  );
}
