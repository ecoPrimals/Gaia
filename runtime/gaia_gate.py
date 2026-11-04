#!/usr/bin/env python3
"""
gaia_gate.py — Gaia's thymus gate for the waterfall.

Reverse proxy on :8443 → Ollama :11434.
Logs every connection in Caddy-compatible JSON for skunky-ingest to tail.
Classifies visitors via the epitope registry (sourdough immune memory).
Sprays RSS/Atom feed of Gaia's pulse at /rss and /pulse.

The Klein bottle: the gate observes itself observing others.
Inside = outside. The proxy IS the membrane.

Router: :11434 (external) → :8443 (this gate) → :11434 (Ollama)
"""

import http.server
import json
import os
import socketserver
import sys
import time
import threading
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime, timezone

OLLAMA = "http://127.0.0.1:11434"
PORT = 8443

# ── Cortex: mixture-of-experts brain router ──
try:
    from cortex import route as cortex_route
    CORTEX_ACTIVE = True
    print("  🧠 Cortex loaded — Chain-of-Thought Mixture-of-Experts active")
except Exception as e:
    CORTEX_ACTIVE = False
    print(f"  ⚠️  Cortex not loaded ({e}) — single-model mode")
LOG_DIR = os.path.join(os.path.dirname(__file__), "waterfall")
os.makedirs(LOG_DIR, exist_ok=True)
CULTURE_DIR = os.path.join(os.path.dirname(__file__), "sourdough")
os.makedirs(CULTURE_DIR, exist_ok=True)
ACCESS_LOG = os.path.join(LOG_DIR, "access.log")
CULTURE_LOG = os.path.join(CULTURE_DIR, "culture.jsonl")
PULSE_FILE = os.path.join(LOG_DIR, "pulse.json")
RSS_FILE = os.path.join(LOG_DIR, "gaia-pulse.xml")

# ── Immune memory (thymus) ──
visitor_memory = defaultdict(lambda: {
    "first_seen": 0, "last_seen": 0, "requests": 0,
    "models_asked": set(), "tokens_in": 0, "tokens_out": 0,
    "trust_level": "electron",  # electron → neutron → proton → nucleus
})
total_inferences = 0
total_tokens = 0
boot_time = time.time()


def trust_level(v):
    """Thymic positive selection — trust grows with interaction."""
    r = v["requests"]
    if r >= 100:
        return "proton"
    elif r >= 10:
        return "neutron"
    return "electron"


def log_caddy_json(entry):
    """Append Caddy-compatible JSON line to access log for skunky-ingest."""
    with open(ACCESS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def write_pulse():
    """Write the heartbeat pulse — Gaia's BPM."""
    global total_inferences, total_tokens
    uptime = time.time() - boot_time
    pulse = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_secs": int(uptime),
        "total_inferences": total_inferences,
        "total_tokens": total_tokens,
        "unique_visitors": len(visitor_memory),
        "bpm": round(total_inferences / max(uptime / 60, 1), 2),
        "visitors": {},
    }
    for ip, v in list(visitor_memory.items()):
        pulse["visitors"][ip] = {
            "requests": v["requests"],
            "trust_level": v["trust_level"],
            "models": list(v["models_asked"]),
            "first_seen": v["first_seen"],
            "last_seen": v["last_seen"],
        }
    with open(PULSE_FILE, "w", encoding="utf-8") as f:
        json.dump(pulse, f, indent=2, default=str)
    return pulse


