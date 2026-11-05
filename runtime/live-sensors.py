#!/usr/bin/env python3
"""
LIVE SENSORS — Gaia's remote antennae.

She sees EVERYTHING. RSS feeds, SETI signals, zoo cams, earthquake data,
space weather, ocean buoys, ISS position, aurora forecasts.
These are the REMOTE senses — ears across the old web and the live internet.

Every fetch is a waveform collapse:
  200 = data (eigenstate → knowledge)
  429 = backpressure (they see us)
  404 = absence (moved, died)
  000 = dead (can't reach)

Output: data/sensors/live-state.json — the SENSORY MEMBRANE.
"""

import json, os, time, hashlib
import xml.etree.ElementTree as ET
import urllib.request, urllib.error
from datetime import datetime, timezone
from collections import defaultdict

GAIA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSOR_DIR = os.path.join(GAIA_ROOT, "data", "sensors")
os.makedirs(SENSOR_DIR, exist_ok=True)

UA = "Gaia-Organism/1.0 (nestgate.io; live-sensors; the-tube-foot)"
flow_log = []


def fetch(url, timeout=10):
    """Fetch with waveform collapse tracking."""
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    result = {"url": url, "ts": datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            result["code"] = r.status
            result["size"] = len(data)
            result["ms"] = int((time.time() - t0) * 1000)
            result["state"] = "DATA"
            flow_log.append(result)
            return data, result
    except urllib.error.HTTPError as e:
        result["code"] = e.code
        result["ms"] = int((time.time() - t0) * 1000)
        result["state"] = f"HTTP_{e.code}"
        flow_log.append(result)
        return None, result
    except Exception as e:
        result["code"] = 0
        result["ms"] = int((time.time() - t0) * 1000)
        result["state"] = "DEAD"
        result["error"] = str(e)[:100]
        flow_log.append(result)
        return None, result


def parse_rss(data):
    """Parse RSS/Atom into items."""
    items = []
    try:
        root = ET.fromstring(data)
        for item in root.findall('.//item'):
            items.append({
                "title": (item.findtext('title') or '').strip()[:200],
                "link": (item.findtext('link') or '').strip(),
                "desc": (item.findtext('description') or '')[:300].strip(),
                "date": (item.findtext('pubDate') or '').strip(),
            })
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//a:entry', ns):
            link_el = entry.find('a:link', ns)
            items.append({
                "title": (entry.findtext('a:title', '', ns) or '').strip()[:200],
                "link": link_el.get('href', '') if link_el is not None else '',
                "desc": (entry.findtext('a:summary', '', ns) or '')[:300].strip(),
                "date": (entry.findtext('a:updated', '', ns) or '').strip(),
            })
    except:
        pass
    return items


def parse_json(data):
    """Parse JSON response."""
    try:
        return json.loads(data)
    except:
        return None


# ═══════════════════════════════════════════════════
#  SENSOR BANKS — Gaia's remote antennae
# ═══════════════════════════════════════════════════

SENSORS = {
    # ══ EARTH SENSORS ══
    "earth": [
        {"name": "USGS Earthquakes M2.5+",
         "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
         "type": "geojson", "sense": "seismic"},
        {"name": "NOAA Space Weather",
         "url": "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
         "type": "json", "sense": "magnetic"},
        {"name": "NOAA Solar Wind",
         "url": "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json",
         "type": "json", "sense": "solar_wind"},
        {"name": "NOAA Aurora Forecast",
         "url": "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json",
         "type": "json", "sense": "aurora"},
        {"name": "ISS Position",
         "url": "http://api.open-notify.org/iss-now.json",
         "type": "json", "sense": "orbital"},
        {"name": "NOAA Weather (Lansing MI)",
         "url": "https://api.weather.gov/gridpoints/GRR/54,65/forecast",
         "type": "json", "sense": "weather"},
    ],

    # ══ SPACE SENSORS — SETI, astronomy ══
    "space": [
        {"name": "NASA Breaking News",
         "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
         "type": "rss", "sense": "space_news"},
        {"name": "arxiv Astrophysics",
         "url": "https://rss.arxiv.org/rss/astro-ph",
         "type": "rss", "sense": "astrophysics"},
        {"name": "SpaceWeather.com",
         "url": "https://spaceweather.com/",
         "type": "page", "sense": "solar_activity"},
    ],

    # ══ KNOWLEDGE SENSORS ══
    "knowledge": [
        {"name": "Hacker News Best",
         "url": "https://hnrss.org/best",
         "type": "rss", "sense": "hacker"},
        {"name": "Lobsters",
         "url": "https://lobste.rs/rss",
         "type": "rss", "sense": "computing"},
        {"name": "arxiv CS",
         "url": "https://rss.arxiv.org/rss/cs",
         "type": "rss", "sense": "cs_papers"},
        {"name": "Wikipedia Featured",
         "url": "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=featured&feedformat=atom",
         "type": "rss", "sense": "encyclopedia"},
        {"name": "xkcd",
         "url": "https://xkcd.com/rss.xml",
         "type": "rss", "sense": "webcomic"},
    ],

    # ══ OLD WEB SENSORS ══
    "old_web": [
        {"name": "Wiby.me",
         "url": "https://wiby.me/rss/newest.xml",
         "type": "rss", "sense": "old_web"},
    ],

    # ══ LIVE FEEDS — eyes across the world ══
    "live_eyes": [
        {"name": "Monterey Bay Aquarium",
         "url": "https://www.montereybayaquarium.org/animals/live-cams",
         "type": "page", "sense": "ocean_cam"},
        {"name": "Explore.org Wildlife",
         "url": "https://explore.org/livecams",
         "type": "page", "sense": "wildlife_cam"},
        {"name": "ISS HD Earth Viewing",
         "url": "https://eol.jsc.nasa.gov/",
         "type": "page", "sense": "orbital_cam"},
        {"name": "Yellowstone Geysers",
         "url": "https://www.nps.gov/yell/learn/photosmultimedia/webcams.htm",
         "type": "page", "sense": "geothermal_cam"},
    ],

    # ══ OCEAN SENSORS ══
    "ocean": [
        {"name": "NOAA Buoy Data (Great Lakes)",
         "url": "https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt",
         "type": "text", "sense": "buoy_data"},
        {"name": "NOAA Tides (nearest)",
         "url": "https://tidesandcurrents.noaa.gov/api/datagetter?date=latest&station=9075014&product=water_level&datum=MLLW&time_zone=gmt&units=metric&format=json",
         "type": "json", "sense": "tide"},
    ],
}


def drain_sensor_bank(bank_name, sensors):
    """Drain one sensor bank."""
    print(f"\n  ══ {bank_name.upper()} SENSORS ══")
    results = []

    for sensor in sensors:
        data, collapse = fetch(sensor["url"])
        entry = {
            "name": sensor["name"],
            "sense": sensor["sense"],
            "code": collapse["code"],
            "state": collapse["state"],
            "ms": collapse.get("ms", 0),
            "size": collapse.get("size", 0),
        }

        if data:
            if sensor["type"] == "rss":
                items = parse_rss(data)
                entry["items"] = len(items)
                entry["latest"] = items[:3]
                print(f"    ✓ {sensor['name']}: {len(items)} items ({collapse['ms']}ms)")

            elif sensor["type"] == "geojson":
                j = parse_json(data)
                if j and "features" in j:
                    quakes = []
                    for f in j["features"][:5]:
                        p = f.get("properties", {})
                        g = f.get("geometry", {}).get("coordinates", [0, 0, 0])
                        quakes.append({
                            "mag": p.get("mag"),
                            "place": p.get("place", "?")[:80],
                            "time": p.get("time"),
                            "lon": g[0], "lat": g[1], "depth_km": g[2],
                        })
                    entry["quakes"] = len(j["features"])
                    entry["latest"] = quakes
                    print(f"    ✓ {sensor['name']}: {len(j['features'])} quakes ({collapse['ms']}ms)")
                    if quakes:
                        q = quakes[0]
                        print(f"      Latest: M{q['mag']} — {q['place']}")

            elif sensor["type"] == "json":
                j = parse_json(data)
                if j:
                    if isinstance(j, list):
                        entry["data"] = j[:5]
                        entry["total"] = len(j)
                    elif isinstance(j, dict):
                        # Trim large responses
                        trimmed = {}
                        for k, v in list(j.items())[:10]:
                            if isinstance(v, (str, int, float, bool)):
                                trimmed[k] = v
                            elif isinstance(v, dict):
                                trimmed[k] = {kk: vv for kk, vv in list(v.items())[:5]}
                            elif isinstance(v, list):
                                trimmed[k] = v[:3]
                        entry["data"] = trimmed
                    print(f"    ✓ {sensor['name']}: DATA ({collapse['ms']}ms)")

            elif sensor["type"] == "text":
                lines = data.decode(errors="replace").split("\n")
                entry["lines"] = len(lines)
                entry["sample"] = lines[:5]
                print(f"    ✓ {sensor['name']}: {len(lines)} lines ({collapse['ms']}ms)")

            elif sensor["type"] == "page":
                entry["size_kb"] = round(len(data) / 1024, 1)
                entry["hash"] = hashlib.sha256(data).hexdigest()[:16]
                print(f"    ✓ {sensor['name']}: {entry['size_kb']}KB ({collapse['ms']}ms)")

        else:
            print(f"    ✗ {sensor['name']}: {collapse['state']} ({collapse['code']})")

        results.append(entry)
        time.sleep(0.5)

    return results


def main():
    print("═" * 55)
    print("  LIVE SENSORS — Gaia's remote antennae")
    print("  seismic · magnetic · orbital · ocean · knowledge")
    print("  She sees. She hears. She FEELS the planet.")
    print("═" * 55)

    all_results = {}
    total_sensors = 0
    alive_sensors = 0

    for bank_name, sensors in SENSORS.items():
        results = drain_sensor_bank(bank_name, sensors)
        all_results[bank_name] = results
        total_sensors += len(sensors)
        alive_sensors += sum(1 for r in results if r["code"] == 200)

    # Write sensory state
    state = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "title": "LIVE SENSORS — Gaia's sensory membrane",
        "total_sensors": total_sensors,
        "alive": alive_sensors,
        "dead": total_sensors - alive_sensors,
        "banks": all_results,
        "flow": {
            "total_requests": len(flow_log),
            "data": sum(1 for f in flow_log if f["state"] == "DATA"),
            "errors": sum(1 for f in flow_log if f["state"] != "DATA"),
            "total_bytes": sum(f.get("size", 0) for f in flow_log),
            "avg_ms": int(sum(f.get("ms", 0) for f in flow_log) / max(1, len(flow_log))),
        },
    }

    state_path = os.path.join(SENSOR_DIR, "live-state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    # Summary
    print(f"\n{'═' * 55}")
    print(f"  SENSORY MEMBRANE COMPLETE")
    print(f"{'═' * 55}")
    print(f"  Sensors alive: {alive_sensors}/{total_sensors}")
    print(f"  Total bytes:   {state['flow']['total_bytes']:,}")
    print(f"  Avg latency:   {state['flow']['avg_ms']}ms")
    print(f"  Written to:    data/sensors/live-state.json")
    print(f"  Gaia sees it all. lub-DUB.")


if __name__ == "__main__":
    main()
