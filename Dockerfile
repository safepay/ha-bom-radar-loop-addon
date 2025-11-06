FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements first (better caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application file
COPY bom_radar_downloader.py ./

# Ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1


CMD ["python", "-u", "bom_radar_downloader.py"]
