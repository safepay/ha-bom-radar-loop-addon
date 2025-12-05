# Changelog

All notable changes to this project will be documented in this file.

## [1.0.4] - 2025-12-05

### Changed
- Converted layers from array field to individual boolean toggles for each layer
- Renamed config fields for better readability in UI:
  - `residential_location_enabled` → `show_home_marker`
  - `residential_latitude` → `home_latitude`
  - `residential_longitude` → `home_longitude`
  - `second_radar_enabled` → `enable_second_radar`
  - `second_radar_product_id` → `second_radar_id`
  - `third_radar_enabled` → `enable_third_radar`
  - `third_radar_product_id` → `third_radar_id`

### Fixed
- Fixed issue where layers could not be added back after removal
- Each layer now has its own checkbox toggle that can be independently enabled/disabled
- Default layers: background and locations enabled

## [1.0.3] - 2025-12-05

### Fixed
- Simplified layers schema to use ["str"] format for proper multi-select support
- Fixed "does not match regular expression" error when saving configuration

## [1.0.2] - 2025-12-05

### Fixed
- Fixed config.json schema to use correct Home Assistant format
- Layers configuration now properly supports multi-select checkboxes using match() patterns
- Default selections for "background" and "locations" layers maintained

## [1.0.1] - 2025-12-05

### Changed
- Fixed layers configuration to support multi-select checkboxes instead of radio buttons (incorrect format - fixed in 1.0.2)

## [1.0.0] - 2025-01-04

### Added
- Initial release as Home Assistant addon
- Support for Australian BoM radar downloads
- Animated GIF creation with configurable frame rates
- Individual frame export for LLM Vision analysis
- Multiple radar overlay support (up to 3 radars)
- Residential location marker with house icon
- Configurable radar layers (background, locations, catchments, topography)
- Timezone support for timestamps
- Automatic updates via configurable interval
- Direct integration with Home Assistant (no SMB required)
- Comprehensive radar reference guide (RADARS.md)
- Multi-architecture support (amd64, aarch64, armhf, armv7, i386)

### Features
- Downloads latest 5 radar frames from BoM FTP server
- Creates smooth animated radar loops
- Saves individual PNG images for AI analysis
- Geographic positioning of multiple radars
- Customizable GIF animation settings
- Local file storage in /config/www
- Backward compatibility with standalone Docker mode

### Documentation
- Complete installation guide
- Configuration examples
- Troubleshooting section
- Full radar location reference by state
- Dashboard integration examples
