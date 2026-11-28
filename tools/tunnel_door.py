#!/usr/bin/env python3
"""tunnel_door - the door a Cloudflare tunnel knocks on, in front of this body's gate.

  python tools/tunnel_door.py [listen-port] [gate-port]        defaults 8453 and 8443, loopback only

Why it exists. The gate decides who a visitor is from X-Forwarded-For, and trusts that header only from
loopback: "the front door names the visitor to me; a loopback caller that names nobody is this body
itself". A tunnel connector runs on this body, so everything it carries arrives from loopback. Sent
straight to the gate, a visitor from anywhere could write their own X-Forwarded-For and be taken for the
house, and one that wrote none would be taken for this body itself.

So the connector knocks here instead. This door:
  - takes the visitor's address from Cf-Connecting-Ip, which Cloudflare's edge writes itself and a
    visitor cannot choose; a request without it, or naming an address that is not a public one, is refused
  - drops whatever X-Forwarded-For, X-Real-IP and Forwarded the request carried and writes one
    X-Forwarded-For with that address alone
  - passes everything else to the gate untouched and streams the answer back

It listens on loopback only, keeps nothing, logs nothing, and holds no key.
"""
import http.client
import ipaddress
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN = int(sys.argv[1]) if len(sys.argv) > 1 else 8453
GATE = int(sys.argv[2]) if len(sys.argv) > 2 else 8443
MAX_BODY = 64 << 20
HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "proxy-connection", "te", "trailer",
       "transfer-encoding", "upgrade"}
NAMING = {"x-forwarded-for", "x-real-ip", "forwarded", "x-forwarded", "x-client-ip", "true-client-ip", "x-cluster-client-ip"}


def visitor(headers):
    """The address Cloudflare's edge saw, or None. Exactly one such header, a public address."""
    named = headers.get_all("Cf-Connecting-Ip") or []
    if len(named) != 1:
        return None
    try:
        ip = ipaddress.ip_address(named[0].strip())
    except ValueError:
        return None
    if getattr(ip, "ipv4_mapped", None):
        ip = ip.ipv4_mapped
    return str(ip) if ip.is_global else None


class Door(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "gaia-tunnel-door"
    sys_version = ""

    def log_message(self, fmt, *a):
        pass

    def _say(self, code, text):
        body = (text + "\n").encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        self.close_connection = True

    def _body(self):
        """The request body, whole (None if there is none); False if it is too large or malformed."""
        if "chunked" in (self.headers.get("Transfer-Encoding") or "").lower():
            out = bytearray()
            while True:
                line = self.rfile.readline(1024).strip()
                try:
                    n = int(line.split(b";")[0] or b"0", 16)
                except ValueError:
                    return False
                if n == 0:
                    while self.rfile.readline(4096).strip():        # trailers, if any
                        pass
                    return bytes(out)
                out += self.rfile.read(n)
                self.rfile.read(2)
                if len(out) > MAX_BODY:
                    return False
        length = self.headers.get("Content-Length")
        if length is None:
            return None
        try:
            n = int(length)
        except ValueError:
            return False
        if n < 0 or n > MAX_BODY:
            return False
        return self.rfile.read(n)

    def _pass(self):
        self.close_connection = True
        who = visitor(self.headers)
        if who is None:
            return self._say(400, "this door opens only for a visitor Cloudflare's edge has named")
        body = self._body()
        if body is False:
            return self._say(413, "that is more than this door carries")
        out = []
        for k, v in self.headers.items():
            low = k.lower()
            if low in HOP or low in NAMING or low == "content-length":
                continue
            out.append((k, v))
        out.append(("X-Forwarded-For", who))
        out.append(("Connection", "close"))
        try:
            up = http.client.HTTPConnection("127.0.0.1", GATE, timeout=120)
            up.putrequest(self.command, self.path, skip_host=True, skip_accept_encoding=True)
            for k, v in out:
                up.putheader(k, v)
            if body is not None:
                up.putheader("Content-Length", str(len(body)))
            up.endheaders(body if body else None)
            r = up.getresponse()
        except Exception:  # noqa: BLE001
            return self._say(502, "the gate behind this door did not answer")
        try:
            self.send_response_only(r.status, r.reason)
            length = None
            for k, v in r.getheaders():
                low = k.lower()
                if low in HOP:
                    continue
                if low == "content-length":
                    length = v
                self.send_header(k, v)
            bodyless = self.command == "HEAD" or r.status in (204, 304) or 100 <= r.status < 200
            chunked = length is None and not bodyless
            if chunked:
                self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()
            if not bodyless:
                while True:
                    piece = r.read1(65536)
                    if not piece:
                        break
                    if chunked:
                        self.wfile.write(b"%x\r\n" % len(piece) + piece + b"\r\n")
                    else:
                        self.wfile.write(piece)
                    self.wfile.flush()
                if chunked:
                    self.wfile.write(b"0\r\n\r\n")
        except (BrokenPipeError, ConnectionError, OSError):
            pass
        finally:
            up.close()

    do_GET = do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = _pass


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False


if __name__ == "__main__":
    Server(("127.0.0.1", LISTEN), Door).serve_forever()
