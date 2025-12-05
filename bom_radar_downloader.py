#!/usr/bin/env python3
import io
import ftplib
import json
import os
import sys
import asyncio
import logging
import time
import urllib.request
import urllib.error
from PIL import Image
from datetime import datetime
from pathlib import Path
import pytz
import math
from radar_metadata import RADAR_METADATA

VERSION = '1.0.6'

# Check for Home Assistant addon options file or fallback to config.yaml
OPTIONS_FILE = Path('/data/options.json')
CONFIG_FILE = Path('/config/config.yaml')


class MapTileProvider:
    """Handles fetching and caching of OpenStreetMap tiles"""

    # OpenStreetMap tile server URL
    OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

    # User-Agent required by OSM tile usage policy
    USER_AGENT = "HomeAssistant-BoM-Radar-Addon/1.0.6 (https://github.com/safepay/ha-bom-radar-loop-addon)"

    # Cache expiry: 30 days (map tiles rarely change)
    CACHE_EXPIRY_SECONDS = 30 * 24 * 3600

    def __init__(self, cache_dir):
        """
        Initialize the map tile provider

        Args:
            cache_dir: Directory path for persistent tile cache
        """
        self.cache_dir = Path(cache_dir)
        self.memory_cache = {}  # Session cache for faster access

        # Create cache directory if it doesn't exist
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created tile cache directory: {self.cache_dir}")

    @staticmethod
    def latlon_to_tile(lat, lon, zoom):
        """
        Convert latitude/longitude to tile coordinates at given zoom level

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            zoom: Zoom level (0-19)

        Returns:
            Tuple of (tile_x, tile_y)
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        tile_x = int((lon + 180.0) / 360.0 * n)
        tile_y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (tile_x, tile_y)

    @staticmethod
    def tile_to_latlon(tile_x, tile_y, zoom):
        """
        Convert tile coordinates to latitude/longitude of tile's NW corner

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            zoom: Zoom level

        Returns:
            Tuple of (lat, lon)
        """
        n = 2.0 ** zoom
        lon = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat = math.degrees(lat_rad)
        return (lat, lon)

    def fetch_tile(self, z, x, y):
        """
        Fetch a single tile with caching

        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            PIL Image object (256x256 pixels)
        """
        # Check memory cache first
        cache_key = f"{z}/{x}/{y}"
        if cache_key in self.memory_cache:
            logging.debug(f"Tile {cache_key} loaded from memory cache")
            return self.memory_cache[cache_key]

        # Check disk cache
        cache_path = self.cache_dir / str(z) / str(x) / f"{y}.png"

        if cache_path.exists():
            # Check if cache is still valid (not expired)
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age < self.CACHE_EXPIRY_SECONDS:
                logging.debug(f"Tile {cache_key} loaded from disk cache (age: {cache_age/86400:.1f} days)")
                tile = Image.open(cache_path).convert('RGBA')
                self.memory_cache[cache_key] = tile
                return tile
            else:
                logging.debug(f"Tile {cache_key} cache expired, re-downloading")

        # Download tile
        url = self.OSM_TILE_URL.format(z=z, x=x, y=y)
        logging.info(f"Downloading tile: {cache_key}")

        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as response:
                tile_data = response.read()
                tile = Image.open(io.BytesIO(tile_data)).convert('RGBA')

            # Save to disk cache
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            tile.save(cache_path, 'PNG')
            logging.debug(f"Tile {cache_key} saved to disk cache")

            # Save to memory cache
            self.memory_cache[cache_key] = tile

            return tile

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            logging.error(f"Failed to download tile {cache_key}: {e}")
            # Return a blank tile as fallback
            return Image.new('RGBA', (256, 256), (200, 200, 200, 255))
        except Exception as e:
            logging.error(f"Unexpected error downloading tile {cache_key}: {e}")
            return Image.new('RGBA', (256, 256), (200, 200, 200, 255))

    def create_background(self, lat, lon, zoom, size=1024):
        """
        Create a stitched map background centered on given coordinates

        Args:
            lat: Center latitude in decimal degrees
            lon: Center longitude in decimal degrees
            zoom: Zoom level
            size: Output size in pixels (default: 1024x1024)

        Returns:
            PIL Image object (size x size pixels)
        """
        logging.info(f"Creating OSM background: lat={lat}, lon={lon}, zoom={zoom}, size={size}x{size}")

        # Calculate exact tile coordinates (with fractional part for sub-tile precision)
        n = 2.0 ** zoom
        exact_x = (lon + 180.0) / 360.0 * n
        exact_y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n

        # Get integer tile coordinates
        center_tile_x = int(exact_x)
        center_tile_y = int(exact_y)

        # Fetch a larger grid to allow for sub-tile centering
        # For 1024x1024 output (4x4 tiles), fetch 6x6 tiles to have margin
        tiles_per_side = (size // 256) + 2  # Add 2 for margin
        half_tiles = tiles_per_side // 2

        # Calculate tile range
        start_x = center_tile_x - half_tiles
        start_y = center_tile_y - half_tiles

        # Create the stitched image (larger than needed)
        stitched_size = tiles_per_side * 256
        stitched = Image.new('RGBA', (stitched_size, stitched_size))

        # Fetch and paste each tile
        for dy in range(tiles_per_side):
            for dx in range(tiles_per_side):
                tile_x = start_x + dx
                tile_y = start_y + dy

                tile = self.fetch_tile(zoom, tile_x, tile_y)

                paste_x = dx * 256
                paste_y = dy * 256
                stitched.paste(tile, (paste_x, paste_y))

        logging.debug(f"Stitched {tiles_per_side}x{tiles_per_side} tiles into {stitched.size} image")

        # Calculate exact pixel position in stitched image
        pixel_x = (exact_x - start_x) * 256
        pixel_y = (exact_y - start_y) * 256

        # Crop to center the image on exact coordinates
        crop_left = int(pixel_x - size / 2)
        crop_top = int(pixel_y - size / 2)
        crop_right = crop_left + size
        crop_bottom = crop_top + size

        # Ensure we're within bounds (should always be true with margin)
        if crop_left >= 0 and crop_top >= 0 and crop_right <= stitched.width and crop_bottom <= stitched.height:
            centered = stitched.crop((crop_left, crop_top, crop_right, crop_bottom))
            logging.debug(f"Cropped to {size}x{size} centered on exact coordinates ({pixel_x:.1f}, {pixel_y:.1f})")
        else:
            # Fallback - shouldn't happen with margin
            logging.warning(f"Crop bounds exceeded (margin insufficient), using rough centering")
            crop_left = max(0, crop_left)
            crop_top = max(0, crop_top)
            crop_right = min(stitched.width, crop_right)
            crop_bottom = min(stitched.height, crop_bottom)
            centered = stitched.crop((crop_left, crop_top, crop_right, crop_bottom))

        return centered


class Config:
    """Configuration management for Home Assistant addon"""

    @staticmethod
    def load():
        """Load configuration from Home Assistant addon options or config file"""

        # Try Home Assistant addon options first
        if OPTIONS_FILE.exists():
            logging.info(f'Loading configuration from Home Assistant addon: {OPTIONS_FILE}')

            with open(OPTIONS_FILE, 'r') as file:
                options = json.load(file)

            # Build output path - Home Assistant addons have access to /config
            output_path = options.get('output_path', 'www/bom_radar')
            output_directory = f'/config/{output_path}'

            # Build layers list from boolean options
            # Background is always included first (not editable)
            layers = ['background']

            # Add optional layers based on user selection (max 4 layers total including background)
            if options.get('layer_catchments', False):
                layers.append('catchments')
            if options.get('layer_topography', False):
                layers.append('topography')
            if options.get('layer_locations', False):
                layers.append('locations')
            if options.get('layer_range', False):
                layers.append('range')

            return {
                # Radar settings
                'product_id': options.get('radar_product_id', 'IDR022'),
                'timezone': options.get('timezone', 'Australia/Melbourne'),

                # Background type
                'background_type': options.get('background_type', 'bom'),

                # Scheduler settings (always enabled in addon mode)
                'scheduler_enabled': True,
                'update_interval': int(options.get('update_interval', 600)),
                'retry_on_error': True,
                'retry_interval': 60,

                # Layers
                'layers': layers,

                # Output settings
                'output_directory': output_directory,
                'animated_gif_filename': 'radar_animated.gif',
                'timestamp_filename': 'radar_last_update.txt',
                'legend_file': '/app/IDR.legend.0.png',

                # GIF settings
                'gif_duration': int(options.get('gif_duration', 500)),
                'gif_last_frame_duration': int(options.get('gif_last_frame_duration', 1000)),
                'gif_loop': 0,

                # Logging
                'log_level': 'INFO',

                # Residential location marker
                'residential_enabled': options.get('residential_location_enabled', False),
                'residential_lat': float(options.get('residential_latitude', -37.8136)),
                'residential_lon': float(options.get('residential_longitude', 144.9631)),

                # Second radar
                'second_radar_enabled': options.get('second_radar_enabled', False),
                'second_radar_product_id': options.get('second_radar_product_id'),

                # Third radar
                'third_radar_enabled': options.get('third_radar_enabled', False),
                'third_radar_product_id': options.get('third_radar_product_id'),

                # Home Assistant addon mode (no SMB needed)
                'addon_mode': True,
            }

        # Fallback to config.yaml for backward compatibility
        elif CONFIG_FILE.exists():
            logging.info(f'Loading configuration from config file: {CONFIG_FILE}')
            import yaml

            with open(CONFIG_FILE, 'r') as file:
                config = yaml.safe_load(file)

            radar = config.get('radar', {})
            scheduler = config.get('scheduler', {})
            smb = config.get('smb', {})
            output = config.get('output', {})
            gif = config.get('gif', {})
            log_config = config.get('logging', {})
            residential = config.get('residential_location', {})
            second_radar = config.get('second_radar', {})
            third_radar = config.get('third_radar', {})

            return {
                # Radar settings
                'product_id': os.getenv('PRODUCT_ID', radar.get('product_id', 'IDR022')),
                'timezone': os.getenv('TIMEZONE', radar.get('timezone', 'Australia/Melbourne')),

                # Background type
                'background_type': os.getenv('BACKGROUND_TYPE', radar.get('background_type', 'bom')),

                # Scheduler settings
                'scheduler_enabled': os.getenv('SCHEDULER_ENABLED', str(scheduler.get('enabled', True))).lower() == 'true',
                'update_interval': int(os.getenv('UPDATE_INTERVAL', scheduler.get('update_interval', 600))),
                'retry_on_error': scheduler.get('retry_on_error', True),
                'retry_interval': int(os.getenv('RETRY_INTERVAL', scheduler.get('retry_interval', 60))),

                # SMB settings (for backward compatibility)
                'smb_server': os.getenv('SMB_SERVER', smb.get('server')),
                'smb_share': os.getenv('SMB_SHARE', smb.get('share')),
                'smb_username': os.getenv('SMB_USERNAME', smb.get('username')),
                'smb_password': os.getenv('SMB_PASSWORD', smb.get('password')),
                'smb_remote_path': os.getenv('SMB_REMOTE_PATH', smb.get('remote_path')),

                # Layers
                'layers': config.get('layers', ['background', 'catchments', 'topography', 'locations']),

                # Output settings
                'output_directory': os.getenv('OUTPUT_DIR', output.get('directory', '/images')),
                'animated_gif_filename': os.getenv('ANIMATED_GIF', output.get('animated_gif', 'radar_animated.gif')),
                'timestamp_filename': os.getenv('TIMESTAMP_FILE', output.get('timestamp_file', 'radar_last_update.txt')),
                'legend_file': os.getenv('LEGEND_FILE', output.get('legend_file', '/app/IDR.legend.0.png')),

                # GIF settings
                'gif_duration': int(os.getenv('GIF_DURATION', gif.get('duration', 500))),
                'gif_last_frame_duration': int(os.getenv('GIF_LAST_FRAME_DURATION', gif.get('last_frame_duration', 1000))),
                'gif_loop': int(os.getenv('GIF_LOOP', gif.get('loop', 0))),

                # Logging
                'log_level': os.getenv('LOG_LEVEL', log_config.get('level', 'INFO')).upper(),

                # Residential location marker
                'residential_enabled': residential.get('enabled', False),
                'residential_lat': residential.get('latitude'),
                'residential_lon': residential.get('longitude'),

                # Second radar
                'second_radar_enabled': second_radar.get('enabled', False),
                'second_radar_product_id': second_radar.get('product_id'),

                # Third radar
                'third_radar_enabled': third_radar.get('enabled', False),
                'third_radar_product_id': third_radar.get('product_id'),

                # Not in addon mode
                'addon_mode': False,
            }

        else:
            logging.error('No configuration file found!')
            logging.error(f'Checked: {OPTIONS_FILE}, {CONFIG_FILE}')
            sys.exit(1)


class RadarProcessor:
    """Processes radar images from BOM FTP"""

    def __init__(self, config):
        self.config = config
        self.frames = []
        self.saved_filenames = []

        # Create output directory if it doesn't exist
        os.makedirs(self.config['output_directory'], exist_ok=True)

        # Initialize map tile provider for OSM backgrounds
        tile_cache_dir = os.path.join(self.config['output_directory'], 'tile_cache')
        self.tile_provider = MapTileProvider(tile_cache_dir)
    
    def load_legend(self):
        """Load the legend image"""
        legend_path = self.config['legend_file']

        if os.path.exists(legend_path):
            legend_image = Image.open(legend_path).convert('RGBA')
            logging.info(f"Loaded legend image: {legend_path} - Size: {legend_image.size}")
            return legend_image
        else:
            logging.warning(f"Legend image not found at {legend_path}")
            return None

    def load_house_icon(self):
        """Load house icon from PNG file

        Returns:
            PIL Image object with RGBA mode, or None if not found
        """
        try:
            # Check multiple possible locations for the icon
            possible_paths = [
                '/app/home-circle-dark.png',
                'home-circle-dark.png',
                os.path.join(os.path.dirname(__file__), 'home-circle-dark.png')
            ]

            icon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break

            if icon_path is None:
                logging.error(f"House icon PNG file not found. Tried: {possible_paths}")
                return None

            # Load PNG directly with PIL
            icon = Image.open(icon_path).convert('RGBA')

            logging.debug(f"Loaded house icon from {icon_path}: {icon.size}")
            return icon

        except Exception as e:
            logging.error(f"Error loading house icon: {e}")
            return None

    def get_optimal_zoom(self, product_id):
        """
        Calculate optimal zoom level for OSM tiles based on radar range

        Args:
            product_id: BOM product ID (e.g., 'IDR022')

        Returns:
            int: Optimal zoom level for map tiles (minimum 9 for sufficient detail)
        """
        # Minimum zoom level for sufficient map detail
        MIN_ZOOM = 9

        # Extract range indicator from product ID (IDRXYZ format)
        # X indicates range: 1=512km, 2=256km, 3=128km, 4=64km
        # Note: Range refers to radius, so diameter is 2x (e.g., 256km range = 512km diameter)
        # Zoom levels calculated to match radar coverage, with minimum of 9 for detail
        if len(product_id) >= 4:
            range_digit = product_id[3]
            zoom_map = {
                '1': 9,   # 512km range (1024km diameter) - minimum zoom for detail
                '2': 9,   # 256km range (512km diameter) - minimum zoom for detail
                '3': 9,   # 128km range (256km diameter)
                '4': 10   # 64km range (128km diameter)
            }
            zoom = zoom_map.get(range_digit, MIN_ZOOM)
            logging.debug(f"Product {product_id} range digit: {range_digit}, zoom: {zoom}")
            return zoom
        else:
            # Default to minimum zoom
            logging.warning(f"Could not determine range from product ID {product_id}, using default zoom {MIN_ZOOM}")
            return MIN_ZOOM

    def create_base_image(self, product_id):
        """
        Create base image with selected background type (BoM or OSM)

        Args:
            product_id: BOM product ID

        Returns:
            PIL Image object (512x512 RGBA)
        """
        background_type = self.config['background_type']

        if background_type == 'openstreetmap':
            logging.info(f"Creating OpenStreetMap background for {product_id}")

            # Get radar coordinates from metadata
            if product_id not in RADAR_METADATA:
                logging.error(f"Product {product_id} not found in radar metadata, falling back to BoM background")
                return self.create_bom_base_image(product_id)

            lat, lon, km_per_pixel = RADAR_METADATA[product_id]
            logging.info(f"Radar center: lat={lat}, lon={lon}")

            # Calculate optimal zoom level
            zoom = self.get_optimal_zoom(product_id)

            # Create high-resolution OSM background (1024x1024)
            try:
                osm_background = self.tile_provider.create_background(
                    lat, lon, zoom, size=1024
                )

                # Downsample to 512x512 with high-quality antialiasing
                osm_resized = osm_background.resize(
                    (512, 512),
                    Image.Resampling.LANCZOS
                )
                logging.info(f"Created OSM background: {osm_resized.size}")

                # Load legend as base (just like BoM backgrounds do)
                # The legend PNG is 512x512 with transparent area for map and opaque legend at bottom
                base_image = self.load_legend()
                if base_image is None:
                    logging.error("Failed to load legend, using OSM background without legend")
                    return osm_resized

                # Composite OSM background onto the legend, preserving the legend area
                # The legend includes the color scale bar plus background, typically 60+ pixels
                legend_height = 60  # Increased from 45 to preserve full legend background

                # Create mask: opaque (255) where we want to paste OSM, transparent (0) for legend area
                from PIL import ImageDraw
                mask = Image.new('L', (512, 512), 255)  # White (opaque) for map area
                draw = ImageDraw.Draw(mask)
                draw.rectangle([(0, 512 - legend_height), (512, 512)], fill=0)  # Black (transparent) for legend

                # Paste OSM background onto legend base using the mask
                base_image.paste(osm_resized, (0, 0), mask)
                logging.debug(f"Composited OSM background onto legend base, preserving bottom {legend_height}px for legend")

                return base_image

            except Exception as e:
                logging.error(f"Failed to create OSM background: {e}")
                logging.info("Falling back to BoM background")
                return self.create_bom_base_image(product_id)

        else:
            # Use BoM background with layers
            return self.create_bom_base_image(product_id)

    def create_bom_base_image(self, product_id):
        """
        Create base image using BoM layers (original behavior)

        Args:
            product_id: BOM product ID

        Returns:
            PIL Image object (512x512 RGBA) with legend, background, and optional layers
        """
        logging.info(f"Creating BoM background for {product_id}")

        # Load legend as base
        base_image = self.load_legend()
        if base_image is None:
            logging.error("Failed to load legend, creating blank image")
            base_image = Image.new('RGBA', (512, 512), (255, 255, 255, 0))

        # Connect to FTP and build composite layers
        try:
            ftp = ftplib.FTP('ftp.bom.gov.au')
            ftp.login()
            ftp.cwd('anon/gen/radar_transparencies/')

            for layer in self.config['layers']:
                filename = f"{product_id}.{layer}.png"
                logging.debug(f"Downloading layer: {layer}")
                file_obj = io.BytesIO()
                ftp.retrbinary('RETR ' + filename, file_obj.write)
                file_obj.seek(0)

                image = Image.open(file_obj).convert('RGBA')
                base_image.paste(image, (0, 0), image)
                logging.debug(f"Added layer: {layer}")

            ftp.quit()
            logging.info(f"BoM base image with all layers created: {base_image.size}")

        except Exception as e:
            logging.error(f"Error creating BoM base image: {e}")

        return base_image

    def get_radar_metadata(self, product_id):
        """Get radar center coordinates and scale from product ID

        Retrieves metadata from the radar_metadata module which contains
        information for all Australian BOM radars.

        Returns:
            tuple: (latitude, longitude, km_per_pixel)
        """
        # Default values if product ID not found
        default_metadata = (0, 0, 1.0)

        metadata = RADAR_METADATA.get(product_id, default_metadata)
        if product_id not in RADAR_METADATA:
            logging.warning(f"Radar metadata not found for {product_id}. Using defaults. "
                          f"House marker may not be accurately positioned.")

        return metadata

    def latlon_to_pixel(self, lat, lon, radar_lat, radar_lon, km_per_pixel, image_size):
        """Convert latitude/longitude to pixel coordinates on radar image

        This uses a simple approximation assuming the radar image is centered
        on the radar location and uses a linear projection.

        Note: BOM radar images are always 512x512 pixels. The composite image
        may be taller due to the legend at the bottom, but the radar center
        is always at (256, 256) in the radar portion of the image.
        """
        # Earth's radius in km
        R = 6371.0

        # Convert to radians
        lat1 = math.radians(radar_lat)
        lon1 = math.radians(radar_lon)
        lat2 = math.radians(lat)
        lon2 = math.radians(lon)

        # Calculate distance in km using Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # For small distances, we can use a simpler approximation
        # Distance in km (north is positive)
        dy = dlat * R
        # Distance in km (east is positive)
        dx = dlon * R * math.cos(lat1)

        # Convert km to pixels
        # BOM radar images are always 512x512, so center is at (256, 256)
        # regardless of the total composite image size (which includes legend)
        RADAR_SIZE = 512
        center_x = RADAR_SIZE // 2  # 256
        center_y = RADAR_SIZE // 2  # 256

        # Calculate pixel position
        # Note: y increases downward in images, so we subtract dy
        pixel_x = center_x + int(dx / km_per_pixel)
        pixel_y = center_y - int(dy / km_per_pixel)

        logging.debug(f"Converted ({lat}, {lon}) to pixel ({pixel_x}, {pixel_y})")
        logging.debug(f"Offset from radar: dx={dx:.2f}km, dy={dy:.2f}km")
        logging.debug(f"Radar center: ({center_x}, {center_y}), Image size: {image_size}")

        return (pixel_x, pixel_y)

    def add_house_marker(self, frame, house_icon):
        """Add house icon to a radar frame at the configured residential location"""
        if not self.config['residential_enabled']:
            return frame

        lat = self.config['residential_lat']
        lon = self.config['residential_lon']

        if lat is None or lon is None:
            logging.warning("Residential location enabled but coordinates not provided")
            return frame

        # Get radar metadata
        product_id = self.config['product_id']
        radar_lat, radar_lon, km_per_pixel = self.get_radar_metadata(product_id)

        # Convert lat/lon to pixel coordinates
        pixel_x, pixel_y = self.latlon_to_pixel(
            lat, lon, radar_lat, radar_lon, km_per_pixel, frame.size
        )

        # Check if coordinates are within image bounds
        icon_size = house_icon.size[0]
        if (0 <= pixel_x < frame.size[0] and 0 <= pixel_y < frame.size[1]):
            # Calculate position to center the icon on the coordinates
            paste_x = pixel_x - icon_size // 2
            paste_y = pixel_y - icon_size // 2

            # Paste the house icon onto the frame
            frame.paste(house_icon, (paste_x, paste_y), house_icon)
            logging.debug(f"Added house marker at pixel ({pixel_x}, {pixel_y})")
        else:
            logging.warning(f"Residential location ({lat}, {lon}) is outside radar image bounds")

        return frame

    def remove_copyright(self, image):
        """Remove top 16px copyright notice from radar image by making it transparent

        Args:
            image: PIL Image object in RGBA mode

        Returns:
            PIL Image with top 16px replaced with transparent pixels
        """
        img = image.copy()
        width, height = img.size

        # Create a transparent strip for the top 16 pixels
        pixels = img.load()
        for y in range(min(16, height)):
            for x in range(width):
                pixels[x, y] = (0, 0, 0, 0)  # Fully transparent

        logging.debug(f"Removed copyright (top 16px) from image {img.size}")
        return img

    def make_timestamp_transparent(self, image):
        """Make timestamp text at bottom of image transparent while preserving radar pixels

        BOM radar images have timestamp text in pure black (RGB 0,0,0) at the bottom.
        The background is already transparent. This function removes only the black text
        while preserving any colored radar data that may overlay the timestamp area.

        Args:
            image: PIL Image object in RGBA mode

        Returns:
            PIL Image with timestamp text made transparent
        """
        img = image.copy()
        width, height = img.size
        pixels = img.load()

        # The timestamp text is in the bottom ~20 pixels
        timestamp_region_height = 20
        start_y = max(0, height - timestamp_region_height)

        # Target pure black (RGB 0,0,0) timestamp text
        # Radar data is never this color, so we can safely remove it
        for y in range(start_y, height):
            for x in range(width):
                r, g, b, a = pixels[x, y]

                # Make black pixels transparent (timestamp text)
                # Allow slight tolerance (≤2) for compression artifacts
                if r <= 2 and g <= 2 and b <= 2:
                    pixels[x, y] = (0, 0, 0, 0)  # Make transparent

        logging.debug(f"Made timestamp text (RGB 0,0,0) transparent in bottom {timestamp_region_height}px of image {img.size}")
        return img

    def calculate_radar_offset(self, primary_product_id, secondary_product_id):
        """Calculate pixel offset between two radars based on their geographic positions

        Args:
            primary_product_id: Product ID of primary radar
            secondary_product_id: Product ID of secondary radar

        Returns:
            tuple: (offset_x, offset_y) in pixels for positioning secondary radar relative to primary
        """
        # Get metadata for both radars
        primary_lat, primary_lon, primary_km_per_pixel = self.get_radar_metadata(primary_product_id)
        secondary_lat, secondary_lon, secondary_km_per_pixel = self.get_radar_metadata(secondary_product_id)

        logging.info(f"Primary radar ({primary_product_id}): lat={primary_lat}, lon={primary_lon}, scale={primary_km_per_pixel}")
        logging.info(f"Secondary radar ({secondary_product_id}): lat={secondary_lat}, lon={secondary_lon}, scale={secondary_km_per_pixel}")

        # Calculate the geographic distance between the two radar centers
        # Use the primary radar's scale for pixel conversion
        R = 6371.0  # Earth's radius in km

        # Convert to radians
        lat1 = math.radians(primary_lat)
        lon1 = math.radians(primary_lon)
        lat2 = math.radians(secondary_lat)
        lon2 = math.radians(secondary_lon)

        # Calculate distance in km
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Distance in km (north is positive)
        dy = dlat * R
        # Distance in km (east is positive)
        dx = dlon * R * math.cos(lat1)

        # Convert km to pixels using primary radar's scale
        offset_x = int(dx / primary_km_per_pixel)
        offset_y = -int(dy / primary_km_per_pixel)  # Negative because y increases downward

        logging.info(f"Radar offset: dx={dx:.2f}km, dy={dy:.2f}km -> pixels=({offset_x}, {offset_y})")

        return (offset_x, offset_y)

    def get_timestamp(self, filename):
        """Extract timestamp from filename for sorting"""
        try:
            parts = filename.split('.')
            if len(parts) >= 3:
                return parts[2]  # YYYYMMDDHHmm
            return filename
        except:
            return filename
    
    def parse_timestamp(self, filename):
        """Parse timestamp from BOM radar filename"""
        try:
            parts = filename.split('.')
            if len(parts) >= 3:
                datetime_str = parts[2]  # YYYYMMDDHHmm format
                
                # Parse the datetime (BOM times are in UTC)
                dt_utc = datetime.strptime(datetime_str, "%Y%m%d%H%M")
                dt_utc = pytz.utc.localize(dt_utc)
                
                # Convert to local timezone
                local_tz = pytz.timezone(self.config['timezone'])
                dt_local = dt_utc.astimezone(local_tz)
                
                # Format both UTC and local times
                utc_time = dt_utc.strftime("%Y-%m-%d %H:%M UTC")
                local_time = dt_local.strftime("%Y-%m-%d %H:%M %Z")
                
                timestamp_content = f"UTC Time: {utc_time}; Local Time ({self.config['timezone']}): {local_time}\n"
                
                logging.info(f"Last radar image - UTC: {utc_time}, Local: {local_time}")
                return timestamp_content
        except Exception as e:
            logging.error(f"Error parsing timestamp from {filename}: {e}")
            return f"Last file: {filename}\nError parsing timestamp: {e}\n"
        
        return None
    
    def process_images(self):
        """Main processing function"""
        self.frames = []
        self.saved_filenames = []

        product_id = self.config['product_id']
        second_radar_enabled = self.config.get('second_radar_enabled', False)
        second_radar_product_id = self.config.get('second_radar_product_id')
        third_radar_enabled = self.config.get('third_radar_enabled', False)
        third_radar_product_id = self.config.get('third_radar_product_id')

        try:
            # Create base image (BoM or OSM background)
            base_image = self.create_base_image(product_id)

            if base_image is None:
                logging.error("Cannot proceed without base image")
                return False

            # Load house icon if residential location is enabled
            house_icon = None
            if self.config['residential_enabled']:
                house_icon = self.load_house_icon()
                if house_icon:
                    logging.info(f"Residential location marker enabled at "
                               f"({self.config['residential_lat']}, {self.config['residential_lon']})")
                else:
                    logging.warning("Could not load house icon, marker will be disabled")

            # Save the legend area (bottom 60px) to re-apply after radar compositing
            # This ensures the legend always appears on top, even if radar data overlaps it
            # Increased from 45 to 60 to include full legend background
            legend_height = 60
            base_width, base_height = base_image.size
            legend_area = None

            if base_height > legend_height:
                legend_area = base_image.crop((0, base_height - legend_height, base_width, base_height))
                logging.debug(f"Saved legend area: {legend_area.size}")
            else:
                logging.warning(f"Base image height ({base_height}) <= legend height ({legend_height}), cannot extract legend")

            # Connect to FTP server for radar data
            logging.info("Connecting to BOM FTP server...")
            ftp = ftplib.FTP('ftp.bom.gov.au')
            ftp.login()
            ftp.cwd('/anon/gen/radar/')

            # Get all matching radar files for primary radar
            all_files = [file for file in ftp.nlst()
                         if file.startswith(product_id)
                         and file.endswith('.png')]

            # Sort by timestamp
            sorted_files = sorted(all_files, key=self.get_timestamp)

            # Get the last 5 (most recent) radar images
            files = sorted_files[-5:]

            logging.info(f"Found {len(all_files)} total radar files for primary radar")
            logging.info(f"Selected most recent 5: {[f.split('.')[2] for f in files]}")

            # Download second radar images if enabled
            second_radar_images = []
            if second_radar_enabled and second_radar_product_id:
                logging.info(f"Second radar enabled: {second_radar_product_id}")

                # Get all matching files for second radar
                all_second_files = [file for file in ftp.nlst()
                                   if file.startswith(second_radar_product_id)
                                   and file.endswith('.png')]

                # Sort by timestamp
                sorted_second_files = sorted(all_second_files, key=self.get_timestamp)

                # Get the last 5 (most recent) radar images
                second_files = sorted_second_files[-5:]

                logging.info(f"Found {len(all_second_files)} total files for second radar")
                logging.info(f"Selected most recent 5: {[f.split('.')[2] for f in second_files]}")

                # Download second radar images
                for file in second_files:
                    logging.debug(f"Processing second radar {file}")
                    file_obj = io.BytesIO()
                    try:
                        ftp.retrbinary('RETR ' + file, file_obj.write)
                        file_obj.seek(0)
                        image = Image.open(file_obj).convert('RGBA')

                        # Process second radar image: remove copyright and timestamp
                        image = self.remove_copyright(image)
                        image = self.make_timestamp_transparent(image)

                        second_radar_images.append(image)
                        logging.debug(f"Successfully processed second radar {file}")
                    except ftplib.all_errors as e:
                        logging.error(f"Error downloading second radar {file}: {e}")
                        second_radar_images.append(None)  # Placeholder for failed download

                # Calculate offset for second radar positioning
                if second_radar_images:
                    offset_x, offset_y = self.calculate_radar_offset(product_id, second_radar_product_id)
                    logging.info(f"Second radar will be offset by ({offset_x}, {offset_y}) pixels")

            # Download third radar images if enabled
            third_radar_images = []
            if third_radar_enabled and third_radar_product_id:
                logging.info(f"Third radar enabled: {third_radar_product_id}")

                # Get all matching files for third radar
                all_third_files = [file for file in ftp.nlst()
                                   if file.startswith(third_radar_product_id)
                                   and file.endswith('.png')]

                # Sort by timestamp
                sorted_third_files = sorted(all_third_files, key=self.get_timestamp)

                # Get the last 5 (most recent) radar images
                third_files = sorted_third_files[-5:]

                logging.info(f"Found {len(all_third_files)} total files for third radar")
                logging.info(f"Selected most recent 5: {[f.split('.')[2] for f in third_files]}")

                # Download third radar images
                for file in third_files:
                    logging.debug(f"Processing third radar {file}")
                    file_obj = io.BytesIO()
                    try:
                        ftp.retrbinary('RETR ' + file, file_obj.write)
                        file_obj.seek(0)
                        image = Image.open(file_obj).convert('RGBA')

                        # Process third radar image: remove copyright and timestamp
                        image = self.remove_copyright(image)
                        image = self.make_timestamp_transparent(image)

                        third_radar_images.append(image)
                        logging.debug(f"Successfully processed third radar {file}")
                    except ftplib.all_errors as e:
                        logging.error(f"Error downloading third radar {file}: {e}")
                        third_radar_images.append(None)  # Placeholder for failed download

                # Calculate offset for third radar positioning
                if third_radar_images:
                    third_offset_x, third_offset_y = self.calculate_radar_offset(product_id, third_radar_product_id)
                    logging.info(f"Third radar will be offset by ({third_offset_x}, {third_offset_y}) pixels")

            # Download and composite the primary radar images
            for i, file in enumerate(files):
                logging.debug(f"Processing primary radar {file}")
                file_obj = io.BytesIO()
                try:
                    ftp.retrbinary('RETR ' + file, file_obj.write)
                    file_obj.seek(0)
                    primary_image = Image.open(file_obj).convert('RGBA')

                    # Start with base image (maintains original size)
                    frame = base_image.copy()

                    # If third radar is enabled, check for overlap and composite if needed
                    # Third radar goes first (bottom layer)
                    if third_radar_enabled and third_radar_images and i < len(third_radar_images):
                        third_image = third_radar_images[i]

                        if third_image is not None:
                            # Check if third radar overlaps with primary radar
                            # Primary radar: (0, 0) to (512, 512)
                            # Third radar: (third_offset_x, third_offset_y) to (third_offset_x + 512, third_offset_y + 512)
                            RADAR_SIZE = 512

                            # Rectangles overlap if they intersect
                            overlaps = (
                                third_offset_x < RADAR_SIZE and (third_offset_x + RADAR_SIZE) > 0 and
                                third_offset_y < RADAR_SIZE and (third_offset_y + RADAR_SIZE) > 0
                            )

                            if overlaps:
                                # Paste third radar first (it should be at the bottom)
                                # PIL will automatically clip if it extends beyond canvas
                                frame.paste(third_image, (third_offset_x, third_offset_y), third_image)
                                logging.debug(f"Pasted third radar at ({third_offset_x}, {third_offset_y}) - overlaps with primary")
                            else:
                                logging.warning(f"Third radar at offset ({third_offset_x}, {third_offset_y}) does not overlap with primary radar - skipping")

                    # If second radar is enabled, check for overlap and composite if needed
                    # Second radar goes on top of third radar (middle layer)
                    if second_radar_enabled and second_radar_images and i < len(second_radar_images):
                        second_image = second_radar_images[i]

                        if second_image is not None:
                            # Check if second radar overlaps with primary radar
                            # Primary radar: (0, 0) to (512, 512)
                            # Second radar: (offset_x, offset_y) to (offset_x + 512, offset_y + 512)
                            RADAR_SIZE = 512

                            # Rectangles overlap if they intersect
                            overlaps = (
                                offset_x < RADAR_SIZE and (offset_x + RADAR_SIZE) > 0 and
                                offset_y < RADAR_SIZE and (offset_y + RADAR_SIZE) > 0
                            )

                            if overlaps:
                                # Paste second radar (it should be below primary but above third)
                                # PIL will automatically clip if it extends beyond canvas
                                frame.paste(second_image, (offset_x, offset_y), second_image)
                                logging.debug(f"Pasted second radar at ({offset_x}, {offset_y}) - overlaps with primary")
                            else:
                                logging.warning(f"Second radar at offset ({offset_x}, {offset_y}) does not overlap with primary radar - skipping")

                    # Paste primary radar on top (always at 0, 0)
                    frame.paste(primary_image, (0, 0), primary_image)

                    # Re-paste legend area on top to ensure it's always visible
                    # This prevents second radar from obscuring the legend
                    if legend_area is not None:
                        legend_y = base_height - legend_height
                        frame.paste(legend_area, (0, legend_y), legend_area)
                        logging.debug(f"Re-pasted legend area at bottom")

                    self.frames.append(frame)
                    logging.debug(f"Successfully processed {file}")
                except ftplib.all_errors as e:
                    logging.error(f"Error downloading {file}: {e}")

            ftp.quit()
            logging.info("Disconnected from FTP server")
            
            if not self.frames:
                logging.error("No frames were processed")
                return False
            
            # Save individual PNG images (without house marker)
            for i, img in enumerate(self.frames):
                filename = f"image_{i+1}.png"
                filepath = os.path.join(self.config['output_directory'], filename)
                img.save(filepath)
                self.saved_filenames.append(filename)
                logging.debug(f"Saved {filepath}")

            logging.info(f"Saved {len(self.saved_filenames)} PNG images")

            # Create GIF frames with house marker (if enabled)
            gif_frames = []
            if house_icon is not None:
                logging.info("Adding house markers to GIF frames only")
                for frame in self.frames:
                    gif_frame = frame.copy()
                    gif_frame = self.add_house_marker(gif_frame, house_icon)
                    gif_frames.append(gif_frame)
            else:
                gif_frames = self.frames

            # Save animated GIF
            gif_filepath = os.path.join(
                self.config['output_directory'],
                self.config['animated_gif_filename']
            )

            # Create duration list with longer pause on last frame
            num_frames = len(gif_frames)
            frame_durations = [self.config['gif_duration']] * num_frames
            if num_frames > 0:
                frame_durations[-1] = self.config['gif_last_frame_duration']
                logging.debug(f"GIF frame durations: {frame_durations}")

            gif_frames[0].save(
                gif_filepath,
                save_all=True,
                append_images=gif_frames[1:],
                duration=frame_durations,
                loop=self.config['gif_loop'],
                optimize=False
            )
            self.saved_filenames.append(self.config['animated_gif_filename'])
            logging.info(f"Saved animated GIF: {gif_filepath} ({num_frames} frames, last frame pauses for {self.config['gif_last_frame_duration']}ms)")
            
            # Extract timestamp from last radar file
            timestamp_content = self.parse_timestamp(files[-1]) if files else None

            # Write timestamp file locally
            if timestamp_content:
                timestamp_filepath = os.path.join(
                    self.config['output_directory'],
                    self.config['timestamp_filename']
                )
                try:
                    with open(timestamp_filepath, 'w') as f:
                        f.write(timestamp_content)
                    logging.info(f"Wrote timestamp file: {timestamp_filepath}")
                except Exception as e:
                    logging.error(f"Failed to write timestamp file: {e}")

            # Transfer to SMB share (only in non-addon mode)
            if not self.config.get('addon_mode', False):
                self.transfer_to_smb(timestamp_content)
            else:
                logging.info(f"Files saved to {self.config['output_directory']}")

            return True
            
        except ftplib.all_errors as e:
            logging.error(f"FTP Error: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def transfer_to_smb(self, timestamp_content):
        """Transfer files to SMB share (deprecated - only for backward compatibility)"""
        if not self.saved_filenames:
            logging.warning("No files to transfer")
            return

        try:
            # Import smbclient only when needed (for backward compatibility)
            try:
                import smbclient
            except ImportError:
                logging.error("SMB transfer requires 'smbprotocol' package. Install with: pip install smbprotocol")
                return

            # Configure SMB client
            smbclient.ClientConfig(
                username=self.config['smb_username'],
                password=self.config['smb_password']
            )

            # Build SMB destination path
            smb_destination_path = (
                f"//{self.config['smb_server']}/{self.config['smb_share']}"
                f"{self.config['smb_remote_path']}"
            )

            # Create destination directory
            try:
                smbclient.makedirs(smb_destination_path, exist_ok=True)
            except Exception as e:
                logging.warning(f"Could not create directory: {e}")

            # Transfer each saved file
            for file_name in self.saved_filenames:
                local_file_path = os.path.join(self.config['output_directory'], file_name)
                smb_file_path = f"{smb_destination_path}/{file_name}"

                logging.debug(f"Transferring {file_name}...")
                try:
                    with open(local_file_path, 'rb') as local_file:
                        with smbclient.open_file(smb_file_path, mode="wb") as smb_file:
                            smb_file.write(local_file.read())
                    logging.debug(f"Successfully transferred {file_name}")
                except Exception as e:
                    logging.error(f"Failed to transfer {file_name}: {e}")

            logging.info(f"Transferred {len(self.saved_filenames)} files to SMB share")

            # Write timestamp file
            if timestamp_content:
                timestamp_file_path = f"{smb_destination_path}/{self.config['timestamp_filename']}"
                try:
                    with smbclient.open_file(timestamp_file_path, mode="w") as timestamp_file:
                        timestamp_file.write(timestamp_content)
                    logging.info(f"Successfully wrote timestamp file")
                except Exception as e:
                    logging.error(f"Failed to write timestamp file: {e}")

        except Exception as e:
            logging.error(f"Transfer error: {e}")
            try:
                import smbclient
                smbclient.reset_connection_cache()
            except:
                pass


async def main():
    """Main application entry point with continuous scheduling"""
    
    # Load configuration
    config = Config.load()
    
    # Setup logging
    log_level = config['log_level']
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        log_level = 'INFO'
        logging.warning(f"Invalid log level '{log_level}'; using INFO")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s: %(message)s',
        stream=sys.stdout,
        force=True
    )
    
    # Make stdout unbuffered
    sys.stdout.reconfigure(line_buffering=True)
    
    logging.info(f'=== Radar Downloader version {VERSION} started ===')
    if config.get('addon_mode', False):
        logging.info('Running in Home Assistant addon mode')
    logging.info(f'Product ID: {config["product_id"]}')
    logging.info(f'Timezone: {config["timezone"]}')
    logging.info(f'Output directory: {config["output_directory"]}')
    
    if config['scheduler_enabled']:
        logging.info(f'Scheduler enabled: Update interval = {config["update_interval"]} seconds')
    else:
        logging.info('Scheduler disabled: Running once and exiting')
    
    # Initialize processor
    processor = RadarProcessor(config)
    
    # Run continuously or once
    if config['scheduler_enabled']:
        run_count = 0
        while True:
            run_count += 1
            logging.info(f'=== Starting radar image processing (run #{run_count}) ===')
            
            try:
                success = processor.process_images()
                
                if success:
                    logging.info('Radar processing completed successfully')
                    sleep_time = config['update_interval']
                else:
                    logging.error('Radar processing failed')
                    if config['retry_on_error']:
                        sleep_time = config['retry_interval']
                        logging.info(f'Will retry in {sleep_time} seconds')
                    else:
                        sleep_time = config['update_interval']
                
                logging.info(f'Next update in {sleep_time} seconds ({sleep_time/60:.1f} minutes)')
                await asyncio.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logging.info('Shutdown requested')
                break
            except Exception as e:
                logging.error(f'Unexpected error in main loop: {e}')
                import traceback
                traceback.print_exc()
                
                if config['retry_on_error']:
                    sleep_time = config['retry_interval']
                    logging.info(f'Retrying in {sleep_time} seconds')
                    await asyncio.sleep(sleep_time)
                else:
                    break
    else:
        # Run once and exit
        logging.info('Running single processing cycle')
        processor.process_images()
        logging.info('Processing complete, exiting')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Application stopped by user')
    except Exception as e:
        logging.error(f'Fatal error: {e}')
        sys.exit(1)