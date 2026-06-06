import { byId, clear, element, renderList, tag } from "./dom.js";
import { traceHash } from "./traceLinks.js";

export function populateUserSelect(users, selectedUser) {
  const select = byId("userSelect");
  clear(select);
  users.forEach((user) => {
    const option = element("option", { textContent: `${user.name} (${user.role})` });
    option.value = user.id;
    select.append(option);
  });
  select.value = selectedUser;
}

export function renderUser(users, selectedUser) {
  const user = users.find((item) => item.id === selectedUser);
  const container = byId("userMeta");
  clear(container);
  if (!user) {
    container.textContent = "No user selected.";
    return;
  }
  container.append(
    element("strong", { textContent: user.name }),
    element("br"),
    tag(user.role),
    tag(user.tenant_id)
  );
}

export function renderDocuments(documents) {
  renderList(
    byId("documents"),
    documents,
    (doc) =>
      element("div", { className: "item" }, [
        element("strong", { textContent: doc.title }),
        element("span", { textContent: doc.source_url }),
        element("br"),
        tag(doc.classification),
        tag(doc.version),
      ]),
    "No visible documents."
  );
}

function sourceSpanLabel(sourceSpan) {
  if (!sourceSpan || sourceSpan.text_unit !== "normalized_text") {
    return "";
  }
  const startLine = Number(sourceSpan.start_line);
  const endLine = Number(sourceSpan.end_line);
  if (!Number.isFinite(startLine) || !Number.isFinite(endLine)) {
    return "";
  }
  return startLine === endLine ? `line ${startLine}` : `lines ${startLine}-${endLine}`;
}

export function renderAnswer(data) {
  const answer = byId("answer");
  clear(answer);
  answer.append(
    element("p", { textContent: data.answer }),
    element("p", {}, [
      tag(`confidence ${data.confidence}`),
      tag(`latency ${data.latency_ms} ms`),
    ])
  );
  if (data.abstain_reason) {
    answer.append(element("p", {}, [tag("abstained", "warn"), document.createTextNode(` ${data.abstain_reason}`)]));
  }
  if (data.security_events.length) {
    answer.append(
      element("p", {}, [
        tag("security event", "danger"),
        document.createTextNode(" Retrieved or user-supplied instructions were ignored."),
      ])
    );
  }

  renderList(
    byId("citations"),
    data.citations,
    (citation) => {
      const spanLabel = sourceSpanLabel(citation.source_span);
      return element("div", { className: "item" }, [
        element("strong", { textContent: citation.title }),
        element("span", { textContent: citation.source_url }),
        element("br"),
        tag(citation.doc_id),
        tag(`score ${citation.score}`),
        spanLabel ? tag(spanLabel) : null,
      ].filter(Boolean));
    },
    "No citations returned."
  );

  byId("trace").textContent = JSON.stringify(
    {
      trace_id: data.trace_id,
      permission_blocked_count: data.permission_blocked_count,
      retrieval_profile: data.retrieval_profile,
      retrieved: data.retrieved,
      missing_evidence: data.missing_evidence,
      security_events: data.security_events,
    },
    null,
    2
  );
}

export function renderAudit(events) {
  const auditTag = (event) => {
    if (event.action === "document_ingested") {
      return tag("ingested");
    }
    return tag(event.details.abstained ? "abstained" : "answered");
  };

  renderList(
    byId("audit"),
    events,
    (event) =>
      element("div", { className: "item" }, [
        element("strong", { textContent: event.action }),
        element("span", { textContent: event.created_at }),
        element("br"),
        tag(event.user_id),
        auditTag(event),
      ]),
    "No audit events."
  );
}

export function renderTraces(traces, selectedTraceId = "") {
  renderList(
    byId("traces"),
    traces,
    (trace) =>
      element("a", {
        className: ["item", "traceLink", trace.id === selectedTraceId ? "selectedTrace" : ""].filter(Boolean).join(" "),
        dataset: { traceId: trace.id },
        href: traceHash(trace.id),
      }, [
        element("strong", { textContent: trace.user_id }),
        element("span", { textContent: trace.question }),
        element("br"),
        tag(trace.id.slice(0, 8)),
        tag(trace.payload.output.abstain_reason ? "abstain" : "answer"),
      ]),
    "No traces."
  );
}
