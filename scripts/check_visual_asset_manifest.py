from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "visual_assets_manifest.json"

REQUIRED_ASSETS = {
    "docs/assets/secure-knowledge-copilot-screenshot.png",
    "docs/assets/regulated-ops-agent-screenshot.png",
    "docs/assets/ai-reliability-incident-console-screenshot.png",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def main() -> int:
    failures: list[str] = []
    if not MANIFEST.exists():
        print("Visual asset manifest check failed:")
        print("- missing docs/visual_assets_manifest.json")
        return 1

    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = payload.get("assets", [])
    paths = {asset.get("path") for asset in assets}
    for required in sorted(REQUIRED_ASSETS - paths):
        failures.append(f"manifest missing required asset: {required}")

    for asset in assets:
        rel_path = asset.get("path")
        if not rel_path:
            failures.append("manifest asset entry is missing path")
            continue
        asset_path = ROOT / rel_path
        if not asset_path.exists():
            failures.append(f"{rel_path}: asset file missing")
            continue

        expected_hash = asset.get("sha256")
        actual_hash = sha256(asset_path)
        if expected_hash != actual_hash:
            failures.append(f"{rel_path}: sha256 mismatch; refresh asset or manifest")

        expected_size = asset.get("size")
        if expected_size:
            actual_size = png_size(asset_path)
            if not actual_size:
                failures.append(f"{rel_path}: expected PNG asset")
            elif list(actual_size) != expected_size:
                failures.append(f"{rel_path}: expected size {expected_size}, found {list(actual_size)}")

        for source in asset.get("source_files", []):
            source_rel = source.get("path")
            source_hash = source.get("sha256")
            if not source_rel or not source_hash:
                failures.append(f"{rel_path}: source entry must include path and sha256")
                continue
            source_path = ROOT / source_rel
            if not source_path.exists():
                failures.append(f"{rel_path}: source file missing: {source_rel}")
                continue
            if sha256(source_path) != source_hash:
                failures.append(f"{rel_path}: source file changed since capture: {source_rel}")

    if failures:
        print("Visual asset manifest check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Visual asset manifest check passed: README screenshots match recorded assets and source hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
