# Visual Asset Hygiene

README screenshots are part of the public product surface. They should not silently drift away from the current frontend.

Run:

```bash
python -B scripts/dev.py visual-assets
```

The check verifies:

- required README screenshot assets exist
- screenshot hashes match `docs/visual_assets_manifest.json`
- screenshot dimensions match the recorded capture viewport
- frontend source files match the hashes recorded when the screenshots were refreshed
- recorded screenshot contrast samples still clear a deterministic minimum ratio

If a frontend HTML, CSS, or JavaScript file changes, refresh the affected screenshot and update the manifest in the same change. The current screenshots were captured at 1400x900 after the local services reported healthy.

To refresh screenshots and rewrite the manifest from live local apps:

```bash
python -B scripts/dev.py refresh-visual-assets
python -B scripts/dev.py visual-assets
```

The refresh command starts the screenshot source services on isolated local ports, waits for `/api/health`, captures 1400x900 browser screenshots, and records screenshot hashes, frontend source hashes, and stable contrast sample regions. It uses Chrome, Chromium, or Edge through `FDE_BROWSER_BIN` or common install paths. Keep it as a maintainer command rather than a required CI step because browser availability is machine-specific; `visual-assets` remains the deterministic release gate.

The contrast check is a screenshot release guard, not a complete accessibility audit. It samples stable regions such as the page title, primary action, and quick-action text, then calculates a WCAG-style relative-luminance contrast ratio from decoded PNG pixels. Failures report the asset, sample name, ratio, and sampled foreground/background colors so a maintainer can fix the visual regression or move the sample region.

When using Chrome or another browser to refresh screenshots, use a temporary browser profile outside the public source tree or remove the profile immediately after capture. Browser profile logs can include local paths, and `python -B scripts/dev.py safety` is expected to catch that.

## Technical Review Framing

The repo treats screenshots like release artifacts, not decorative leftovers. If the UI changes without refreshed screenshots, or a refreshed screenshot loses obvious text/button contrast in tracked sample regions, the visual asset gate fails.
