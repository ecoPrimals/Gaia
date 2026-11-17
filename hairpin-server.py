"""Hairpin server — serves Gaia's wiki + API on port 8080.
When eastGate is FLUX, this keeps hud.primals.eco alive from blueGate.
Hosts file points primals.eco domains → 127.0.0.1, this catches them."""
import http.server, json, os, socketserver, urllib.parse, urllib.request

PORT = 8080
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
WIKI_API = "http://localhost:8889"

class HairpinHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=STATIC, **kw)

    def do_GET(self):
        host = self.headers.get("Host", "")
        path = self.path

        # API proxy to live server
        if path.startswith("/api/"):
            try:
                r = urllib.request.urlopen(f"{WIKI_API}{path}", timeout=5)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(r.read())
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # Serve wiki.html as default for hud.primals.eco
        if "hud.primals" in host or path == "/" or path == "":
            self.path = "/wiki.html"

        # For primals.eco root, show wiki too
        if path == "/" and ("primals" in host or "localhost" in host):
            self.path = "/wiki.html"

        super().do_GET()

    def log_message(self, fmt, *args):
        print(f"[hairpin] {self.client_address[0]} → {self.headers.get('Host','?')}{self.path}")

print(f"""
╔══════════════════════════════════════════╗
║  HAIRPIN SERVER — eastGate bypass        ║
║  Port: {PORT}                              ║
║  Static: {STATIC}
║  API proxy: {WIKI_API}
║                                          ║
║  hud.primals.eco:{PORT} → wiki.html        ║
║  primals.eco:{PORT} → wiki.html            ║
║  localhost:{PORT} → wiki.html              ║
║  /api/* → live API server :{PORT+1}         ║
╚══════════════════════════════════════════╝
""")

with socketserver.TCPServer(("0.0.0.0", PORT), HairpinHandler) as httpd:
    httpd.serve_forever()
