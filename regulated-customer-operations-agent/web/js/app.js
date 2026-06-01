import { api } from "./api.js";
import { byId } from "./dom.js";
import { installTraceCopyButton } from "./clipboard.js";
import {
  populateCaseSelect,
  populateUserSelect,
  renderApprovals,
  renderAudit,
  renderCaseSummary,
  renderDecision,
  renderTraces,
} from "./renderers.js";

const state = {
  users: [],
  cases: [],
  selectedUser: "ivy",
  selectedCase: "case-1001",
  lastTraceId: "",
};

const setTraceCopyState = installTraceCopyButton(byId("copyTraceId"), () => state.lastTraceId);

async function loadUsers() {
  const data = await api("/api/users");
  state.users = data.users;
  populateUserSelect(state.users, state.selectedUser);
}

async function loadCases() {
  const data = await api("/api/cases");
  state.cases = data.cases;
  populateCaseSelect(state.cases, state.selectedCase);
  renderCaseSummary(state.cases, state.selectedCase);
}

async function runAgent() {
  const data = await api("/api/agent", {
    method: "POST",
    body: JSON.stringify({
      user_id: state.selectedUser,
      case_id: state.selectedCase,
      message: byId("message").value.trim(),
    }),
  });
  renderDecision(data);
  state.lastTraceId = data.trace_id;
  setTraceCopyState(data.trace_id);
  await refreshOperationalViews();
}

async function approve(approvalId) {
  const data = await api("/api/approval/approve", {
    method: "POST",
    body: JSON.stringify({ approval_id: approvalId, approver_id: "sam" }),
  });
  byId("decision").textContent = `Approved ${approvalId}: ${data.result}`;
  await refreshOperationalViews();
}

async function loadApprovals() {
  const data = await api("/api/approvals");
  renderApprovals(data.approvals, approve);
}

async function loadAudit() {
  const data = await api("/api/audit?limit=12");
  renderAudit(data.events);
}

async function loadTraces() {
  const data = await api("/api/traces?limit=8");
  renderTraces(data.traces);
}

async function runEval() {
  byId("evalOutput").textContent = "Running eval gate...";
  const data = await api("/api/eval/run", { method: "POST", body: "{}" });
  byId("evalOutput").textContent = JSON.stringify(data, null, 2);
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
  byId("health").textContent = health.status === "ok" ? "Healthy" : health.status;
  await loadUsers();
  await refreshOperationalViews();
}

byId("userSelect").addEventListener("change", (event) => {
  state.selectedUser = event.target.value;
});

byId("caseSelect").addEventListener("change", (event) => {
  state.selectedCase = event.target.value;
  renderCaseSummary(state.cases, state.selectedCase);
});

byId("runAgent").addEventListener("click", runAgent);
byId("runEval").addEventListener("click", runEval);

document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => {
    byId("message").value = button.dataset.message;
  });
});

boot().catch((error) => {
  byId("health").textContent = "Error";
  byId("decision").textContent = error.message;
});
