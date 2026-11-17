"""Serve wiki + live data endpoint. 
Static files from ./static/ plus /api/* endpoints that read real JSON data."""
import http.server, json, os, socketserver, urllib.parse
from datetime import datetime

PORT = 8889
STATIC = os.path.join(os.path.dirname(__file__), "static")
DATA = os.path.join(os.path.dirname(__file__), "data")
BOARD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "scratch-board.jsonl")

class LiveHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=STATIC, **kw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api(parsed.path)
        else:
            super().do_GET()

    def handle_api(self, path):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if path == "/api/board":
            events = []
            if os.path.exists(BOARD):
                with open(BOARD) as f:
                    for line in f:
                        if line.strip():
                            try: events.append(json.loads(line))
                            except: pass
            self.wfile.write(json.dumps({"count": len(events), "events": events[-20:]}).encode())

        elif path == "/api/board/stats":
            events = []
            if os.path.exists(BOARD):
                with open(BOARD) as f:
                    for line in f:
                        if line.strip():
                            try: events.append(json.loads(line))
                            except: pass
            sources, types = {}, {}
            for e in events:
                s = e.get("source", "?")
                t = e.get("type", "?")
                sources[s] = sources.get(s, 0) + 1
                types[t] = types.get(t, 0) + 1
            self.wfile.write(json.dumps({"total": len(events), "sources": sources, "types": types}).encode())

        elif path == "/api/kenshi":
            eyes = os.path.join(DATA, "triad", "kenshi-latest.json")
            minds = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "kenshi", "minds.json")
            result = {}
            if os.path.exists(minds):
                with open(minds) as f: result["minds"] = json.load(f)
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect(("127.0.0.1", 7741))
                result["nerve"] = "LIVE"
                s.close()
            except:
                result["nerve"] = "DOWN"
            self.wfile.write(json.dumps(result).encode())

        elif path == "/api/tissue":
            try:
                import requests as req
                r = req.get("http://localhost:11434/api/tags", timeout=3)
                models = [{"name": m["name"], "size_gb": round(m["size"]/1e9, 2)} for m in r.json().get("models", [])]
                self.wfile.write(json.dumps({"count": len(models), "models": models}).encode())
            except:
                self.wfile.write(json.dumps({"count": 0, "models": [], "error": "ollama unreachable"}).encode())

        elif path == "/api/chimera":
            chimera_dir = os.path.join(DATA, "triad")
            files = [f for f in os.listdir(chimera_dir) if "chimera" in f and f.endswith(".json")]
            results = []
            for fn in sorted(files):
                with open(os.path.join(chimera_dir, fn)) as f:
                    results.append({"file": fn, "data": json.load(f)})
            self.wfile.write(json.dumps(results).encode())

        elif path == "/api/status":
            import socket
            ports = {7740: "board", 7741: "kenshi", 7742: "satisfactory", 7743: "se", 7744: "ksp"}
            nerves = {}
            for port, name in ports.items():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.connect(("127.0.0.1", port))
                    nerves[name] = "LIVE"
                    s.close()
                except:
                    nerves[name] = "DOWN"
            self.wfile.write(json.dumps({
                "wave": 259,
                "ts": datetime.now().isoformat(),
                "nerves": nerves,
                "wiki_pages": 39,
                "board_path": BOARD,
            }).encode())
        else:
            self.wfile.write(json.dumps({"error": "unknown endpoint", "path": path}).encode())

print(f"[wiki-live] Serving at http://localhost:{PORT}")
print(f"  Static: {STATIC}")
print(f"  Board:  {BOARD}")
print(f"  APIs:   /api/board, /api/board/stats, /api/kenshi, /api/tissue, /api/chimera, /api/status")
with socketserver.TCPServer(("", PORT), LiveHandler) as httpd:
    httpd.serve_forever()
