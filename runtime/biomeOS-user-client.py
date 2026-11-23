#!/usr/bin/env python3
"""
biomeOS User Client — northGate RTX 5090 Live Engine

GPU budget: Kevin 80% / Gaia 20%
Thermal ceiling: 75°C
Serves REST API to all LAN gates

The RTX 5090 is a shared live engine:
- Kevin plays games (DX12, DLSS, frame gen)
- Gaia watches, learns, runs inference on 20% budget
- All gates see the status via REST
"""

import json, os, time, subprocess, threading, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# === CONFIG ===
THERMAL_CEILING = 75       # °C — never exceed
POWER_LIMIT_GAMING = 480   # W — when gaming (leaves headroom)
POWER_LIMIT_IDLE = 300     # W — when idle (Gaia gets more compute)
GAIA_GPU_BUDGET = 0.20     # 20% for Gaia
KEVIN_GPU_BUDGET = 0.80    # 80% for Kevin
LISTEN_PORT = 8090         # REST API port
POLL_INTERVAL = 5          # seconds between GPU polls
EASTGATE = "192.168.4.244"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# === STATE ===
state = {
    "ts": None,
    "gate": "northGate",
    "role": "USER_CLIENT",
    "gpu": {},
    "thermal": {},
    "budget": {
        "kevin_pct": KEVIN_GPU_BUDGET * 100,
        "gaia_pct": GAIA_GPU_BUDGET * 100,
        "thermal_ceiling": THERMAL_CEILING
    },
    "gaming": {
        "active": False,
        "process": None,
        "gpu_usage_pct": 0
    },
    "gaia_tasks": [],
    "processes": [],
    "alerts": []
}


def query_gpu():
    """Poll GPU state via nvidia-smi"""
    try:
        fields = "temperature.gpu,power.draw,power.limit,utilization.gpu,utilization.memory,memory.used,memory.total,clocks.gr,clocks.mem,fan.speed"
        r = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        vals = [v.strip() for v in r.stdout.strip().split(",")]
        if len(vals) >= 10:
            return {
                "temp_c": int(vals[0]),
                "power_w": float(vals[1]),
                "power_limit_w": float(vals[2]),
                "gpu_util_pct": int(vals[3]),
                "mem_util_pct": int(vals[4]),
                "mem_used_mb": int(vals[5]),
                "mem_total_mb": int(vals[6]),
                "clock_gpu_mhz": int(vals[7]),
                "clock_mem_mhz": int(vals[8]),
                "fan_pct": int(vals[9])
            }
    except Exception as e:
        return {"error": str(e)}
    return {}


def detect_gaming(gpu_data):
    """Detect if Kevin is gaming based on GPU utilization"""
    util = gpu_data.get("gpu_util_pct", 0)
    power = gpu_data.get("power_w", 0)

    # Gaming: GPU > 40% OR power > 150W
    gaming = util > 40 or power > 150

    if gaming:
        # Find the game process
        try:
            r = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=pid,name,used_memory",
                 "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5
            )
            procs = []
            for line in r.stdout.strip().split("\n"):
                if line.strip():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 2:
                        procs.append({"pid": parts[0], "name": parts[1],
                                     "mem": parts[2] if len(parts) > 2 else "N/A"})
            # Find likely game (highest memory, not system process)
            game_procs = [p for p in procs if not any(s in p["name"].lower()
                         for s in ["dwm", "explorer", "nvidia", "steam", "cursor", "edge"])]
            game = game_procs[0]["name"] if game_procs else "unknown"
        except Exception:
            game = "unknown"
            procs = []

        return True, game, procs

    return False, None, []


