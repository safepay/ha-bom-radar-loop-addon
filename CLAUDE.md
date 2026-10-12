# CLAUDE.md

Guidance for AI agents (and humans) working in this repo. Keep it short and
repo-specific: record the non-obvious, not what the code already shows.

## What this is

A Home Assistant **add-on** that turns Australian BoM radar into an animated GIF
and transparent per-frame PNGs, **plus a bundled Lovelace card** that renders
those frames on a live Leaflet map. Both live in `bom-radar-loop/`. There is
**no build step** for either — the Python runs as-is in the add-on container,
and the card JS is shipped and loaded verbatim (no bundler, no transpile).

- Add-on (Python): `bom_radar_downloader.py` (`MapTileProvider`, `Config`,
  `RadarProcessor`), `radar_metadata.py` (radar coordinate table).
- Card (vanilla JS): `bom-radar-card.js` (the card) and `bom-radar-loader.js`
  (the resource you register; it cache-busts the card by add-on version).
- The add-on writes to `/config/www/bom_radar/`, served by HA at
  `/local/bom_radar/`: the GIF, `image_1..5.png`, `frames/`,
  `radar_manifest.json` (card data), `radar_status.json` (monitoring).

## Workflow rules (read first)

- **Use a pull request — always the default.** Branch → PR → merge to `main`;
  do not push directly to `main`. `main` is what the HA add-on store serves to
  every user, so an un-reviewed push ships straight to production. A direct push
  happens only when the maintainer explicitly okays that one change.
- **Never bump the version in a PR.** Several PRs merge to `main` with the
  version untouched, then a release is cut from the **Actions → Release**
  workflow (`workflow_dispatch`, choose patch/minor/major). See
  `.github/RELEASING.md`.
- **Two version sources, kept in sync by the release workflow only:** `version`
  in `bom-radar-loop/config.json` and `VERSION` in `bom_radar_downloader.py`.
  Don't edit either by hand.
- **Changelog:** add entries under `## [Unreleased]` in
  `bom-radar-loop/CHANGELOG.md` (it lives inside the add-on folder on purpose,
  so HA shows it in the update dialog). The release workflow stamps the heading.

## Keep these in sync when you change one

- **Add/rename/remove a config option** → update `config.json` `options` **and**
  its `schema`, `translations/en.yaml` (label + description), and `DOCS.md`.
- **Change supported architectures** → `config.json` `arch` **and**
  `build.json` `build_from`. Only `aarch64` and `amd64` are supported (32-bit
  `armhf`/`armv7`/`i386` were dropped — the linter flags them).
- **Change radar/output behaviour** → check the matching card logic in
  `bom-radar-card.js` reads the manifest the same way.

## Card gotchas (hard-won; see CHANGELOG)

- **HA renders cards in shadow DOM**, so a stylesheet loaded into
  `document.head` never reaches the map. The critical Leaflet layout CSS is
  inlined in the card's own `<style>` — keep it that way.
- **Register once.** The whole file is wrapped in a run-once IIFE guard
  (`window.__bomRadarCardInit`); HA can evaluate the resource more than once.
- **0×0 container.** HA lays cards out after creating them, so Leaflet can init
  into a zero-size box. The card defers fit-to-coverage behind a resize observer
  and re-runs `invalidateSize()` — don't remove that.
- **Base maps:** Esri (keyless, embeddable) is the default. OSM is blocked for
  embedded use ("Access blocked") and is YAML-only, not in the visual editor.
- **Loader vs card:** users register `bom-radar-loader.js`, which imports
  `bom-radar-card.js?v=<version>`. The loader is meant to never change.

## Add-on / radar facts

- BoM product IDs are `IDRxyz`; the **last digit is the range**: `1`=512km,
  `2`=256km, `3`=128km, `4`=64km. The card treats the ranges as a
  home-focused resolution pyramid and switches between them as you zoom.
- The add-on **writes output only on a successful run**, so the card/GIF have no
  data until the first good cycle completes.
- `Dockerfile` installs Python deps with `--break-system-packages` (required on
  Alpine + Python 3.12). Deps are pinned loosely in `requirements.txt`.

## Validating changes

- CI runs `frenck/action-addon-linter` on every push/PR (`.github/workflows/
  lint.yaml`) against `bom-radar-loop/`. Keep `config.json` lint-clean (e.g. no
  default-valued keys the linter rejects).
- There is **no unit-test suite**. The real test for card changes is rendering
  the card in a running Home Assistant and checking the browser console.
- Commit and PR conventions (attribution, text wrapping) follow the repo
  owner's global rules — this file doesn't restate them.
