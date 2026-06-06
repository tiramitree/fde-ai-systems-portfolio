from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FrontendProject:
    name: str
    root: Path
    title: str
    required_ids: set[str]
    required_data_attribute: str
    minimum_quick_actions: int


PROJECTS = [
    FrontendProject(
        name="secure-enterprise-knowledge-copilot",
        root=ROOT / "secure-enterprise-knowledge-copilot",
        title="Secure Enterprise Knowledge Copilot",
        required_ids={
            "health",
            "themeToggle",
            "userSelect",
            "userMeta",
            "documents",
            "ingestionSummary",
            "ingestTitle",
            "ingestClassification",
            "ingestRoles",
            "ingestMime",
            "ingestBody",
            "ingestReplace",
            "ingestDocument",
            "ingestionStatus",
            "runEval",
            "evalOutput",
            "question",
            "ask",
            "answer",
            "citations",
            "trace",
            "copyTraceId",
            "copyTraceLink",
            "audit",
            "traces",
            "scenarioSummary",
            "scenarioDraft",
            "scenarioDiff",
            "scenarioStatus",
            "saveScenarioDraft",
            "copyScenarioDraft",
            "resetScenarioDraft",
            "clearScenarioDraft",
        },
        required_data_attribute="data-question",
        minimum_quick_actions=4,
    ),
    FrontendProject(
        name="regulated-customer-operations-agent",
        root=ROOT / "regulated-customer-operations-agent",
        title="Regulated Customer Operations Agent",
        required_ids={
            "health",
            "themeToggle",
            "userSelect",
            "caseSelect",
            "caseSummary",
            "runEval",
            "evalOutput",
            "message",
            "runAgent",
            "decision",
            "approvals",
            "trace",
            "copyTraceId",
            "copyTraceLink",
            "audit",
            "traces",
            "scenarioSummary",
            "scenarioDraft",
            "scenarioDiff",
            "scenarioStatus",
            "saveScenarioDraft",
            "copyScenarioDraft",
            "resetScenarioDraft",
            "clearScenarioDraft",
        },
        required_data_attribute="data-message",
        minimum_quick_actions=4,
    ),
    FrontendProject(
        name="ai-reliability-incident-console",
        root=ROOT / "ai-reliability-incident-console",
        title="AI Reliability Incident Console",
        required_ids={
            "health",
            "themeToggle",
            "userSelect",
            "releaseSelect",
            "releaseSummary",
            "incidentSelect",
            "incidentSummary",
            "runEval",
            "evalOutput",
            "runTriage",
            "decision",
            "failedEvals",
            "trace",
            "copyTraceId",
            "copyTraceLink",
            "audit",
            "traces",
            "scenarioSummary",
            "scenarioDraft",
            "scenarioDiff",
            "scenarioStatus",
            "saveScenarioDraft",
            "copyScenarioDraft",
            "resetScenarioDraft",
            "clearScenarioDraft",
        },
        required_data_attribute="data-incident",
        minimum_quick_actions=2,
    ),
]


class FrontendHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.labels_for: set[str] = set()
        self.links: list[str] = []
        self.scripts: list[dict[str, str]] = []
        self.data_attributes: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if "id" in attr_map:
            self.ids.append(attr_map["id"])
        if tag == "label" and "for" in attr_map:
            self.labels_for.add(attr_map["for"])
        if tag == "link" and attr_map.get("rel") == "stylesheet" and "href" in attr_map:
            self.links.append(attr_map["href"])
        if tag == "script" and "src" in attr_map:
            self.scripts.append(attr_map)
        for name in attr_map:
            if name.startswith("data-"):
                self.data_attributes.append(name)
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def parse_html(path: Path) -> FrontendHtmlParser:
    parser = FrontendHtmlParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def local_asset_path(project: FrontendProject, src: str) -> Path | None:
    if src.startswith(("http://", "https://", "//")):
        return None
    normalized = src.split("?", 1)[0].split("#", 1)[0]
    if normalized.startswith("/"):
        return project.root / "web" / normalized.lstrip("/")
    return project.root / "web" / normalized


