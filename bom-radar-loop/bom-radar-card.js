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
        title: "BoM Radar",
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
    if (this._config.title) card.header = this._config.title;

    const content = document.createElement("div");
    content.className = "bom-radar-content";

    const mapEl = document.createElement("div");
    mapEl.className = "bom-radar-map";
    mapEl.style.height = this._config.height;
    mapEl.style.width = "100%";
    mapEl.style.borderRadius = "0";

    const controls = document.createElement("div");
    controls.className = "bom-radar-controls";
    controls.innerHTML = `
      <button class="bom-radar-play" title="Play/pause" aria-label="Play or pause">&#9654;</button>
      <input class="bom-radar-slider" type="range" min="0" max="0" value="0" step="1" aria-label="Radar frame" />
      <span class="bom-radar-time">--:--</span>
    `;

    const legend = document.createElement("img");
    legend.className = "bom-radar-legend";
    legend.alt = "Rainfall intensity legend";
    legend.style.display = "none";

    const style = document.createElement("style");
    style.textContent = `
      .bom-radar-content { padding: 0 0 8px 0; }
      .bom-radar-map { background: var(--card-background-color, #222); }
      .bom-radar-map .bom-radar-frame { image-rendering: auto; }
      .bom-radar-controls {
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
      .bom-radar-legend { display: block; width: calc(100% - 28px); margin: 4px 14px 0 14px; height: 10px; }
      .bom-radar-error { padding: 16px; color: var(--error-color, #db4437); }
      .bom-radar-home {
        width: 18px; height: 18px; border-radius: 50% 50% 50% 0;
        background: var(--primary-color, #03a9f4); border: 2px solid #fff;
        transform: rotate(-45deg); box-shadow: 0 0 4px rgba(0,0,0,.5);
      }
    `;

    content.appendChild(mapEl);
    content.appendChild(controls);
    content.appendChild(legend);
    card.appendChild(style);
    card.appendChild(content);
    this.appendChild(card);

    this._mapEl = mapEl;
    this._legendEl = legend;
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

    // Leaflet needs a correctly-sized container; HA often renders cards hidden first.
    this._resizeObserver = new ResizeObserver(() => this._map && this._map.invalidateSize());
    this._resizeObserver.observe(this._mapEl);
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
      if (this._selectLevels()) this._showIndex(this._currentIndex ?? 0);
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
          });
        }
      });
      if (levels.length) this._stations.push({ role: radar.role, levels, active: 0 });
    });

    this._timestamps = this._manifest.timestamps || [];
    this._slider.max = Math.max(0, this._timestamps.length - 1);

    // Home marker (resolved from HA first, addon manifest as fallback).
    this._updateHomeMarker();

    // Legend.
    if (this._config.show_legend && this._manifest.legend_url) {
      this._legendEl.src = this._resolveUrl(this._manifest.legend_url) + `?t=${Date.now()}`;
      this._legendEl.style.display = "block";
    } else {
      this._legendEl.style.display = "none";
    }

    if (fitView && allBounds.length) {
      const dz = this._config.default_zoom;
      if (dz != null) {
        // Open at a fixed zoom, centred on home (if known) or the radar coverage.
        const home = this._homeLatLon();
        const center =
          this._config.default_center === "home" && home
            ? home
            : this._L.latLngBounds(allBounds).getCenter();
        this._map.setView(center, Number(dz));
      } else {
        this._map.fitBounds(allBounds, { padding: [10, 10] });
      }
    }

    this._selectLevels();

    if (this._timestamps.length && this._stations.length) {
      this._showIndex(this._timestamps.length - 1); // Start on the newest frame.
      if (wasPlaying || (fitView && this._config.autoplay)) this._play();
    } else {
      this._timeLabel.textContent = "No data";
    }
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

    this._stations.forEach((st) => {
      let active = -1; // -1 = this station shows nothing (panned fully out of view).

      // Candidate levels are those actually visible in the current view.
      const visible = st.levels.filter((lv) => view.intersects(lv.bounds));
      if (visible.length) {
        const atOrBelow = visible.filter((lv) => lv.native_zoom <= zoom);
        // Zoomed in enough for one or more levels: use the finest. Otherwise
        // (zoomed out past all levels) show the widest visible for context.
        const chosen = atOrBelow.length
          ? atOrBelow.reduce((best, lv) => (lv.native_zoom > best.native_zoom ? lv : best))
          : visible.reduce((best, lv) => (lv.native_zoom < best.native_zoom ? lv : best));
        active = st.levels.indexOf(chosen);
      }

      if (active !== st.active) {
        st.active = active;
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

    this._stations.forEach((st) => {
      st.levels.forEach((lv, idx) => {
        const active = idx === st.active;
        Object.entries(lv.framesByTs).forEach(([t, overlay]) => {
          overlay.setOpacity(active && t === ts ? this._opacity : 0);
        });
      });
    });

    this._currentIndex = i;
    this._slider.value = i;
    this._timeLabel.textContent = this._labels[ts] || ts;
  }

  _togglePlay() {
    if (this._playing) this._stop();
    else this._play();
  }

  _play() {
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

  static getStubConfig() {
    return { title: "BoM Radar", manifest: "/local/bom_radar/radar_manifest.json" };
  }
}

customElements.define("bom-radar-card", BomRadarCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "bom-radar-card",
  name: "BoM Radar Card",
  description: "Interactive, pannable Australian BoM weather radar with time animation.",
  preview: false,
  documentationURL: "https://github.com/safepay/ha-bom-radar-loop-addon",
});

console.info(
  "%c BOM-RADAR-CARD %c loaded ",
  "color: white; background: #03a9f4; font-weight: 700;",
  "color: #03a9f4; background: white; font-weight: 700;"
);
