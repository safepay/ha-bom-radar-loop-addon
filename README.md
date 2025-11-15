# Home Assistant Australian BoM Radar Loop Creator in Docker
Docker container for Home Assistant BoM Radar Loop plus individual radar images to enable use in LLM Vision

The Home Assitant LLM Vision analyser requires separate radar images to process when looking for storm events.

This Docker container creates those images, plus a useful animated GIF for showing on your dashboards. There is also a useful timestamp file for use with an AI prompt to help it understand the BoM image timestamps.

Note that I run this on a Synology NAS so it is set up for that in terms of directories.

Just change `/volume1/docker/bom_radar_downloader` to the path that suits your file system.

## Installation

### On Docker
Create the following directory structure somewhere on the machine where you run Docker:
```
/volume1/docker/bom_radar_downloader/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── bom_radar_downloader.py
├── radar_metadata.py
├── config.yaml
├── IDR.legend.0.png
├── home-circle-dark.png
└── images/  (created automatically)
```
### On Home Assistant
Edit the `config.yaml` file to suit your requirements. The intructions are in the file on what to change.

On your Home Assistant create a `images` folder under `/config/www` as per your config file in the `Output Configuration` section.

Then build and run as required by Docker.

## Features

### Second Radar Support (Optional)
You can now overlay a second radar on your primary radar for extended coverage. This is useful for:
- Tracking storms moving between radar coverage areas
- Getting a wider view of weather patterns
- Combining adjacent radars for seamless coverage

To enable:
1. Edit `config.yaml` and set `second_radar.enabled: true`
2. Set `second_radar.product_id` to your desired secondary radar (e.g., `IDR022` for Melbourne)
3. The second radar will automatically:
   - Have its copyright notice removed (top 16px)
   - Have its timestamp text made transparent
   - Be positioned geographically relative to the primary radar
   - Appear below the primary radar in the composite (primary radar on top)
   - Maintain the primary radar's center as the image center

### Residential Location Marker (Optional)
Add a house icon to show your location on the radar loop. Configure in `config.yaml` under `residential_location`.

### Configurable Last Frame Pause
The final frame in the animated GIF can pause longer before the loop restarts, making it easier to see the most recent radar data. Configure `gif.last_frame_duration` in `config.yaml` (default: 1000ms).
