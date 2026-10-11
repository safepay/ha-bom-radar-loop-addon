# Home Assistant Australian BoM Radar Loop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Addon-blue.svg)](https://www.home-assistant.io/)

Animated radar loops and individual radar frames from Australian Bureau of Meteorology data for Home Assistant dashboards and AI-powered weather analysis.

## Features

- 🤖 **LLM Vision Ready**: Individual PNG frames for AI-powered storm detection and analysis
- 🗺️ **Choose Background**: BoM official or OpenStreetMap (higher resolution with tile caching)
- 🎬 **Animated Loops**: Smooth GIF animations for dashboards
- 🌏 **Multiple Radars**: Overlay up to 3 radars for extended coverage
- 🏠 **Location Marker**: Show your home on the radar
- ⚡ **Auto-Updates**: Continuously fetches latest radar images

## Installation

1. **Add Repository** to Home Assistant:
   - Settings → Add-ons → Add-on Store → ⋮ (menu) → Repositories
   - Paste: `https://github.com/safepay/ha-bom-radar-loop-addon`

2. **Install** "Australian BoM Radar Loop" from the addon store

3. **Configure** in the Configuration tab:
   - Set your `radar_product_id` (see [Quick Reference](#quick-reference) or [RADARS.md](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/bom-radar-loop/RADARS.md))
   - Set your `timezone` (e.g., `Australia/Melbourne`)

4. **Start** the addon (enable "Start on boot" recommended)

## Using in Home Assistant

**⚠️ Important**: You MUST use Local File camera integration + Picture Entity card to avoid caching issues.

### Setup (Required)

1. **Add Local File Integration**:
   - Settings → Devices & Services → Add Integration → Local File
   - File path: `/config/www/bom_radar/radar_animated.gif`
   - Name: "BoM Radar Loop"

2. **Add Picture Entity Card** to dashboard:

```yaml
type: picture-entity
entity: camera.bom_radar_loop
camera_entity: camera.bom_radar_loop
camera_view: live
show_name: true
show_state: false
```

   **Note**: Set both `entity` and `camera_entity` to `camera.bom_radar_loop`

**Why?** Simple picture cards cache images and won't update. Local File camera + Picture Entity ensures proper refreshing.

### Interactive Radar Map (recommended)

As well as the GIF, the addon writes transparent, georeferenced radar frames plus a `radar_manifest.json`, and ships a custom Lovelace card (`bom-radar-card.js`) that renders them on a **real pannable/zoomable map** with a play/pause/scrub timeline - instead of a fixed loop you can move around the map covered by your chosen radars.

1. **Register the card as a resource** (the addon has already copied it into `/config/www/bom_radar/`):
   - Settings → Dashboards → ⋮ → Resources → Add Resource
   - URL: `/local/bom_radar/bom-radar-card.js`
   - Type: **JavaScript Module**

2. **Add the card** to a dashboard:

```yaml
type: custom:bom-radar-card
title: BoM Radar
# All options below are optional:
height: "420px"
default_zoom: 8          # omit to fit all radar coverage; set to open zoomed on home
default_center: home     # "home" (uses your HA location) or "radars"
show_home: true          # home marker, from your Home Assistant location
base_map: esri           # esri | esri_topo | esri_gray | satellite | osm  (osm may be blocked for embedding)
```

> Which radars and how many zoom ranges are downloaded is set in the **addon** configuration (`map_detail` and the radar options), not on the card.

How it behaves:

- **Zoom in** and the card automatically switches to the finer radar ranges around your home; **zoom out** for the wider-range picture.
- **Rural homes** outside the small radii fall back to the widest range that still reaches them.
- The home marker uses your **Home Assistant** location automatically (no need to set coordinates just for the map).

### LLM Vision Analysis

Individual radar frames are perfect for AI analysis:

```yaml
type: picture
image: /local/bom_radar/image_5.png  # Most recent frame
```

Five frames available: `image_1.png` (oldest) to `image_5.png` (newest). Use with Claude Vision, GPT-4 Vision, or other LLM tools for:
- Storm detection and tracking
- Rainfall intensity analysis
- Weather pattern recognition
- Automated weather alerts

## Configuration

### Basic

```yaml
radar_product_id: IDR022      # Your radar (see Quick Reference below)
timezone: Australia/Melbourne
update_interval: 600          # Seconds (10 minutes)
background_type: bom          # "bom" or "openstreetmap" (GIF only)
map_detail: standard          # Interactive card: minimal | standard | high
```

- `map_detail`: how many ranges the interactive card can zoom through - `standard` = 512/256/128km, `high` also fetches 64km (more data each update), `minimal` keeps a single range.

### Background Options

- **bom** (default): Official BoM background with customizable layers
- **openstreetmap**: Higher resolution street maps with automatic tile caching

BoM layers (only with BoM background): locations, catchments, topography, range

### Optional Features

**Multiple Radars** (must be same range as primary, different station):

```yaml
second_radar_enabled: true
second_radar_product_id: IDR953
```

**Home Marker** (shows on GIF only):
```yaml
residential_location_enabled: true
residential_latitude: -37.8136
residential_longitude: 144.9631
```

## Quick Reference

| City | 128km | 256km |
|------|-------|-------|
| Sydney | IDR713 | IDR712 |
| Melbourne | IDR023 | IDR022 |
| Brisbane | IDR663 | IDR662 |
| Perth | IDR703 | IDR702 |
| Adelaide | IDR643 | IDR642 |
| Canberra | IDR403 | IDR402 |

**Full list**: [RADARS.md](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/RADARS.md)

## Troubleshooting

**Images not updating?**
- Use Local File integration + Picture Entity card (not simple picture card)
- Check addon is running (green status)
- View addon logs for errors

**OpenStreetMap not working?**
- First run downloads tiles (30-60 seconds)
- Check logs for tile download errors
- Addon falls back to BoM if tiles fail

**No images appearing?**
- Check addon logs
- Verify `/config/www/bom_radar/` exists
- BoM FTP may be temporarily unavailable

## Output Files

Located in `/config/www/bom_radar/`:
- `radar_animated.gif` - Animated loop (5 frames) for dashboards
- `image_1.png` to `image_5.png` - Individual frames for LLM Vision analysis
- `radar_last_update.txt` - Timestamp information
- `radar_status.json` - Detailed radar status and availability (new in v1.0.8)

Access via `/local/bom_radar/filename` in dashboards and automations.

The status file includes real-time information about radar availability, offline detection, and frame generation - perfect for monitoring and automation. See [DOCS.md](bom-radar-loop/DOCS.md#radar-status-file) for details.

## Documentation

- **Full Documentation**: [DOCS.md](DOCS.md)
- **All Radars by State**: [RADARS.md](RADARS.md)
- **Docker Installation**: [DOCKER.md](DOCKER.md)

## Support

- **Issues**: https://github.com/safepay/ha-bom-radar-loop-addon/issues

## Credits

Radar data: Australian Bureau of Meteorology

## License

MIT License
