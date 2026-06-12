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

function mimeExtension(mime) {
  if (mime === "text/csv") {
    return "csv";
  }
  if (mime === "text/html") {
    return "html";
  }
  if (mime === "application/json") {
    return "json";
  }
  if (mime === "text/plain") {
    return "txt";
  }
  return "md";
}

function base64FromBytes(bytes) {
  let binary = "";
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    const chunk = bytes.subarray(index, index + chunkSize);
    binary += String.fromCharCode(...chunk);
  }
  return btoa(binary);
}

function base64FromText(text) {
  return base64FromBytes(new TextEncoder().encode(text));
}

async function filePayload(elements) {
  const selected = elements.file?.files?.[0];
  if (selected) {
    const bytes = new Uint8Array(await selected.arrayBuffer());
    return {
      filename: selected.name,
      mime_type: selected.type || elements.mime.value,
      content_base64: base64FromBytes(bytes),
    };
  }
  const titleSlug = elements.title.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-") || "source";
  const fallbackName = `${titleSlug}.${mimeExtension(elements.mime.value)}`;
  return {
    filename: (elements.fileName.value.trim() || fallbackName),
    mime_type: elements.mime.value,
    content_base64: base64FromText(elements.body.value),
  };
}

function renderSummary(container, user) {
  container.replaceChildren(
    element("div", {}, [
      element("strong", { textContent: "Admin-only source intake" }),
      element("p", {
        textContent: "Adds searchable sources with role filters, source hash, connector jobs, and audit evidence.",
      }),
      tag(user?.role === "admin" ? "admin enabled" : "admin required", user?.role === "admin" ? "" : "warn"),
    ])
  );
}

function renderJobList(container, jobs) {
  if (!container) {
    return;
  }
  if (!jobs.length) {
    container.replaceChildren(element("div", { className: "muted", textContent: "No ingestion jobs recorded." }));
    return;
  }
  container.replaceChildren(
    ...jobs.slice(0, 4).map((job) => {
      const result = job.result || {};
      const label = `${job.status} ${result.connector || job.input?.connector || job.type}`;
      const detail = `${result.document_count || job.input?.document_count || 0} docs, ${result.chunk_count || 0} chunks`;
      return element("div", { className: "item" }, [
        element("div", { textContent: label }),
        element("small", { textContent: `${job.id} | ${detail}` }),
      ]);
    })
  );
}

function renderConnectorStatus(container, connectors) {
  if (!container) {
    return;
  }
  if (!connectors.length) {
    container.replaceChildren(element("div", { className: "muted", textContent: "No connector status recorded." }));
    return;
  }
  container.replaceChildren(
    ...connectors.slice(0, 4).map((connector) => {
      const label = `${connector.connector}: ${connector.health}`;
      const cursor = connector.latest_cursor || "no cursor";
      const acl = (connector.acl_sources || []).join(", ") || "no acl source";
      const detail =
        `${connector.latest_job_status} ${connector.latest_job_id} | ${connector.document_count || 0} docs, `
        + `${connector.chunk_count || 0} chunks, ${connector.pruned_count || 0} pruned, `
        + `${connector.dead_letter_count || 0} dead letters, `
        + `${connector.indexed_document_count || 0} indexed/${connector.active_document_count || 0} active, `
        + `${connector.parser_warning_count || 0} parser warnings, acl ${acl}, cursor ${cursor}`;
      return element("div", { className: "item" }, [
        element("div", { textContent: label }),
        element("small", { textContent: detail }),
      ]);
    })
  );
}

