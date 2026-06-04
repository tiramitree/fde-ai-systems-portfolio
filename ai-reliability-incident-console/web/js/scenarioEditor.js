import { copyText } from "./clipboard.js";

function draftKey(appName) {
  return `fde-scenario-draft:${appName}`;
}

function formatFiles(files) {
  return JSON.stringify(files, null, 2);
}

function summarize(files) {
  return files.map((file) => `${file.path} (${file.record_count})`).join(" | ");
}

function normalize(value) {
  if (Array.isArray(value)) {
    return value.map(normalize);
  }
  if (value && typeof value === "object") {
    return Object.keys(value).sort().reduce((result, key) => {
      result[key] = normalize(value[key]);
      return result;
    }, {});
  }
  return value;
}

function signature(value) {
  return JSON.stringify(normalize(value));
}

function filesByPath(files) {
  const map = new Map();
  files.forEach((file, index) => {
    const path = file && typeof file.path === "string" ? file.path : `draft-item-${index + 1}`;
    map.set(path, file);
  });
  return map;
}

function diffRows(seedFiles, draftFiles) {
  const seedMap = filesByPath(seedFiles);
  const draftMap = filesByPath(draftFiles);
  const paths = Array.from(new Set([...seedMap.keys(), ...draftMap.keys()])).sort();
  return paths.map((path) => {
    if (!seedMap.has(path)) {
      return { path, state: "added" };
    }
    if (!draftMap.has(path)) {
      return { path, state: "removed" };
    }
    return {
      path,
      state: signature(seedMap.get(path)) === signature(draftMap.get(path)) ? "unchanged" : "changed",
    };
  });
}

export function installScenarioEditor({ loadScenario, summary, draft, diff, status, saveButton, resetButton, clearButton, copyButton }) {
  let seedText = "";
  let seedFiles = [];
  let storageKey = "";
  let loaded = false;

  function setStatus(message, state = "neutral") {
    status.textContent = message;
    status.dataset.state = state;
  }

  function renderDiff(rows) {
    diff.replaceChildren();
    rows.forEach((row) => {
      const item = document.createElement("div");
      item.className = "scenarioDiffRow";
      const state = document.createElement("span");
      state.className = `scenarioDiffState ${row.state}`;
      state.textContent = row.state;
      const path = document.createElement("span");
      path.className = "scenarioDiffPath";
      path.textContent = row.path;
      item.append(state, path);
      diff.append(item);
    });
  }

  function setDiffMessage(message) {
    diff.replaceChildren();
    diff.textContent = message;
  }

  function validateDraft() {
    try {
      const parsed = JSON.parse(draft.value);
      if (!Array.isArray(parsed)) {
        throw new Error("draft must be a file array");
      }
      saveButton.disabled = false;
      copyButton.disabled = !loaded;
      renderDiff(diffRows(seedFiles, parsed));
      setStatus("Valid local draft", "ok");
      return true;
    } catch (error) {
      saveButton.disabled = true;
      copyButton.disabled = true;
      setDiffMessage("Fix JSON to compare draft.");
      setStatus(`Invalid JSON: ${error.message}`, "error");
      return false;
    }
  }

  loadScenario()
    .then((payload) => {
      const scenario = payload.scenario;
      storageKey = draftKey(scenario.app);
      seedFiles = scenario.files;
      seedText = formatFiles(seedFiles);
      const savedDraft = localStorage.getItem(storageKey);
      summary.textContent = summarize(scenario.files);
      draft.value = savedDraft || seedText;
      loaded = true;
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
  copyButton.addEventListener("click", async () => {
    try {
      await copyText(draft.value);
      setStatus("Draft copied", "ok");
    } catch {
      setStatus("Copy failed", "error");
    }
  });
  clearButton.addEventListener("click", () => {
    localStorage.removeItem(storageKey);
    draft.value = seedText;
    clearButton.disabled = true;
    validateDraft();
    setStatus("Local draft cleared", "ok");
  });
}
