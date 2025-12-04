# Home Assistant Australian BoM Radar Loop Addon

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Addon-blue.svg)](https://www.home-assistant.io/)

Home Assistant addon for Australian Bureau of Meteorology (BoM) Radar Loop with individual radar images for LLM Vision analysis.

This addon creates animated radar loops and individual frame images from Australian BoM radar data, perfect for:
- **Dashboard Display**: Beautiful animated radar loops for your Home Assistant dashboards
- **LLM Vision Analysis**: Separate radar images for AI-powered storm detection and analysis
- **Automation**: Use radar data in your Home Assistant automations with timestamped images

## Features

✨ **Easy Installation**: Install directly from the Home Assistant addon store
🌏 **Multiple Radars**: Support for overlaying up to 3 radars for extended coverage
🏠 **Location Marker**: Show your home location on the radar loop
⚡ **Automated Updates**: Continuously downloads and processes latest radar images
🎨 **Customizable**: Choose radar layers, update intervals, and GIF settings
🕐 **Timezone Support**: Timestamps in both UTC and your local timezone

## Installation

### Home Assistant Addon (Recommended)

1. **Add the Repository**:
   - Navigate to **Settings** → **Add-ons** → **Add-on Store** in Home Assistant
   - Click the three dots (⋮) in the top right corner
   - Select **Repositories**
   - Add this repository URL: `https://github.com/safepay/ha-bom-radar-loop-addon`
   - Click **Add** then **Close**

2. **Install the Addon**:
   - Refresh the Add-on Store page
   - Find "Australian BoM Radar Loop" in the list
   - Click on it and press **Install**

3. **Configure the Addon**:
   - Go to the **Configuration** tab
   - Set your `radar_product_id` (find yours at http://www.bom.gov.au/australia/radar/)
   - Set your `timezone` (e.g., `Australia/Melbourne`)
   - Adjust other settings as needed (see Configuration section below)

4. **Start the Addon**:
   - Go to the **Info** tab
   - Click **Start**
   - Optionally enable **Start on boot** and **Watchdog**

5. **Access Your Radar Images**:
   - Images will be available at `/config/www/bom_radar/`
   - Access in dashboards via `/local/bom_radar/radar_animated.gif`

### Standalone Docker Installation (Advanced)

If you prefer to run this outside of Home Assistant as a standalone Docker container, see the [Docker Installation Guide](DOCKER.md).

## Configuration

The addon can be configured through the Home Assistant UI:

### Basic Settings

```yaml
radar_product_id: IDR022
timezone: Australia/Melbourne
update_interval: 600
output_path: www/bom_radar
```

- **radar_product_id**: Your BoM radar ID (find at http://www.bom.gov.au/australia/radar/)
- **timezone**: Your local timezone (e.g., `Australia/Melbourne`, `Australia/Sydney`)
- **update_interval**: Seconds between updates (600 = 10 minutes, minimum 60)
- **output_path**: Where to save images relative to `/config` (default: `www/bom_radar`)

### Radar Layers

Choose which map layers to display:

```yaml
layers:
  - background
  - locations
```

Available options: `background`, `locations`, `catchments`, `topography`

### Multiple Radar Support

Overlay up to 3 radars for extended coverage:

```yaml
second_radar_enabled: true
second_radar_product_id: IDR022
third_radar_enabled: false
third_radar_product_id: IDR023
```

Radars are automatically positioned based on their geographic locations.

### Residential Location Marker

Add a house icon showing your location:

```yaml
residential_location_enabled: true
residential_latitude: -37.8136
residential_longitude: 144.9631
```

Note: The marker only appears on the animated GIF, not static images.

### GIF Settings

```yaml
gif_duration: 500
gif_last_frame_duration: 1000
```

- **gif_duration**: Milliseconds per frame (default: 500)
- **gif_last_frame_duration**: Pause on last frame in milliseconds (default: 1000)

## Using Radar Images in Home Assistant

### Display Animated Radar on Dashboard

Add a picture entity card to your dashboard:

```yaml
type: picture-entity
entity: camera.your_camera  # Optional
image: /local/bom_radar/radar_animated.gif
show_state: false
show_name: false
```

Or use a simple picture card:

```yaml
type: picture
image: /local/bom_radar/radar_animated.gif
```

### Access Individual Frames

Individual radar frames are saved as `image_1.png` through `image_5.png`. These can be used with LLM Vision for AI-powered storm analysis:

```yaml
type: picture
image: /local/bom_radar/image_5.png  # Most recent frame
```

### Timestamp Information

The addon creates `radar_last_update.txt` with UTC and local timestamps. You can use this in automations or AI prompts.

## Finding Your Radar Product ID

**📍 See the complete [Radar Reference Guide (RADARS.md)](RADARS.md)** - All Australian radars organized by state with product IDs and coordinates.

### Quick Reference - Major Cities

| City | Product ID | Range | Alternative |
|------|-----------|-------|-------------|
| **Sydney** | IDR713 | 128km | IDR712 (256km) |
| **Melbourne** | IDR023 | 128km | IDR022 (256km) |
| **Brisbane** | IDR663 | 128km | IDR662 (256km) |
| **Perth** | IDR703 | 128km | IDR702 (256km) |
| **Adelaide** | IDR643 | 128km | IDR642 (256km) |
| **Canberra** | IDR403 | 128km | IDR402 (256km) |

**Tip**: The 128km range provides the best balance of coverage and detail for most users.

## Troubleshooting

### Addon won't start
- Check the addon logs for errors
- Verify your `radar_product_id` is valid
- Ensure your timezone string is correct

### No images appearing
- Check that the addon is running (green status)
- View the addon logs for FTP connection errors
- Ensure `/config/www/bom_radar/` directory exists
- The BoM FTP server may occasionally be unavailable

### Images not updating
- Check your `update_interval` setting
- Review addon logs for errors
- Verify you have internet connectivity
- The BoM FTP updates every 6-10 minutes

### House marker not visible
- Marker only appears on `radar_animated.gif`, not static images
- Verify `residential_location_enabled: true`
- Check coordinates are within radar coverage area
- Ensure coordinates are correct (negative for southern/western hemispheres)

## Output Files

The addon creates these files in your configured output directory (default: `/config/www/bom_radar/`):

- `radar_animated.gif` - Animated radar loop (5 frames)
- `image_1.png` through `image_5.png` - Individual radar frames (oldest to newest)
- `radar_last_update.txt` - Timestamp information

Access these in Home Assistant dashboards via `/local/bom_radar/filename`

## Credits

- Radar data provided by the Australian Bureau of Meteorology (BoM)
- Home icon from open source icon libraries

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: https://github.com/safepay/ha-bom-radar-loop-addon/issues
- **Discussions**: https://github.com/safepay/ha-bom-radar-loop-addon/discussions
