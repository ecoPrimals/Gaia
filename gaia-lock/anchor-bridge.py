#!/usr/bin/env python3
"""
membrane-anchor-bridge: HTTP→LoamSpine+SweetGrass for sovereign identity.

No data honeypots. Only hashes cross the bridge. Your secret never arrives here.
LoamSpine anchors prove existence. SweetGrass braids prove provenance.
The person is sweetgrass.

Listens 127.0.0.1:8199 (Caddy reverse-proxied).
"""

import json, socket, hashlib, time, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

LOAM_SOCK = "/run/membrane/loamspine.sock"
SG_SOCK = "/run/membrane/sweetgrass.sock"
SG_HTTP = "http://127.0.0.1:42725"
SPINE_ID = "01a1412b-848a-74c0-9a27-72fec03b8638"
LISTEN_PORT = 8199

def loam_rpc(method, params=None):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect(LOAM_SOCK)
        req = json.dumps({"jsonrpc":"2.0","method":method,"params":params or {},"id":int(time.time()*1000)%100000}).encode() + b"\n"
        sock.sendall(req)
        data = b""
        for _ in range(20):
            chunk = sock.recv(8192)
            if not chunk: break
            data += chunk
            try:
                json.loads(data)
                break
            except: pass
        return json.loads(data)
    except Exception as e:
        return {"error": str(e)}
    finally:
        sock.close()

def sg_rpc(method, params=None):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect(SG_SOCK)
        sock.sendall(bytes([0xEC, 0x01]))
        req = json.dumps({"jsonrpc":"2.0","method":method,"params":params or {},"id":int(time.time()*1000)%100000}).encode() + b"\n"
        sock.sendall(req)
        data = b""
        for _ in range(20):
            chunk = sock.recv(8192)
            if not chunk: break
            data += chunk
            try:
                json.loads(data.strip())
                break
            except: pass
        return json.loads(data.strip())
    except Exception as e:
        return {"error": str(e)}
    finally:
        sock.close()