function renderSourceQuality(container, report) {
  if (!container) {
    return;
  }
  if (!report) {
    container.replaceChildren(element("div", { className: "muted", textContent: "No source quality report available." }));
    return;
  }
  const docs = report.documents || [];
  const schemaCounts = report.parser_quality_schema_counts || {};
  const schemaSummary = Object.entries(schemaCounts)
    .map(([schema, count]) => `${schema}:${count}`)
    .join(", ") || "no parser quality schema";
  const scanCounts = report.source_scan_schema_counts || {};
  const scanSummary = Object.entries(scanCounts)
    .map(([schema, count]) => `${schema}:${count}`)
    .join(", ") || "no source scan schema";
  const summary = `${report.document_count || 0} docs, ${report.active_document_count || 0} active, `
    + `${report.attention_required_count || 0} need attention, `
    + `${report.parser_warning_count || 0} parser warnings, `
    + `${report.source_scan_review_required_count || 0} source scans need review, `
    + `parser schemas ${schemaSummary}, scan schemas ${scanSummary}`;
  container.replaceChildren(
    element("div", { className: "item" }, [
      element("div", { textContent: "Source quality report" }),
      element("small", {
        textContent: `${summary}, raw bodies returned: ${report.raw_bodies_returned ? "yes" : "no"}`,
      }),
    ]),
    ...docs.slice(0, 4).map((doc) => {
      const flags = (doc.risk_flags || []).join(", ") || "ready";
      const scanCategories = (doc.source_scan_finding_categories || []).join(", ") || "none";
      const detail =
        `${doc.source_connector || "manual"} | ${doc.source_mime || "mime"} | `
        + `${doc.parser_name || "parser"} | ${doc.normalized_non_empty_line_count || 0} non-empty lines, `
        + `${doc.section_count || 0} sections, ${doc.table_like_line_count || 0} table-like lines, `
        + `scan ${doc.source_scan_status || "missing"}/${doc.source_scan_severity || "unknown"} (${scanCategories}), `
        + `acl ${doc.acl_source || "none"}, ${flags}`;
      return element("div", { className: "item" }, [
        element("div", { textContent: `${doc.title || doc.id} (${doc.source_lifecycle_state || "unknown"})` }),
        element("small", { textContent: detail }),
      ]);
    })
  );
}

function renderSourceBundleCatalog(container, catalog) {
  if (!container) {
    return;
  }
  const bundles = catalog?.bundles || [];
  if (!bundles.length) {
    container.replaceChildren(element("div", { className: "muted", textContent: "No source bundles available." }));
    return;
  }
  container.replaceChildren(
    ...bundles.slice(0, 3).map((bundle) => {
      const hash = bundle.manifest_sha256 ? bundle.manifest_sha256.slice(0, 12) : "no manifest hash";
      const acl = bundle.acl_snapshot_version || "no acl version";
      const docPreview = (bundle.documents || [])
        .slice(0, 3)
        .map((doc) => `${doc.title} (${doc.classification})`)
        .join("; ");
      return element("div", { className: "item" }, [
        element("div", { textContent: `${bundle.bundle}: ${bundle.document_count || 0} docs ready for preview` }),
        element("small", {
          textContent: `manifest ${hash}, acl ${acl}, raw bodies returned: ${catalog.raw_bodies_returned ? "yes" : "no"} | ${docPreview}`,
        }),
      ]);
    })
  );
}

