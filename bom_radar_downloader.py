#!/usr/bin/env python3
import io
import ftplib
import smbclient
import os
import sys
import asyncio
import logging
from PIL import Image
from datetime import datetime
from pathlib import Path
import pytz
import yaml

VERSION = '1.0.0'

# Check multiple possible config file locations
CONFIG_PATHS = [
    Path('/app/config.yaml'),
    Path('config.yaml'),
    Path('/config/config.yaml'),
]

CONFIG_FILE = None
for path in CONFIG_PATHS:
    if path.exists():
        CONFIG_FILE = path
        break


class Config:
    """Configuration management"""
    
    @staticmethod
    def load():
        """Load configuration from file with environment variable overrides"""
        if not CONFIG_FILE or not CONFIG_FILE.exists():
            logging.error('No configuration file found!')
            logging.error('Checked paths: ' + ', '.join(str(p) for p in CONFIG_PATHS))
            sys.exit(1)
        
        logging.info(f'Loading configuration from: {CONFIG_FILE}')
        
        with open(CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)
        
        # Allow environment variable overrides
        radar = config.get('radar', {})
        scheduler = config.get('scheduler', {})
        smb = config.get('smb', {})
        output = config.get('output', {})
        gif = config.get('gif', {})
        log_config = config.get('logging', {})
        
        return {
            # Radar settings
            'product_id': os.getenv('PRODUCT_ID', radar.get('product_id', 'IDR022')),
            'timezone': os.getenv('TIMEZONE', radar.get('timezone', 'Australia/Melbourne')),
            
            # Scheduler settings
            'scheduler_enabled': os.getenv('SCHEDULER_ENABLED', str(scheduler.get('enabled', True))).lower() == 'true',
            'update_interval': int(os.getenv('UPDATE_INTERVAL', scheduler.get('update_interval', 600))),
            'retry_on_error': scheduler.get('retry_on_error', True),
            'retry_interval': int(os.getenv('RETRY_INTERVAL', scheduler.get('retry_interval', 60))),
            
            # SMB settings
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
            'gif_loop': int(os.getenv('GIF_LOOP', gif.get('loop', 0))),
            
            # Logging
            'log_level': os.getenv('LOG_LEVEL', log_config.get('level', 'INFO')).upper(),
        }


class RadarProcessor:
    """Processes radar images from BOM FTP"""
    
    def __init__(self, config):
        self.config = config
        self.frames = []
        self.saved_filenames = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.config['output_directory'], exist_ok=True)
    
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
        
        try:
            # Load the legend image as the base
            base_image = self.load_legend()
            
            if base_image is None:
                logging.error("Cannot proceed without legend image")
                return False
            
            # Connect to FTP server
            logging.info("Connecting to BOM FTP server...")
            ftp = ftplib.FTP('ftp.bom.gov.au')
            ftp.login()
            
            # Build composite layers on top of the legend base
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
            
            logging.info(f"Base image with all layers size: {base_image.size}")
            
            # Get radar images
            ftp.cwd('/anon/gen/radar/')
            
            # Get all matching radar files
            all_files = [file for file in ftp.nlst()
                         if file.startswith(product_id)
                         and file.endswith('.png')]
            
            # Sort by timestamp
            sorted_files = sorted(all_files, key=self.get_timestamp)
            
            # Get the last 5 (most recent) radar images
            files = sorted_files[-5:]
            
            logging.info(f"Found {len(all_files)} total radar files")
            logging.info(f"Selected most recent 5: {[f.split('.')[2] for f in files]}")
            
            # Download and composite the radar images
            for file in files:
                logging.debug(f"Processing {file}")
                file_obj = io.BytesIO()
                try:
                    ftp.retrbinary('RETR ' + file, file_obj.write)
                    file_obj.seek(0)
                    image = Image.open(file_obj).convert('RGBA')
                    frame = base_image.copy()
                    frame.paste(image, (0, 0), image)
                    self.frames.append(frame)
                    logging.debug(f"Successfully processed {file}")
                except ftplib.all_errors as e:
                    logging.error(f"Error downloading {file}: {e}")
            
            ftp.quit()
            logging.info("Disconnected from FTP server")
            
            if not self.frames:
                logging.error("No frames were processed")
                return False
            
            # Save individual PNG images
            for i, img in enumerate(self.frames):
                filename = f"image_{i+1}.png"
                filepath = os.path.join(self.config['output_directory'], filename)
                img.save(filepath)
                self.saved_filenames.append(filename)
                logging.debug(f"Saved {filepath}")
            
            logging.info(f"Saved {len(self.saved_filenames)} PNG images")
            
            # Save animated GIF
            gif_filepath = os.path.join(
                self.config['output_directory'],
                self.config['animated_gif_filename']
            )
            self.frames[0].save(
                gif_filepath,
                save_all=True,
                append_images=self.frames[1:],
                duration=self.config['gif_duration'],
                loop=self.config['gif_loop'],
                optimize=False
            )
            self.saved_filenames.append(self.config['animated_gif_filename'])
            logging.info(f"Saved animated GIF: {gif_filepath}")
            
            # Extract timestamp from last radar file
            timestamp_content = self.parse_timestamp(files[-1]) if files else None
            
            # Transfer to SMB share
            self.transfer_to_smb(timestamp_content)
            
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
        """Transfer files to SMB share"""
        if not self.saved_filenames:
            logging.warning("No files to transfer")
            return
        
        try:
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
                    
        except smbclient.exceptions.SMBException as e:
            logging.error(f"SMB Error: {e}")
        except Exception as e:
            logging.error(f"Transfer error: {e}")
        finally:
            smbclient.reset_connection_cache()


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
    logging.info(f'Configuration loaded from: {CONFIG_FILE}')
    logging.info(f'Product ID: {config["product_id"]}')
    logging.info(f'Timezone: {config["timezone"]}')
    
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