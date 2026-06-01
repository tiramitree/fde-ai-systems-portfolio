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

If a frontend HTML, CSS, or JavaScript file changes, refresh the screenshot and update the manifest in the same change. The current screenshots were captured at 1400x900 after both local services reported healthy.

When using Chrome or another browser to refresh screenshots, use a temporary browser profile outside the public source tree or remove the profile immediately after capture. Browser profile logs can include local paths, and `python -B scripts/dev.py safety` is expected to catch that.

## Interview Framing

The repo treats screenshots like release artifacts, not decorative leftovers. If the UI changes without refreshed screenshots, the visual asset gate fails.