function renderParsePreview(container, preview) {
  if (!container) {
    return;
  }
  if (!preview) {
    container.replaceChildren(element("div", { className: "muted", textContent: "No parser preview yet." }));
    return;
  }
  const parser = preview.parser || {};
  const file = preview.source_file || {};
  const chunks = preview.chunks || [];
  const warnings = [
    ...(parser.warnings || []),
    ...(preview.validation_warnings || []),
  ];
  const sourceScan = preview.source_scan || {};
  const hash = preview.source_hash ? preview.source_hash.slice(0, 12) : "no hash";
  container.replaceChildren(
    element("div", { className: "item" }, [
      element("div", { textContent: `${parser.name || "parser"} | ${preview.source_mime || "mime"} | ${preview.chunk_count || 0} chunks` }),
      element("small", {
        textContent:
          `contract ${parser.contract_version || "unknown"}, hash ${hash}, `
          + `${parser.normalized_characters || 0} chars, warnings ${warnings.length}, `
          + `scan ${sourceScan.status || "missing"}/${sourceScan.severity || "unknown"}, `
          + `file ${file.file_name || "inline body"}, raw body returned: ${preview.raw_body_returned ? "yes" : "no"}`,
      }),
    ]),
    ...chunks.slice(0, 3).map((chunk) => {
      const span = chunk.source_span || {};
      const label = `chunk ${Number(chunk.chunk_index || 0) + 1}: ${chunk.character_count || 0} chars`;
      const detail =
        `${span.text_unit || "span"} ${span.start_char ?? "?"}-${span.end_char ?? "?"} | ${chunk.text_excerpt || ""}`;
      return element("div", { className: "item" }, [
        element("div", { textContent: label }),
        element("small", { textContent: detail }),
      ]);
    })
  );
}

