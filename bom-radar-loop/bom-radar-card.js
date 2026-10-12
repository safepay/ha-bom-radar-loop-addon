/*
 * BoM Radar Card — an interactive, pannable weather-radar card for Home Assistant.
 *
 * Companion to the "Australian BoM Radar Loop" addon. Instead of showing a baked
 * GIF loop, this card renders a real slippy map (Leaflet) and overlays the
 * transparent radar frames the addon writes, georeferenced to each radar's true
 * geographic bounds. You can pan and zoom freely across the whole area covered by
 * the chosen radars and scrub/animate through time.
 *
 * Data source: the addon writes `radar_manifest.json` plus transparent frames
 * into /config/www/bom_radar/, served by Home Assistant at /local/bom_radar/.
 *
 * Install: copy this file to /config/www/bom_radar/bom-radar-card.js (the addon
 * does this automatically), then add it as a Lovelace resource of type "module".
 */

// Run-once guard: Home Assistant can evaluate this resource more than once in a
// single frontend session (e.g. after removing and re-adding it, or via a
// cache-busted URL). Wrapping the whole file in a flag-guarded IIFE keeps the
// top-level declarations function-scoped and ensures the card is only defined
// and listed once, with no "already declared" / "already defined" errors.
(function () {
  if (window.__bomRadarCardInit) return;
  window.__bomRadarCardInit = true;

const LEAFLET_VERSION = "1.9.4";
const LEAFLET_JS = `https://unpkg.com/leaflet@${LEAFLET_VERSION}/dist/leaflet.js`;
const LEAFLET_CSS = `https://unpkg.com/leaflet@${LEAFLET_VERSION}/dist/leaflet.css`;

// Esri ArcGIS basemaps are keyless and permit embedding (note: {z}/{y}/{x}
// order and no {s} subdomains). They are the reliable default because OSM's
// volunteer tile servers block app/embedded use under their usage policy.
const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services";
const BASE_MAPS = {
  esri: {
    url: `${ESRI}/World_Street_Map/MapServer/tile/{z}/{y}/{x}`,
    attribution: "Tiles &copy; Esri",
    maxZoom: 19,
  },
  esri_topo: {
    url: `${ESRI}/World_Topo_Map/MapServer/tile/{z}/{y}/{x}`,
    attribution: "Tiles &copy; Esri",
    maxZoom: 19,
  },
  esri_gray: {
    url: `${ESRI}/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}`,
    attribution: "Tiles &copy; Esri",
    maxZoom: 16,
  },
  satellite: {
    url: `${ESRI}/World_Imagery/MapServer/tile/{z}/{y}/{x}`,
    attribution: "Tiles &copy; Esri",
    maxZoom: 19,
  },
  // OSM and Carto are offered but may be blocked / need a key; use with care.
  osm: {
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap contributors",
    subdomains: "abc",
    maxZoom: 19,
  },
  voyager: {
    url: "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap, &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 20,
  },
  light: {
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap, &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 20,
  },
  dark: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap, &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 20,
  },
};

// Load Leaflet once per page, shared across every instance of the card.
function loadLeaflet() {
  if (window.L) return Promise.resolve(window.L);
  if (window.__bomRadarLeafletPromise) return window.__bomRadarLeafletPromise;

  window.__bomRadarLeafletPromise = new Promise((resolve, reject) => {
    if (!document.querySelector("link[data-bom-radar-leaflet]")) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = LEAFLET_CSS;
      link.setAttribute("data-bom-radar-leaflet", "");
      document.head.appendChild(link);
    }
    const script = document.createElement("script");
    script.src = LEAFLET_JS;
    script.async = true;
    script.onload = () => resolve(window.L);
    script.onerror = () => reject(new Error("Failed to load Leaflet from CDN"));
    document.head.appendChild(script);
  });
  return window.__bomRadarLeafletPromise;
}

