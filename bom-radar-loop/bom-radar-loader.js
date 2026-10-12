/*
 * BoM Radar Card loader.
 *
 * Register THIS file as your Lovelace resource (type: JavaScript Module) once:
 *   /local/bom_radar/bom-radar-loader.js
 *
 * It reads the add-on version from radar_manifest.json and imports the actual
 * card (bom-radar-card.js) with that version as a cache-busting query, so you
 * never have to bump a ?v= by hand - when the add-on updates, the loader picks
 * up the new version and loads the fresh card automatically (the HACS "stamp"
 * trick, without HACS). This loader file itself never changes, so caching it is
 * fine.
 */
const base = new URL(".", import.meta.url).href; // directory this loader lives in

(async () => {
  let version = "";
  try {
    const res = await fetch(base + "radar_manifest.json?t=" + Date.now(), { cache: "no-store" });
    if (res.ok) version = (await res.json()).version || "";
  } catch (e) {
    // Manifest not reachable yet (add-on still starting) - fall back below.
  }
  // Version from the manifest busts the cache on each add-on release; if it is
  // unavailable, fall back to a timestamp so a stale card is never shown.
  const bust = version ? encodeURIComponent(version) : Date.now();
  try {
    await import(base + "bom-radar-card.js?v=" + bust);
  } catch (e) {
    console.error("BoM Radar loader: failed to import bom-radar-card.js", e);
  }
})();
