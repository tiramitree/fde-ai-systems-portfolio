function draftKey(appName) {
  return `fde-scenario-draft:${appName}`;
}

function formatFiles(files) {
  return JSON.stringify(files, null, 2);
}

function summarize(files) {
  return files.map((file) => `${file.path} (${file.record_count})`).join(" | ");
}

export function installScenarioEditor({ loadScenario, summary, draft, status, saveButton, resetButton, clearButton }) {
  let seedText = "";
  let storageKey = "";

  function setStatus(message, state = "neutral") {
    status.textContent = message;
    status.dataset.state = state;
  }

  function validateDraft() {
    try {
      JSON.parse(draft.value);
      saveButton.disabled = false;
      setStatus("Valid local draft", "ok");
      return true;
    } catch (error) {
      saveButton.disabled = true;
      setStatus(`Invalid JSON: ${error.message}`, "error");
      return false;
    }
  }

  loadScenario()
    .then((payload) => {
      const scenario = payload.scenario;
      storageKey = draftKey(scenario.app);
      seedText = formatFiles(scenario.files);
      const savedDraft = localStorage.getItem(storageKey);
      summary.textContent = summarize(scenario.files);
      draft.value = savedDraft || seedText;
      resetButton.disabled = false;
      clearButton.disabled = !savedDraft;
      validateDraft();
      if (savedDraft) {
        setStatus("Local draft restored", "ok");
      }
    })
    .catch((error) => {
      setStatus(error.message, "error");
    });

  draft.addEventListener("input", validateDraft);
  saveButton.addEventListener("click", () => {
    if (!validateDraft()) {
      return;
    }
    localStorage.setItem(storageKey, draft.value);
    clearButton.disabled = false;
    setStatus("Local draft saved", "ok");
  });
  resetButton.addEventListener("click", () => {
    draft.value = seedText;
    validateDraft();
    setStatus("Seed snapshot restored", "ok");
  });
  clearButton.addEventListener("click", () => {
    localStorage.removeItem(storageKey);
    draft.value = seedText;
    clearButton.disabled = true;
    validateDraft();
    setStatus("Local draft cleared", "ok");
  });
}
