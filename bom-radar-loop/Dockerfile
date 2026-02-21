ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash

WORKDIR /app

# Copy and install requirements first (better caching)
COPY requirements.txt ./

# Install Python dependencies (--break-system-packages is required for Python 3.12+ in Alpine)
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application files
COPY bom_radar_downloader.py ./
COPY radar_metadata.py ./
COPY home-circle-dark.png ./
COPY radar-colour-bar.png ./
COPY run.sh /

# Make run script executable
RUN chmod a+x /run.sh

# Ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1

# Health check: verify the output directory exists and was written to recently.
# The radar_status.json file is written each successful run, so its presence
# and recency (within 2x the default update interval) confirms the addon is alive.
HEALTHCHECK --interval=300s --timeout=10s --start-period=120s --retries=3 \
    CMD test -f /config/www/bom_radar/radar_status.json || exit 1

CMD ["/run.sh"]
