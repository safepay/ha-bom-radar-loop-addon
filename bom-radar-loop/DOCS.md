# Australian BoM Radar Loop

Turns Australian Bureau of Meteorology (BoM) radar data into two things for your Home Assistant dashboard:

- an **interactive, pannable radar map** (via the included Lovelace card), and
- a classic **animated GIF loop**.

It also saves the individual radar frames so you can feed them to LLM Vision for storm detection and analysis.

## Quick start

1. Install the add-on, then set at least:
   - `radar_product_id` — your radar (see [Finding your radar](#finding-your-radar-product-id) or [RADARS.md](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/bom-radar-loop/RADARS.md))
   - `timezone` — e.g. `Australia/Melbourne`
2. **Start** the add-on (enable "Start on boot"). It writes to `/config/www/bom_radar/`, which Home Assistant serves at `/local/bom_radar/`.
3. Add the interactive card (below) or the GIF to a dashboard.

The add-on only writes files on a successful run, so after the first start give it a minute (or restart it) before the card or GIF will have data.

## Interactive radar card (recommended)

The add-on ships the card and copies it into the output folder, so you only need to register it once.

1. **Settings → Dashboards → ⋮ → Resources → Add Resource**
   - URL: `/local/bom_radar/bom-radar-loader.js`
   - Type: **JavaScript Module**
2. Add the card to a dashboard (Add Card → Manual):

```yaml
type: custom:bom-radar-card
title: BoM Radar
```

Then hard-refresh the browser once.

> **Updates are cache-busted for you.** On storage-mode dashboards (resources managed in the UI, as above), the add-on registers and version-stamps the card resource itself through Home Assistant's API, using a digest of the card's contents (`bom-radar-card.js?v=<hash>`). When the add-on updates, the stamp changes and HA serves the fresh card after one browser refresh - no manual `?v=` bump. This is why the add-on requests Home Assistant API access.
>
> **Why the loader is still shipped.** If your resources are managed in YAML (read-only to the API), register `bom-radar-loader.js` instead of the card: it reads the add-on version and imports the matching card, so updates are still picked up automatically. Registering `/local/bom_radar/bom-radar-card.js` directly also works, but then you must add `?v=N` and bump it after each update to beat the browser cache.

**How it behaves:** zoom in and the card switches to the finer radar ranges around your home; zoom out for the wider picture. A home marker is placed from your Home Assistant location automatically. Play/pause and a timeline let you scrub through the frames. The crosshair button under the zoom control recentres the map to its starting view (your home/coverage centre and `default_zoom`).

**Card options** (all optional):

| Option | Default | Notes |
|--------|---------|-------|
| `height` | `420px` | Map height |
| `base_map` | `esri` | `esri`, `esri_topo`, `esri_gray`, `satellite`, `osm` |
| `default_zoom` | *(fit)* | A number opens at that zoom; omit to fit all coverage |
| `default_center` | `home` | `home` or `radars` |
| `show_home` | `true` | Show the home marker |
| `opacity` | `0.85` | Radar overlay opacity |
| `frame_delay` | `500` | Milliseconds per frame |

> The default base map is **Esri** because OpenStreetMap's tile servers block embedded use. `osm` is still selectable but may fail to load; the Carto styles need an API key.

> Which radars and how many zoom ranges are downloaded is set in the **add-on** configuration (`map_detail` and the radar options) — not on the card.

## Configuration

```yaml
radar_product_id: IDR022
timezone: Australia/Melbourne
update_interval: 600
output_path: www/bom_radar
map_detail: standard
background_type: bom
```

- **radar_product_id** — your BoM radar. The last digit is the range: `1`=512km, `2`=256km, `3`=128km, `4`=64km.
- **timezone** — used for the timestamps shown on the loop and card.
- **update_interval** — seconds between updates (minimum 60; 600 = 10 minutes).
- **output_path** — folder under `/config` for the output (default `www/bom_radar`).
- **map_detail** — how many ranges the interactive card can zoom through:
  - `minimal` — only your chosen range
  - `standard` — 512 + 256 + 128km (default)
  - `high` — also 64km, for close-in suburb detail (more data each update)
- **background_type** — background for the **GIF only** (`bom` or `openstreetmap`). It does not affect the interactive card, which uses its own live map.

### GIF settings

```yaml
gif_duration: 500            # milliseconds per frame
gif_last_frame_duration: 1000 # extra pause on the latest frame
```

### BoM layers (GIF, `background_type: bom` only)

Toggle extra layers drawn on the GIF: `layer_locations` (town names, on by default), `layer_catchments`, `layer_topography`, `layer_range` (range rings).

### Home marker (GIF)

```yaml
residential_location_enabled: true
residential_latitude: -37.8136
residential_longitude: 144.9631
```

This marker is drawn on the **GIF**. The interactive card uses your Home Assistant location instead, so you don't need to set these just for the card.

### Multiple radars (extended coverage)

```yaml
second_radar_enabled: true
second_radar_product_id: IDR703
third_radar_enabled: true
third_radar_product_id: IDR143
```

Rules (checked at startup; see the add-on log):

- **Coverage must overlap.** Secondary/tertiary radars must be neighbouring stations whose coverage overlaps the primary — not a far-away city. Melbourne + Perth is rejected.
- **Different stations.** Each must be a different physical station from the primary and from each other.
- **GIF overlay only — same range.** For the composited GIF, the secondary/tertiary product IDs must use the **same range** as the primary (same last digit). The interactive card has no such restriction and overlays each radar at its own range.

## Using the GIF in Home Assistant

The GIF updates in place, so a plain picture card would cache it. Use a **Local File camera + Picture Entity**:

1. **Settings → Devices & Services → Add Integration → Local File**, path `/config/www/bom_radar/radar_animated.gif`, name it e.g. "BoM Radar Loop".
2. Add a **Picture Entity** card:

```yaml
type: picture-entity
entity: camera.bom_radar_loop
camera_entity: camera.bom_radar_loop
camera_view: live
show_name: true
show_state: false
```

## Output files

In `/config/www/bom_radar/` (served at `/local/bom_radar/`):

- `radar_animated.gif` — the animated loop
- `image_1.png` … `image_5.png` — individual frames (oldest → newest), for LLM Vision
- `frames/` + `radar_manifest.json` — data for the interactive card
- `bom-radar-card.js` — the Lovelace card; `bom-radar-loader.js` — the resource you register (auto cache-busts the card)
- `radar_last_update.txt` — UTC + local timestamp
- `radar_status.json` — per-radar availability (see below)

### Status file (`radar_status.json`)

Reports whether each radar is online, for monitoring and automations. Key fields: `overall_status` (`online` / `partial` / `offline`), `*_online`, `*_timestamps`, `latest_timestamp`, `last_updated`. Example REST sensor:

```yaml
sensor:
  - platform: rest
    resource: http://homeassistant.local:8123/local/bom_radar/radar_status.json
    name: Radar Status
    value_template: "{{ value_json.overall_status }}"
    scan_interval: 600
```

## Finding your radar product ID

| City | 128km | 256km |
|------|-------|-------|
| Sydney | IDR713 | IDR712 |
| Melbourne | IDR023 | IDR022 |
| Brisbane | IDR663 | IDR662 |
| Perth | IDR703 | IDR702 |
| Adelaide | IDR643 | IDR642 |
| Canberra | IDR403 | IDR402 |
| Hobart | IDR763 | IDR762 |
| Darwin | IDR633 | IDR632 |

Full list by state: [RADARS.md](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/bom-radar-loop/RADARS.md).

## Troubleshooting

**Card: "Custom element doesn't exist: bom-radar-card"** — the resource isn't registered, or the browser cached an old page. Re-check the resource URL and type (JavaScript Module), then hard-refresh. After an add-on update the card is normally re-stamped automatically (storage-mode dashboards); if you manage resources in YAML, use the loader or append/bump a `?v=` on the resource URL to bust the cache.

**Card: "Could not load radar manifest"** — the add-on hasn't written files yet (restart it and wait a cycle), or your `output_path` isn't the default (then set `manifest: /local/<your_path>/radar_manifest.json` on the card).

**Card: base map is blank / "Access blocked"** — you're using `base_map: osm`, which OpenStreetMap blocks for embedding. Remove the option (defaults to Esri) or pick an Esri style.

**No images appearing** — check the add-on log; verify `/config/www/bom_radar/` exists and that `/local/bom_radar/…` is reachable. The BoM FTP server is occasionally unavailable.

**Home marker missing on the GIF** — the GIF marker needs `residential_location_enabled: true` and coordinates inside the radar's coverage. (The card uses your HA location instead.)

## Support

Issues and requests: [GitHub Issues](https://github.com/safepay/ha-bom-radar-loop-addon/issues)

Radar data provided by the Australian Bureau of Meteorology (BoM).
