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
import {
  populateUserSelect,
  renderAnswer,
  renderAudit,
  renderDocuments,
  renderTraces,
  renderUser,
} from "./renderers.js";

const state = {
  users: [],
  selectedUser: "alice",
  lastTraceId: "",
};

const setTraceCopyState = installTraceCopyButton(byId("copyTraceId"), () => state.lastTraceId);
const setTraceLinkCopyState = installCopyButton(byId("copyTraceLink"), () => traceUrl(state.lastTraceId));
installScenarioEditor({
  loadScenario: () => api("/api/scenario"),
  summary: byId("scenarioSummary"),
  draft: byId("scenarioDraft"),
  status: byId("scenarioStatus"),
  saveButton: byId("saveScenarioDraft"),
  resetButton: byId("resetScenarioDraft"),
  clearButton: byId("clearScenarioDraft"),
});

async function loadUsers() {
  const data = await api("/api/users");
  state.users = data.users;
  populateUserSelect(state.users, state.selectedUser);
  renderUser(state.users, state.selectedUser);
}

async function loadDocuments() {
  const data = await api(`/api/documents?user_id=${encodeURIComponent(state.selectedUser)}`);
  renderDocuments(data.documents);
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

async function ask() {
  const question = byId("question").value.trim();
  if (!question) {
    return;
  }
  byId("answer").textContent = "Running retrieval and generation...";
  const data = await api("/api/query", {
    method: "POST",
    body: JSON.stringify({ user_id: state.selectedUser, question }),
  });
  renderAnswer(data);
  state.lastTraceId = data.trace_id;
  setTraceCopyState(data.trace_id);
  setTraceLinkCopyState(data.trace_id);
  setTraceHash(data.trace_id);
  await refreshObservability();
}

async function runEval() {
  byId("evalOutput").textContent = "Running eval gate...";
  const data = await api("/api/eval/run", { method: "POST", body: "{}" });
  byId("evalOutput").textContent = JSON.stringify(data, null, 2);
  await refreshObservability();
}

async function refreshObservability() {
  await loadAudit();
  await loadTraces();
}

async function boot() {
  try {
    const health = await api("/api/health");
    byId("health").textContent = health.status === "ok" ? "Healthy" : health.status;
    await loadUsers();
    await loadDocuments();
    await refreshObservability();
  } catch (error) {
    byId("health").textContent = "Error";
    byId("answer").textContent = error.message;
  }
}

byId("userSelect").addEventListener("change", async (event) => {
  state.selectedUser = event.target.value;
  renderUser(state.users, state.selectedUser);
  await loadDocuments();
});

byId("ask").addEventListener("click", ask);
byId("runEval").addEventListener("click", runEval);
installTraceHashSync();
installTraceKeyboardNavigation(byId("traces"));

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    byId("question").value = button.dataset.question;
  });
});

boot();