class BomRadarCard extends HTMLElement {
  setConfig(config) {
    this._config = Object.assign(
      {
        // title is intentionally NOT defaulted - omitting it from the config
        // means no card header (removing `title:` from YAML removes the header).
        manifest: "/local/bom_radar/radar_manifest.json",
        base_map: "esri",
        height: "420px",
        opacity: 0.85,
        frame_delay: 500,
        last_frame_delay: 1600,
        autoplay: true,
        show_home: true,
        show_legend: true,
        default_zoom: null, // null = fit all radar coverage; a number = open at that zoom
        default_center: "home", // "home" | "radars" - what default_zoom centres on
      },
      config || {}
    );
    this._manifestBase = this._config.manifest.replace(/[^/]*$/, "");
    this._opacity = Number(this._config.opacity);
    this._delay = Number(this._config.frame_delay);
    this._lastDelay = Number(this._config.last_frame_delay);
    // Reflect title/opacity changes live if the card is already built.
    if (this._card) this._card.header = this._config.title || undefined;
    if (this._mapEl) this._mapEl.style.flexBasis = this._config.height;
    // HA normally calls setConfig before attaching, but if the element is
    // already connected (e.g. a reconfigure), build now too.
    if (this.isConnected && !this._built) this._build();
  }

  set hass(hass) {
    // HA sets this on every state change. We use it only to read the home
    // location (hass.config.latitude/longitude) so the card can place the
    // marker itself, independent of the addon's residential_* config.
    this._hass = hass;
    if (this._map) this._updateHomeMarker();
  }

  connectedCallback() {
    if (!this._built) {
      this._build();
    }
  }

  disconnectedCallback() {
    this._stop();
    if (this._refreshTimer) clearInterval(this._refreshTimer);
    if (this._resizeObserver) this._resizeObserver.disconnect();
  }

