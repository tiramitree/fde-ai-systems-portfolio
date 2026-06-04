export function traceHash(traceId) {
  return traceId ? `#trace=${encodeURIComponent(traceId)}` : "";
}

export function traceUrl(traceId) {
  if (!traceId) {
    return "";
  }
  const url = new URL(window.location.href);
  url.hash = traceHash(traceId).slice(1);
  return url.toString();
}

export function selectedTraceId() {
  const hash = window.location.hash.replace(/^#/, "");
  const params = new URLSearchParams(hash);
  return params.get("trace") || "";
}

export function setTraceHash(traceId) {
  if (!traceId) {
    return;
  }
  const url = new URL(window.location.href);
  url.hash = traceHash(traceId).slice(1);
  window.history.replaceState(null, "", url);
}

export function syncTraceSelection() {
  const selected = selectedTraceId();
  let selectedNode = null;
  document.querySelectorAll("[data-trace-id]").forEach((node) => {
    const active = Boolean(selected) && node.dataset.traceId === selected;
    node.classList.toggle("selectedTrace", active);
    if (active) {
      node.setAttribute("aria-current", "true");
      selectedNode = node;
    } else {
      node.removeAttribute("aria-current");
    }
  });
  if (selectedNode) {
    selectedNode.scrollIntoView({ block: "nearest" });
  }
}

export function installTraceHashSync(onHashChange = () => {}) {
  window.addEventListener("hashchange", () => {
    syncTraceSelection();
    onHashChange(selectedTraceId());
  });
}
