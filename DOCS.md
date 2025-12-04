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
  - Find your radar ID at: http://www.bom.gov.au/australia/radar/
  - Click on your local radar and look at the URL (e.g., IDR022, IDR703, etc.)
- **timezone**: Your local timezone (e.g., Australia/Melbourne, Australia/Sydney)
- **update_interval**: Seconds between radar updates (600 = 10 minutes, minimum 60)
- **output_path**: Path relative to /config where images will be saved (default: www/bom_radar)

### Radar Layers

Choose which map layers to overlay on the radar:

```yaml
layers:
  - background
  - locations
```

Available layers:
- **background**: Terrain background
- **locations**: City and town names
- **catchments**: Water catchment areas
- **topography**: Topographic lines

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

### Display Animated Radar Loop

Add a picture entity card to your dashboard:

```yaml
type: picture-entity
entity: camera.your_camera  # Optional
image: /local/bom_radar/radar_animated.gif
show_state: false
show_name: false
```

Or use a picture card:

```yaml
type: picture
image: /local/bom_radar/radar_animated.gif
```

### Access Individual Frames

Individual radar frames are saved as `image_1.png` through `image_5.png` in your output directory. These can be used with LLM Vision for storm detection and analysis.

### Timestamp Information

The addon creates a `radar_last_update.txt` file containing:
- UTC timestamp
- Local timestamp in your configured timezone

This can be useful for AI prompts or automation.

## Finding Your Radar Product ID

1. Visit http://www.bom.gov.au/australia/radar/
2. Click on your nearest radar location
3. Look at the URL in your browser - it will contain the radar ID
4. Common radar IDs:
   - **IDR013**: Adelaide (Buckland Park)
   - **IDR022**: Melbourne (Laverton)
   - **IDR023**: Geelong
   - **IDR033**: Brisbane (Marburg)
   - **IDR703**: Sydney (Terrey Hills)

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
