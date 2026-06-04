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

export function installTraceKeyboardNavigation(container) {
  const navigationKeys = ["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft", "Home", "End"];

  container.addEventListener("keydown", (event) => {
    const traceNodes = Array.from(container.querySelectorAll("[data-trace-id]"));
    if (!traceNodes.length) {
      return;
    }

    if (event.key === " " && traceNodes.includes(document.activeElement)) {
      event.preventDefault();
      document.activeElement.click();
      return;
    }

    if (!navigationKeys.includes(event.key)) {
      return;
    }

    event.preventDefault();
    const selectedIndex = traceNodes.findIndex((node) => node.classList.contains("selectedTrace"));
    const activeIndex = traceNodes.indexOf(document.activeElement);
    const currentIndex = activeIndex >= 0 ? activeIndex : Math.max(selectedIndex, 0);
    let nextIndex = currentIndex;

    if (event.key === "ArrowDown" || event.key === "ArrowRight") {
      nextIndex = Math.min(currentIndex + 1, traceNodes.length - 1);
    } else if (event.key === "ArrowUp" || event.key === "ArrowLeft") {
      nextIndex = Math.max(currentIndex - 1, 0);
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = traceNodes.length - 1;
    }

    traceNodes[nextIndex].focus({ preventScroll: true });
    traceNodes[nextIndex].scrollIntoView({ block: "nearest" });
  });
}

export function installTraceHashSync(onHashChange = () => {}) {
  window.addEventListener("hashchange", () => {
    syncTraceSelection();
    onHashChange(selectedTraceId());
  });
}
