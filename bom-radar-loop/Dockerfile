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
COPY IDR.legend.0.png ./
COPY run.sh /

# Make run script executable
RUN chmod a+x /run.sh

# Ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1

CMD ["/run.sh"]