def check_html(project: FrontendProject, parser: FrontendHtmlParser) -> list[str]:
    failures: list[str] = []
    title = "".join(parser.title_parts).strip()
    if title != project.title:
        failures.append(f"{project.name}: expected title {project.title!r}, found {title!r}")

    ids = set(parser.ids)
    duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicates:
        failures.append(f"{project.name}: duplicate DOM id(s): {', '.join(duplicates)}")

    missing_ids = sorted(project.required_ids - ids)
    if missing_ids:
        failures.append(f"{project.name}: missing required DOM id(s): {', '.join(missing_ids)}")

    missing_input_labels = sorted(
        field_id
        for field_id in ("userSelect", "caseSelect", "question", "message")
        if field_id in project.required_ids and field_id not in parser.labels_for
    )
    if missing_input_labels:
        failures.append(f"{project.name}: missing label for input id(s): {', '.join(missing_input_labels)}")

    quick_actions = parser.data_attributes.count(project.required_data_attribute)
    if quick_actions < project.minimum_quick_actions:
        failures.append(
            f"{project.name}: expected at least {project.minimum_quick_actions} quick actions, found {quick_actions}"
        )

    if "/styles.css" not in parser.links:
        failures.append(f"{project.name}: missing /styles.css stylesheet link")
    for link in parser.links:
        asset = local_asset_path(project, link)
        if asset is None:
            failures.append(f"{project.name}: remote stylesheet is not allowed: {link}")
        elif not asset.exists():
            failures.append(f"{project.name}: stylesheet target missing: {link}")

    module_scripts = [script for script in parser.scripts if script.get("type") == "module"]
    if len(module_scripts) != 1 or module_scripts[0].get("src") != "/js/app.js":
        failures.append(f"{project.name}: expected exactly one module script at /js/app.js")
    for script in parser.scripts:
        asset = local_asset_path(project, script["src"])
        if asset is None:
            failures.append(f"{project.name}: remote script is not allowed: {script['src']}")
        elif not asset.exists():
            failures.append(f"{project.name}: script target missing: {script['src']}")
    return failures


def imported_modules(js_path: Path) -> list[str]:
    text = js_path.read_text(encoding="utf-8")
    return re.findall(r"^\s*import\s+.*?\s+from\s+[\"'](\./[^\"']+)[\"'];", text, flags=re.MULTILINE)


def by_id_calls(js_path: Path) -> set[str]:
    return set(re.findall(r"\bbyId\([\"']([^\"']+)[\"']\)", js_path.read_text(encoding="utf-8")))


def api_paths(js_path: Path) -> set[str]:
    text = js_path.read_text(encoding="utf-8")
    literal_paths = set(re.findall(r"\bapi\([\"'](/api/[^\"']*)[\"']", text))
    template_paths = set(re.findall(r"\bapi\(`(/api/[^`$]*)", text))
    return literal_paths | template_paths


def check_javascript(project: FrontendProject, html_ids: set[str]) -> list[str]:
    failures: list[str] = []
    js_dir = project.root / "web" / "js"
    expected_modules = {
        "api.js",
        "app.js",
        "clipboard.js",
        "dom.js",
        "renderers.js",
        "scenarioEditor.js",
        "theme.js",
        "traceLinks.js",
    }
    present_modules = {path.name for path in js_dir.glob("*.js")}
    missing_modules = sorted(expected_modules - present_modules)
    if missing_modules:
        failures.append(f"{project.name}: missing JS module(s): {', '.join(missing_modules)}")

    for js_path in sorted(js_dir.glob("*.js")):
        rel = js_path.relative_to(ROOT).as_posix()
        for imported in imported_modules(js_path):
            target = (js_path.parent / imported).resolve()
            if js_path.parent.resolve() not in target.parents and target != js_path.parent.resolve():
                failures.append(f"{rel}: import escapes module directory: {imported}")
            elif not target.exists():
                failures.append(f"{rel}: missing imported module: {imported}")

        missing_dom_ids = sorted(by_id_calls(js_path) - html_ids)
        if missing_dom_ids:
            failures.append(f"{rel}: byId target(s) missing from HTML: {', '.join(missing_dom_ids)}")

        for path in sorted(api_paths(js_path)):
            if not path.startswith("/api/"):
                failures.append(f"{rel}: API path must be rooted under /api/: {path}")

    app_text = (js_dir / "app.js").read_text(encoding="utf-8")
    clipboard_text = (js_dir / "clipboard.js").read_text(encoding="utf-8")
    required_app_markers = [
        'import { installCopyButton, installTraceCopyButton } from "./clipboard.js";',
        'import { installScenarioEditor } from "./scenarioEditor.js";',
        'import { installThemeToggle } from "./theme.js";',
        'installThemeToggle(byId("themeToggle"))',
        "installTraceKeyboardNavigation",
        'lastTraceId: ""',
        'loadScenario: () => api("/api/scenario")',
        'installTraceCopyButton(byId("copyTraceId"), () => state.lastTraceId)',
        'installCopyButton(byId("copyTraceLink"), () => traceUrl(state.lastTraceId))',
        "state.lastTraceId = data.trace_id",
        "setTraceCopyState(data.trace_id)",
        "setTraceLinkCopyState(data.trace_id)",
        "setTraceHash(data.trace_id)",
        "selectedTraceId()",
        "syncTraceSelection()",
        'installTraceKeyboardNavigation(byId("traces"))',
    ]
    for marker in required_app_markers:
        if marker not in app_text:
            failures.append(f"{project.name}: app.js missing trace-copy marker: {marker}")

    required_clipboard_markers = [
        "export function installCopyButton",
        "export async function copyText",
        "export function installTraceCopyButton",
        "navigator.clipboard.writeText",
        'document.createElement("textarea")',
        'button.disabled = !value',
    ]
    for marker in required_clipboard_markers:
        if marker not in clipboard_text:
            failures.append(f"{project.name}: clipboard.js missing marker: {marker}")

    trace_links_text = (js_dir / "traceLinks.js").read_text(encoding="utf-8")
    required_trace_link_markers = [
        "export function traceHash",
        "export function traceUrl",
        "export function selectedTraceId",
        "export function setTraceHash",
        "export function syncTraceSelection",
        "export function installTraceKeyboardNavigation",
        "export function installTraceHashSync",
        "[data-trace-id]",
        "ArrowDown",
        "focus(",
        "URLSearchParams",
    ]
    for marker in required_trace_link_markers:
        if marker not in trace_links_text:
            failures.append(f"{project.name}: traceLinks.js missing marker: {marker}")

    renderers_text = (js_dir / "renderers.js").read_text(encoding="utf-8")
    for marker in ["traceHash(trace.id)", "selectedTrace"]:
        if marker not in renderers_text:
            failures.append(f"{project.name}: renderers.js missing trace deep-link marker: {marker}")
    if project.name == "secure-enterprise-knowledge-copilot" and "retrieval_profile: data.retrieval_profile" not in renderers_text:
        failures.append(f"{project.name}: renderers.js missing retrieval profile trace detail")
    if "data-trace-id" not in renderers_text and "dataset: { traceId: trace.id }" not in renderers_text:
        failures.append(f"{project.name}: renderers.js missing trace id data marker")

    if project.name == "secure-enterprise-knowledge-copilot":
        ingestion_text = (js_dir / "ingestion.js").read_text(encoding="utf-8")
        required_ingestion_markers = [
            "export function installIngestionPanel",
            "/api/documents/ingest",
            "admin required",
            "source_hash",
            "onIngested",
            "currentUser",
        ]
        for marker in required_ingestion_markers:
            if marker not in ingestion_text and marker not in app_text:
                failures.append(f"{project.name}: ingestion.js missing marker: {marker}")

    scenario_text = (js_dir / "scenarioEditor.js").read_text(encoding="utf-8")
    required_scenario_markers = [
        "export function installScenarioEditor",
        "localStorage.getItem",
        "localStorage.setItem",
        "localStorage.removeItem",
        "copyText",
        "copyButton",
        "diffRows",
        "scenarioDiffRow",
        "scenarioDiffState",
        "JSON.parse",
        "JSON.stringify",
        "saveScenarioDraft",
        "copyScenarioDraft",
    ]
    for marker in required_scenario_markers:
        if marker not in scenario_text and marker not in app_text:
            failures.append(f"{project.name}: scenarioEditor.js missing marker: {marker}")

    theme_text = (js_dir / "theme.js").read_text(encoding="utf-8")
    required_theme_markers = [
        "export function installThemeToggle",
        "localStorage.getItem",
        "localStorage.setItem",
        "prefers-color-scheme: dark",
        "document.documentElement.dataset.theme",
        "aria-checked",
    ]
    for marker in required_theme_markers:
        if marker not in theme_text:
            failures.append(f"{project.name}: theme.js missing marker: {marker}")
    return failures


