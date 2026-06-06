import { element, tag } from "./dom.js";

function selectedOptions(select) {
  return Array.from(select.selectedOptions).map((option) => option.value);
}

function setStatus(node, message, state = "") {
  node.textContent = message;
  if (state) {
    node.dataset.state = state;
  } else {
    delete node.dataset.state;
  }
}

function renderSummary(container, user) {
  container.replaceChildren(
    element("div", {}, [
      element("strong", { textContent: "Admin-only source intake" }),
      element("p", {
        textContent: "Adds searchable sources with role filters, source hash, and audit evidence.",
      }),
      tag(user?.role === "admin" ? "admin enabled" : "admin required", user?.role === "admin" ? "" : "warn"),
    ])
  );
}

function buildPayload(elements, userId) {
  const allowedRoles = selectedOptions(elements.roles);
  return {
    user_id: userId,
    replace: elements.replace.checked,
    document: {
      title: elements.title.value.trim(),
      body: elements.body.value.trim(),
      classification: elements.classification.value,
      allowed_roles: allowedRoles,
      source_url: `ingested://acme/${elements.title.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
      source_mime: elements.mime.value,
      version: "ui-draft",
    },
  };
}

function buildSampleSyncPayload(userId) {
  return {
    user_id: userId,
    replace: true,
    connector: {
      name: "local-drive-demo",
      cursor: "2026-06-06T00:00:00Z",
      acl_source: "fixture-acl-v1",
      acl_snapshot: {
        version: "fixture-acl-v1",
        documents: {
          "drive-doc-source-sync-playbook-2026": {
            allowed_roles: ["employee", "manager", "admin"],
            permission_id: "drive-acl-source-sync-playbook-v1",
            principal_count: 3,
          },
          "drive-json-finance-retention-controls-2026": {
            allowed_roles: ["manager", "admin"],
            permission_id: "drive-acl-finance-controls-v1",
            principal_count: 2,
          },
        },
      },
    },
    documents: [
      {
        external_id: "drive-doc-source-sync-playbook-2026",
        title: "Source Sync Playbook 2026",
        body: (
          "Source Sync Playbook 2026\n\n"
          + "After each connector sync, administrators must review parser warnings, ACL source mappings, "
          + "and trace-to-eval candidates before promoting new knowledge into the trusted answer path."
        ),
        classification: "internal",
        allowed_roles: ["employee", "manager", "admin"],
        source_mime: "text/markdown",
        updated_at: "2026-06-06",
      },
      {
        external_id: "drive-json-finance-retention-controls-2026",
        title: "Finance Retention Control Notes 2026",
        body: JSON.stringify({
          policy: "Finance Retention Control Notes 2026",
          owner: "Finance Operations",
          summary:
            "Confidential retention controls require manager review, audit linkage, and approval evidence before wider access.",
          review: {
            acl_source: "fixture-acl-v1",
            cadence: "monthly",
            escalation: "admin approval required",
          },
        }),
        classification: "confidential",
        allowed_roles: ["manager", "admin"],
        source_mime: "application/json",
        updated_at: "2026-06-06",
      },
    ],
  };
}

function buildSampleSyncJobPayload(userId) {
  return {
    user_id: userId,
    type: "source_sync",
    idempotency_key: "local-drive-demo-source-sync-2026-06-06",
    payload: buildSampleSyncPayload(userId),
  };
}

export function installIngestionPanel({ api, elements, currentUser, onIngested }) {
  async function sync() {
    const user = currentUser();
    const isAdmin = user?.role === "admin";
    renderSummary(elements.summary, user);
    elements.button.disabled = !isAdmin;
    elements.syncButton.disabled = !isAdmin;
    if (!isAdmin) {
      setStatus(elements.status, "Switch to Avery Admin before ingesting a source.");
    } else if (!elements.status.textContent || elements.status.textContent.includes("Switch to")) {
      setStatus(elements.status, "Ready to ingest a local source.", "ok");
    }
  }

  async function submit() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.button.disabled = true;
    setStatus(elements.status, "Ingesting document...");
    try {
      const payload = buildPayload(elements, user.id);
      const data = await api("/api/documents/ingest", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const doc = data.document;
      const parserName = data.ingestion?.parser?.name || "parser";
      setStatus(
        elements.status,
        `Ingested ${doc.title} via ${parserName} (${data.chunk_count} chunk, hash ${data.ingestion.source_hash.slice(0, 12)}...).`,
        "ok"
      );
      await onIngested(data);
    } catch (error) {
      setStatus(elements.status, error.message, "error");
    } finally {
      await sync();
    }
  }

  async function syncSampleSource() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.button.disabled = true;
    elements.syncButton.disabled = true;
    setStatus(elements.status, "Queueing sample connector sync job...");
    try {
      const data = await api("/api/ingestion/jobs", {
        method: "POST",
        body: JSON.stringify(buildSampleSyncJobPayload(user.id)),
      });
      const sync = data.result?.sync || data.job?.result || {};
      const replayed = data.idempotency_replayed ? "Replayed" : "Completed";
      setStatus(
        elements.status,
        `${replayed} job ${data.job.id} (${data.job.status}): ${sync.document_count || 0} docs from ${sync.connector || "connector"} (${sync.chunk_count || 0} chunks).`,
        "ok"
      );
      await onIngested(data);
    } catch (error) {
      setStatus(elements.status, error.message, "error");
    } finally {
      await sync();
    }
  }

  elements.button.addEventListener("click", submit);
  elements.syncButton.addEventListener("click", syncSampleSource);
  sync();
  return { sync };
}
