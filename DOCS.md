# Australian BoM Radar Loop

Creates animated radar loops and individual images from Australian Bureau of Meteorology (BoM) radar data for use in Home Assistant dashboards and LLM Vision analysis.

## Features

- **Automated Radar Downloads**: Fetches the latest radar images from the Australian Bureau of Meteorology FTP server
- **Animated GIF Creation**: Generates smooth radar loop animations for your dashboards
- **Individual Frame Export**: Saves separate radar images for use with LLM Vision analysis
- **Multiple Radar Overlay**: Supports overlaying up to 3 radars for extended coverage
- **Residential Location Marker**: Add a house icon showing your location on the radar
- **Customizable Layers**: Choose which map layers to display (background, locations, catchments, topography)
- **Configurable Update Interval**: Set how frequently radar images are updated
- **Timezone Support**: Timestamps in both UTC and your local timezone

## Installation

1. Add this repository to your Home Assistant add-on store:
   - Go to **Settings** → **Add-ons** → **Add-on Store**
   - Click the three dots in the top right and select **Repositories**
   - Add the repository URL
   - Find "Australian BoM Radar Loop" in the add-on store and click **Install**

2. Configure the add-on (see Configuration section below)

3. Start the add-on

4. The radar images will be saved to `/config/www/bom_radar/` (or your configured path)

## Configuration

### Basic Configuration

```yaml
radar_product_id: IDR022
timezone: Australia/Melbourne
update_interval: 600
output_path: www/bom_radar
```

- **radar_product_id**: Your BoM radar product ID (e.g., IDR022 for Melbourne, IDR023 for Geelong)
  - See the **Quick Reference** table below for major cities
  - For all radars by state, see [RADARS.md](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/RADARS.md) (open link in browser)
- **timezone**: Your local timezone (e.g., Australia/Melbourne, Australia/Sydney)
- **update_interval**: Seconds between radar updates (600 = 10 minutes, minimum 60)
- **output_path**: Path relative to /config where images will be saved (default: www/bom_radar)

### Radar Layers

Choose which map layers to overlay on the radar. The **background layer is always included** (not editable). You can toggle these optional layers:

- **layer_locations**: City and town names (enabled by default)
- **layer_catchments**: Water catchment areas
- **layer_topography**: Topographic lines
- **layer_range**: Range rings

Simply check/uncheck the layers you want in the add-on configuration UI. The background layer is automatically included with all selections.

### GIF Animation Settings

```yaml
gif_duration: 500
gif_last_frame_duration: 1000
```

- **gif_duration**: Milliseconds per frame (default: 500)
- **gif_last_frame_duration**: Milliseconds to pause on last frame (default: 1000)

### Residential Location Marker

Add a house icon to show your location on the radar loop:

```yaml
residential_location_enabled: true
residential_latitude: -37.8136
residential_longitude: 144.9631
```

**Note**: The house marker only appears on the animated GIF, not on static images.

### Multiple Radar Support

Overlay additional radars for extended coverage:

```yaml
second_radar_enabled: true
second_radar_product_id: IDR022
third_radar_enabled: false
third_radar_product_id: IDR023
```

The radars will be layered with your primary radar on top, second radar in the middle, and third radar on the bottom. They are automatically positioned based on their geographic locations.

## Using Radar Images in Home Assistant

### Step 1: Add Local File Camera Integration

First, add the animated radar GIF as a camera entity using the **Local File** integration:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for and select **Local File**
4. Enter the file path: `/config/www/bom_radar/radar_animated.gif`
5. Give it a name like "BoM Radar Loop"
6. Click **Submit**

This creates a camera entity (e.g., `camera.bom_radar_loop`) that you can use in your dashboard.

### Step 2: Add to Dashboard with Picture Glance Card

Now add the radar to your dashboard using a **Picture Glance** card:

1. Edit your dashboard
2. Click **Add Card**
3. Select **Picture Glance**
4. Configure the card:

```yaml
type: picture-glance
title: Melbourne Radar
camera_image: camera.bom_radar_loop
camera_view: live
entities: []
```

The Picture Glance card will automatically refresh and show the latest animated radar loop.

### Alternative: Simple Picture Card

If you prefer a simpler static image reference (without camera entity):

```yaml
type: picture
image: /local/bom_radar/radar_animated.gif
```

**Note**: The Picture Glance card with camera entity is recommended as it handles updates more reliably.

### Access Individual Frames

Individual radar frames are saved as `image_1.png` through `image_5.png` in your output directory. These can be used with LLM Vision for storm detection and analysis.

### Timestamp Information

The addon creates a `radar_last_update.txt` file containing:
- UTC timestamp
- Local timestamp in your configured timezone

This can be useful for AI prompts or automation.

## Finding Your Radar Product ID

**See the complete [Radar Reference Guide (RADARS.md)](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/RADARS.md)** for a comprehensive list of all Australian radar locations organized by state.

### Quick Reference - Major Cities

| City | Recommended Product ID | Range |
|------|----------------------|-------|
| **Sydney** | IDR713 | 128km |
| **Melbourne** | IDR023 | 128km |
| **Brisbane** | IDR663 | 128km |
| **Perth** | IDR703 | 128km |
| **Adelaide** | IDR643 | 128km |
| **Canberra** | IDR403 | 128km |
| **Hobart** | IDR763 | 128km |
| **Darwin** | IDR633 | 128km |

Each radar location has multiple product IDs for different coverage ranges (64km, 128km, 256km, 512km). The 128km range is recommended for most users as it provides a good balance of coverage and detail.

For a complete list of all radars organized by state/territory, see [RADARS.md](https://github.com/safepay/ha-bom-radar-loop-addon/blob/main/RADARS.md).

## Troubleshooting

### Addon won't start
- Check the addon logs for errors
- Ensure your `radar_product_id` is valid
- Verify your `output_path` is accessible

### No images appearing
- Check that `/config/www/bom_radar/` directory exists and has files
- Verify the addon is running (check logs)
- Ensure your Home Assistant can access `/local/bom_radar/` URLs

### Images not updating
- Check your `update_interval` setting
- Review addon logs for FTP connection errors
- BoM FTP server may occasionally be unavailable

### House marker not appearing
- House marker only appears on the animated GIF, not static images
- Verify `residential_location_enabled: true`
- Check your latitude/longitude coordinates are correct
- Ensure coordinates fall within your radar's coverage area

## Support

For issues, feature requests, or questions:
- GitHub Issues: [https://github.com/safepay/ha-bom-radar-loop-addon/issues](https://github.com/safepay/ha-bom-radar-loop-addon/issues)

## Credits

Radar data provided by the Australian Bureau of Meteorology (BoM).
