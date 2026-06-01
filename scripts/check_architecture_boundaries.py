from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ProjectBoundary:
    name: str
    root: Path
    package: str
    app_allowed_modules: frozenset[str]
    required_symbols: dict[str, frozenset[str]]
    forbidden_backend_imports: frozenset[str]


PROJECTS = [
    ProjectBoundary(
        name="Secure Enterprise Knowledge Copilot",
        root=ROOT / "secure-enterprise-knowledge-copilot",
        package="copilot",
        app_allowed_modules=frozenset({"copilot.api", "copilot.storage"}),
        required_symbols={
            "app.py": frozenset({"Handler", "main"}),
            "src/copilot/api.py": frozenset({"ApiError", "CopilotApi"}),
            "src/copilot/answering.py": frozenset({"generate_answer"}),
            "src/copilot/retrieval.py": frozenset({"retrieve", "tokenize"}),
            "src/copilot/security.py": frozenset({"detect_prompt_injection", "sanitize_evidence"}),
            "src/copilot/storage.py": frozenset({"JsonStore", "connect", "init_db"}),
            "src/copilot/evals.py": frozenset({"run_evals"}),
        },
        forbidden_backend_imports=frozenset({"ops_agent", "scripts", "web", "docs", "app"}),
    ),
    ProjectBoundary(
        name="Regulated Customer Operations Agent",
        root=ROOT / "regulated-customer-operations-agent",
        package="ops_agent",
        app_allowed_modules=frozenset({"ops_agent.api", "ops_agent.storage"}),
        required_symbols={
            "app.py": frozenset({"Handler", "main"}),
            "src/ops_agent/api.py": frozenset({"ApiError", "OpsAgentApi"}),
            "src/ops_agent/agent.py": frozenset({"classify_intent", "process_message"}),
            "src/ops_agent/tools.py": frozenset(
                {
                    "approve_action",
                    "direct_side_effect_blocked",
                    "request_approval",
                    "search_listings",
                    "search_recall_policy",
                }
            ),
            "src/ops_agent/storage.py": frozenset({"JsonStore", "connect", "init_state"}),
            "src/ops_agent/evals.py": frozenset({"run_evals"}),
        },
        forbidden_backend_imports=frozenset({"copilot", "scripts", "web", "docs", "app"}),
    ),
]


IMPORT_FROM_RE = re.compile(r"\bfrom\s+['\"](?P<specifier>[^'\"]+)['\"]")
SIDE_EFFECT_IMPORT_RE = re.compile(r"^\s*import\s+['\"](?P<specifier>[^'\"]+)['\"]", re.MULTILINE)


def parse_python(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def imported_modules(tree: ast.Module, current_package: str | None = None) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if current_package and node.module:
                    modules.append(f"{current_package}.{node.module}")
                elif current_package:
                    modules.append(current_package)
            elif node.module:
                modules.append(node.module)
    return modules


def top_level_symbols(tree: ast.Module) -> set[str]:
    symbols: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            symbols.add(node.target.id)
    return symbols


def check_required_symbols(project: ProjectBoundary) -> list[str]:
    failures: list[str] = []
    for rel_path, expected_symbols in project.required_symbols.items():
        path = project.root / rel_path
        if not path.exists():
            failures.append(f"{project.name}: missing required module {rel_path}")
            continue
        symbols = top_level_symbols(parse_python(path))
        for symbol in sorted(expected_symbols - symbols):
            failures.append(f"{project.name}: {rel_path} missing symbol {symbol}")
    return failures


def check_app_is_thin(project: ProjectBoundary) -> list[str]:
    failures: list[str] = []
    app_path = project.root / "app.py"
    tree = parse_python(app_path)
    for module in imported_modules(tree):
        if module == project.package or module.startswith(f"{project.package}."):
            imported = module
            if imported == project.package:
                failures.append(f"{project.name}: app.py imports package root directly")
            elif imported not in project.app_allowed_modules:
                failures.append(
                    f"{project.name}: app.py imports {imported}; HTTP shell may only depend on "
                    f"{', '.join(sorted(project.app_allowed_modules))}"
                )
    return failures


def check_backend_import_boundaries(project: ProjectBoundary) -> list[str]:
    failures: list[str] = []
    package_root = project.root / "src" / project.package
    for path in sorted(package_root.glob("*.py")):
        rel_path = path.relative_to(project.root).as_posix()
        tree = parse_python(path)
        modules = imported_modules(tree, project.package)
        for module in modules:
            top = module.split(".", 1)[0]
            if top in project.forbidden_backend_imports:
                failures.append(f"{project.name}: {rel_path} imports forbidden boundary {module}")
            if path.name != "api.py" and module == f"{project.package}.api":
                failures.append(f"{project.name}: {rel_path} imports API layer")
        if path.name == "storage.py":
            for module in modules:
                if module.startswith(f"{project.package}.") and module != project.package:
                    failures.append(f"{project.name}: {rel_path} should not import higher package modules")
    return failures


def javascript_imports(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    imports = [match.group("specifier") for match in IMPORT_FROM_RE.finditer(text)]
    imports.extend(match.group("specifier") for match in SIDE_EFFECT_IMPORT_RE.finditer(text))
    return imports


def check_frontend_module_boundaries(project: ProjectBoundary) -> list[str]:
    failures: list[str] = []
    web_dir = project.root / "web"
    js_dir = web_dir / "js"
    for path in sorted(js_dir.glob("*.js")):
        rel_path = path.relative_to(project.root).as_posix()
        for specifier in javascript_imports(path):
            if not specifier.startswith(("./", "../")):
                failures.append(f"{project.name}: {rel_path} imports non-local frontend module {specifier}")
                continue
            resolved = (path.parent / specifier).resolve()
            if web_dir.resolve() not in resolved.parents and resolved != web_dir.resolve():
                failures.append(f"{project.name}: {rel_path} imports outside web boundary: {specifier}")
            if resolved.suffix != ".js":
                failures.append(f"{project.name}: {rel_path} imports non-JS module {specifier}")
            if not resolved.exists():
                failures.append(f"{project.name}: {rel_path} imports missing module {specifier}")
    return failures


def check_project_isolation() -> list[str]:
    failures: list[str] = []
    first, second = PROJECTS
    cross_pairs = [
        (first.root, second.root.name),
        (second.root, first.root.name),
    ]
    for root, other_project_dir in cross_pairs:
        for path in sorted((root / "src").rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if other_project_dir in text:
                failures.append(
                    f"{root.name}: {path.relative_to(root).as_posix()} references sibling project directory "
                    f"{other_project_dir}"
                )
    return failures


def main() -> int:
    failures: list[str] = []
    for project in PROJECTS:
        failures.extend(check_required_symbols(project))
        failures.extend(check_app_is_thin(project))
        failures.extend(check_backend_import_boundaries(project))
        failures.extend(check_frontend_module_boundaries(project))
    failures.extend(check_project_isolation())

    if failures:
        print("Architecture boundary check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Architecture boundary check passed.")
    print("- app.py files stay as HTTP/static shells over API classes")
    print("- backend src packages do not import sibling projects, web assets, docs, scripts, or app.py")
    print("- non-API backend modules do not import the API layer")
    print("- frontend JavaScript modules stay local to their web boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