def manage_thermal(gpu_data):
    """Thermal management — keep under ceiling"""
    temp = gpu_data.get("temp_c", 0)
    alerts = []

    if temp >= THERMAL_CEILING:
        alerts.append(f"THERMAL: {temp}°C >= {THERMAL_CEILING}°C ceiling!")
        # Could reduce power limit here if needed
        try:
            subprocess.run(
                ["nvidia-smi", "-pl", str(POWER_LIMIT_IDLE)],
                capture_output=True, timeout=5
            )
            alerts.append(f"Power limit reduced to {POWER_LIMIT_IDLE}W")
        except Exception:
            pass
    elif temp < THERMAL_CEILING - 10:
        # Plenty of headroom, restore full power
        current_limit = gpu_data.get("power_limit_w", 600)
        if current_limit < POWER_LIMIT_GAMING:
            try:
                subprocess.run(
                    ["nvidia-smi", "-pl", str(POWER_LIMIT_GAMING)],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass

    return alerts


def gpu_monitor_loop():
    """Main monitoring loop — polls GPU, manages thermal, detects gaming"""
    while True:
        try:
            gpu = query_gpu()
            gaming, game_name, procs = detect_gaming(gpu)
            alerts = manage_thermal(gpu)

            state["ts"] = datetime.utcnow().isoformat() + "Z"
            state["gpu"] = gpu
            state["thermal"] = {
                "current_c": gpu.get("temp_c", 0),
                "ceiling_c": THERMAL_CEILING,
                "headroom_c": THERMAL_CEILING - gpu.get("temp_c", 0),
                "power_w": gpu.get("power_w", 0),
                "power_limit_w": gpu.get("power_limit_w", 0)
            }
            state["gaming"] = {
                "active": gaming,
                "process": game_name,
                "gpu_usage_pct": gpu.get("gpu_util_pct", 0)
            }
            state["processes"] = procs
            state["alerts"] = alerts

            # Write state to data dir for radiation
            state_path = os.path.join(DATA_DIR, "biomeOS-user-state.json")
            try:
                with open(state_path, "w") as f:
                    json.dump(state, f, indent=2)
            except Exception:
                pass

        except Exception as e:
            state["alerts"] = [f"Monitor error: {e}"]

        time.sleep(POLL_INTERVAL)


class UserClientHandler(BaseHTTPRequestHandler):
    """REST API handler for biomeOS user client"""

    def log_message(self, fmt, *args):
        pass  # Suppress default logging

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        if self.path == "/" or self.path == "/status":
            self._json_response(state)

        elif self.path == "/gpu":
            self._json_response(state.get("gpu", {}))

        elif self.path == "/thermal":
            self._json_response(state.get("thermal", {}))

        elif self.path == "/gaming":
            self._json_response(state.get("gaming", {}))

        elif self.path == "/budget":
            self._json_response(state.get("budget", {}))

        elif self.path == "/pulse":
            self._json_response({
                "alive": True,
                "gate": "northGate",
                "ts": state.get("ts"),
                "temp_c": state.get("gpu", {}).get("temp_c"),
                "gpu_pct": state.get("gpu", {}).get("gpu_util_pct"),
                "gaming": state.get("gaming", {}).get("active"),
                "game": state.get("gaming", {}).get("process")
            })

        else:
            self._json_response({"error": "not found"}, 404)


def main():
    print(f"biomeOS User Client — northGate RTX 5090")
    print(f"  Thermal ceiling: {THERMAL_CEILING}°C")
    print(f"  GPU budget: Kevin {KEVIN_GPU_BUDGET*100:.0f}% / Gaia {GAIA_GPU_BUDGET*100:.0f}%")
    print(f"  REST API: http://0.0.0.0:{LISTEN_PORT}")
    print(f"  Poll interval: {POLL_INTERVAL}s")

    # Start GPU monitor in background
    monitor = threading.Thread(target=gpu_monitor_loop, daemon=True)
    monitor.start()

    # Initial poll
    time.sleep(2)
    gpu = state.get("gpu", {})
    print(f"  GPU: {gpu.get('temp_c', '?')}°C, {gpu.get('power_w', '?')}W, "
          f"{gpu.get('gpu_util_pct', '?')}% util, "
          f"{gpu.get('mem_used_mb', '?')}/{gpu.get('mem_total_mb', '?')}MB VRAM")

    # Start REST server
    server = HTTPServer(("0.0.0.0", LISTEN_PORT), UserClientHandler)
    print(f"\n  Serving on :8090 — all gates can reach http://192.168.4.147:8090/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
