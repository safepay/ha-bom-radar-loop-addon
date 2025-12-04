# Home Assistant Australian BoM Radar Loop Creator in Docker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub stars](https://img.shields.io/github/stars/safepay/ha-bom-radar-loop-docker?style=social)](https://github.com/safepay/ha-bom-radar-loop-docker/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/safepay/ha-bom-radar-loop-docker?style=social)](https://github.com/safepay/ha-bom-radar-loop-docker/network/members)

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

## Docker Commands

### Option 1: Using Synology Container Manager (Recommended for Synology NAS)
This project was originally built for Synology NAS systems.

1. Open **Container Manager** on your Synology NAS
2. Go to **Project** and click **Create**
3. Set the project folder to `/volume1/docker/bom_radar_downloader` (or your chosen location)
4. Select **Set path** and choose the folder containing your Dockerfile
5. Container Manager will automatically detect the Dockerfile
6. Click **Build** to create the image
7. Once built, click **Run** to start the container with the configured volume mounts

The Container Manager will handle the volume mappings as defined in your project setup.

### Option 2: Using the Dockerfile (Command Line)
This repository includes a Dockerfile for building a custom image.

1. Build the image from the directory containing the Dockerfile:
```bash
docker build -t bom-radar-loop .
```

2. Run the container with volume mounts:
```bash
docker run -d \
  --name bom-radar-loop \
  -v /volume1/docker/bom_radar_downloader/config.yaml:/config/config.yaml \
  -v /volume1/docker/bom_radar_downloader/IDR.legend.0.png:/IDR.legend.0.png \
  -v /volume1/docker/bom_radar_downloader/images:/images \
  --restart unless-stopped \
  bom-radar-loop
```

### Option 3: Using Python Base Image (Ubuntu/Linux)
If you prefer not to use the Dockerfile, you can run directly from a Python base image.

```bash
docker run -d \
  --name bom-radar-loop \
  -v /volume1/docker/bom_radar_downloader:/app \
  -v /volume1/docker/bom_radar_downloader/images:/images \
  -w /app \
  --restart unless-stopped \
  python:3.11-slim \
  sh -c "pip install --no-cache-dir -r requirements.txt && python -u bom_radar_downloader.py"
```

**Note:** Replace `/volume1/docker/bom_radar_downloader` with your actual path on Ubuntu systems (e.g., `/home/user/bom-radar-loop`).

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

### Third Radar Support (Optional)
You can also overlay a third radar for even more extended coverage. The third radar works just like the second radar and uses the same processing logic.

To enable:
1. Edit `config.yaml` and set `third_radar.enabled: true`
2. Set `third_radar.product_id` to your desired third radar
3. The third radar will automatically:
   - Have its copyright notice removed (top 16px)
   - Have its timestamp text made transparent
   - Be positioned geographically relative to the primary radar
   - Appear below both the second and primary radars in the composite
   - Layering order (bottom to top): Third radar → Second radar → Primary radar

### Residential Location Marker (Optional)
Add a house icon to show your location on the radar loop. Configure in `config.yaml` under `residential_location`.

### Configurable Last Frame Pause
The final frame in the animated GIF can pause longer before the loop restarts, making it easier to see the most recent radar data. Configure `gif.last_frame_duration` in `config.yaml` (default: 1000ms).