  async _build() {
    if (!this._config || this._built) return; // Need a config; never build twice.
    this._built = true;

    const card = document.createElement("ha-card");
    card.className = "bom-radar-ha-card";
    if (this._config.title) card.header = this._config.title;
    this._card = card;

    const content = document.createElement("div");
    content.className = "bom-radar-content";

    const mapEl = document.createElement("div");
    mapEl.className = "bom-radar-map";
    // flex-basis is the masonry height; in a sections grid the map grows/shrinks
    // to fill the resized cell (floored by min-height in the CSS below).
    mapEl.style.flexBasis = this._config.height;
    mapEl.style.width = "100%";

    const controls = document.createElement("div");
    controls.className = "bom-radar-controls";
    controls.innerHTML = `
      <button class="bom-radar-play" title="Play/pause" aria-label="Play or pause">&#9654;</button>
      <input class="bom-radar-slider" type="range" min="0" max="0" value="0" step="1" aria-label="Radar frame" />
      <span class="bom-radar-time">--:--</span>
    `;

    const legend = document.createElement("div");
    legend.className = "bom-radar-legend";
    legend.style.display = "none";
    legend.innerHTML = `
      <span class="bom-radar-legend-cap">Light</span>
      <img class="bom-radar-legend-bar" alt="Rainfall intensity" />
      <span class="bom-radar-legend-cap">Heavy</span>
    `;

    const style = document.createElement("style");
    style.textContent = `
      /* Fill the card so the map resizes with the (sections) grid cell, while
         flex-basis (set inline from the height option) is the masonry height. */
      bom-radar-card { display: block; height: 100%; }
      .bom-radar-ha-card { height: 100%; display: flex; flex-direction: column; overflow: hidden; }
      .bom-radar-content { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; padding: 0 0 8px 0; }
      .bom-radar-map { flex: 1 1 auto; min-height: 180px; background: var(--card-background-color, #222); }
      .bom-radar-map .bom-radar-frame { image-rendering: auto; }
      .bom-radar-controls {
        flex: 0 0 auto;
        display: flex; align-items: center; gap: 10px;
        padding: 8px 14px 2px 14px;
      }
      .bom-radar-play {
        flex: 0 0 auto; width: 34px; height: 34px; border-radius: 50%;
        border: none; cursor: pointer; font-size: 14px; line-height: 34px;
        color: var(--text-primary-color, #fff);
        background: var(--primary-color, #03a9f4);
      }
      .bom-radar-slider { flex: 1 1 auto; cursor: pointer; }
      .bom-radar-time {
        flex: 0 0 auto; min-width: 72px; text-align: right;
        font-variant-numeric: tabular-nums;
        color: var(--primary-text-color);
      }
      .bom-radar-legend {
        flex: 0 0 auto; display: flex; align-items: center; gap: 8px;
        margin: 6px 14px 0 14px;
      }
      .bom-radar-legend-bar {
        flex: 1 1 auto; height: 8px; border-radius: 4px; display: block;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,.12);
      }
      .bom-radar-legend-cap {
        flex: 0 0 auto; font-size: 11px; color: var(--secondary-text-color);
      }
      .bom-radar-error { padding: 16px; color: var(--error-color, #db4437); }
      .bom-radar-home {
        width: 18px; height: 18px; border-radius: 50% 50% 50% 0;
        background: var(--primary-color, #03a9f4); border: 2px solid #fff;
        transform: rotate(-45deg); box-shadow: 0 0 4px rgba(0,0,0,.5);
      }

      /* --- Critical Leaflet layout, scoped to this card. Home Assistant
         renders cards inside shadow DOM, so Leaflet's own stylesheet (loaded
         into document.head) does not reach the map - without these rules the
         tiles have no positioning and scatter/drift when you pan. --- */
      .bom-radar-map { overflow: hidden; background: #a0d6f5; font-family: inherit; }
      .bom-radar-map .leaflet-pane,
      .bom-radar-map .leaflet-tile,
      .bom-radar-map .leaflet-marker-icon,
      .bom-radar-map .leaflet-marker-shadow,
      .bom-radar-map .leaflet-tile-container,
      .bom-radar-map .leaflet-pane > svg,
      .bom-radar-map .leaflet-pane > canvas,
      .bom-radar-map .leaflet-zoom-box,
      .bom-radar-map .leaflet-image-layer,
      .bom-radar-map .leaflet-layer { position: absolute; left: 0; top: 0; }
      .bom-radar-map .leaflet-tile { width: 256px; height: 256px; filter: inherit;
        visibility: hidden; -webkit-user-select: none; user-select: none; -webkit-user-drag: none; }
      .bom-radar-map .leaflet-tile-loaded { visibility: inherit; }
      .bom-radar-map .leaflet-tile,
      .bom-radar-map .leaflet-image-layer { max-width: none !important; max-height: none !important; }
      .bom-radar-map .leaflet-pane { z-index: 400; }
      .bom-radar-map .leaflet-tile-pane { z-index: 200; }
      .bom-radar-map .leaflet-overlay-pane { z-index: 400; }
      .bom-radar-map .leaflet-shadow-pane { z-index: 500; }
      .bom-radar-map .leaflet-marker-pane { z-index: 600; }
      .bom-radar-map .leaflet-tooltip-pane { z-index: 650; }
      .bom-radar-map .leaflet-popup-pane { z-index: 700; }
      .bom-radar-map .leaflet-map-pane canvas { z-index: 100; }
      .bom-radar-map .leaflet-map-pane svg { z-index: 200; }
      .bom-radar-map .leaflet-overlay-pane svg { max-width: none !important; max-height: none !important; }
      .bom-radar-map .leaflet-zoom-animated { transform-origin: 0 0; }
      .bom-radar-map .leaflet-zoom-anim .leaflet-zoom-animated {
        transition: transform .25s cubic-bezier(0,0,.25,1); }
      .bom-radar-map .leaflet-zoom-anim .leaflet-tile,
      .bom-radar-map .leaflet-pan-anim .leaflet-tile { transition: none; }
      .bom-radar-map .leaflet-zoom-anim .leaflet-zoom-hide { visibility: hidden; }
      .bom-radar-map .leaflet-control { position: relative; z-index: 800; pointer-events: auto; float: left; clear: both; }
      .bom-radar-map .leaflet-top, .bom-radar-map .leaflet-bottom { position: absolute; z-index: 1000; pointer-events: none; }
      .bom-radar-map .leaflet-top { top: 0; }
      .bom-radar-map .leaflet-bottom { bottom: 0; }
      .bom-radar-map .leaflet-left { left: 0; }
      .bom-radar-map .leaflet-right { right: 0; }
      .bom-radar-map .leaflet-right .leaflet-control { float: right; margin-right: 10px; }
      .bom-radar-map .leaflet-left .leaflet-control { margin-left: 10px; }
      .bom-radar-map .leaflet-top .leaflet-control { margin-top: 10px; }
      .bom-radar-map .leaflet-bottom .leaflet-control { margin-bottom: 10px; }
      .bom-radar-map .leaflet-bar { box-shadow: 0 1px 5px rgba(0,0,0,.4); border-radius: 4px; }
      .bom-radar-map .leaflet-bar a { background: #fff; border-bottom: 1px solid #ccc;
        width: 26px; height: 26px; line-height: 26px; display: block; text-align: center;
        text-decoration: none; color: #000; font: bold 18px 'Lucida Console', Monaco, monospace; }
      .bom-radar-map .leaflet-bar a:hover { background: #f4f4f4; }
      .bom-radar-map .leaflet-bar a:first-child { border-top-left-radius: 4px; border-top-right-radius: 4px; }
      .bom-radar-map .leaflet-bar a:last-child { border-bottom: none; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; }
      .bom-radar-map .leaflet-control-attribution { background: rgba(255,255,255,.7); margin: 0; padding: 0 5px;
        color: #333; font: 11px/1.5 "Helvetica Neue", Arial, Helvetica, sans-serif; }
      .bom-radar-map .leaflet-control-attribution a { color: #0078A8; text-decoration: none; }
    `;

    content.appendChild(mapEl);
    content.appendChild(controls);
    content.appendChild(legend);
    card.appendChild(style);
    card.appendChild(content);
    this.appendChild(card);

    this._mapEl = mapEl;
    this._legendEl = legend;
    this._legendImg = legend.querySelector(".bom-radar-legend-bar");
    this._playBtn = controls.querySelector(".bom-radar-play");
    this._slider = controls.querySelector(".bom-radar-slider");
    this._timeLabel = controls.querySelector(".bom-radar-time");

    this._playBtn.addEventListener("click", () => this._togglePlay());
    this._slider.addEventListener("input", () => {
      this._stop();
      this._showIndex(Number(this._slider.value));
    });

    try {
      this._L = await loadLeaflet();
    } catch (e) {
      this._showError("Could not load the map library (Leaflet). Check your internet connection.");
      return;
    }

    this._initMap();
    await this._loadManifest(true);

    // Re-fetch the manifest on the addon's cadence to pick up new frames.
    const refreshMs = Math.max((this._manifest?.update_interval || 600) * 1000, 60000);
    this._refreshTimer = setInterval(() => this._loadManifest(false), refreshMs);

    // Leaflet needs a correctly-sized container, but HA often lays the card out
    // AFTER the map is created (especially in the card-editor preview), so the
    // map can init at 0x0 - loading a single tile and fitting to nothing. On
    // every resize, fix the tile grid and apply any fit that was waiting for a
    // real size.
    this._resizeObserver = new ResizeObserver(() => {
      if (!this._map) return;
      this._map.invalidateSize();
      if (this._needsFit) this._applyFit();
    });
    this._resizeObserver.observe(this._mapEl);

    // Belt-and-braces nudge in case the observer's first callback predates layout.
    setTimeout(() => {
      if (this._map) {
        this._map.invalidateSize();
        if (this._needsFit) this._applyFit();
      }
    }, 250);
  }