def check_project(project: FrontendProject) -> list[str]:
    html_path = project.root / "web" / "index.html"
    if not html_path.exists():
        return [f"{project.name}: missing web/index.html"]
    parser = parse_html(html_path)
    failures = []
    failures.extend(check_html(project, parser))
    failures.extend(check_javascript(project, set(parser.ids)))
    styles = (project.root / "web" / "styles.css").read_text(encoding="utf-8")
    for marker in [
        ".sectionHeader",
        ".sectionActions",
        ".secondaryButton",
        ".secondaryButton:disabled",
        ".topbarActions",
        ".themeToggle",
        ':root[data-theme="dark"]',
        "overflow-x: hidden",
        "overflow-wrap: anywhere",
        "@media (max-width: 700px)",
        "button:focus-visible",
        "select:focus-visible",
        "textarea:focus-visible",
        "input:focus-visible",
        ".traceLink",
        ".traceLink:focus-visible",
        "prefers-reduced-motion",
        "animation-duration",
        "transition-duration",
        "--focus-ring",
        ".selectedTrace",
        ".scenarioDraft",
        ".scenarioDiff",
        ".scenarioDiffState",
        ".scenarioStatus",
    ]:
        if marker not in styles:
            failures.append(f"{project.name}: styles.css missing trace-copy style marker: {marker}")
    if project.name == "secure-enterprise-knowledge-copilot":
        for marker in [".ingestionBody", ".inlineCheck", ".ingestionGrid", ".ingestionWide"]:
            if marker not in styles:
                failures.append(f"{project.name}: styles.css missing ingestion style marker: {marker}")
    return failures


def main() -> int:
    failures: list[str] = []
    for project in PROJECTS:
        failures.extend(check_project(project))

    if failures:
        print("Frontend integrity check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Frontend integrity check passed: HTML assets, ES modules, DOM wiring, labels, "
        "trace-copy controls, keyboard trace navigation, copyable scenario drafts, local diffs, accessibility CSS, theme controls, and quick actions are intact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
