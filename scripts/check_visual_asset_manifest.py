from __future__ import annotations

import hashlib
import json
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "visual_assets_manifest.json"

REQUIRED_ASSETS = {
    "docs/assets/secure-knowledge-copilot-screenshot.png",
    "docs/assets/regulated-ops-agent-screenshot.png",
    "docs/assets/ai-reliability-incident-console-screenshot.png",
}


class PngImage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.width, self.height, self.channels, self.rows = self._decode(path)

    @staticmethod
    def _decode(path: Path) -> tuple[int, int, int, list[list[int]]]:
        data = path.read_bytes()
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("expected PNG asset")

        offset = 8
        width = height = bit_depth = color_type = None
        idat = b""
        while offset < len(data):
            length = int.from_bytes(data[offset : offset + 4], "big")
            chunk_type = data[offset + 4 : offset + 8]
            chunk = data[offset + 8 : offset + 8 + length]
            offset += length + 12
            if chunk_type == b"IHDR":
                width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk)
            elif chunk_type == b"IDAT":
                idat += chunk
            elif chunk_type == b"IEND":
                break

        if width is None or height is None or bit_depth != 8 or color_type not in {2, 6}:
            raise ValueError("expected 8-bit RGB/RGBA PNG asset")

        channels = 3 if color_type == 2 else 4
        raw = zlib.decompress(idat)
        stride = width * channels
        rows: list[list[int]] = []
        previous = [0] * stride
        position = 0
        for _ in range(height):
            filter_type = raw[position]
            position += 1
            scanline = list(raw[position : position + stride])
            position += stride
            decoded = [0] * stride
            for index, value in enumerate(scanline):
                left = decoded[index - channels] if index >= channels else 0
                above = previous[index]
                upper_left = previous[index - channels] if index >= channels else 0
                if filter_type == 0:
                    result = value
                elif filter_type == 1:
                    result = value + left
                elif filter_type == 2:
                    result = value + above
                elif filter_type == 3:
                    result = value + ((left + above) // 2)
                elif filter_type == 4:
                    result = value + paeth(left, above, upper_left)
                else:
                    raise ValueError(f"unsupported PNG filter type: {filter_type}")
                decoded[index] = result & 0xFF
            rows.append(decoded)
            previous = decoded
        return width, height, channels, rows

    def pixel(self, x: int, y: int) -> tuple[int, int, int]:
        index = x * self.channels
        return tuple(self.rows[y][index : index + 3])  # type: ignore[return-value]

    def region_pixels(self, region: list[int]) -> list[tuple[int, int, int]]:
        x, y, width, height = region
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > self.width or y + height > self.height:
            raise ValueError(f"region out of bounds: {region}")
        pixels: list[tuple[int, int, int]] = []
        for row in range(y, y + height):
            for column in range(x, x + width):
                pixels.append(self.pixel(column, row))
        return pixels


def paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def channel_luminance(value: int) -> float:
    channel = value / 255
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def luminance(color: tuple[int, int, int]) -> float:
    red, green, blue = color
    return 0.2126 * channel_luminance(red) + 0.7152 * channel_luminance(green) + 0.0722 * channel_luminance(blue)


def contrast_ratio(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    first_luminance = luminance(first)
    second_luminance = luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def dominant_color(pixels: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    counts: dict[tuple[int, int, int], int] = {}
    for pixel in pixels:
        counts[pixel] = counts.get(pixel, 0) + 1
    return max(counts.items(), key=lambda item: item[1])[0]


def contrast_sample(image: PngImage, sample: dict) -> tuple[float, tuple[int, int, int], tuple[int, int, int]]:
    region = sample.get("region")
    if not isinstance(region, list) or len(region) != 4:
        raise ValueError("contrast sample must include a four-number region")
    pixels = image.region_pixels([int(value) for value in region])
    kind = sample.get("kind")
    if kind == "dark_text_on_light":
        background_point = sample.get("background")
        if not isinstance(background_point, list) or len(background_point) != 2:
            raise ValueError("dark_text_on_light sample must include a background point")
        background = image.pixel(int(background_point[0]), int(background_point[1]))
        foreground = min(pixels, key=luminance)
    elif kind == "light_text_on_fill":
        background = dominant_color(pixels)
        foreground = max(pixels, key=luminance)
    else:
        raise ValueError(f"unknown contrast sample kind: {kind}")
    return contrast_ratio(foreground, background), foreground, background


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

        contrast_samples = asset.get("contrast_samples", [])
        if not contrast_samples:
            failures.append(f"{rel_path}: missing contrast sample definitions")
        else:
            try:
                image = PngImage(asset_path)
                for sample in contrast_samples:
                    name = sample.get("name", "unnamed sample")
                    minimum_ratio = float(sample.get("minimum_ratio", 4.5))
                    ratio, foreground, background = contrast_sample(image, sample)
                    if ratio < minimum_ratio:
                        failures.append(
                            f"{rel_path}: contrast sample {name!r} ratio {ratio:.2f}:1 below "
                            f"{minimum_ratio:.2f}:1; foreground={foreground}, background={background}"
                        )
            except Exception as exc:
                failures.append(f"{rel_path}: contrast sample check failed: {exc}")

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

    print("Visual asset manifest check passed: README screenshots match recorded assets, source hashes, and contrast samples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
