from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATTERNS = [
    "sk-",
    "CV_Runze",
    "Runze Zheng",
    "C:\\NYU",
    "C:\\Users",
    "C:/Users",
    "OneDrive",
    "xwechat",
    "wxid_",
    "11758",
    "github_pat_",
    "ghp_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "AKIA",
    "BEGIN PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
]

FORBIDDEN_POSITIONING_PATTERNS = [
    "inter" + "view",
    "res" + "ume",
    "car" + "eer",
    "job" + " search",
    "hir" + "ing",
    "personal" + " development",
    "面" + "试",
    "简" + "历",
    "求" + "职",
    "个人" + "发展",
]

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".html",
    ".css",
    ".js",
    ".example",
    ".dockerignore",
    ".gitignore",
    "",
}

TEXT_FILE_NAMES = {
    ".env.example",
    "Dockerfile",
    "LICENSE",
}

SELF_ALLOWLIST = {
    "scripts/public_safety_scan.py",
}

LOCAL_BROWSER_PROFILE_PREFIXES = (
    "out/",
    "tmp-chrome-preview-profile/",
    "tmp-edge-preview-profile/",
)


def is_text_candidate(path: Path) -> bool:
    return path.suffix in TEXT_EXTENSIONS or path.name in TEXT_FILE_NAMES


def tracked_files(root: Path = ROOT) -> set[str] | None:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def check_forbidden_content(root: Path = ROOT) -> list[str]:
    failures = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if ".git/" in rel or rel in SELF_ALLOWLIST:
            continue
        if any(rel.startswith(prefix) for prefix in LOCAL_BROWSER_PROFILE_PREFIXES):
            continue
        if not is_text_candidate(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                failures.append(f"forbidden public-safety pattern {pattern!r} in {rel}")
    return failures


def check_public_positioning(root: Path = ROOT) -> list[str]:
    failures = []
    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()
        if ".git/" in rel or rel in SELF_ALLOWLIST:
            continue
        if any(rel.startswith(prefix) for prefix in LOCAL_BROWSER_PROFILE_PREFIXES):
            continue
        lowered_rel = rel.lower()
        for pattern in FORBIDDEN_POSITIONING_PATTERNS:
            if pattern in lowered_rel:
                failures.append(f"non-industrial positioning term {pattern!r} in file path {rel}")
        if not path.is_file() or not is_text_candidate(path):
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_POSITIONING_PATTERNS:
            if pattern in text:
                failures.append(f"non-industrial positioning term {pattern!r} in {rel}")
    return failures


def check_runtime_artifacts(root: Path = ROOT) -> list[str]:
    failures = []
    git_files = tracked_files(root)
    if git_files is None:
        return failures
    forbidden_names = {
        "runtime_state.json",
        "eval_runtime_state.json",
        "runtime_state.tmp",
        "server.log",
        "server.err.log",
        "server.job.log",
        "write-test.txt",
    }
    forbidden_suffixes = {".pyc", ".sqlite", ".sqlite-journal"}
    for rel in git_files:
        parts = rel.split("/")
        name = parts[-1]
        if "__pycache__" in parts:
            failures.append(f"runtime artifact present: {rel}")
        elif name in forbidden_names:
            failures.append(f"runtime artifact present: {rel}")
        elif any(name.endswith(suffix) for suffix in forbidden_suffixes):
            failures.append(f"runtime artifact present: {rel}")
    return failures


def run_scan(root: Path = ROOT) -> list[str]:
    failures = []
    failures.extend(check_forbidden_content(root))
    failures.extend(check_public_positioning(root))
    failures.extend(check_runtime_artifacts(root))
    return failures


def main() -> int:
    failures = run_scan(ROOT)
    if failures:
        print("Public safety scan failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Public safety scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
