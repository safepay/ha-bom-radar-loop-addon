# Changelog

All notable changes to this project will be documented in this file. Older releases are in [CHANGELOG-ARCHIVE.md](CHANGELOG-ARCHIVE.md).

## [1.1.5] - 2026-10-12

### Added

- **Automatic card cache-busting on update (storage-mode dashboards):** the add-on now registers and version-stamps the `bom-radar-card` Lovelace resource for you through Home Assistant's API, using a digest of the card's contents (`bom-radar-card.js?v=<hash>`). When the add-on updates, the card's bytes change, so the stamp changes and Home Assistant serves the fresh card after a single browser refresh - the same approach HACS uses, done from the add-on. If you already registered `bom-radar-loader.js`, it is left in place as the cache-busting path. YAML-managed resources are read-only, so those setups keep using the bundled loader (or a manual `?v=`). This needs the new `homeassistant_api` permission, which is why the add-on now requests access to the Home Assistant API.

### Fixed

- **Radar vanishing, reappearing or staying blocky as you zoom**: the card chose each radar range by whether its square merely *touched* the view, then drew only that one level. If your home sat off-centre from the radar, a fine range could clip the view and paint only a sliver (the rest of the screen went blank), and with two overlapping radars one could blank the other entirely at certain zooms - so radar disappeared at one zoom and came back at another, or stayed low-resolution however far you zoomed. The card now selects by **coverage**: it shows the single finest range whose square fully covers the viewport (climbing 512 → 256 → 128 → 64 km as you zoom in), and only falls back to showing every radar's widest range when no single range can cover the view (the zoomed-right-out national view). One radar, one range, one capture time on screen at a time - no mixed resolutions, no blank edges, no blink on/off between zoom levels.

## [1.1.4] - 2026-10-12

### Fixed

- **"Image not available" boxes on the radar**: a frame that failed to load showed the browser's broken-image icon. The card now shows a transparent image instead (nothing), so a missing frame is never visible.
- **Frames could briefly go missing after an update**: each run deleted every frame file and rewrote them, so a browser still showing the previous manifest's frames would 404 them. The add-on now keeps the last few generations of frames (retention window) instead of wiping them each run.

### Changed

- **Card tidy-up**: removed the broken Carto base maps (`voyager`/`light`/`dark`, which needed an API key) and deduplicated the map CSS. Base map options are now `esri`, `esri_topo`, `esri_gray`, `satellite`, and `osm` (YAML only).

## [1.1.3] - 2026-10-12

### Added

- **Auto cache-busting loader**: the add-on now ships `bom-radar-loader.js`. Register it as your Lovelace resource (instead of the card directly) and you never have to add/bump a `?v=` by hand again - the loader reads the add-on version from the manifest and loads the matching card, so updates are picked up automatically (the HACS "stamp" trick, without HACS).

### Fixed

- **Mixed radar resolutions when zoomed in with multiple radars**: overlapping radars drew one radar's fine detail and another's coarse blocks in the same place. The card now shows a single resolution at a time - it finds the finest range in view and hides any coarser radar - so zooming into your home area shows just that radar's detail, while a zoomed-out view still shows all radars for coverage.
- **OpenStreetMap base map removed from the editor**: OSM blocks embedded use ("Access blocked"), so it is no longer offered in the visual editor (the Esri options and satellite work; OSM remains available via YAML for networks that allow it).

