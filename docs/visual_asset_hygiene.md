# Visual Asset Hygiene

Desktop and mobile demo screenshots are part of the public product surface. They should not silently drift away from the current frontend.

Run:

```bash
python -B scripts/dev.py visual-assets
```

The check verifies:

- required desktop and mobile screenshot assets exist
- screenshot hashes match `docs/visual_assets_manifest.json`
- screenshot dimensions match the recorded capture viewport
- frontend source files match the hashes recorded when the screenshots were refreshed
- recorded screenshot contrast samples still clear a deterministic minimum ratio

If a frontend HTML, CSS, or JavaScript file changes, refresh the affected screenshots and update the manifest in the same change. The current desktop screenshots were captured at 1400x900, and the current mobile / narrow viewport screenshots were captured at 500x844, after the local services reported healthy.

To refresh screenshots and rewrite the manifest from live local apps:

```bash
python -B scripts/dev.py refresh-visual-assets
python -B scripts/dev.py visual-asset-diff
python -B scripts/dev.py visual-assets
```

The refresh command starts the screenshot source services on isolated local ports, waits for `/api/health`, captures desktop and mobile / narrow viewport browser screenshots, and records screenshot hashes, frontend source hashes, dimensions, and stable contrast sample regions. It uses Chrome, Chromium, or Edge through `FDE_BROWSER_BIN` or common install paths. Keep it as a maintainer command rather than a required CI step because browser availability is machine-specific; `visual-assets` remains the deterministic release gate.

The diff summary command compares `docs/visual_assets_manifest.json` with the manifest at `HEAD` by default. It prints only changed paths, asset kinds, dimensions, hash prefixes, source-hash change counts, and contrast ratios, so screenshot refreshes can be reviewed without dumping binary image contents into logs. Use `--base <ref>` on `scripts/summarize_visual_asset_diff.py` when reviewing against another Git ref.

The contrast check is a screenshot release guard, not a complete accessibility audit. It samples stable regions such as the page title, primary action, and quick-action text, then calculates a WCAG-style relative-luminance contrast ratio from decoded PNG pixels. Failures report the asset, sample name, ratio, and sampled foreground/background colors so a maintainer can fix the visual regression or move the sample region.

When using Chrome or another browser to refresh screenshots, use a temporary browser profile outside the public source tree or remove the profile immediately after capture. Browser profile logs can include local paths, and `python -B scripts/dev.py safety` is expected to catch that.

## Troubleshooting Refresh Failures

Browser not found:

- Run `python -B scripts/refresh_visual_assets.py --check-browser` to test browser discovery without touching screenshots.
- Install Chrome, Chromium, or Edge, or point `FDE_BROWSER_BIN` at the browser executable for the current shell only.
- On PowerShell, use `$env:FDE_BROWSER_BIN="<browser-executable-path>"` before the refresh command.
- Do not commit local browser paths, browser profiles, or command output that includes a user directory.

Service did not become healthy:

- Run `python -B scripts/dev.py health` first if the default demo ports should already be available.
- If another local process is using a preferred port, rerun `python -B scripts/dev.py refresh-visual-assets`; the script falls back to an available local port.
- Treat repeated health failures as an app/runtime issue, then run `python -B scripts/dev.py quality` after the fix.

Screenshot size mismatch:

- Desktop screenshots are expected to be 1400x900.
- Mobile / narrow viewport screenshots are expected to be 500x844.
- A different size usually means the browser ignored `--window-size`, the wrong executable was selected, or the capture was interrupted.
- Re-run with a clean temporary browser profile and confirm `python -B scripts/dev.py visual-assets` before committing.

Tiny screenshot file:

- A tiny PNG usually means the page was blank, the service was not ready, or the browser failed before rendering the app.
- Confirm `/api/health` is healthy, then refresh again.
- Open the generated PNG before committing when the byte-size guard fires during development.

Hash or source-file mismatch:

- If an asset hash changed, commit the refreshed screenshot and manifest together.
- If a frontend HTML, CSS, or JavaScript source hash changed, refresh the affected screenshots instead of editing the manifest by hand.
- Use `python -B scripts/dev.py visual-asset-diff` to explain the changed paths, dimensions, hash prefixes, source-hash counts, and contrast ratios before review.

Contrast sample failure:

- First inspect the screenshot to confirm whether the UI actually lost readable text contrast.
- If the UI regressed, fix the CSS or component state and refresh again.
- If the UI is correct but the sampled region moved, update the stable sample coordinates in `scripts/refresh_visual_assets.py`, refresh assets, and run both `visual-asset-diff` and `visual-assets`.

Safety scan failure after capture:

- Remove browser profiles, logs, local paths, and runtime state from the working tree.
- Keep only intentional screenshot assets and `docs/visual_assets_manifest.json`.
- Re-run `python -B scripts/dev.py safety` before committing.

## Technical Review Framing

The repo treats screenshots like release artifacts, not decorative leftovers. If the UI changes without refreshed desktop and mobile screenshots, or a refreshed screenshot loses obvious text/button contrast in tracked sample regions, the visual asset gate fails. The diff summary gives reviewers a compact explanation of what changed before they open the images.
