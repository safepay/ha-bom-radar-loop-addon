# Changelog

All notable changes to this project will be documented in this file. Older releases are in [CHANGELOG-ARCHIVE.md](CHANGELOG-ARCHIVE.md).

## [Unreleased]

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

## [1.1.2] - 2026-10-12

### Added

- **Visual card editor**: the card now ships a config editor (title, base map, height, default zoom, opacity, autoplay, home marker, legend), so it is no longer YAML-only and the "Visual editor not supported" notice is gone.
- **Resizable in both dimensions**: the card fills its grid cell and reports grid options, so in a sections dashboard you can drag to resize its height and width; the `height` option remains the default/masonry height.

### Changed

- **Animation starts automatically** once the map is sized and has frames (no need to press play).
- **Title is optional**: removing `title:` from the card config now removes the header (it is no longer defaulted to "BoM Radar").
- **Legend tidied up**: the rainfall colour bar is now rounded with "Light"/"Heavy" captions and aligned with the controls.

### Fixed

- **Radar animation flickered and showed too few distinct frames**: ranges are captured at different minute offsets, but the add-on forced every range onto one shared 5-timestamp window (dropping most of each range's frames) and the card animated over the merged union (so frames blanked on/off and repeated). Now each range keeps its own most-recent 5 frames, and the card animates over the active range's own frames - five distinct images, no flicker.
- **Radar map tiles scattered / drifted when panning (and showed as a single tile)**: Home Assistant renders cards inside shadow DOM, so Leaflet's stylesheet (loaded into `document.head`) never reached the map - the tiles got no `position: absolute` or pane z-indexes and scattered when you panned. The card now inlines the critical Leaflet layout CSS in its own `<style>` block (scoped to the card), so it renders correctly regardless of shadow-DOM boundaries. Verified by rendering the card inside a shadow root.
- **"No changelog found" on add-on update**: Home Assistant reads the changelog from the add-on's own folder, but it lived at the repository root. Moved `CHANGELOG.md` into `bom-radar-loop/` so the Supervisor shows it in the update dialog (takes effect from the next release onward).
- **Map rendered as a single tile in the wrong place**: Home Assistant lays cards out after creating them (worst of all in the card-editor preview), so Leaflet initialised in a 0x0 container - loading one tile and fitting to nothing, leaving the view on the fallback (central Australia). The card now re-runs `invalidateSize()` and defers the fit-to-coverage until the container actually has a size (driven by a resize observer), so it fills with tiles and centres on your radar.
- **Duplicate card in the picker**: if Home Assistant evaluated `bom-radar-card.js` more than once in a session (e.g. after removing and re-adding the resource, or via a cache-busted URL), the card registered itself twice and appeared twice in the card list, with a possible "already declared/defined" error. The card now wraps itself in a run-once guard and only registers once.

### Changed

- **Dropped deprecated 32-bit architectures** (`armhf`, `armv7`, `i386`) from `config.json` and `build.json`. Home Assistant removed support for them in 2025.12, and the add-on linter flags them. Only `aarch64` and `amd64` remain.
- **Rewrote and simplified the documentation**: `DOCS.md` now leads with the interactive card, covers `map_detail` and the card options, and trims the outdated/verbose sections; the `README.md` is a concise landing page that points to `DOCS.md` (and its broken `DOCS.md`/`RADARS.md`/`DOCKER.md` links are fixed).

