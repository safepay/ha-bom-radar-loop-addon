#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Australian BoM Radar Loop addon..."

# Create output directory if it doesn't exist
OUTPUT_PATH=$(bashio::config 'output_path')
mkdir -p "/config/${OUTPUT_PATH}"

bashio::log.info "Output directory: /config/${OUTPUT_PATH}"
bashio::log.info "Radar Product ID: $(bashio::config 'radar_product_id')"

# Run the Python application
python3 -u /app/bom_radar_downloader.py
