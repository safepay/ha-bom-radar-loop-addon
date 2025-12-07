ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python, Node.js, and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    nodejs \
    npm \
    wget \
    # Build tools for TileServer GL
    build-base \
    g++ \
    make \
    pkgconf \
    # Graphics libraries for TileServer GL canvas rendering
    cairo-dev \
    pango-dev \
    pixman-dev \
    libjpeg-turbo-dev \
    giflib-dev \
    librsvg-dev \
    # Runtime libraries
    cairo \
    pango \
    pixman \
    giflib

WORKDIR /app

# Copy and install requirements first (better caching)
COPY requirements.txt ./

# Install Python dependencies (--break-system-packages is required for Python 3.12+ in Alpine)
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Install TileServer GL globally
RUN npm install -g tileserver-gl@5.4.0

# Copy application files
COPY bom_radar_downloader.py ./
COPY radar_metadata.py ./
COPY home-circle-dark.png ./
COPY IDR.legend.0.png ./
COPY tileserver-config.json ./
COPY run.sh /

# Make run script executable
RUN chmod a+x /run.sh

# Ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1

CMD ["/run.sh"]
