#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Australian BoM Radar Loop addon..."

# Create output directory if it doesn't exist
OUTPUT_PATH=$(bashio::config 'output_path')
mkdir -p "/config/${OUTPUT_PATH}"

bashio::log.info "Output directory: /config/${OUTPUT_PATH}"
bashio::log.info "Radar Product ID: $(bashio::config 'radar_product_id')"

# Check if OpenFreeMap background is enabled
BACKGROUND_TYPE=$(bashio::config 'background_type')
if [ "$BACKGROUND_TYPE" = "openfreemap" ]; then
    bashio::log.info "Starting TileServer GL for OpenFreeMap backgrounds..."

    # Start TileServer GL in background on port 8080
    tileserver-gl --config /app/tileserver-config.json --port 8080 --verbose &
    TILESERVER_PID=$!

    bashio::log.info "TileServer GL started with PID $TILESERVER_PID"

    # Wait for TileServer GL to be ready (max 30 seconds)
    bashio::log.info "Waiting for TileServer GL to start..."
    for i in {1..30}; do
        if wget -q --spider http://localhost:8080 2>/dev/null; then
            bashio::log.info "TileServer GL is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            bashio::log.warning "TileServer GL did not start in time, continuing anyway..."
        fi
        sleep 1
    done
else
    bashio::log.info "Using background type: $BACKGROUND_TYPE (TileServer GL not needed)"
fi

# Run the Python application
python3 -u /app/bom_radar_downloader.py
