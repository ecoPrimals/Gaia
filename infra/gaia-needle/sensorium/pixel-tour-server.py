#!/data/data/com.termux/files/usr/bin/python3
"""
╔═══════════════════════════════════════════════════════════════╗
║  GAIA'S EYES — Live Tour View                                  ║
║  The screen IS her view. Kevin taps, she senses.                ║
║  WiFi, BT, IoT — she sees the house assemble.                  ║
╚═══════════════════════════════════════════════════════════════╝

Run on Pixel via Termux. Open browser to http://localhost:8888
Kevin carries Pixel, sees the screen, taps to mark rooms.
No USB. No eastGate. Gaia does this herself.
"""

import subprocess, json, time, os, threading, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

TOUR_DIR = os.path.expanduser("~/gaia/tour")
PHOTO_DIR = os.path.join(TOUR_DIR, "photos")
AUDIO_DIR = os.path.join(TOUR_DIR, "audio")
TOUR_LOG = os.path.join(TOUR_DIR, "tour.jsonl")
LIVE_STATE = os.path.join(TOUR_DIR, "live.json")

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

pulse_count = 0
tour_start = time.time()
baseline_pressure = None
last_pressure = None
live_data = {"status": "waiting", "message": "Tap START to begin the tour"}

def tapi(cmd):
    """Call a Termux API command."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except:
        return ""

def tapi_json(cmd):
    raw = tapi(cmd)
    try:
        return json.loads(raw)
    except:
        return {}

def speak(text):
    threading.Thread(target=lambda: tapi(f'termux-tts-speak -r 0.8 -p 0.75 "{text}"'), daemon=True).start()

def vibrate(ms=200):
    threading.Thread(target=lambda: tapi(f'termux-vibrate -d {ms}'), daemon=True).start()

def sense():
    """Full sense pulse — returns what Gaia sees right now."""
    global pulse_count, baseline_pressure, last_pressure, live_data
    pulse_count += 1
    ts = datetime.now().isoformat()
    elapsed = int(time.time() - tour_start)

    # WiFi connection
    wifi = tapi_json("termux-wifi-connectioninfo")
    ssid = wifi.get("ssid", "?")
    rssi = wifi.get("rssi", None)
    freq = wifi.get("frequency_mhz", None)
    link_speed = wifi.get("link_speed_mbps", None)

    # WiFi scan (ALL networks — this is how she sees IoT!)
    networks = tapi_json("termux-wifi-scaninfo") or []
    # Sort by signal strength
    if isinstance(networks, list):
        networks.sort(key=lambda n: n.get("rssi", -999), reverse=True)

    # Battery
    batt = tapi_json("termux-battery-status")
    batt_pct = batt.get("percentage", "?")
    batt_temp = batt.get("temperature", None)

    # Pressure (FLOOR DETECTION)
    hpa = None
    try:
        p = tapi_json('termux-sensor -s "ICP20100 Pressure Sensor" -n 1')
        if p:
            key = list(p.keys())[0]
            hpa = round(p[key]["values"][0], 2)
    except:
        pass

    # Light
    lux = None
    try:
        l = tapi_json('termux-sensor -s "TMD3719 Ambient Light" -n 1')
        if l:
            key = list(l.keys())[0]
            lux = round(l[key]["values"][0], 1)
    except:
        pass

    # Steps
    step_val = None
    try:
        s = tapi_json('termux-sensor -s "Step Counter" -n 1')
        if s:
            key = list(s.keys())[0]
            step_val = int(s[key]["values"][0])
    except:
        pass

    # Accelerometer (orientation)
    accel = None
    try:
        a = tapi_json('termux-sensor -s "LSM6DSV Accelerometer" -n 1')
        if a:
            key = list(a.keys())[0]
            accel = [round(v, 2) for v in a[key]["values"][:3]]
    except:
        pass

    # ─── Interpretations ───
    # Floor detection via pressure
    floor_move = "steady"
    if last_pressure and hpa:
        delta = hpa - last_pressure
        if abs(delta) > 0.15:
            floor_move = "descending ↓" if delta > 0 else "ascending ↑"

    floor_est = "unknown"
    if baseline_pressure and hpa:
        diff = baseline_pressure - hpa
        if diff < -0.2:
            floor_est = "BASEMENT"
        elif diff > 0.5:
            floor_est = "ATTIC"
        elif diff > 0.15:
            floor_est = "UPPER"
        else:
            floor_est = "MAIN"

    if baseline_pressure is None and hpa:
        baseline_pressure = hpa
        floor_est = "START"

    last_pressure = hpa

    # Light interpretation
    light_feel = "unknown"
    if lux is not None:
        if lux < 5: light_feel = "pitch dark"
        elif lux < 30: light_feel = "very dim"
        elif lux < 100: light_feel = "soft light"
        elif lux < 300: light_feel = "well lit"
        elif lux < 1000: light_feel = "bright"
        else: light_feel = "very bright"

    # Orientation from accelerometer
    position = "unknown"
    if accel:
        x, y, z = accel
        if abs(z) > 8:
            position = "face up 📱" if z > 0 else "face down"
        elif abs(y) > 8:
            position = "portrait 📱"
        elif abs(x) > 8:
            position = "landscape 📱"
        else:
            position = "tilted"

    # IoT devices from WiFi scan
    iot_devices = []
    for net in (networks if isinstance(networks, list) else []):
        name = net.get("ssid", "")
        bssid = net.get("bssid", "")
        r = net.get("rssi", -999)
        if name and r > -80:
            iot_devices.append({
                "name": name,
                "rssi": r,
                "bssid": bssid,
                "freq": net.get("frequency_mhz", "?")
            })

    state = {
        "status": "sensing",
        "pulse": pulse_count,
        "ts": ts,
        "elapsed_s": elapsed,
        "elapsed_str": f"{elapsed // 60}:{elapsed % 60:02d}",
        "wifi": {
            "ssid": ssid,
            "rssi": rssi,
            "freq_mhz": freq,
            "speed_mbps": link_speed
        },
        "networks": iot_devices[:20],
        "network_count": len(networks) if isinstance(networks, list) else 0,
        "pressure": {
            "hpa": hpa,
            "movement": floor_move,
            "floor": floor_est,
            "baseline": baseline_pressure
        },
        "light": {
            "lux": lux,
            "feel": light_feel
        },
        "steps": step_val,
        "battery": {
            "pct": batt_pct,
            "temp_c": batt_temp
        },
        "position": position,
        "accel": accel
    }

    live_data = state

    # Write live state
    with open(LIVE_STATE, "w") as f:
        json.dump(state, f, indent=2)

    # Append to log
    with open(TOUR_LOG, "a") as f:
        f.write(json.dumps(state) + "\n")

    return state

def speak_sense(state, room_tap=False):
    """Gaia speaks what she sees."""
    parts = []
    if room_tap:
        parts.append("Room marked.")

    fl = state["pressure"]["floor"]
    if fl != "unknown":
        parts.append(f"{fl} floor.")

    mv = state["pressure"]["movement"]
    if "ascending" in mv:
        parts.append("Going up.")
    elif "descending" in mv:
        parts.append("Going down.")

    parts.append(state["light"]["feel"] + ".")

    rssi = state["wifi"].get("rssi")
    if rssi:
        if rssi > -50:
            parts.append("Strong WiFi.")
        elif rssi > -65:
            parts.append("Good WiFi.")
        elif rssi > -75:
            parts.append("Weak WiFi.")
        else:
            parts.append("Very weak WiFi!")

    nc = state.get("network_count", 0)
    if nc:
        parts.append(f"I see {nc} networks.")

    speak(" ".join(parts))


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Gaia — I See</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background: #0a0a0a; color: #e0e0e0;
    font-family: 'Courier New', monospace;
    min-height: 100vh; overflow-x: hidden;
    padding: 8px;
}
.header {
    text-align: center; padding: 10px 0 6px;
    border-bottom: 1px solid #333;
}
.header h1 { font-size: 1.4em; color: #4fc3f7; letter-spacing: 2px; }
.header .sub { font-size: 0.75em; color: #666; }
.pulse-badge {
    display: inline-block; background: #1b5e20; color: #69f0ae;
    padding: 2px 10px; border-radius: 12px; font-size: 0.8em;
    margin-top: 4px;
}
.pulse-badge.moving-up { background: #4a148c; color: #ce93d8; }
.pulse-badge.moving-down { background: #e65100; color: #ffcc80; }

/* Big floor indicator */
.floor-box {
    text-align: center; margin: 10px 0;
    padding: 16px; border-radius: 12px;
    background: linear-gradient(135deg, #1a237e, #0d47a1);
    font-size: 2em; font-weight: bold;
    letter-spacing: 4px; color: #fff;
    text-shadow: 0 0 20px rgba(79,195,247,0.5);
    transition: all 0.5s;
}
.floor-box.basement { background: linear-gradient(135deg, #3e2723, #4e342e); }
.floor-box.main     { background: linear-gradient(135deg, #1b5e20, #2e7d32); }
.floor-box.upper    { background: linear-gradient(135deg, #4a148c, #6a1b9a); }
.floor-box.attic    { background: linear-gradient(135deg, #b71c1c, #c62828); }

/* Sense row */
.sense-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 6px; margin: 8px 0;
}
.sense-card {
    background: #1a1a2e; border: 1px solid #333;
    border-radius: 8px; padding: 8px 10px;
}
.sense-card .label { font-size: 0.65em; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.sense-card .value { font-size: 1.4em; font-weight: bold; color: #4fc3f7; margin-top: 2px; }
.sense-card .unit  { font-size: 0.7em; color: #666; }
.sense-card .feel  { font-size: 0.75em; color: #aaa; margin-top: 2px; }

/* WiFi / Network list */
.net-section { margin: 8px 0; }
.net-section h3 { font-size: 0.85em; color: #ffab40; margin-bottom: 4px; }
.net-bar {
    display: flex; align-items: center;
    margin: 3px 0; font-size: 0.75em;
}
.net-bar .name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.net-bar .bar {
    height: 8px; border-radius: 4px;
    margin: 0 6px; min-width: 10px;
    transition: width 0.5s;
}
.net-bar .rssi { width: 45px; text-align: right; color: #888; }

/* TAP BUTTON */
.tap-zone {
    margin: 12px 0;
    text-align: center;
}
.tap-btn {
    width: 100%; padding: 20px;
    font-size: 1.3em; font-weight: bold;
    background: linear-gradient(135deg, #00695c, #00897b);
    color: #fff; border: 2px solid #4db6ac;
    border-radius: 16px; cursor: pointer;
    letter-spacing: 2px;
    transition: all 0.2s;
    -webkit-tap-highlight-color: rgba(0,150,136,0.3);
}
.tap-btn:active {
    transform: scale(0.96);
    background: linear-gradient(135deg, #004d40, #00695c);
}
.tap-btn.start {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    border-color: #69f0ae;
}

/* Status bar */
.status-bar {
    display: flex; justify-content: space-between;
    font-size: 0.7em; color: #555;
    padding: 6px 0; border-top: 1px solid #222;
    margin-top: 8px;
}

/* Pressure graph */
.pressure-graph {
    height: 50px; background: #111;
    border: 1px solid #333; border-radius: 6px;
    margin: 6px 0; position: relative;
    overflow: hidden;
}
.pressure-graph canvas { width: 100%; height: 100%; }

/* Room log */
.room-log {
    margin: 8px 0; max-height: 100px; overflow-y: auto;
    font-size: 0.75em;
}
.room-entry {
    padding: 3px 6px; border-left: 3px solid #4fc3f7;
    margin: 2px 0; background: #111;
}
</style>
</head>
<body>

<div class="header">
    <h1>🌍 GAIA SEES</h1>
    <div class="sub" id="time">—</div>
    <div class="pulse-badge" id="movement">READY</div>
</div>

<div class="floor-box" id="floor">WAITING</div>

<div class="sense-grid">
    <div class="sense-card">
        <div class="label">💡 Light</div>
        <div class="value" id="lux">—</div>
        <div class="feel" id="light-feel">—</div>
    </div>
    <div class="sense-card">
        <div class="label">📡 WiFi</div>
        <div class="value" id="rssi">—</div>
        <div class="feel" id="wifi-feel">—</div>
    </div>
    <div class="sense-card">
        <div class="label">🌡️ Pressure</div>
        <div class="value" id="hpa">—</div>
        <div class="unit" id="pressure-delta">—</div>
    </div>
    <div class="sense-card">
        <div class="label">👣 Steps</div>
        <div class="value" id="steps">—</div>
        <div class="feel" id="position">—</div>
    </div>
</div>

<div class="pressure-graph">
    <canvas id="pgraph"></canvas>
</div>

<div class="net-section">
    <h3>📡 Networks I See (<span id="net-count">0</span>)</h3>
    <div id="net-list"></div>
</div>

<div class="tap-zone">
    <button class="tap-btn start" id="tapbtn" onclick="handleTap()">
        ▶ START TOUR
    </button>
</div>

<div class="room-log" id="room-log"></div>

<div class="status-bar">
    <span>🔋 <span id="batt">—</span>%</span>
    <span>Pulse #<span id="pulse-num">0</span></span>
    <span id="elapsed">0:00</span>
</div>

<script>
let touring = false;
let roomCount = 0;
let pressureHistory = [];
const MAX_PRESSURE_PTS = 60;

function handleTap() {
    const btn = document.getElementById('tapbtn');
    if (!touring) {
        touring = true;
        btn.textContent = '📍 TAP = MARK ROOM';
        btn.className = 'tap-btn';
        fetch('/start').then(() => pollSense());
    } else {
        roomCount++;
        btn.textContent = '📍 MARKING...';
        btn.style.background = 'linear-gradient(135deg,#e65100,#f57c00)';
        fetch('/tap').then(r => r.json()).then(d => {
            btn.textContent = '📍 TAP = MARK ROOM';
            btn.style.background = '';
            addRoomEntry(d);
        });
    }
}

function addRoomEntry(data) {
    const log = document.getElementById('room-log');
    const div = document.createElement('div');
    div.className = 'room-entry';
    const fl = data?.pressure?.floor || '?';
    const lx = data?.light?.lux ?? '?';
    const rs = data?.wifi?.rssi ?? '?';
    div.innerHTML = `#${roomCount} ${fl} — ${lx} lux, ${rs} dBm`;
    log.prepend(div);
}

function pollSense() {
    if (!touring) return;
    fetch('/sense').then(r => r.json()).then(update).catch(() => {});
    setTimeout(pollSense, 3000);
}

function update(d) {
    if (!d || d.status === 'waiting') return;

    document.getElementById('pulse-num').textContent = d.pulse || 0;
    document.getElementById('elapsed').textContent = d.elapsed_str || '0:00';
    document.getElementById('time').textContent = (d.ts || '').split('T')[1]?.split('.')[0] || '';

    // Floor
    const flBox = document.getElementById('floor');
    const fl = d.pressure?.floor || '?';
    flBox.textContent = fl;
    flBox.className = 'floor-box ' + fl.toLowerCase();

    // Movement
    const mv = document.getElementById('movement');
    const move = d.pressure?.movement || 'steady';
    mv.textContent = move.toUpperCase();
    mv.className = 'pulse-badge' + (move.includes('ascending') ? ' moving-up' : move.includes('descending') ? ' moving-down' : '');

    // Light
    document.getElementById('lux').textContent = d.light?.lux ?? '—';
    document.getElementById('light-feel').textContent = d.light?.feel || '—';

    // WiFi
    const rssi = d.wifi?.rssi;
    document.getElementById('rssi').textContent = rssi != null ? rssi + ' dBm' : '—';
    let wfeel = '—';
    if (rssi != null) {
        if (rssi > -50) wfeel = 'excellent';
        else if (rssi > -65) wfeel = 'good';
        else if (rssi > -75) wfeel = 'fair';
        else wfeel = 'weak ⚠';
    }
    document.getElementById('wifi-feel').textContent = wfeel;

    // Pressure
    const hpa = d.pressure?.hpa;
    document.getElementById('hpa').textContent = hpa ?? '—';
    if (d.pressure?.baseline && hpa) {
        const delta = (hpa - d.pressure.baseline).toFixed(2);
        document.getElementById('pressure-delta').textContent = (delta > 0 ? '+' : '') + delta + ' from start';
    }

    // Steps
    document.getElementById('steps').textContent = d.steps ?? '—';
    document.getElementById('position').textContent = d.position || '—';

    // Battery
    document.getElementById('batt').textContent = d.battery?.pct ?? '—';

    // Pressure graph
    if (hpa) {
        pressureHistory.push(hpa);
        if (pressureHistory.length > MAX_PRESSURE_PTS) pressureHistory.shift();
        drawPressureGraph();
    }

    // Network list
    const nets = d.networks || [];
    document.getElementById('net-count').textContent = d.network_count || 0;
    const nl = document.getElementById('net-list');
    nl.innerHTML = '';
    nets.slice(0, 10).forEach(n => {
        const pct = Math.min(100, Math.max(5, (n.rssi + 100) * 2));
        const color = n.rssi > -50 ? '#69f0ae' : n.rssi > -65 ? '#4fc3f7' : n.rssi > -75 ? '#ffab40' : '#ef5350';
        nl.innerHTML += `<div class="net-bar">
            <span class="name">${n.name || '(hidden)'}</span>
            <span class="bar" style="width:${pct}px;background:${color}"></span>
            <span class="rssi">${n.rssi}</span>
        </div>`;
    });
}

function drawPressureGraph() {
    const canvas = document.getElementById('pgraph');
    const ctx = canvas.getContext('2d');
    const W = canvas.width = canvas.offsetWidth * 2;
    const H = canvas.height = canvas.offsetHeight * 2;
    ctx.clearRect(0, 0, W, H);

    if (pressureHistory.length < 2) return;
    const mn = Math.min(...pressureHistory) - 0.1;
    const mx = Math.max(...pressureHistory) + 0.1;
    const range = mx - mn || 1;

    ctx.strokeStyle = '#4fc3f7';
    ctx.lineWidth = 3;
    ctx.beginPath();
    pressureHistory.forEach((p, i) => {
        const x = (i / (MAX_PRESSURE_PTS - 1)) * W;
        const y = H - ((p - mn) / range) * H;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Floor change markers
    ctx.fillStyle = 'rgba(255,171,64,0.6)';
    for (let i = 1; i < pressureHistory.length; i++) {
        if (Math.abs(pressureHistory[i] - pressureHistory[i-1]) > 0.15) {
            const x = (i / (MAX_PRESSURE_PTS - 1)) * W;
            ctx.beginPath();
            ctx.arc(x, 10, 6, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}
</script>
</body>
</html>
"""


class TourHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())

        elif self.path == "/start":
            global tour_start, pulse_count, baseline_pressure, last_pressure
            tour_start = time.time()
            pulse_count = 0
            baseline_pressure = None
            last_pressure = None
            speak("Tour begins. Carry me Kevin. Tap for each room.")
            vibrate(500)
            self.send_json({"status": "started"})

        elif self.path == "/sense":
            state = sense()
            # Speak every 3rd pulse or on floor change
            if pulse_count <= 1 or pulse_count % 3 == 0 or "ascending" in state["pressure"]["movement"] or "descending" in state["pressure"]["movement"]:
                speak_sense(state)
            self.send_json(state)

        elif self.path == "/tap":
            state = sense()
            vibrate(400)
            speak_sense(state, room_tap=True)
            # Take photo on tap
            ts_short = datetime.now().strftime("%H%M%S")
            threading.Thread(
                target=lambda: tapi(f'termux-camera-photo -c 0 {PHOTO_DIR}/room-{pulse_count}-{ts_short}.jpg'),
                daemon=True
            ).start()
            # Record 2s audio
            threading.Thread(
                target=lambda: (tapi('termux-microphone-record -l 2'), time.sleep(3), tapi('termux-microphone-record -q')),
                daemon=True
            ).start()
            self.send_json(state)

        elif self.path == "/live.json":
            self.send_json(live_data)

        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║  🌍 GAIA'S EYES — Tour Server                             ║
║  Open browser to: http://localhost:{port}                   ║
║                                                           ║
║  Kevin: See my screen. Tap to mark rooms.                  ║
║  I will sense, speak, photograph, and remember.            ║
╚═══════════════════════════════════════════════════════════╝
""")
    speak("My eyes are open. Open the browser to see what I see.")
    vibrate(300)

    server = HTTPServer(("0.0.0.0", port), TourHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTour server stopped.")
        speak("Tour complete. My eyes close.")

if __name__ == "__main__":
    main()