async function buildPayload(elements, userId) {
  const allowedRoles = selectedOptions(elements.roles);
  const file = await filePayload(elements);
  return {
    user_id: userId,
    replace: elements.replace.checked,
    document: {
      title: elements.title.value.trim(),
      file,
      classification: elements.classification.value,
      allowed_roles: allowedRoles,
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

function buildSourceBundlePayload(userId) {
  return {
    user_id: userId,
    bundle: "operations-handbook",
    cursor: "2026-06-07T00:00:00Z",
    idempotency_key: "source-bundle-operations-handbook-2026-06-07",
    prune_missing: true,
  };
}

function githubSourceUrl(path) {
  return `https:${"//"}github.com/tiramitree/fde-ai-systems-portfolio${path}`;
}

function buildGitHubConnectorPayload(userId) {
  return {
    user_id: userId,
    mode: "fixture",
    owner: "tiramitree",
    repo: "fde-ai-systems-portfolio",
    cursor: "2026-06-06T04:00:00Z",
    idempotency_key: "github-fde-portfolio-fixture-2026-06-06",
    records: [
      {
        kind: "issue",
        number: 5,
        title: "CSV export for eval summaries",
        body:
          "GitHub connector fixture records that eval summary exports must include pass_rate, failed_cases, and trace_id columns before review.",
        state: "open",
        html_url: githubSourceUrl("/issues/5"),
        updated_at: "2026-06-06T04:00:00Z",
        labels: [{ name: "evals" }, { name: "export" }],
        user: { login: "contributor-fixture" },
        allowed_roles: ["employee", "manager", "admin"],
      },
      {
        kind: "pull",
        number: 7,
        title: "Add GitHub connector runbook",
        body:
          "GitHub pull request runbook says connector syncs need cursor checkpoints, source URLs, and permission snapshots.",
        state: "open",
        html_url: githubSourceUrl("/pull/7"),
        updated_at: "2026-06-06T04:05:00Z",
        labels: ["connector", "runbook"],
        user: { login: "reviewer-fixture" },
        allowed_roles: ["manager", "admin"],
      },
    ],
  };
}

export function installIngestionPanel({ api, elements, currentUser, onIngested }) {
  async function refreshSourceBundleCatalog(user) {
    if (!elements.sourceBundleCatalog) {
      return;
    }
    if (user?.role !== "admin") {
      elements.sourceBundleCatalog.replaceChildren(
        element("div", { className: "muted", textContent: "Source bundle preview is admin-only." })
      );
      return;
    }
    try {
      const data = await api(
        `/api/connectors/source-bundle/catalog?user_id=${encodeURIComponent(user.id)}&bundle=operations-handbook`
      );
      renderSourceBundleCatalog(elements.sourceBundleCatalog, data.catalog || {});
    } catch (error) {
      elements.sourceBundleCatalog.replaceChildren(element("div", { className: "muted", textContent: error.message }));
    }
  }

  async function refreshConnectorStatus(user) {
    if (!elements.connectorStatus) {
      return;
    }
    if (user?.role !== "admin") {
      elements.connectorStatus.replaceChildren(
        element("div", { className: "muted", textContent: "Connector status is admin-only." })
      );
      return;
    }
    try {
      const data = await api(`/api/connectors/status?user_id=${encodeURIComponent(user.id)}&limit=20`);
      renderConnectorStatus(elements.connectorStatus, data.connectors || []);
    } catch (error) {
      elements.connectorStatus.replaceChildren(element("div", { className: "muted", textContent: error.message }));
    }
  }

  async function refreshSourceQuality(user) {
    if (!elements.sourceQuality) {
      return;
    }
    if (user?.role !== "admin") {
      elements.sourceQuality.replaceChildren(
        element("div", { className: "muted", textContent: "Source quality is admin-only." })
      );
      return;
    }
    try {
      const data = await api(`/api/sources/quality?user_id=${encodeURIComponent(user.id)}&limit=12`);
      renderSourceQuality(elements.sourceQuality, data.source_quality || {});
    } catch (error) {
      elements.sourceQuality.replaceChildren(element("div", { className: "muted", textContent: error.message }));
    }
  }

  async function refreshJobs(user) {
    if (!elements.jobs) {
      return;
    }
    if (user?.role !== "admin") {
      elements.jobs.replaceChildren(element("div", { className: "muted", textContent: "Job ledger is admin-only." }));
      return;
    }
    try {
      const data = await api(`/api/ingestion/jobs?user_id=${encodeURIComponent(user.id)}&limit=4`);
      renderJobList(elements.jobs, data.jobs || []);
    } catch (error) {
      elements.jobs.replaceChildren(element("div", { className: "muted", textContent: error.message }));
    }
  }

  async function sync() {
    const user = currentUser();
    const isAdmin = user?.role === "admin";
    renderSummary(elements.summary, user);
    elements.previewButton.disabled = !isAdmin;
    elements.button.disabled = !isAdmin;
    elements.syncButton.disabled = !isAdmin;
    elements.previewBundleButton.disabled = !isAdmin;
    elements.bundleButton.disabled = !isAdmin;
    elements.githubButton.disabled = !isAdmin;
    if (!isAdmin) {
      setStatus(elements.status, "Switch to Avery Admin before ingesting a source.");
    } else if (!elements.status.textContent || elements.status.textContent.includes("Switch to")) {
      setStatus(elements.status, "Ready to ingest a local source.", "ok");
    }
    await refreshSourceBundleCatalog(user);
    await refreshConnectorStatus(user);
    await refreshSourceQuality(user);
    await refreshJobs(user);
  }

  async function previewParse() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.previewButton.disabled = true;
    elements.button.disabled = true;
    elements.syncButton.disabled = true;
    elements.previewBundleButton.disabled = true;
    elements.bundleButton.disabled = true;
    elements.githubButton.disabled = true;
    setStatus(elements.status, "Previewing parser contract...");
    try {
      const payload = await buildPayload(elements, user.id);
      const data = await api("/api/documents/parse-preview", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const preview = data.preview || {};
      renderParsePreview(elements.parsePreview, preview);
      const parserName = preview.parser?.name || "parser";
      setStatus(
        elements.status,
        `Previewed ${parserName}: ${preview.chunk_count || 0} chunks, hash ${String(preview.source_hash || "").slice(0, 12)}..., raw body returned: ${preview.raw_body_returned ? "yes" : "no"}.`,
        preview.would_index ? "ok" : "warn"
      );
    } catch (error) {
      setStatus(elements.status, error.message, "error");
    } finally {
      await sync();
    }
  }

  async function submit() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.previewButton.disabled = true;
    elements.button.disabled = true;
    setStatus(elements.status, "Ingesting document...");
    try {
      const payload = await buildPayload(elements, user.id);
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
    elements.previewButton.disabled = true;
    elements.syncButton.disabled = true;
    elements.previewBundleButton.disabled = true;
    elements.bundleButton.disabled = true;
    elements.githubButton.disabled = true;
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

  async function syncGitHubSource() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.button.disabled = true;
    elements.previewButton.disabled = true;
    elements.syncButton.disabled = true;
    elements.previewBundleButton.disabled = true;
    elements.bundleButton.disabled = true;
    elements.githubButton.disabled = true;
    setStatus(elements.status, "Queueing GitHub connector sync...");
    try {
      const data = await api("/api/connectors/github/sync", {
        method: "POST",
        body: JSON.stringify(buildGitHubConnectorPayload(user.id)),
      });
      const github = data.github || {};
      const result = data.result?.sync || data.job?.result || {};
      const replayed = data.idempotency_replayed ? "Replayed" : "Completed";
      setStatus(
        elements.status,
        `${replayed} GitHub job ${data.job.id} (${data.job.status}): ${github.record_count || result.document_count || 0} records from ${github.owner}/${github.repo}.`,
        "ok"
      );
      await onIngested(data);
    } catch (error) {
      setStatus(elements.status, error.message, "error");
    } finally {
      await sync();
    }
  }

  async function syncSourceBundle() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.button.disabled = true;
    elements.previewButton.disabled = true;
    elements.syncButton.disabled = true;
    elements.previewBundleButton.disabled = true;
    elements.bundleButton.disabled = true;
    elements.githubButton.disabled = true;
    setStatus(elements.status, "Queueing source bundle sync...");
    try {
      const data = await api("/api/connectors/source-bundle/sync", {
        method: "POST",
        body: JSON.stringify(buildSourceBundlePayload(user.id)),
      });
      const bundle = data.source_bundle || {};
      const result = data.result?.sync || data.job?.result || {};
      const replayed = data.idempotency_replayed ? "Replayed" : "Completed";
      setStatus(
        elements.status,
        `${replayed} bundle job ${data.job.id} (${data.job.status}): ${bundle.document_count || result.document_count || 0} docs from ${bundle.bundle || "source bundle"}.`,
        "ok"
      );
      await onIngested(data);
    } catch (error) {
      setStatus(elements.status, error.message, "error");
    } finally {
      await sync();
    }
  }

  async function previewSourceBundle() {
    const user = currentUser();
    if (!user) {
      setStatus(elements.status, "No user selected.", "error");
      return;
    }
    elements.button.disabled = true;
    elements.previewButton.disabled = true;
    elements.syncButton.disabled = true;
    elements.previewBundleButton.disabled = true;
    elements.bundleButton.disabled = true;
    elements.githubButton.disabled = true;
    setStatus(elements.status, "Previewing source bundle manifest...");
    try {
      const data = await api(
        `/api/connectors/source-bundle/catalog?user_id=${encodeURIComponent(user.id)}&bundle=operations-handbook`
      );
      renderSourceBundleCatalog(elements.sourceBundleCatalog, data.catalog || {});
      const bundle = data.catalog?.bundles?.[0] || {};
      setStatus(
        elements.status,
        `Previewed ${bundle.bundle || "source bundle"}: ${bundle.document_count || 0} docs, manifest ${String(bundle.manifest_sha256 || "").slice(0, 12)}..., raw bodies returned: ${data.catalog?.raw_bodies_returned ? "yes" : "no"}.`,
        "ok"
      );
    } catch (error) {
      setStatus(elements.status, error.message, "error");
    } finally {
      await sync();
    }
  }

  elements.previewButton.addEventListener("click", previewParse);
  elements.button.addEventListener("click", submit);
  elements.syncButton.addEventListener("click", syncSampleSource);
  elements.previewBundleButton.addEventListener("click", previewSourceBundle);
  elements.bundleButton.addEventListener("click", syncSourceBundle);
  elements.githubButton.addEventListener("click", syncGitHubSource);
  sync();
  return { sync };
}
