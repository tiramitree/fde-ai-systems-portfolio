import { byId, setOptions } from "./dom.js";

export function populateUserSelect(users, selectedUser) {
  setOptions(byId("userSelect"), users, selectedUser, (user) => `${user.name} (${user.role})`);
}

export function populateReleaseSelect(releases, selectedRelease) {
  setOptions(byId("releaseSelect"), releases, selectedRelease, (release) => `${release.id} - ${release.status}`);
}

export function populateIncidentSelect(incidents, selectedIncident) {
  setOptions(byId("incidentSelect"), incidents, selectedIncident, (incident) => `${incident.id} - ${incident.severity}`);
}

export function renderReleaseSummary(releases, releaseId) {
  const release = releases.find((item) => item.id === releaseId);
  byId("releaseSummary").innerHTML = release
    ? `
      <strong>${release.name}</strong>
      <div>${release.change_summary}</div>
      <span class="tag">${release.status}</span>
      <span class="tag">${release.traffic_percent}% traffic</span>
    `
    : "No release loaded.";
}

export function renderIncidentSummary(incidents, incidentId) {
  const incident = incidents.find((item) => item.id === incidentId);
  byId("incidentSummary").innerHTML = incident
    ? `
      <strong>${incident.title}</strong>
      <div>${incident.summary}</div>
      <span class="tag ${incident.severity === "high" ? "danger" : "warn"}">${incident.severity}</span>
      <span class="tag">${incident.status}</span>
    `
    : "No incident loaded.";
}

export function renderDecision(data) {
  const decision = data.decision;
  byId("decision").innerHTML = `
    <strong>${decision.recommendation}</strong>
    <div>${decision.root_cause}</div>
    <span class="tag ${decision.release_blocked ? "danger" : "warn"}">
      ${decision.release_blocked ? "release blocked" : "monitor"}
    </span>
    <span class="tag">${decision.severity}</span>
    <h2>Remediation</h2>
    <ol>${data.remediation_steps.map((step) => `<li>${step}</li>`).join("")}</ol>
  `;
  byId("trace").textContent = JSON.stringify(data.evidence, null, 2);
}

export function renderFailedEvals(rows) {
  byId("failedEvals").innerHTML =
    rows
      .map(
        (row) => `
          <div class="item">
            <strong>${row.id}</strong>
            <div>${row.details}</div>
            <span class="tag ${row.severity === "high" ? "danger" : "warn"}">${row.severity}</span>
            <span class="tag">${row.category}</span>
          </div>
        `,
      )
      .join("") || '<div class="item">No failed evals linked.</div>';
}

export function renderAudit(events) {
  byId("audit").innerHTML =
    events
      .map(
        (event) => `
          <div class="item">
            <strong>${event.action}</strong>
            <div>${event.user_id} - ${event.created_at}</div>
            <span class="tag">${event.details.trace_id || "no trace"}</span>
          </div>
        `,
      )
      .join("") || '<div class="item">No audit events yet.</div>';
}

export function renderTraces(traces) {
  byId("traces").innerHTML =
    traces
      .map(
        (trace) => `
          <div class="item">
            <strong>${trace.id}</strong>
            <div>${trace.incident_id} - ${trace.result.recommendation}</div>
            <span class="tag ${trace.result.release_blocked ? "danger" : "warn"}">
              ${trace.result.release_blocked ? "blocked" : "monitor"}
            </span>
          </div>
        `,
      )
      .join("") || '<div class="item">No traces yet.</div>';
}
