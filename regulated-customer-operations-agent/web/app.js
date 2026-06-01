const state = {
  users: [],
  cases: [],
  selectedUser: "ivy",
  selectedCase: "case-1001",
};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function renderCases() {
  const item = state.cases.find((caseItem) => caseItem.id === state.selectedCase);
  $("caseSummary").innerHTML = item
    ? `<strong>${item.id}</strong><br>${item.summary}<br><span class="tag">${item.status}</span>`
    : "No case loaded.";
}

async function loadUsers() {
  const data = await api("/api/users");
  state.users = data.users;
  $("userSelect").innerHTML = data.users
    .map((user) => `<option value="${user.id}">${user.name} (${user.role})</option>`)
    .join("");
  $("userSelect").value = state.selectedUser;
}

async function loadCases() {
  const data = await api("/api/cases");
  state.cases = data.cases;
  $("caseSelect").innerHTML = data.cases
    .map((caseItem) => `<option value="${caseItem.id}">${caseItem.id}</option>`)
    .join("");
  $("caseSelect").value = state.selectedCase;
  renderCases();
}

function renderDecision(data) {
  const blocked = data.blocked_actions.length
    ? `<p><span class="tag warn">blocked side effect</span> ${data.blocked_actions[0].reason || data.blocked_actions[0].reason}</p>`
    : "";
  const approvals = data.approvals.length
    ? `<p><span class="tag">approval ${data.approvals[0].id}</span><span class="tag">${data.approvals[0].status}</span></p>`
    : "";
  const policies = data.cited_policies
    .map((policy) => `<span class="tag">${policy.id}</span>`)
    .join("");
  $("decision").innerHTML = `
    <p>${data.response}</p>
    <p><span class="tag">${data.intent}</span>${policies}</p>
    ${approvals}
    ${blocked}
  `;
  $("trace").textContent = JSON.stringify(
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

async function runAgent() {
  const data = await api("/api/agent", {
    method: "POST",
    body: JSON.stringify({
      user_id: state.selectedUser,
      case_id: state.selectedCase,
      message: $("message").value.trim(),
    }),
  });
  renderDecision(data);
  await refreshOperationalViews();
}

async function approve(approvalId) {
  const data = await api("/api/approval/approve", {
    method: "POST",
    body: JSON.stringify({ approval_id: approvalId, approver_id: "sam" }),
  });
  $("decision").innerHTML = `<p>Approved ${approvalId}: ${data.result}</p>`;
  await refreshOperationalViews();
}

async function loadApprovals() {
  const data = await api("/api/approvals");
  $("approvals").innerHTML = data.approvals.length
    ? data.approvals
        .map(
          (approval) => `
        <div class="item">
          <strong>${approval.id} ${approval.action_type}</strong>
          <span>${approval.reason}</span><br>
          <span class="tag">${approval.status}</span>
          <span class="tag">${approval.requested_by}</span>
          ${
            approval.status === "pending"
              ? `<button data-approval="${approval.id}">Approve as supervisor</button>`
              : ""
          }
        </div>`
        )
        .join("")
    : `<div class="item muted">No approvals.</div>`;
  document.querySelectorAll("[data-approval]").forEach((button) => {
    button.addEventListener("click", () => approve(button.dataset.approval));
  });
}

async function loadAudit() {
  const data = await api("/api/audit?limit=12");
  $("audit").innerHTML = data.events
    .map(
      (event) => `
      <div class="item">
        <strong>${event.action}</strong>
        <span>${event.created_at}</span><br>
        <span class="tag">${event.user_id}</span>
      </div>`
    )
    .join("");
}

async function loadTraces() {
  const data = await api("/api/traces?limit=8");
  $("traces").innerHTML = data.traces
    .map(
      (trace) => `
      <div class="item">
        <strong>${trace.intent}</strong>
        <span>${trace.message}</span><br>
        <span class="tag">${trace.id.slice(0, 8)}</span>
      </div>`
    )
    .join("");
}

async function runEval() {
  $("evalOutput").textContent = "Running eval gate...";
  const data = await api("/api/eval/run", { method: "POST", body: "{}" });
  $("evalOutput").textContent = JSON.stringify(data, null, 2);
  await refreshOperationalViews();
}

async function refreshOperationalViews() {
  await loadCases();
  await loadApprovals();
  await loadAudit();
  await loadTraces();
}

async function boot() {
  const health = await api("/api/health");
  $("health").textContent = health.status;
  await loadUsers();
  await loadCases();
  await refreshOperationalViews();
}

$("userSelect").addEventListener("change", (event) => {
  state.selectedUser = event.target.value;
});

$("caseSelect").addEventListener("change", (event) => {
  state.selectedCase = event.target.value;
  renderCases();
});

$("runAgent").addEventListener("click", runAgent);
$("runEval").addEventListener("click", runEval);
document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => {
    $("message").value = button.dataset.message;
  });
});

boot().catch((error) => {
  $("health").textContent = "error";
  $("decision").textContent = error.message;
});

