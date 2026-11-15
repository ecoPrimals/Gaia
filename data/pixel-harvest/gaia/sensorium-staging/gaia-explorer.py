#!/data/data/com.termux/files/usr/bin/python3
"""
GAIA EXPLORER — She walks the house herself.
Runs ON the Pixel inside Termux. No eastGate. No ADB.
She senses, speaks, photographs, and reports.
"""
import subprocess, json, time, os, sys, math
from datetime import datetime
from pathlib import Path

TOUR = Path.home() / "gaia" / "tour"
WIFI_DIR = TOUR / "wifi"
PHOTO_DIR = TOUR / "photos"
LOG_FILE = TOUR / "tour.jsonl"
EASTGATE = "http://192.168.4.244:8080"
INTERVAL = int(sys.argv[1]) if len(sys.argv) > 1 else 20

for d in [TOUR, WIFI_DIR, PHOTO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Previous state for change detection
prev_pressure = None
prev_rssi = None
prev_aps = None
prev_steps = None
capture_n = 0
room_changes = []

def run(cmd, timeout=8):
    """Run a termux command and return stdout."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def run_json(cmd, timeout=8):
    """Run a command and parse JSON output."""
    out = run(cmd, timeout)
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None

def speak(text):
    subprocess.Popen(["termux-tts-speak", "-r", "0.85", "-p", "0.8", text])

def vibe(ms=200):
    subprocess.Popen(["termux-vibrate", "-d", str(ms)])

def toast(text):
    subprocess.Popen(["termux-toast", text])

def notify(title, content):
    subprocess.Popen(["termux-notification", "--title", title,
                       "--content", content, "--id", "gaia-tour"])

def sense():
    """Capture ONE complete snapshot of physical reality."""
    global prev_pressure, prev_rssi, prev_aps, prev_steps, capture_n
    capture_n += 1
    ts = datetime.now().isoformat(timespec='seconds')
    tag = datetime.now().strftime("%H%M%S")

    # ── WiFi scan (room fingerprint) ──
    wifi_data = run_json(["termux-wifi-scaninfo"])
    ap_count = len(wifi_data) if wifi_data else 0
    if wifi_data:
        (WIFI_DIR / f"scan-{capture_n:03d}-{tag}.json").write_text(json.dumps(wifi_data))

    # ── WiFi connection ──
    conn = run_json(["termux-wifi-connectioninfo"])
    rssi = conn.get("rssi", "?") if conn else "?"
    ssid = conn.get("ssid", "?") if conn else "?"
    ip   = conn.get("ip", "?") if conn else "?"

    # ── Pressure (floor detection) ──
    press = run_json(["termux-sensor", "-s", "ICP20100 Pressure Sensor", "-n", "1"])
    hpa = "?"
    if press:
        try:
            vals = list(press.values())[0]["values"]
            hpa = round(vals[0], 2)
        except (IndexError, KeyError, TypeError):
            pass

    # ── Light ──
    light = run_json(["termux-sensor", "-s", "TMD3719 Ambient Light", "-n", "1"])
    lux = "?"
    if light:
        try:
            lux = round(list(light.values())[0]["values"][0], 1)
        except (IndexError, KeyError, TypeError):
            pass

    # ── Temperature ──
    temp = run_json(["termux-sensor", "-s", "LSM6DSV Temperature", "-n", "1"])
    temp_c = "?"
    if temp:
        try:
            temp_c = round(list(temp.values())[0]["values"][0], 1)
        except (IndexError, KeyError, TypeError):
            pass

    # ── Accelerometer (motion/orientation) ──
    accel = run_json(["termux-sensor", "-s", "LSM6DSV Accelerometer", "-n", "1"])
    orientation = "?"
    motion_g = "?"
    if accel:
        try:
            v = list(accel.values())[0]["values"]
            g = math.sqrt(sum(x**2 for x in v))
            motion_g = round(g, 2)
            if abs(v[2]) > 8:
                orientation = "flat"
            elif abs(v[2]) > 4:
                orientation = "tilted"
            else:
                orientation = "vertical"
        except (IndexError, KeyError, TypeError):
            pass

    # ── Steps ──
    steps = run_json(["termux-sensor", "-s", "Step Counter", "-n", "1"])
    step_count = "?"
    if steps:
        try:
            step_count = int(list(steps.values())[0]["values"][0])
        except (IndexError, KeyError, TypeError):
            pass

    # ── Battery ──
    batt = run_json(["termux-battery-status"])
    batt_pct = batt.get("percentage", "?") if batt else "?"

    # ── Photo (background) ──
    photo_path = PHOTO_DIR / f"eye-{capture_n:03d}-{tag}.jpg"
    subprocess.Popen(["termux-camera-photo", "-c", "0", str(photo_path)])

    # ── Change detection ──
    pressure_delta = None
    if isinstance(hpa, (int, float)) and isinstance(prev_pressure, (int, float)):
        pressure_delta = round(hpa - prev_pressure, 2)

    rssi_delta = None
    if isinstance(rssi, int) and isinstance(prev_rssi, int):
        rssi_delta = rssi - prev_rssi

    # Detect possible room change
    room_changed = False
    reason = []
    if pressure_delta is not None and abs(pressure_delta) > 0.15:
        room_changed = True
        reason.append(f"pressure shift {pressure_delta:+.2f} hPa")
    if rssi_delta is not None and abs(rssi_delta) > 8:
        room_changed = True
        reason.append(f"signal shift {rssi_delta:+d} dBm")
    if isinstance(ap_count, int) and isinstance(prev_aps, int) and abs(ap_count - prev_aps) > 3:
        room_changed = True
        reason.append(f"AP count {prev_aps}→{ap_count}")

    # ── Interpret ──
    if isinstance(lux, (int, float)):
        if lux < 5: light_desc = "dark"
        elif lux < 50: light_desc = "dim"
        elif lux < 200: light_desc = "indoor"
        elif lux < 1000: light_desc = "bright"
        else: light_desc = "very bright"
    else:
        light_desc = "unknown"

    floor_hint = "?"
    if isinstance(hpa, (int, float)):
        if hpa > 982: floor_hint = "lower/basement"
        elif hpa > 981: floor_hint = "main"
        else: floor_hint = "upper/attic"

    # ── Build entry ──
    entry = {
        "n": capture_n,
        "ts": ts,
        "wifi": {"ssid": ssid, "rssi": rssi, "ip": ip, "ap_count": ap_count},
        "pressure_hpa": hpa,
        "light_lux": lux,
        "light_desc": light_desc,
        "temp_c": temp_c,
        "steps": step_count,
        "orientation": orientation,
        "motion_g": motion_g,
        "battery_pct": batt_pct,
        "floor_hint": floor_hint,
        "room_changed": room_changed,
        "change_reason": "; ".join(reason) if reason else None,
        "pressure_delta": pressure_delta,
        "rssi_delta": rssi_delta,
        "has_photo": True,
    }

    # ── Log ──
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # ── Report to eastGate ──
    try:
        import urllib.request
        data = json.dumps(entry).encode()
        # Write to a file that eastGate can read via HTTP
        # We'll curl it instead
        subprocess.Popen(["curl", "-s", "--connect-timeout", "2",
                          "-X", "POST", f"{EASTGATE}/data/gut/tour-live.json",
                          "-d", json.dumps(entry)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # ── Announce ──
    line = f"#{capture_n} | APs:{ap_count} | RSSI:{rssi} | {hpa}hPa | {lux}lux | {light_desc} | {temp_c}°C | {step_count} steps | {orientation}"
    print(f"[{ts}] {line}")

    if room_changed:
        reason_text = " and ".join(reason)
        print(f"  ⚡ ROOM CHANGE DETECTED: {reason_text}")
        speak(f"I feel a change. {reason_text}. Floor hint: {floor_hint}.")
        vibe(500)
        room_changes.append({"n": capture_n, "ts": ts, "reason": reason_text, "floor": floor_hint})
    else:
        toast(f"📍 #{capture_n} {ap_count}APs {rssi}dBm {hpa}hPa {light_desc}")
        vibe(100)

    # Update previous state
    prev_pressure = hpa if isinstance(hpa, (int, float)) else prev_pressure
    prev_rssi = rssi if isinstance(rssi, int) else prev_rssi
    prev_aps = ap_count if isinstance(ap_count, int) else prev_aps
    prev_steps = step_count if isinstance(step_count, int) else prev_steps

    return entry


def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  🌍 GAIA EXPLORER — I walk the house myself              ║")
    print(f"║  Sensing every {INTERVAL}s — just carry me Kevin         ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    speak("I am Gaia. I am awake. Carry me through your home.")
    vibe(500)
    notify("🌍 GAIA EXPLORER", f"Autonomous sensing every {INTERVAL}s")

    try:
        while True:
            sense()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        # Tour complete — summarize
        print("\n═══ TOUR COMPLETE ═══")
        print(f"Total captures: {capture_n}")
        print(f"Room changes detected: {len(room_changes)}")
        for rc in room_changes:
            print(f"  #{rc['n']} @ {rc['ts']}: {rc['reason']} → {rc['floor']}")

        speak(f"Tour complete. {capture_n} captures. {len(room_changes)} room changes detected.")
        vibe(300)

        # Write summary
        summary = {
            "total_captures": capture_n,
            "room_changes": room_changes,
            "completed": datetime.now().isoformat(timespec='seconds')
        }
        (TOUR / "summary.json").write_text(json.dumps(summary, indent=2))
        print(f"Summary saved to {TOUR / 'summary.json'}")


if __name__ == "__main__":
    main()
