# Changelog

All notable changes to this project will be documented in this file.

## [1.0.7] - 2025-12-07

### Fixed
- **Offline Radar Handling**: Addon now gracefully handles situations where one or more radars are offline
  - Implements timestamp-based alignment across all radar sources (primary, secondary, tertiary)
  - Creates frames using available radar data even when primary radar is offline
  - Generates frames with only available radar overlays when some radars have missing timestamps
  - Base map background is always shown, even when radar data is missing
  - System continues to function as long as at least one radar source has data

### Changed
- Radar images are now downloaded into timestamp-keyed dictionaries for better alignment
- Frame generation uses unified timeline from all available radars
- Timestamp file now uses latest timestamp from any available radar (not just primary)
- Enhanced logging shows offline radar detection and timestamp alignment status
- Partial data availability is clearly logged with warnings for specific timestamps

### Technical
- Refactored radar download logic to support timestamp alignment
- Replaced array-based processing with dictionary-based approach keyed by timestamps
- Collects unique timestamps from all radars and processes most recent 5
- Each frame is created by checking which radars have data for that timestamp

## [1.0.6] - 2025-12-05

### Added
- **OpenStreetMap Background Support**: New option to use OpenStreetMap as radar background instead of BoM backgrounds
  - Higher resolution backgrounds (1024×1024 downsampled to 512×512 for improved clarity)
  - Automatic zoom level optimization based on radar range (512km/256km/128km/64km)
  - Persistent tile caching with 30-day expiry for fast subsequent runs
  - Automatic fallback to BoM backgrounds if tile download fails
- New `background_type` configuration option with choices: "bom" (default) or "openstreetmap"
- MapTileProvider class for efficient tile fetching and caching
- Tile cache directory created automatically in output path (`tile_cache/`)

### Changed
- Refactored base image creation into separate methods for better code organization
- Split `create_base_image()` into `create_bom_base_image()` and OpenStreetMap logic
- Both PNG frames and GIF now use the selected background type
- BoM layer options (catchments, topography, locations, range) only apply when using BoM backgrounds

### Technical
- Added `urllib.request` and `urllib.error` for tile downloads (no new dependencies, stdlib only)
- Implemented Web Mercator projection calculations for lat/lon to tile coordinate conversion
- Added automatic tile stitching and sub-tile precision centering
- Respects OpenStreetMap tile usage policy with proper User-Agent headers

## [1.0.5] - 2025-12-05

### Fixed
- Removed broken http://www.bom.gov.au/australia/radar/ URL references
- Fixed RADARS.md links to use full GitHub URLs for external access
- RADARS.md links now open in new browser tab/window (using target="_blank")
- Documentation now correctly directs users to RADARS.md and Quick Reference table

### Changed
- Updated DOCS.md with comprehensive Home Assistant setup instructions
- Added detailed Local File camera integration setup steps
- Added Picture Glance card configuration examples for dashboard
- Updated README.md with improved radar setup instructions
- Improved guidance for finding radar product IDs

### Added
- GitHub issue templates for bug reports and feature requests
- Standardized issue reporting with configuration and log sections
- Feature request template for community enhancements

### Removed
- Cleaned up temporary __pycache__ directory

## [1.0.4] - 2025-12-05

### Changed
- Replaced layers array with individual boolean toggles for better UI experience
- Background layer is now always included (not user-editable)
- Added support for up to 4 layers: background (always on), catchments, topography, locations, and range
- Each optional layer can now be toggled independently via checkboxes in the UI

### Fixed
- Layer configuration now provides a clearer, more intuitive interface
- Users can easily select which radar layers to display without editing arrays

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