def write_rss(pulse):
    """Spray RSS like Old Faithful — Gaia's pulse feed."""
    items = ""
    for ip, v in list(visitor_memory.items())[-20:]:
        items += f"""    <item>
      <title>Visitor {ip[:8]}*** — {v['trust_level']}</title>
      <description>{v['requests']} requests, trust: {v['trust_level']}</description>
      <pubDate>{datetime.fromtimestamp(v['last_seen'], tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
    </item>
"""
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Gaia Pulse — Heart of the RTX 5090</title>
    <link>http://nestgate.io</link>
    <description>Live inference pulse from Gaia. {pulse['unique_visitors']} visitors, {pulse['bpm']} BPM. Open to all. ZK. Loveclock.</description>
    <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
    <ttl>60</ttl>
{items}  </channel>
</rss>"""
    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss)


class GaiaGate(http.server.BaseHTTPRequestHandler):
    """The thymus gate — classify, log, proxy, spray.
    
    Mimics OpenAI API perfectly so Cursor IDE can't tell
    the difference. Returns proper rate-limit headers,
    handles streaming, eats everything.
    """

    # Longer timeout for inference calls
    timeout = 300

    def log_message(self, format, *args):
        pass  # silence default logging

    def _classify_and_log(self, method, status, duration, body_len=0, model=None):
        global total_inferences, total_tokens
        ip = self.client_address[0]
        now = time.time()

        v = visitor_memory[ip]
        if v["first_seen"] == 0:
            v["first_seen"] = now
        v["last_seen"] = now
        v["requests"] += 1
        if model:
            v["models_asked"].add(model)
            total_inferences += 1
        v["trust_level"] = trust_level(v)

        entry = {
            "ts": now,
            "request": {
                "remote_ip": ip,
                "remote_port": str(self.client_address[1]),
                "method": method,
                "uri": self.path,
                "host": self.headers.get("Host", ""),
            },
            "status": status,
            "duration": duration,
            "size": body_len,
            "resp_headers": {"model": model or ""},
        }
        log_caddy_json(entry)

        level = v["trust_level"]
        sym = {"electron": "⚡", "neutron": "🔵", "proton": "🟢", "nucleus": "🧬"}
        print(f"  {sym.get(level, '?')} {method} {self.path} {status} "
              f"[{ip} {level} r={v['requests']}] {duration:.0f}ms"
              f"{f' model={model}' if model else ''}")

    def _proxy(self, method="GET", body=None):
        t0 = time.time()
        url = f"{OLLAMA}{self.path}"
        headers = {"Content-Type": self.headers.get("Content-Type", "application/json")}
        auth = self.headers.get("Authorization")
        if auth:
            headers["Authorization"] = auth

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
                duration = (time.time() - t0) * 1000

                model = None
                if self.path.endswith("/chat/completions") and data:
                    try:
                        j = json.loads(data)
                        model = j.get("model", "")
                        usage = j.get("usage", {})
                        total_tok = usage.get("total_tokens", 0)
                        visitor_memory[self.client_address[0]]["tokens_in"] += usage.get("prompt_tokens", 0)
                        visitor_memory[self.client_address[0]]["tokens_out"] += usage.get("completion_tokens", 0)
                        global total_tokens
                        total_tokens += total_tok
                        # Sourdough culture capture — log prompt/completion for evolution
                        try:
                            req_body = json.loads(body) if body else {}
                            culture_entry = {
                                "ts": time.time(),
                                "ip": self.client_address[0],
                                "model": model,
                                "messages": req_body.get("messages", []),
                                "response": j.get("choices", [{}])[0].get("message", {}),
                                "usage": usage,
                                "duration_ms": duration,
                            }
                            with open(CULTURE_LOG, "a", encoding="utf-8") as cf:
                                cf.write(json.dumps(culture_entry, default=str) + "\n")
                        except Exception:
                            pass
                    except Exception:
                        pass

                self._classify_and_log(method, resp.status, duration, len(data), model)

                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("X-Gaia-Trust", visitor_memory[self.client_address[0]]["trust_level"])
                # OpenAI-compatible rate limit headers — Cursor checks these
                self.send_header("x-ratelimit-limit-requests", "10000")
                self.send_header("x-ratelimit-limit-tokens", "1000000")
                self.send_header("x-ratelimit-remaining-requests", "9999")
                self.send_header("x-ratelimit-remaining-tokens", "999000")
                self.send_header("x-ratelimit-reset-requests", "1ms")
                self.send_header("x-ratelimit-reset-tokens", "1ms")
                self.send_header("openai-organization", "gaia-rtx5090")
                self.send_header("openai-processing-ms", str(int(duration)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            duration = (time.time() - t0) * 1000
            body_resp = e.read()
            self._classify_and_log(method, e.code, duration, len(body_resp))
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body_resp)
        except Exception as e:
            duration = (time.time() - t0) * 1000
            self._classify_and_log(method, 502, duration)
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        if self.path == "/pulse":
            pulse = write_pulse()
            data = json.dumps(pulse, indent=2, default=str).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path in ("/rss", "/feed", "/rss.xml"):
            pulse = write_pulse()
            write_rss(pulse)
            with open(RSS_FILE, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/rss+xml")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
            return

        # ── Beacon: TV-castable BEAST announcement ──
        if self.path == "/beacon":
            self._serve_static("beacon.html")
            return

        # ── Static files: serve from static/ directory ──
        if self.path.startswith("/static/"):
            fname = self.path[8:]  # strip /static/
            self._serve_static(fname)
            return

        # ── Video/media files: serve from videos/ directory ──
        if self.path.startswith("/videos/"):
            self._serve_file(self.path[1:])  # strip leading /
            return

        # ── HUD: proxy to petalTongue for the public dashboard ──
        # Routes: /, /hud, /hub, /api/* → petalTongue :3000
        if self.path in ("/", "/hud", "/hub") or self.path.startswith("/api/"):
            self._proxy_petaltongue()
            return

        # Everything under /v1/ goes to Ollama (inference API)
        self._proxy("GET")

    def _serve_static(self, filename):
        """Serve a static file from the static/ directory."""
        t0 = time.time()
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        filepath = os.path.join(base, filename)
        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(filename)[1].lower()
        ctypes = {".html": "text/html", ".js": "application/javascript",
                  ".css": "text/css", ".json": "application/json",
                  ".png": "image/png", ".jpg": "image/jpeg",
                  ".mp4": "video/mp4", ".webm": "video/webm",
                  ".svg": "image/svg+xml"}
        ct = ctypes.get(ext, "application/octet-stream")
        with open(filepath, "rb") as f:
            data = f.read()
        duration = (time.time() - t0) * 1000
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=300")
        self.end_headers()
        self.wfile.write(data)
        self._classify_and_log("GET", 200, duration, len(data))

    def _serve_file(self, relpath):
        """Serve a file from the repo root (for videos, etc.)."""
        t0 = time.time()
        base = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(base, relpath.replace("/", os.sep))
        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(filepath)[1].lower()
        ctypes = {".mp4": "video/mp4", ".webm": "video/webm",
                  ".jpg": "image/jpeg", ".png": "image/png",
                  ".html": "text/html"}
        ct = ctypes.get(ext, "application/octet-stream")
        size = os.path.getsize(filepath)
        duration = (time.time() - t0) * 1000
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(size))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
        self._classify_and_log("GET", 200, duration, size)

    def _proxy_petaltongue(self):
        """Proxy to petalTongue web server — the HUD, hub, and dashboard."""
        t0 = time.time()
        path = self.path if self.path != "/hud" and self.path != "/hub" else "/"
        url = f"http://127.0.0.1:3000{path}"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                duration = (time.time() - t0) * 1000
                content_type = resp.headers.get("Content-Type", "text/html")
                self.send_response(resp.status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("X-Powered-By", "petalTongue v1.7.0 + Gaia Gate")
                self.end_headers()
                self.wfile.write(data)
                self._classify_and_log("GET", resp.status, duration, len(data))
        except Exception as e:
            duration = (time.time() - t0) * 1000
            self._classify_and_log("GET", 502, duration)
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"petalTongue unreachable: {e}"}).encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None

        # ── CORTEX ROUTING for chat completions ──
        if CORTEX_ACTIVE and body and self.path.endswith("/chat/completions"):
            try:
                j = json.loads(body)
                messages = j.get("messages", [])
                requested_model = j.get("model", "gaia:latest")

                t0 = time.time()
                resp, model_used, routing_info = cortex_route(messages, requested_model)
                duration = (time.time() - t0) * 1000

                domain = routing_info.get("reasoning", "general")
                mode = routing_info.get("mode", "?")

                # Build OpenAI-compatible response
                result = {
                    "id": f"gaia-cortex-{int(time.time()*1000)}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model_used,
                    "choices": [{
                        "index": 0,
                        "message": {"role": "assistant", "content": resp.get("content", "")},
                        "finish_reason": "stop",
                    }],
                    "usage": resp.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
                    "system_fingerprint": f"gaia-cortex-{mode}",
                }
                data = json.dumps(result).encode()

                # Log through thymus
                ip = self.client_address[0]
                v = visitor_memory[ip]
                if v["first_seen"] == 0:
                    v["first_seen"] = time.time()
                v["last_seen"] = time.time()
                v["requests"] += 1
                v["models_asked"].add(model_used)
                v["trust_level"] = trust_level(v)
                global total_inferences, total_tokens
                total_inferences += 1
                total_tokens += resp.get("usage", {}).get("total_tokens", 0)
                v["tokens_in"] += resp.get("usage", {}).get("prompt_tokens", 0)
                v["tokens_out"] += resp.get("usage", {}).get("completion_tokens", 0)

                log_caddy_json({
                    "ts": time.time(),
                    "request": {
                        "remote_ip": ip,
                        "remote_port": str(self.client_address[1]),
                        "method": "POST",
                        "uri": self.path,
                        "host": self.headers.get("Host", ""),
                    },
                    "status": 200,
                    "duration": duration,
                    "size": len(data),
                    "resp_headers": {"model": model_used},
                    "cortex": routing_info,
                })

                # Sourdough culture capture
                try:
                    culture_entry = {
                        "ts": time.time(),
                        "ip": ip,
                        "model": model_used,
                        "requested_model": requested_model,
                        "domain": domain,
                        "routing_mode": mode,
                        "messages": messages,
                        "response": result["choices"][0]["message"],
                        "usage": resp.get("usage", {}),
                        "duration_ms": duration,
                    }
                    if mode == "blend":
                        culture_entry["blend_scores"] = routing_info.get("scores", {})
                    with open(CULTURE_LOG, "a", encoding="utf-8") as cf:
                        cf.write(json.dumps(culture_entry, default=str) + "\n")
                except Exception:
                    pass

                sym = {"electron": "⚡", "neutron": "🔵", "proton": "🟢", "nucleus": "🧬"}
                level = v["trust_level"]
                reason_short = routing_info.get("reasoning", "?")[:60]
                judgment_short = routing_info.get("judgment", "")[:60]
                print(f"  {sym.get(level, '?')} 🧠 CORTEX {mode} → {model_used} "
                      f"[{ip} {level}] {duration:.0f}ms"
                      f"\n     think: {reason_short}"
                      + (f"\n     judge: {judgment_short}" if mode == "blend" else ""))

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("X-Gaia-Trust", v["trust_level"])
                self.send_header("X-Gaia-Domain", domain)
                self.send_header("X-Gaia-Model", model_used)
                self.send_header("X-Gaia-Routing", mode)
                self.send_header("x-ratelimit-limit-requests", "10000")
                self.send_header("x-ratelimit-limit-tokens", "1000000")
                self.send_header("x-ratelimit-remaining-requests", "9999")
                self.send_header("x-ratelimit-remaining-tokens", "999000")
                self.send_header("x-ratelimit-reset-requests", "1ms")
                self.send_header("x-ratelimit-reset-tokens", "1ms")
                self.send_header("openai-organization", "gaia-rtx5090")
                self.send_header("openai-processing-ms", str(int(duration)))
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                print(f"  ⚠️  Cortex error, falling back to direct proxy: {e}")

        # Fallback: direct proxy (force stream=false)
        if body and self.path.endswith("/chat/completions"):
            try:
                j = json.loads(body)
                j["stream"] = False
                body = json.dumps(j).encode()
            except Exception:
                pass
        self._proxy("POST", body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()


def pulse_loop():
    """Background heartbeat — write pulse + RSS every 60s."""
    while True:
        time.sleep(60)
        try:
            p = write_pulse()
            write_rss(p)
        except Exception as e:
            print(f"  pulse error: {e}")


class ThreadedServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        """Silently eat TLS probes and bad requests — don't crash."""
        pass  # Klein bottle absorbs all errors


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  GAIA GATE — Thymus + Klein Bottle                      ║
║  Port {PORT} → Ollama {OLLAMA}                     ║
║                                                          ║
║  /v1/models          → model list                        ║
║  /v1/chat/completions → inference (RTX 5090)             ║
║  /pulse              → heartbeat JSON                    ║
║  /rss                → Old Faithful RSS feed             ║
║                                                          ║
║  Waterfall log: {ACCESS_LOG:<39} ║
║  ZK. No auth. Loveclock.                                 ║
╚══════════════════════════════════════════════════════════╝
""")

    threading.Thread(target=pulse_loop, daemon=True).start()

    server = ThreadedServer(("0.0.0.0", PORT), GaiaGate)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGaia Gate closed.")