  // Centre/zoom on the radar coverage, but only once the container has a real
  // size (otherwise Leaflet fits against 0 pixels and lands on the fallback
  // view). Until then this is a no-op and the resize observer retries.
  _applyFit() {
    if (!this._map || !this._needsFit || !this._fitBounds || !this._fitBounds.length) return;
    const el = this._mapEl;
    if (!el || el.offsetWidth === 0 || el.offsetHeight === 0) return; // wait for a size
    this._map.invalidateSize();
    const dz = this._config.default_zoom;
    if (dz != null) {
      const home = this._homeLatLon();
      const center =
        this._config.default_center === "home" && home
          ? home
          : this._L.latLngBounds(this._fitBounds).getCenter();
      this._map.setView(center, Number(dz));
    } else {
      this._map.fitBounds(this._fitBounds, { padding: [10, 10] });
    }
    this._needsFit = false;
    this._selectLevels();
    this._rebuildTimeline();
    if (this._timestamps && this._timestamps.length) {
      this._showIndex(this._currentIndex ?? this._timestamps.length - 1);
      // Start the animation automatically once the map is sized and has frames.
      if (this._config.autoplay) this._play();
    }
  }

  _initMap() {
    const L = this._L;
    this._map = L.map(this._mapEl, {
      zoomControl: true,
      attributionControl: true,
      scrollWheelZoom: true,
    });
    const base = BASE_MAPS[this._config.base_map] || BASE_MAPS.esri;
    const tileOpts = { attribution: base.attribution, maxZoom: base.maxZoom };
    if (base.subdomains) tileOpts.subdomains = base.subdomains;
    L.tileLayer(base.url, tileOpts).addTo(this._map);

    // Sensible default view until the manifest's bounds load.
    this._map.setView([-25.0, 134.0], 4);

    // When the user zooms or pans, re-pick the best range level per station so
    // zooming in reveals finer detail (and rural homes fall back to a wider
    // range that still reaches them).
    this._map.on("zoomend moveend", () => {
      if (this._selectLevels()) {
        this._rebuildTimeline();
        this._showIndex(this._currentIndex ?? 0);
      }
    });
  }

