const state = {
  users: [],
  selectedUser: "alice",
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

function renderUser() {
  const user = state.users.find((item) => item.id === state.selectedUser);
  $("userMeta").innerHTML = user
    ? `<strong>${user.name}</strong><br><span class="tag">${user.role}</span><span class="tag">${user.tenant_id}</span>`
    : "No user selected.";
}

async function loadUsers() {
  const data = await api("/api/users");
  state.users = data.users;
  $("userSelect").innerHTML = state.users
    .map((user) => `<option value="${user.id}">${user.name} (${user.role})</option>`)
    .join("");
  $("userSelect").value = state.selectedUser;
  renderUser();
}

async function loadDocuments() {
  const data = await api(`/api/documents?user_id=${encodeURIComponent(state.selectedUser)}`);
  $("documents").innerHTML = data.documents
    .map(
      (doc) => `
      <div class="item">
        <strong>${doc.title}</strong>
        <span>${doc.source_url}</span><br>
        <span class="tag">${doc.classification}</span>
        <span class="tag">${doc.version}</span>
      </div>`
    )
    .join("");
}

function renderAnswer(data) {
  const security = data.security_events.length
    ? `<p><span class="tag danger">security event</span> Retrieved content contained instruction-like text and was ignored.</p>`
    : "";
  const abstain = data.abstain_reason ? `<p><span class="tag warn">abstained</span> ${data.abstain_reason}</p>` : "";
  $("answer").innerHTML = `
    <p>${data.answer}</p>
    <p><span class="tag">confidence ${data.confidence}</span><span class="tag">latency ${data.latency_ms} ms</span></p>
    ${abstain}
    ${security}
  `;
  $("citations").innerHTML = data.citations.length
    ? data.citations
        .map(
          (citation) => `
        <div class="item">
          <strong>${citation.title}</strong>
          <span>${citation.source_url}</span><br>
          <span class="tag">${citation.doc_id}</span>
          <span class="tag">score ${citation.score}</span>
        </div>`
        )
        .join("")
    : `<div class="item muted">No citations returned.</div>`;
  $("trace").textContent = JSON.stringify(
    {
      trace_id: data.trace_id,
      permission_blocked_count: data.permission_blocked_count,
      retrieved: data.retrieved,
      missing_evidence: data.missing_evidence,
      security_events: data.security_events,
    },
    null,
    2
  );
}

async function ask() {
  const question = $("question").value.trim();
  if (!question) return;
  $("answer").textContent = "Running retrieval and generation...";
  const data = await api("/api/query", {
    method: "POST",
    body: JSON.stringify({ user_id: state.selectedUser, question }),
  });
  renderAnswer(data);
  await loadAudit();
  await loadTraces();
}

async function runEval() {
  $("evalOutput").textContent = "Running eval gate...";
  const data = await api("/api/eval/run", { method: "POST", body: "{}" });
  $("evalOutput").textContent = JSON.stringify(data, null, 2);
  await loadAudit();
  await loadTraces();
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
        <span class="tag">${event.details.abstained ? "abstained" : "answered"}</span>
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
        <strong>${trace.user_id}</strong>
        <span>${trace.question}</span><br>
        <span class="tag">${trace.id.slice(0, 8)}</span>
        <span class="tag">${trace.payload.output.abstain_reason ? "abstain" : "answer"}</span>
      </div>`
    )
    .join("");
}

async function boot() {
  try {
    const health = await api("/api/health");
    $("health").textContent = health.status;
    await loadUsers();
    await loadDocuments();
    await loadAudit();
    await loadTraces();
  } catch (error) {
    $("health").textContent = "error";
    $("answer").textContent = error.message;
  }
}

$("userSelect").addEventListener("change", async (event) => {
  state.selectedUser = event.target.value;
  renderUser();
  await loadDocuments();
});

$("ask").addEventListener("click", ask);
$("runEval").addEventListener("click", runEval);
document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    $("question").value = button.dataset.question;
  });
});

boot();

