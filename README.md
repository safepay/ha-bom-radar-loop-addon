# Home Assistant Australian BoM Radar Loop

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Addon-blue.svg)](https://www.home-assistant.io/)

A Home Assistant add-on that turns Australian Bureau of Meteorology radar into an **interactive, pannable map** (via an included Lovelace card), a classic **animated GIF loop**, and individual frames for LLM Vision analysis.

## Features

- 🗺️ **Interactive radar card** — a real pannable/zoomable Leaflet map with a play/pause timeline; zoom in for finer detail around home
- 🎬 **Animated GIF loop** — for a simple dashboard picture
- 🌏 **Multiple radars** — overlay up to 3 neighbouring radars for extended coverage
- 🏠 **Home marker** — from your Home Assistant location, automatically
- 🤖 **LLM Vision ready** — individual PNG frames for AI storm detection
- ⚡ **Auto-updates** — fetches the latest radar on your chosen interval

## Install

1. **Settings → Add-ons → Add-on Store → ⋮ → Repositories**, paste:
   `https://github.com/safepay/ha-bom-radar-loop-addon`
2. Install **Australian BoM Radar Loop**.
3. Set `radar_product_id` (see [Radar quick reference](#radar-quick-reference) / [RADARS.md](bom-radar-loop/RADARS.md)) and `timezone`, then **Start** (enable "Start on boot").

## Add the interactive card

The add-on copies the card into `/config/www/bom_radar/`. Register it once:

- **Settings → Dashboards → ⋮ → Resources → Add Resource**
  - URL `/local/bom_radar/bom-radar-card.js`, type **JavaScript Module**

Then add it to a dashboard:

```yaml
type: custom:bom-radar-card
title: BoM Radar
```

Zoom in and the card switches to the finer radar ranges around your home; zoom out for the wider picture. See [DOCS.md](bom-radar-loop/DOCS.md#interactive-radar-card-recommended) for all card options.

## Add the GIF (optional)

The GIF updates in place, so use a **Local File camera + Picture Entity** (a plain picture card would cache it). Full steps in [DOCS.md](bom-radar-loop/DOCS.md#using-the-gif-in-home-assistant).

## Radar quick reference

| City | 128km | 256km |
|------|-------|-------|
| Sydney | IDR713 | IDR712 |
| Melbourne | IDR023 | IDR022 |
| Brisbane | IDR663 | IDR662 |
| Perth | IDR703 | IDR702 |
| Adelaide | IDR643 | IDR642 |
| Canberra | IDR403 | IDR402 |

Full list by state: [RADARS.md](bom-radar-loop/RADARS.md).

## Documentation

- **Full documentation** (config, card options, usage, troubleshooting): [DOCS.md](bom-radar-loop/DOCS.md)
- **All radars by state**: [RADARS.md](bom-radar-loop/RADARS.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## Support

Issues and requests: <https://github.com/safepay/ha-bom-radar-loop-addon/issues>

Radar data provided by the Australian Bureau of Meteorology. MIT licensed.