  _resolveUrl(url) {
    if (/^https?:\/\//.test(url) || url.startsWith("/")) return url;
    return this._manifestBase + url;
  }

  async _loadManifest(firstLoad) {
    let manifest;
    try {
      const res = await fetch(`${this._config.manifest}?t=${Date.now()}`, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      manifest = await res.json();
    } catch (e) {
      if (firstLoad) {
        this._showError(
          `Could not load radar manifest from ${this._config.manifest}. ` +
            `Is the addon running and writing to that folder?`
        );
      }
      return;
    }

    // Skip a full rebuild if nothing changed (avoids disrupting playback).
    const latest = manifest.timestamps?.[manifest.timestamps.length - 1];
    if (!firstLoad && latest === this._latestTimestamp) return;
    this._latestTimestamp = latest;
    this._manifest = manifest;

    this._rebuildOverlays(firstLoad);
  }

  _rebuildOverlays(fitView) {
    const L = this._L;
    const wasPlaying = this._playing;
    this._stop();

    // Tear down any previous overlays (the home marker is managed separately).
    if (this._stations) {
      this._stations.forEach((st) =>
        st.levels.forEach((lv) =>
          Object.values(lv.framesByTs).forEach((o) => this._map.removeLayer(o))
        )
      );
    }

    this._stations = [];
    this._labels = {};
    const allBounds = [];

    (this._manifest.radars || []).forEach((radar) => {
      // Order levels widest-range first so the fallback (index 0) is the widest.
      const levelsSrc = (radar.levels || []).slice().sort((a, b) => b.range_km - a.range_km);
      const levels = [];
      levelsSrc.forEach((lvl) => {
        const b = lvl.bounds;
        const latLngBounds = L.latLngBounds([b.south, b.west], [b.north, b.east]);
        allBounds.push([b.south, b.west], [b.north, b.east]);
        const framesByTs = {};
        (lvl.frames || []).forEach((fr) => {
          const overlay = L.imageOverlay(this._resolveUrl(fr.url), latLngBounds, {
            opacity: 0,
            interactive: false,
            className: "bom-radar-frame",
          });
          overlay.addTo(this._map);
          framesByTs[fr.timestamp] = overlay;
          this._labels[fr.timestamp] = fr.time_local || fr.timestamp;
        });
        if (Object.keys(framesByTs).length) {
          levels.push({
            range_km: lvl.range_km,
            native_zoom: lvl.native_zoom,
            bounds: latLngBounds,
            framesByTs,
            // This level's own frame timestamps, sorted. Different ranges are
            // captured at different minute offsets, so a level will not have a
            // frame at every global timeline step.
            sortedTs: Object.keys(framesByTs).sort(),
          });
        }
      });
      if (levels.length) this._stations.push({ role: radar.role, levels, active: 0 });
    });

    this._globalTimestamps = this._manifest.timestamps || [];

    // Home marker (resolved from HA first, addon manifest as fallback).
    this._updateHomeMarker();

    // Legend.
    if (this._config.show_legend && this._manifest.legend_url && this._legendImg) {
      this._legendImg.src = this._resolveUrl(this._manifest.legend_url) + `?t=${Date.now()}`;
      this._legendEl.style.display = "flex";
    } else {
      this._legendEl.style.display = "none";
    }

    // Remember the coverage to fit; _applyFit() runs it once the map has a size.
    this._fitBounds = allBounds;
    this._needsFit = fitView && allBounds.length > 0;

    this._currentIndex = null;
    this._selectLevels();
    this._rebuildTimeline();
    this._applyFit();

    if (this._timestamps.length && this._stations.length) {
      this._showIndex(this._timestamps.length - 1); // Start on the newest frame.
      if (wasPlaying || (fitView && this._config.autoplay)) this._play();
    } else {
      this._timeLabel.textContent = "No data";
    }
  }

  // The animation timeline is the active (primary) range's own frames, so every
  // step shows a distinct image. Different ranges are captured at different
  // minute offsets, so animating over the merged union would repeat/blank
  // frames. Rebuilt whenever the active level changes (e.g. on zoom).
  _rebuildTimeline() {
    let tl = null;
    const stations = this._stations || [];
    const primary = stations.find((s) => s.role === "primary") || stations[0];
    if (primary && primary.active >= 0 && primary.levels[primary.active]) {
      tl = primary.levels[primary.active].sortedTs;
    }
    if (!tl || !tl.length) tl = this._globalTimestamps || [];
    this._timestamps = tl;
    this._slider.max = Math.max(0, tl.length - 1);
    if (this._currentIndex == null || this._currentIndex > tl.length - 1) {
      this._currentIndex = tl.length - 1; // default to the newest frame
    }
    this._slider.value = this._currentIndex;
  }

  // Choose, per station, the finest range level whose coverage still intersects
  // the current viewport. This gives home-area detail when zoomed in, while a
  // rural home outside the small radii falls back to the widest range that
  // reaches it. Returns true if any station's active level changed.
  _selectLevels() {
    if (!this._stations || !this._map) return false;
    const view = this._map.getBounds();
    const zoom = this._map.getZoom();
    let changed = false;

    // First pass: each station's best level given the current view/zoom.
    const desired = this._stations.map((st) => {
      // Candidate levels are those actually visible in the current view.
      const visible = st.levels.filter((lv) => view.intersects(lv.bounds));
      if (!visible.length) return -1; // panned fully out of view
      const atOrBelow = visible.filter((lv) => lv.native_zoom <= zoom);
      // Zoomed in enough for one or more levels: use the finest. Otherwise
      // (zoomed out past all levels) show the widest visible for context.
      const chosen = atOrBelow.length
        ? atOrBelow.reduce((best, lv) => (lv.native_zoom > best.native_zoom ? lv : best))
        : visible.reduce((best, lv) => (lv.native_zoom < best.native_zoom ? lv : best));
      return st.levels.indexOf(chosen);
    });

    // Second pass: show a single resolution at a time. With multiple overlapping
    // radars a zoomed-in view would otherwise mix one radar's fine detail with
    // another's coarse blocks in the same place. Find the finest range in view
    // and hide any radar coarser than it. Zoomed out, all radars are on the same
    // wide range so none are hidden (full coverage); over a rural area where only
    // a coarse radar reaches, that coarse one is the finest present, so it shows.
    const activeZooms = desired.map((d, i) =>
      d >= 0 ? this._stations[i].levels[d].native_zoom : -Infinity
    );
    const finest = Math.max(...activeZooms);
    if (finest > -Infinity) {
      this._stations.forEach((st, i) => {
        if (desired[i] >= 0 && st.levels[desired[i]].native_zoom < finest) desired[i] = -1;
      });
    }

    this._stations.forEach((st, i) => {
      if (desired[i] !== st.active) {
        st.active = desired[i];
        changed = true;
      }
    });
    return changed;
  }

  _homeLatLon() {
    // Prefer Home Assistant's own configured home location.
    const cfg = this._hass && this._hass.config;
    if (cfg && typeof cfg.latitude === "number" && typeof cfg.longitude === "number") {
      return [cfg.latitude, cfg.longitude];
    }
    // Fall back to the addon's residential marker from the manifest.
    const home = this._manifest && this._manifest.home;
    if (home && home.enabled && home.lat != null && home.lon != null) {
      return [home.lat, home.lon];
    }
    return null;
  }

  _updateHomeMarker() {
    if (!this._map || !this._L) return;
    const pos = this._config.show_home ? this._homeLatLon() : null;
    if (!pos) {
      if (this._homeMarker) {
        this._map.removeLayer(this._homeMarker);
        this._homeMarker = null;
      }
      return;
    }
    if (this._homeMarker) {
      this._homeMarker.setLatLng(pos); // Move the existing marker (idempotent).
      return;
    }
    const icon = this._L.divIcon({
      className: "",
      html: '<div class="bom-radar-home"></div>',
      iconSize: [18, 18],
      iconAnchor: [9, 18],
    });
    this._homeMarker = this._L.marker(pos, { icon, interactive: false }).addTo(this._map);
  }

  _showIndex(i) {
    if (!this._timestamps || !this._timestamps.length || !this._stations) return;
    i = Math.max(0, Math.min(i, this._timestamps.length - 1));
    const ts = this._timestamps[i];

    let shownTs = ts;
    this._stations.forEach((st) => {
      st.levels.forEach((lv, idx) => {
        const active = idx === st.active;
        // Hold-last: show this level's most recent frame at or before the
        // current step (its earliest if none yet), rather than blanking when
        // the level has no frame at this exact timestamp. Without this the
        // animation flickers on/off as the merged timeline steps through
        // timestamps that only some ranges captured.
        let frameTs = null;
        if (active) {
          for (const t of lv.sortedTs) {
            if (t <= ts) frameTs = t;
          }
          if (frameTs === null) frameTs = lv.sortedTs[0];
          if (st.role !== "secondary" && st.role !== "tertiary") shownTs = frameTs;
        }
        Object.entries(lv.framesByTs).forEach(([t, overlay]) => {
          overlay.setOpacity(active && t === frameTs ? this._opacity : 0);
        });
      });
    });

    this._currentIndex = i;
    this._slider.value = i;
    this._timeLabel.textContent = this._labels[shownTs] || this._labels[ts] || ts;
  }

  _togglePlay() {
    if (this._playing) this._stop();
    else this._play();
  }

  _play() {
    if (this._playing) return; // already running - keep a single timer
    if (!this._timestamps || this._timestamps.length < 2) return;
    this._playing = true;
    this._playBtn.innerHTML = "&#10073;&#10073;"; // pause glyph
    const step = () => {
      if (!this._playing) return;
      let next = this._currentIndex + 1;
      if (next >= this._timestamps.length) next = 0;
      this._showIndex(next);
      const onLast = next === this._timestamps.length - 1;
      this._timer = setTimeout(step, onLast ? this._lastDelay : this._delay);
    };
    this._timer = setTimeout(step, this._delay);
  }

  _stop() {
    this._playing = false;
    if (this._timer) clearTimeout(this._timer);
    if (this._playBtn) this._playBtn.innerHTML = "&#9654;"; // play glyph
  }

  _showError(msg) {
    const card = this.querySelector("ha-card") || this;
    const err = document.createElement("div");
    err.className = "bom-radar-error";
    err.textContent = msg;
    card.appendChild(err);
  }

  getCardSize() {
    const h = parseInt(this._config?.height, 10) || 420;
    return Math.ceil(h / 50) + 1;
  }

  // Sections dashboard: make the card resizable in both dimensions (drag the
  // grid handles). Rows set the height, columns the width, each clamped.
  getGridOptions() {
    const rows = Math.max(3, Math.round((parseInt(this._config?.height, 10) || 420) / 56));
    return {
      rows,
      min_rows: 3,
      max_rows: 20,
      columns: 12,
      min_columns: 6,
      max_columns: 12,
    };
  }

  // Older HA layout API (pre-getGridOptions); harmless where unused.
  getLayoutOptions() {
    const opts = this.getGridOptions();
    return {
      grid_rows: opts.rows,
      grid_min_rows: opts.min_rows,
      grid_max_rows: opts.max_rows,
      grid_columns: 4,
      grid_min_columns: 2,
      grid_max_columns: 4,
    };
  }

  static getConfigElement() {
    return document.createElement("bom-radar-card-editor");
  }

  static getStubConfig() {
    return { manifest: "/local/bom_radar/radar_manifest.json" };
  }
}

// Visual configuration editor shown in the Lovelace card editor. Plain inputs
// that emit `config-changed` so the card is no longer YAML-only.
class BomRadarCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = Object.assign({}, config);
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  _emit() {
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this._config },
        bubbles: true,
        composed: true,
      })
    );
  }

  _render() {
    if (!this._config) return;
    const c = this._config;
    const esc = (v) => (v == null ? "" : String(v)).replace(/"/g, "&quot;");
    const sel = (v, opt) => (v === opt ? " selected" : "");
    this.innerHTML = `
      <style>
        .bre { padding: 12px 8px; display: flex; flex-direction: column; gap: 12px; }
        .bre .row { display: flex; align-items: center; gap: 12px; }
        .bre label { flex: 1 1 auto; color: var(--primary-text-color); }
        .bre input, .bre select { flex: 0 0 auto; }
        .bre input[type="text"], .bre input[type="number"], .bre select {
          min-width: 160px; padding: 6px 8px;
          background: var(--secondary-background-color); color: var(--primary-text-color);
          border: 1px solid var(--divider-color); border-radius: 4px;
        }
        .bre .hint { color: var(--secondary-text-color); font-size: 12px; margin-top: -6px; }
      </style>
      <div class="bre">
        <div class="row"><label>Title (blank for none)</label>
          <input type="text" data-k="title" value="${esc(c.title)}"></div>
        <div class="row"><label>Base map</label>
          <select data-k="base_map">
            <option value="esri"${sel(c.base_map, "esri")}>Esri street</option>
            <option value="esri_topo"${sel(c.base_map, "esri_topo")}>Esri topographic</option>
            <option value="esri_gray"${sel(c.base_map, "esri_gray")}>Esri light grey</option>
            <option value="satellite"${sel(c.base_map, "satellite")}>Satellite</option>
          </select></div>
        <div class="row"><label>Height</label>
          <input type="text" data-k="height" value="${esc(c.height || "420px")}"></div>
        <div class="hint">e.g. 420px. In a sections dashboard you can also drag to resize.</div>
        <div class="row"><label>Default zoom (blank = fit radars)</label>
          <input type="number" data-k="default_zoom" min="4" max="12" value="${esc(c.default_zoom)}"></div>
        <div class="row"><label>Opacity</label>
          <input type="number" data-k="opacity" min="0.1" max="1" step="0.05" value="${esc(c.opacity == null ? 0.85 : c.opacity)}"></div>
        <div class="row"><label>Autoplay</label>
          <input type="checkbox" data-k="autoplay" ${c.autoplay !== false ? "checked" : ""}></div>
        <div class="row"><label>Show home marker</label>
          <input type="checkbox" data-k="show_home" ${c.show_home !== false ? "checked" : ""}></div>
        <div class="row"><label>Show legend</label>
          <input type="checkbox" data-k="show_legend" ${c.show_legend !== false ? "checked" : ""}></div>
      </div>
    `;
    this.querySelectorAll("[data-k]").forEach((el) => {
      el.addEventListener("change", () => this._onChange(el));
    });
  }

  _onChange(el) {
    const key = el.getAttribute("data-k");
    const cfg = Object.assign({}, this._config);
    if (el.type === "checkbox") {
      cfg[key] = el.checked;
    } else if (el.type === "number") {
      cfg[key] = el.value === "" ? null : Number(el.value);
    } else {
      const v = el.value.trim();
      if (v === "") delete cfg[key]; // blank removes the option (e.g. title)
      else cfg[key] = v;
    }
    this._config = cfg;
    this._emit();
  }
}

// Register idempotently. Home Assistant can load this resource more than once
// in the same frontend session (e.g. the module stays registered after you
// remove and re-add the resource), so guard against defining the element twice
// and against listing the card twice in the picker.
if (!customElements.get("bom-radar-card")) {
  customElements.define("bom-radar-card", BomRadarCard);
  if (!customElements.get("bom-radar-card-editor")) {
    customElements.define("bom-radar-card-editor", BomRadarCardEditor);
  }

  window.customCards = window.customCards || [];
  if (!window.customCards.some((card) => card.type === "bom-radar-card")) {
    window.customCards.push({
      type: "bom-radar-card",
      name: "BoM Radar Card",
      description: "Interactive, pannable Australian BoM weather radar with time animation.",
      preview: false,
      configurable: true,
      documentationURL: "https://github.com/safepay/ha-bom-radar-loop-addon",
    });
  }

  console.info(
    "%c BOM-RADAR-CARD %c loaded ",
    "color: white; background: #03a9f4; font-weight: 700;",
    "color: #03a9f4; background: white; font-weight: 700;"
  );
}
})();
