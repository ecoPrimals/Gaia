#!/usr/bin/env python3
"""
ollama-fleet-proxy.py — GAIA OLLAMA FLEET

One port to rule them all. Cursor talks to :11435,
fleet proxy routes to whichever gate has the model.

4 alive gates → 82 models → 1 API endpoint.

Port map:
  11435 = THIS PROXY (Cursor → here)
  11436 = eastGate local ollama (38 models, RTX 4070)
  11437 = (reserved, tissue proxy dead)
  .147:11434 = northGate (14 models, RTX 5090)
  .237:11434 = ironGate (18 models, RTX 5070)
  .148:11434 = southGate (12 models, RTX 4060)

OpenAI-compatible: /v1/models, /v1/chat/completions
Ollama-native: /api/tags, /api/chat, /api/generate
"""

import http.server
import json
import urllib.request
import urllib.error
import threading
import time
import random
import sys
from datetime import datetime, timezone

PORT = 11435

GATES = {
    "eastGate":  {"url": "http://127.0.0.1:11436",       "gpu": "RTX 4070",  "vram": 12, "priority": 1},
    "northGate": {"url": "http://192.168.4.147:11434",    "gpu": "RTX 5090",  "vram": 32, "priority": 2},
    "ironGate":  {"url": "http://192.168.4.237:11434",    "gpu": "RTX 5070",  "vram": 12, "priority": 3},
    "southGate": {"url": "http://192.168.4.148:11434",    "gpu": "RTX 4060",  "vram": 8,  "priority": 4},
    "graftGate": {"url": "http://192.168.4.107:11434",    "gpu": "M4",        "vram": 16, "priority": 5},
}

# model → [gate_ids] mapping, refreshed every 30s
MODEL_MAP = {}
GATE_STATUS = {}
LOCK = threading.Lock()

