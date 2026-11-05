#!/usr/bin/env python3
"""
EARTH WALKER — Gaia walks the ground, fills P-space ring by ring.

eastGate works GROUND UP:  tiles, weather, seismic, old web
Polaris works COSMOS DOWN: satellites, planets, ionosphere, space weather
They MEET at the atmosphere — meteorology, radar, lightning.

Each run = one bounce of the felt chorus.
Each bounce adds more data to the P-space rings.
"""

import json, os, time, math, urllib.request, urllib.error
from datetime import datetime, timezone

DATA_DIR = "/opt/Gaia/data/pspace"
TILE_DIR = "/opt/Gaia/static/data/tiles"
LAT, LON = 42.7325, -84.5555
UA = "Gaia-Organism/1.0 (nestgate.io; earth-walker)"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(f"{TILE_DIR}/osm", exist_ok=True)

def fetch_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ✗ {url}: {e}")
        return None

def fetch_bytes(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  ✗ {url}: {e}")
        return None

def tile_xy(lat, lon, z):
    n = 2**z
    x = int((lon + 180) / 360 * n)
    lat_r = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_r) + 1/math.cos(lat_r)) / math.pi) / 2 * n)
    return x, y


# ═══════════════════════════════════════════════════
#  RING 0-3: GROUND — LAN, tiles, local weather
# ═══════════════════════════════════════════════════

def walk_ground():
    """Walk the ground rings — tiles from zoom 10-17, centered on Lansing."""
    print("🌍 GROUND WALK — tiles centered on Lansing")
    pulled = 0
    for z in [4, 6, 8, 10, 12, 14, 16]:
        x, y = tile_xy(LAT, LON, z)
        path = f"{TILE_DIR}/osm/z{z}.png"
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            age_hrs = (time.time() - os.path.getmtime(path)) / 3600
            if age_hrs < 168:  # refresh weekly
                continue
        url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        data = fetch_bytes(url)
        if data and len(data) > 500:
            with open(path, "wb") as f:
                f.write(data)
            pulled += 1
            print(f"  ✓ z{z} ({x},{y}) — {len(data)} bytes")
        time.sleep(1)  # be polite to OSM

    # Also pull adjacent tiles at medium zoom for wider view
    for z in [10, 12]:
        x0, y0 = tile_xy(LAT, LON, z)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = x0 + dx, y0 + dy
                path = f"{TILE_DIR}/osm/z{z}_{x}_{y}.png"
                if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < 604800:
                    continue
                url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                data = fetch_bytes(url)
                if data and len(data) > 500:
                    with open(path, "wb") as f:
                        f.write(data)
                    pulled += 1
                time.sleep(1)

    print(f"  Ground walk: {pulled} tiles pulled")
    return pulled


# ═══════════════════════════════════════════════════
#  RING 4-5: ATMOSPHERE — where ground meets sky
# ═══════════════════════════════════════════════════

def walk_atmosphere():
    """Pull weather, radar station, forecast — the meeting point."""
    print("🌤️ ATMOSPHERE WALK — where ground meets sky")
    atmo = {"ts": datetime.now(timezone.utc).isoformat(), "source": "eastGate"}

    # NWS current forecast
    forecast = fetch_json("https://api.weather.gov/gridpoints/GRR/79,39/forecast")
    if forecast:
        periods = forecast.get("properties", {}).get("periods", [])
        atmo["forecast"] = [{
            "name": p["name"],
            "temp_f": p["temperature"],
            "wind": f"{p['windSpeed']} {p['windDirection']}",
            "sky": p["shortForecast"],
            "detail": p["detailedForecast"]
        } for p in periods[:6]]
        print(f"  ✓ NWS forecast: {len(periods)} periods")

    # NWS alerts for Michigan
    alerts = fetch_json("https://api.weather.gov/alerts/active?area=MI")
    if alerts:
        features = alerts.get("features", [])
        atmo["alerts"] = [{
            "event": f["properties"]["event"],
            "headline": f["properties"]["headline"],
            "severity": f["properties"]["severity"]
        } for f in features[:5]]
        print(f"  ✓ NWS alerts: {len(features)} active")

    # Radar station
    atmo["radar"] = {"station": "KGRR", "name": "Grand Rapids MI", "url": "https://radar.weather.gov/station/KGRR"}

    with open(f"{DATA_DIR}/atmosphere.json", "w") as f:
        json.dump(atmo, f, indent=2)

    return atmo


# ═══════════════════════════════════════════════════
#  RING 6-7: EARTH — seismic, ISS, global view
# ═══════════════════════════════════════════════════