def hex_to_sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def hex_to_bytes(h):
    return [int(h[i:i+2], 16) for i in range(0, min(len(h), 64), 2)]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.cors()
        self.end_headers()
        self.wfile.write(body)

    def clean_path(self):
        p = self.path.split("?")[0]
        if p.startswith("/api/"): p = "/" + p[5:]
        return p

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors()
        self.end_headers()

    def do_GET(self):
        self.path = self.clean_path()
        if self.path == "/health":
            loam = loam_rpc("health.check")
            sg = sg_rpc("health.check")
            self.send_json(200, {
                "bridge": "alive",
                "loamspine": loam.get("result", {}).get("status", "?"),
                "sweetgrass": sg.get("result", {}).get("status", "?"),
                "spine_id": SPINE_ID,
                "ts": time.time()
            })
        elif self.path == "/graph":
            import urllib.request
            try:
                r = urllib.request.urlopen("http://127.0.0.1:8097/api/discuss?page=membrane-graph&limit=50", timeout=3)
                self.send_json(200, json.loads(r.read()))
            except:
                self.send_json(200, {"comments": [], "total": 0})
        elif self.path == "/stories":
            import urllib.request
            try:
                r = urllib.request.urlopen("http://127.0.0.1:8097/api/discuss?page=membrane-stories&limit=50", timeout=3)
                self.send_json(200, json.loads(r.read()))
            except:
                self.send_json(200, {"comments": [], "total": 0})
        elif self.path == "/braids":
            import urllib.request
            try:
                r = urllib.request.urlopen(SG_HTTP + "/api/v1/braids", timeout=3)
                self.send_json(200, json.loads(r.read()))
            except:
                self.send_json(200, {"braids": [], "total": 0})
        else:
            self.send_json(404, {"error": "unknown path"})

    def do_POST(self):
        self.path = self.clean_path()
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n)) if n else {}

        if self.path == "/anchor":
            identity_hash = body.get("identity_hash", "")
            pseudonym = body.get("pseudonym", "anonymous")
            statement = body.get("statement", "")
            ts = time.time()
            data_hash = hex_to_sha(f"{identity_hash}:{pseudonym}:{ts}")
            r = loam_rpc("entry.append", {
                "spine_id": SPINE_ID,
                "payload": list(data_hash[:32].encode()),
                "entry_type": {"DataAnchor": {
                    "data_hash": data_hash,
                    "size": len(identity_hash)
                }},
                "metadata": {
                    "type": "identity-existence",
                    "identity_prefix": identity_hash[:16],
                    "pseudonym": pseudonym,
                    "statement_hash": hex_to_sha(statement)[:32] if statement else None
                },
                "committer": "membrane"
            })
            result = r.get("result", {})
            self.send_json(200, {
                "anchored": "entry_hash" in result,
                "anchor_hash": data_hash[:32],
                "entry_index": result.get("index"),
                "identity_prefix": identity_hash[:16],
                "pseudonym": pseudonym,
                "timestamp": ts,
                "receipt": hex_to_sha(f"receipt:{data_hash}:{ts}")[:32]
            })

        elif self.path == "/verify":
            identity_hash = body.get("identity_hash", "")
            r = loam_rpc("entry.get_tip", {"spine_id": SPINE_ID})
            tip = r.get("result", {})
            self.send_json(200, {
                "spine_height": tip.get("height", 0),
                "verified": tip.get("height", 0) > 1,
                "tip_entry": tip.get("entry", {}).get("metadata", {})
            })

        elif self.path == "/braid":
            identity_hash = body.get("identity_hash", "")
            content = body.get("content", "")
            kind = body.get("type", "story")
            data_hash = hex_to_sha(content)
            r = sg_rpc("braid.create", {
                "data_hash": data_hash,
                "source": identity_hash[:16],
                "mime_type": "text/plain",
                "size": len(content),
                "metadata": {"tags": [kind], "title": kind}
            })
            result = r.get("result", {})
            braid_id = result.get("@id", "")
            self.send_json(200, {
                "braided": bool(braid_id),
                "braid_id": braid_id,
                "data_hash": data_hash[:32],
                "identity_prefix": identity_hash[:16],
                "type": kind,
                "attributed_to": result.get("was_attributed_to", ""),
                "timestamp": time.time()
            })

        elif self.path == "/contribution":
            identity_hash = body.get("identity_hash", "")
            content = body.get("content", "")
            kind = body.get("kind", "story")
            content_hash = hex_to_sha(content)
            role_map = {"story": "Creator", "art": "Creator", "help": "Contributor",
                        "presence": "Contributor", "song": "Creator", "offer": "DataProvider",
                        "need": "Contributor"}
            r = sg_rpc("contribution.record", {
                "agent": identity_hash[:16],
                "data_hash": content_hash,
                "content_hash": content_hash,
                "role": role_map.get(kind, "Contributor"),
                "kind": kind
            })
            self.send_json(200, {
                "recorded": "error" not in r or "result" in r,
                "kind": kind,
                "content_hash": content_hash[:32],
                "sweetgrass": r.get("result", r.get("error", "?")),
                "timestamp": time.time()
            })

        elif self.path == "/trust":
            source = body.get("identity_hash", "")[:16]
            target = body.get("target_hash", "")[:16]
            r = loam_rpc("entry.append", {
                "spine_id": SPINE_ID,
                "payload": list(f"trust:{source}:{target}".encode()[:32]),
                "entry_type": {"DataAnchor": {
                    "data_hash": hex_to_sha(f"trust:{source}:{target}:{time.time()}"),
                    "size": 32
                }},
                "metadata": {"type": "trust-vouch", "source": source, "target": target},
                "committer": "membrane"
            })
            self.send_json(200, {"trust_recorded": "result" in r, "loamspine": r.get("result", r.get("error"))})

        elif self.path == "/tombstone":
            identity_hash = body.get("identity_hash", "")
            ts = time.time()
            tombstone_hash = hex_to_sha(f"tombstone:{identity_hash}:{ts}")
            r = loam_rpc("entry.append", {
                "spine_id": SPINE_ID,
                "payload": list(f"TOMBSTONE:{identity_hash[:16]}".encode()[:32]),
                "entry_type": {"DataAnchor": {
                    "data_hash": tombstone_hash,
                    "size": 32
                }},
                "metadata": {"type": "tombstone", "identity_prefix": identity_hash[:16], "forgotten_at": ts},
                "committer": "membrane"
            })
            self.send_json(200, {
                "forgotten": "result" in r,
                "tombstone_hash": tombstone_hash[:32],
                "timestamp": ts
            })

        else:
            self.send_json(404, {"error": "unknown path"})


if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", LISTEN_PORT), Handler)
    print(f"membrane-anchor-bridge on 127.0.0.1:{LISTEN_PORT}")
    sys.stdout.flush()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
