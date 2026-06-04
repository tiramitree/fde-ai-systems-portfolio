const STORAGE_KEY = "regulated-customer-operations-agent-theme";

function readStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Keep the demo usable when browser storage is disabled.
  }
}

function preferredTheme() {
  const storedTheme = readStoredTheme();
  if (storedTheme === "dark" || storedTheme === "light") {
    return storedTheme;
  }
  const media = window.matchMedia?.("(prefers-color-scheme: dark)");
  return media?.matches ? "dark" : "light";
}

function applyTheme(toggle, theme) {
  const dark = theme === "dark";
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  document.documentElement.style.colorScheme = dark ? "dark" : "light";
  toggle.checked = dark;
  toggle.setAttribute("aria-checked", String(dark));
}

export function installThemeToggle(toggle) {
  applyTheme(toggle, preferredTheme());
  toggle.addEventListener("change", () => {
    const nextTheme = toggle.checked ? "dark" : "light";
    writeStoredTheme(nextTheme);
    applyTheme(toggle, nextTheme);
  });
}
