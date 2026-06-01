export function installTraceCopyButton(button, getTraceId) {
  const idleText = button.textContent;

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }

  function flash(label) {
    button.textContent = label;
    window.setTimeout(() => {
      button.textContent = idleText;
    }, 1200);
  }

  button.disabled = true;
  button.addEventListener("click", async () => {
    const traceId = getTraceId();
    if (!traceId) {
      return;
    }
    try {
      await copyText(traceId);
      flash("Copied");
    } catch {
      flash("Copy failed");
    }
  });

  return function setTraceId(traceId) {
    button.disabled = !traceId;
  };
}
