import { api } from "./api.js";
import { byId } from "./dom.js";
import { installTraceCopyButton } from "./clipboard.js";
import {
  populateIncidentSelect,
  populateReleaseSelect,
  populateUserSelect,
  renderAudit,
  renderDecision,
  renderFailedEvals,
  renderIncidentSummary,
  renderReleaseSummary,
  renderTraces,
} from "./renderers.js";

const state = {
  users: [],
  releases: [],
  incidents: [],
  selectedUser: "maya",
  selectedRelease: "rel-2026-06-01",
  selectedIncident: "inc-2026-014",
  lastTraceId: "",
};

const setTraceCopyState = installTraceCopyButton(byId("copyTraceId"), () => state.lastTraceId);

async function loadUsers() {
  const data = await api("/api/users");
  state.users = data.users;
  populateUserSelect(state.users, state.selectedUser);
}

async function loadReleases() {
  const data = await api("/api/releases");
  state.releases = data.releases;
  populateReleaseSelect(state.releases, state.selectedRelease);
  renderReleaseSummary(state.releases, state.selectedRelease);
}

async function loadIncidents() {
  const data = await api("/api/incidents");
  state.incidents = data.incidents;
  populateIncidentSelect(state.incidents, state.selectedIncident);
  renderIncidentSummary(state.incidents, state.selectedIncident);
}

async function runTriage() {
  const data = await api("/api/triage", {
    method: "POST",
    body: JSON.stringify({
      user_id: state.selectedUser,
      release_id: state.selectedRelease,
      incident_id: state.selectedIncident,
    }),
  });
  renderDecision(data);
  renderFailedEvals(data.failed_evals);
  state.lastTraceId = data.trace_id;
  setTraceCopyState(data.trace_id);
  await refreshEvidence();
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
  byId("evalOutput").textContent = "Running triage evals...";
  const data = await api("/api/eval/run", { method: "POST", body: "{}" });
  byId("evalOutput").textContent = JSON.stringify(data, null, 2);
  await refreshEvidence();
}

async function refreshEvidence() {
  await loadAudit();
  await loadTraces();
}

async function boot() {
  const health = await api("/api/health");
  byId("health").textContent = health.status === "ok" ? "Healthy" : health.status;
  await loadUsers();
  await loadReleases();
  await loadIncidents();
  await refreshEvidence();
}

byId("userSelect").addEventListener("change", (event) => {
  state.selectedUser = event.target.value;
});

byId("releaseSelect").addEventListener("change", (event) => {
  state.selectedRelease = event.target.value;
  renderReleaseSummary(state.releases, state.selectedRelease);
});

byId("incidentSelect").addEventListener("change", (event) => {
  state.selectedIncident = event.target.value;
  renderIncidentSummary(state.incidents, state.selectedIncident);
});

byId("runTriage").addEventListener("click", runTriage);
byId("runEval").addEventListener("click", runEval);

document.querySelectorAll("[data-incident]").forEach((button) => {
  button.addEventListener("click", () => {
    state.selectedIncident = button.dataset.incident;
    byId("incidentSelect").value = state.selectedIncident;
    renderIncidentSummary(state.incidents, state.selectedIncident);
  });
});

boot().catch((error) => {
  byId("health").textContent = "Error";
  byId("decision").textContent = error.message;
});