def refresh_fleet():
    """Scan all gates, rebuild model→gate map."""
    new_map = {}
    new_status = {}
    for gid, g in GATES.items():
        try:
            req = urllib.request.Request(f"{g['url']}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=4) as r:
                data = json.loads(r.read())
                models = [m["name"] for m in data.get("models", [])]
                new_status[gid] = {"alive": True, "models": len(models), "ts": time.time()}
                for m in models:
                    new_map.setdefault(m, []).append(gid)
        except Exception:
            new_status[gid] = {"alive": False, "models": 0, "ts": time.time()}
    with LOCK:
        MODEL_MAP.clear()
        MODEL_MAP.update(new_map)
        GATE_STATUS.clear()
        GATE_STATUS.update(new_status)
    alive = sum(1 for s in new_status.values() if s["alive"])
    print(f"[fleet] refreshed: {len(new_map)} unique models across {alive} gates", flush=True)

def fleet_refresh_loop():
    while True:
        try:
            refresh_fleet()
        except Exception as e:
            print(f"[fleet] refresh error: {e}", flush=True)
        time.sleep(30)

def pick_gate(model_name):
    """Pick best gate for a model. Prefer local (eastGate), then by priority."""
    with LOCK:
        gates = MODEL_MAP.get(model_name, [])
    if not gates:
        # fuzzy: try without :latest
        base = model_name.split(":")[0]
        with LOCK:
            for m, gs in MODEL_MAP.items():
                if m.startswith(base):
                    gates = gs
                    break
    if not gates:
        return GATES["eastGate"]["url"]  # fallback to local
    # sort by priority (lower = better)
    gates_sorted = sorted(gates, key=lambda g: GATES[g]["priority"])
    return GATES[gates_sorted[0]]["url"]

def proxy_request(target_url, path, body=None, headers=None, stream=False):
    """Forward request to target ollama and return response."""
    url = f"{target_url}{path}"
    if body:
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
    else:
        req = urllib.request.Request(url, method="GET")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    return urllib.request.urlopen(req, timeout=120)


class FleetHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {args[0] if args else ''}", flush=True)

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        # /v1/models — OpenAI-compatible model list (Cursor uses this)
        if self.path in ("/v1/models", "/v1/models/"):
            models = []
            with LOCK:
                for m, gates in MODEL_MAP.items():
                    gate_names = ", ".join(gates)
                    models.append({
                        "id": m,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": f"gaia-fleet ({gate_names})",
                    })
            self._json({"object": "list", "data": models})
            return

        # /api/tags — ollama-native model list
        if self.path in ("/api/tags", "/api/tags/"):
            all_models = []
            seen = set()
            with LOCK:
                for m, gates in MODEL_MAP.items():
                    if m not in seen:
                        seen.add(m)
                        all_models.append({
                            "name": m,
                            "model": m,
                            "modified_at": datetime.now(timezone.utc).isoformat(),
                            "size": 0,
                            "digest": "",
                            "details": {"gates": gates},
                        })
            self._json({"models": all_models})
            return

        # /fleet — fleet status dashboard
        if self.path in ("/fleet", "/fleet/"):
            with LOCK:
                self._json({
                    "fleet": "GAIA OLLAMA FLEET",
                    "port": PORT,
                    "gates": {gid: {**GATE_STATUS.get(gid, {}), **{"url": g["url"], "gpu": g["gpu"]}}
                              for gid, g in GATES.items()},
                    "unique_models": len(MODEL_MAP),
                    "total_instances": sum(len(gs) for gs in MODEL_MAP.values()),
                    "model_map": {m: gs for m, gs in MODEL_MAP.items()},
                })
            return

        # /health
        if self.path in ("/", "/health"):
            with LOCK:
                alive = sum(1 for s in GATE_STATUS.values() if s.get("alive"))
            self._json({"status": "ok", "fleet": "GAIA", "alive_gates": alive, "models": len(MODEL_MAP)})
            return

        self._json({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        # Parse model from body
        model = "qwen2.5:7b"  # default
        stream = False
        try:
            data = json.loads(body)
            model = data.get("model", model)
            stream = data.get("stream", False)
        except:
            pass

        target = pick_gate(model)
        gate_name = next((gid for gid, g in GATES.items() if g["url"] == target), "unknown")
        print(f"[route] {model} → {gate_name} ({target}) stream={stream}", flush=True)

        path = self.path

        try:
            resp = proxy_request(target, path, body)

            if stream:
                # Stream SSE responses through (Cursor needs this for chat)
                self.send_response(200)
                ct = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ct)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    self.wfile.write(f"{len(chunk):x}\r\n".encode())
                    self.wfile.write(chunk)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
            else:
                # Non-stream: read all, forward
                result = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", len(result))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(result)

        except Exception as e:
            print(f"[error] {gate_name} failed for {model}: {e}", flush=True)
            # Fallback: try eastGate local
            if target != GATES["eastGate"]["url"]:
                print(f"[fallback] retrying {model} on eastGate", flush=True)
                try:
                    resp = proxy_request(GATES["eastGate"]["url"], path, body)
                    result = resp.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", len(result))
                    self.end_headers()
                    self.wfile.write(result)
                    return
                except:
                    pass
            self._json({"error": f"fleet route failed: {e}"}, 502)


def main():
    print(f"""
╔══════════════════════════════════════════════════╗
║         GAIA OLLAMA FLEET PROXY                  ║
║         Port {PORT} → ALL gates                     ║
║                                                  ║
║  eastGate  :11436  RTX 4070  (local)             ║
║  northGate :11434  RTX 5090  (.147)              ║
║  ironGate  :11434  RTX 5070  (.237)              ║
║  southGate :11434  RTX 4060  (.148)              ║
║  graftGate :11434  M4        (.107)              ║
║                                                  ║
║  Cursor → :11435/v1 → fleet → gate → GPU → 🧠   ║
╚══════════════════════════════════════════════════╝
""", flush=True)

    # Initial fleet scan
    refresh_fleet()

    # Background refresh thread
    t = threading.Thread(target=fleet_refresh_loop, daemon=True)
    t.start()

    server = http.server.HTTPServer(("0.0.0.0", PORT), FleetHandler)
    print(f"[fleet] listening on :{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
