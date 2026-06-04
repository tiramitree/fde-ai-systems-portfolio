from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from check_visual_asset_manifest import MANIFEST, ROOT, PngImage, contrast_sample, png_size, sha256


def load_current_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        raise FileNotFoundError("missing docs/visual_assets_manifest.json")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def load_base_manifest(ref: str) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "show", f"{ref}:docs/visual_assets_manifest.json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"could not read base manifest from {ref}: {detail}")
    return json.loads(result.stdout)


def asset_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        raise ValueError("manifest assets must be a list")
    mapped: dict[str, dict[str, Any]] = {}
    for asset in assets:
        path = asset.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("manifest asset entry must include path")
        mapped[path] = asset
    return mapped


def short_hash(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "missing"
    return value[:12]


def format_size(value: object) -> str:
    if isinstance(value, list) and len(value) == 2:
        return f"{value[0]}x{value[1]}"
    if isinstance(value, tuple) and len(value) == 2:
        return f"{value[0]}x{value[1]}"
    return "missing"


def source_hashes(asset: dict[str, Any] | None) -> dict[str, str]:
    if not asset:
        return {}
    sources: dict[str, str] = {}
    for source in asset.get("source_files", []):
        path = source.get("path")
        digest = source.get("sha256")
        if isinstance(path, str) and isinstance(digest, str):
            sources[path] = digest
    return sources


def source_change_summary(base: dict[str, Any] | None, current: dict[str, Any] | None) -> str:
    base_sources = source_hashes(base)
    current_sources = source_hashes(current)
    paths = sorted(set(base_sources) | set(current_sources))
    if not paths:
        return "0 source hashes tracked"
    added = sum(1 for path in paths if path not in base_sources)
    removed = sum(1 for path in paths if path not in current_sources)
    changed = sum(
        1
        for path in paths
        if path in base_sources and path in current_sources and base_sources[path] != current_sources[path]
    )
    unchanged = len(paths) - added - removed - changed
    return f"{changed} changed, {added} added, {removed} removed, {unchanged} unchanged"


def asset_signature(asset: dict[str, Any] | None) -> tuple[Any, ...] | None:
    if not asset:
        return None
    samples = [
        (
            sample.get("name"),
            sample.get("kind"),
            tuple(sample.get("region", [])),
            tuple(sample.get("background", [])) if "background" in sample else None,
            sample.get("minimum_ratio"),
        )
        for sample in asset.get("contrast_samples", [])
    ]
    return (
        asset.get("kind"),
        tuple(asset.get("size", [])),
        asset.get("sha256"),
        tuple(sorted(source_hashes(asset).items())),
        tuple(samples),
    )


def asset_status(base: dict[str, Any] | None, current: dict[str, Any] | None) -> str:
    if base and current:
        return "unchanged" if asset_signature(base) == asset_signature(current) else "changed"
    if current:
        return "added"
    return "removed"


def current_file_checks(asset: dict[str, Any]) -> tuple[list[str], list[str]]:
    lines: list[str] = []
    failures: list[str] = []
    rel_path = asset["path"]
    path = ROOT / rel_path
    if not path.exists():
        return [], [f"{rel_path}: asset file missing"]

    actual_hash = sha256(path)
    actual_size = png_size(path)
    manifest_hash = asset.get("sha256")
    manifest_size = asset.get("size")
    if actual_hash != manifest_hash:
        failures.append(f"{rel_path}: file hash does not match manifest")
    if actual_size and list(actual_size) != manifest_size:
        failures.append(f"{rel_path}: file size {format_size(actual_size)} does not match manifest")

    samples = asset.get("contrast_samples", [])
    if not samples:
        failures.append(f"{rel_path}: missing contrast samples")
        return lines, failures

    image = PngImage(path)
    for sample in samples:
        name = sample.get("name", "unnamed sample")
        minimum_ratio = float(sample.get("minimum_ratio", 4.5))
        ratio, _, _ = contrast_sample(image, sample)
        outcome = "pass" if ratio >= minimum_ratio else "fail"
        lines.append(f"{name}: {outcome} {ratio:.2f}:1 >= {minimum_ratio:.2f}:1")
        if ratio < minimum_ratio:
            failures.append(f"{rel_path}: contrast sample {name!r} is below minimum ratio")
    return lines, failures


def summarize(base_ref: str) -> tuple[str, list[str]]:
    base_assets = asset_map(load_base_manifest(base_ref))
    current_assets = asset_map(load_current_manifest())
    paths = sorted(set(base_assets) | set(current_assets))
    changed_paths = [
        path
        for path in paths
        if asset_status(base_assets.get(path), current_assets.get(path)) != "unchanged"
    ]
    lines = [
        "Visual asset diff summary",
        f"Base: {base_ref}",
        "Manifest: docs/visual_assets_manifest.json",
        f"Assets changed: {len(changed_paths)}/{len(paths)}",
    ]
    failures: list[str] = []

    if not paths:
        lines.append("- no visual assets found")
        return "\n".join(lines), ["manifest has no visual assets"]

    for path in paths:
        base = base_assets.get(path)
        current = current_assets.get(path)
        status = asset_status(base, current)
        if status == "unchanged":
            if current:
                _, current_failures = current_file_checks(current)
                failures.extend(current_failures)
            continue
        active = current or base
        assert active is not None
        lines.extend(
            [
                f"- {path} [{status}]",
                f"  kind: {active.get('kind', 'missing')}",
                f"  size: {format_size(base.get('size') if base else None)} -> {format_size(current.get('size') if current else None)}",
                f"  sha256: {short_hash(base.get('sha256') if base else None)} -> {short_hash(current.get('sha256') if current else None)}",
                f"  source hashes: {source_change_summary(base, current)}",
            ]
        )
        if current:
            contrast_lines, contrast_failures = current_file_checks(current)
            failures.extend(contrast_failures)
            lines.append("  contrast samples:")
            for contrast_line in contrast_lines:
                lines.append(f"    - {contrast_line}")

    if not changed_paths:
        lines.append("- no visual asset differences against base")
    return "\n".join(lines), failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize visual asset manifest changes without printing binary image contents.",
    )
    parser.add_argument("--base", default="HEAD", help="Git ref to compare against. Defaults to HEAD.")
    args = parser.parse_args()

    try:
        summary, failures = summarize(args.base)
    except Exception as exc:
        print(f"Visual asset diff summary failed: {exc}", file=sys.stderr)
        return 1

    print(summary)
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
