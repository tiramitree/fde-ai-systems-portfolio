import { api } from "./api.js";
import { byId } from "./dom.js";
import { installCopyButton, installTraceCopyButton } from "./clipboard.js";
import { installScenarioEditor } from "./scenarioEditor.js";
import {
  installTraceHashSync,
  installTraceKeyboardNavigation,
  selectedTraceId,
  setTraceHash,
  syncTraceSelection,
  traceUrl,
} from "./traceLinks.js";
import { installThemeToggle } from "./theme.js";
import {
  populateCaseSelect,
  renderActionOutbox,
  renderActionRuns,
  populateUserSelect,
  renderApprovals,
  renderAudit,
  renderCaseSummary,
  renderDecision,
  renderToolRegistry,
  renderTraces,
  renderWorkflowRuns,
} from "./renderers.js";

const state = {
  users: [],
  cases: [],
  selectedUser: "ivy",
  selectedCase: "case-1001",
  lastTraceId: "",
};

const setTraceCopyState = installTraceCopyButton(byId("copyTraceId"), () => state.lastTraceId);
const setTraceLinkCopyState = installCopyButton(byId("copyTraceLink"), () => traceUrl(state.lastTraceId));
installScenarioEditor({
  loadScenario: () => api("/api/scenario"),
  summary: byId("scenarioSummary"),
  draft: byId("scenarioDraft"),
  diff: byId("scenarioDiff"),
  status: byId("scenarioStatus"),
  saveButton: byId("saveScenarioDraft"),
  resetButton: byId("resetScenarioDraft"),
  clearButton: byId("clearScenarioDraft"),
  copyButton: byId("copyScenarioDraft"),
});
installThemeToggle(byId("themeToggle"));

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
  setTraceLinkCopyState(data.trace_id);
  setTraceHash(data.trace_id);
  await refreshOperationalViews();
}

async function approve(approvalId) {
  const data = await api("/api/approval/approve", {
    method: "POST",
    body: JSON.stringify({ approval_id: approvalId, approver_id: "sam" }),
  });
  const execution = data.execution ? ` (${data.execution.id})` : "";
  const outbox = data.outbox_item ? ` via ${data.outbox_item.id}` : "";
  byId("decision").textContent = `Approved ${approvalId}: ${data.result}${execution}${outbox}`;
  await refreshOperationalViews();
}

async function rejectApproval(approvalId) {
  const data = await api("/api/approval/reject", {
    method: "POST",
    body: JSON.stringify({
      approval_id: approvalId,
      reviewer_id: "sam",
      reason: "supervisor rejected this controlled demo action",
    }),
  });
  const outbox = data.outbox_item ? ` via ${data.outbox_item.id}` : "";
  byId("decision").textContent = `Rejected ${approvalId}: ${data.result}${outbox}`;
  await refreshOperationalViews();
}

async function retryOutbox(outboxId) {
  const data = await api("/api/action-outbox/retry", {
    method: "POST",
    body: JSON.stringify({ outbox_id: outboxId, operator_id: "sam" }),
  });
  const execution = data.execution ? ` (${data.execution.id})` : "";
  byId("decision").textContent = `Retried ${outboxId}: ${data.result}${execution}`;
  await refreshOperationalViews();
}

async function loadApprovals() {
  const data = await api("/api/approvals");
  renderApprovals(data.approvals, approve, rejectApproval);
}

async function loadToolRegistry() {
  const data = await api("/api/tool-registry");
  renderToolRegistry(data.tools);
}

async function loadActionRuns() {
  const data = await api("/api/action-runs?limit=6");
  renderActionRuns(data.action_runs);
}

async function loadWorkflowRuns() {
  const data = await api("/api/workflow-runs?limit=6");
  renderWorkflowRuns(data.workflow_runs);
}

async function loadActionOutbox() {
  const data = await api("/api/action-outbox?limit=6");
  renderActionOutbox(data.action_outbox, retryOutbox);
}

async function loadAudit() {
  const data = await api("/api/audit?limit=12");
  renderAudit(data.events);
}

async function loadTraces() {
  const data = await api("/api/traces?limit=8");
  renderTraces(data.traces, selectedTraceId());
  syncTraceSelection();
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
  await loadWorkflowRuns();
  await loadActionOutbox();
  await loadActionRuns();
  await loadAudit();
  await loadTraces();
}

async function boot() {
  const health = await api("/api/health");
  byId("health").textContent = health.status === "ok" ? "Healthy" : health.status;
  await loadUsers();
  await loadToolRegistry();
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
installTraceHashSync();
installTraceKeyboardNavigation(byId("traces"));

document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => {
    byId("message").value = button.dataset.message;
  });
});

boot().catch((error) => {
  byId("health").textContent = "Error";
  byId("decision").textContent = error.message;
});
