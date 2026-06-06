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

export function installIngestionPanel({ api, elements, currentUser, onIngested }) {
  async function sync() {
    const user = currentUser();
    const isAdmin = user?.role === "admin";
    renderSummary(elements.summary, user);
    elements.button.disabled = !isAdmin;
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

  elements.button.addEventListener("click", submit);
  sync();
  return { sync };
}