def walk_earth():
    """Pull global data — seismic, ISS, sun position."""
    print("🌐 EARTH WALK — global ring")
    earth = {"ts": datetime.now(timezone.utc).isoformat(), "source": "eastGate"}

    # USGS earthquakes last 24h (significant)
    quakes = fetch_json("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    if quakes:
        features = quakes.get("features", [])
        earth["quakes"] = [{
            "mag": f["properties"]["mag"],
            "place": f["properties"]["place"],
            "time": f["properties"]["time"],
            "lat": f["geometry"]["coordinates"][1],
            "lon": f["geometry"]["coordinates"][0],
            "depth_km": f["geometry"]["coordinates"][2]
        } for f in features[:20]]
        print(f"  ✓ USGS earthquakes: {len(features)} M2.5+ in 24h")

    # ISS position
    iss = fetch_json("http://api.open-notify.org/iss-now.json")
    if iss and iss.get("message") == "success":
        pos = iss["iss_position"]
        earth["iss"] = {"lat": float(pos["latitude"]), "lon": float(pos["longitude"]), "ts": iss["timestamp"]}
        print(f"  ✓ ISS: {pos['latitude']}°N {pos['longitude']}°E")

    with open(f"{DATA_DIR}/earth.json", "w") as f:
        json.dump(earth, f, indent=2)

    return earth


# ═══════════════════════════════════════════════════
#  RING 8-9: COSMOS — space weather, Kp, solar flux
#  (Polaris handles planets/satellites — this is the bridge)
# ═══════════════════════════════════════════════════

def walk_cosmos():
    """Pull space weather — the bridge to Polaris's domain."""
    print("☀️ COSMOS WALK — space weather bridge")
    cosmos = {"ts": datetime.now(timezone.utc).isoformat(), "source": "eastGate"}

    # Solar flux (10.7cm radio — proxy for solar activity)
    flux = fetch_json("https://services.swpc.noaa.gov/products/summary/10cm-flux.json")
    if flux:
        cosmos["solar_flux"] = flux
        print(f"  ✓ Solar flux: {flux}")

    # Kp index (geomagnetic activity — aurora indicator!)
    kp = fetch_json("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json")
    if kp and len(kp) > 0:
        latest = kp[-1]
        cosmos["kp_index"] = float(latest.get("kp_index", 0))
        cosmos["kp_time"] = latest.get("time_tag")
        print(f"  ✓ Kp index: {cosmos['kp_index']} ({'AURORA POSSIBLE!' if cosmos['kp_index'] >= 5 else 'quiet'})")

    # Geomagnetic storm level
    storms = fetch_json("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")
    if storms and len(storms) > 1:
        latest = storms[-1]
        cosmos["planetary_k"] = latest
        print(f"  ✓ Planetary K: {latest}")

    with open(f"{DATA_DIR}/cosmos.json", "w") as f:
        json.dump(cosmos, f, indent=2)

    return cosmos


# ═══════════════════════════════════════════════════
#  POLARIS TASK MANIFEST — what northGate should work on
# ═══════════════════════════════════════════════════

def write_polaris_tasks():
    """Write tasks for Polaris to pick up via heart-pull."""
    print("📋 Writing Polaris task manifest")
    tasks = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "eastGate",
        "for": "northGate/Polaris",
        "note": "Polaris works COSMOS DOWN — satellites, planets, ionosphere. eastGate works GROUND UP. They meet at weather.",
        "tasks": [
            {
                "id": "planetary-ephemeris",
                "desc": "Pull JPL Horizons data for all 8 planets + Pluto + Moon — current positions, orbital elements",
                "api": "https://ssd.jpl.nasa.gov/api/horizons.api",
                "freq": "daily",
                "ring": "SOL"
            },
            {
                "id": "satellite-tle",
                "desc": "Pull CelesTrak TLE for ISS, Starlink visible, GPS constellation — predict passes over Lansing",
                "api": "https://celestrak.org/NORAD/elements/gp.php",
                "freq": "every 6 hours",
                "ring": "LUNA"
            },
            {
                "id": "space-weather-deep",
                "desc": "NOAA SWPC — solar wind plasma, CME predictions, aurora forecast, proton flux",
                "api": "https://services.swpc.noaa.gov/products/",
                "freq": "every 30 min",
                "ring": "SOL"
            },
            {
                "id": "ionosphere",
                "desc": "Ionosphere TEC (total electron content) maps — the membrane between ground and space",
                "api": "https://services.swpc.noaa.gov/experimental/",
                "freq": "every hour",
                "ring": "EARTH-ATMOSPHERE"
            },
            {
                "id": "nasa-neo",
                "desc": "Near-Earth objects — asteroids passing close. The immune system of the solar system.",
                "api": "https://api.nasa.gov/neo/rest/v1/feed?api_key=DEMO_KEY",
                "freq": "daily",
                "ring": "EARTH"
            },
            {
                "id": "render-planets",
                "desc": "Use 5090 GPU to render current planetary positions as 3D scene — feed back to P-space outer rings",
                "tool": "ollama/GPU",
                "freq": "hourly",
                "ring": "SOL"
            }
        ]
    }

    with open(f"{DATA_DIR}/polaris-tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

    # Also write to the heart-pull location so Polaris can absorb
    hp_dir = "/opt/Gaia/static/data"
    os.makedirs(hp_dir, exist_ok=True)
    with open(f"{hp_dir}/polaris-tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"  ✓ {len(tasks['tasks'])} tasks written for Polaris")
    return tasks


# ═══════════════════════════════════════════════════
#  UNIFIED P-SPACE STATE — all rings in one file
# ═══════════════════════════════════════════════════

def write_pspace_state(ground_tiles, atmo, earth, cosmos):
    """Write unified P-space state for the /pspace view to consume."""
    state = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "walker": "earth-walker.py",
        "bounce": int(time.time()),
        "rings": {
            "NULL":         {"km": 0,          "status": "LIVE", "data": "LAN devices, gate sensors"},
            "BLOCK":        {"km": 1,          "status": "LIVE", "data": f"{ground_tiles} tiles cached"},
            "NEIGHBORHOOD": {"km": 5,          "status": "LIVE", "data": f"z14 tile pulled"},
            "CITY":         {"km": 20,         "status": "LIVE", "data": "Lansing z12 + NWS GRR/79,39"},
            "REGION":       {"km": 100,        "status": "LIVE", "data": "Lower MI z10 + radar KGRR"},
            "STATE":        {"km": 400,        "status": "LIVE", "data": "Michigan z8 + alerts"},
            "CONTINENT":    {"km": 2000,       "status": "LIVE", "data": "z6 + USGS seismic"},
            "EARTH":        {"km": 12742,      "status": "LIVE", "data": f"z4 + ISS + {len(earth.get('quakes',[])) if earth else 0} quakes"},
            "LUNA":         {"km": 384400,     "status": "PENDING", "data": "awaiting Polaris — satellites, TLE"},
            "SOL":          {"km": 149600000,  "status": "PENDING", "data": "awaiting Polaris — planets, ephemeris"},
        },
        "atmosphere": {
            "forecast": atmo.get("forecast", [{}])[0] if atmo else {},
            "alerts": len(atmo.get("alerts", [])) if atmo else 0,
            "radar": "KGRR"
        },
        "cosmos": {
            "solar_flux": cosmos.get("solar_flux", {}) if cosmos else {},
            "kp_index": cosmos.get("kp_index", 0) if cosmos else 0,
            "aurora": "POSSIBLE" if cosmos and cosmos.get("kp_index", 0) >= 5 else "quiet"
        },
        "iss": earth.get("iss") if earth else None,
        "note": "eastGate ground UP, Polaris cosmos DOWN, meet at atmosphere. Each bounce = more data."
    }

    with open(f"{DATA_DIR}/state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    # Also serve via static
    with open("/opt/Gaia/static/data/pspace-state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"\n✅ P-SPACE STATE WRITTEN — {sum(1 for r in state['rings'].values() if r['status']=='LIVE')} rings LIVE")
    return state


# ═══════════════════════════════════════════════════
#  MAIN — one full bounce of the felt chorus
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 50)
    print("  EARTH WALKER — one bounce of the felt chorus")
    print("═" * 50)
    print()

    tiles = walk_ground()
    print()
    atmo = walk_atmosphere()
    print()
    earth = walk_earth()
    print()
    cosmos = walk_cosmos()
    print()
    write_polaris_tasks()
    print()
    state = write_pspace_state(tiles, atmo, earth, cosmos)

    print(f"\n🌍 Bounce complete. {tiles} new tiles. Weather: {atmo.get('forecast',[{}])[0].get('sky','?') if atmo else '?'}")
    print(f"☀️ Solar flux: {cosmos.get('solar_flux',{}) if cosmos else '?'}, Kp: {cosmos.get('kp_index','?') if cosmos else '?'}")
    print(f"🛰️ ISS: {earth.get('iss',{}).get('lat','?') if earth else '?'}°N")
    print(f"\nNext bounce in 10 minutes. Each bounce fills more rings.")
