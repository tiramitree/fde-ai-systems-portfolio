export function installCopyButton(button, getText) {
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
    const text = getText();
    if (!text) {
      return;
    }
    try {
      await copyText(text);
      flash("Copied");
    } catch {
      flash("Copy failed");
    }
  });

  return function setCopyValue(value) {
    button.disabled = !value;
  };
}

export function installTraceCopyButton(button, getTraceId) {
  return installCopyButton(button, getTraceId);
}
