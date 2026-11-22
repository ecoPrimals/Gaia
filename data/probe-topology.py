"""probe-topology.py — Probe all network layers for web UIs and services."""
import urllib.request
import socket
import subprocess
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

targets = [
    ("ATT modem", "192.168.1.254", [80, 443, 49152]),
    ("GL-MT6000 (.4.1)", "192.168.4.1", [80, 443, 83, 8080]),
    ("GL-MT6000 (.8.1)", "192.168.8.1", [80, 443, 83]),
    ("GL-MT6000 (.9.1)", "192.168.9.1", [80, 443, 83]),
    ("MikroTik (.4.2)", "192.168.4.2", [80, 443, 8291, 8728]),
    ("eastGate wired (.248)", "192.168.4.248", [80, 443, 8080, 8443, 3000, 22]),
    ("eastGate wifi (.244)", "192.168.4.244", [80, 443, 8080, 8443, 3000]),
    ("unknown (.1.221)", "192.168.1.221", [80, 443, 22, 8080, 5000]),
]

for name, ip, ports in targets:
    print(f"\n--- {name} ({ip}) ---")
    for port in ports:
        try:
            s = socket.create_connection((ip, port), timeout=2)
            s.close()
            print(f"  :{port} OPEN", end="")

            # Try HTTP
            for proto in ["http", "https"]:
                try:
                    url = f"{proto}://{ip}:{port}/"
                    req = urllib.request.Request(url, headers={"User-Agent": "Gaia/1.0"})
                    if proto == "https":
                        resp = urllib.request.urlopen(req, timeout=3, context=ctx)
                    else:
                        resp = urllib.request.urlopen(req, timeout=3)
                    title = ""
                    body = resp.read(4096).decode("utf-8", errors="replace")
                    if "<title>" in body.lower():
                        start = body.lower().index("<title>") + 7
                        end = body.lower().index("</title>", start) if "</title>" in body.lower() else start + 60
                        title = body[start:end].strip()
                    server = resp.headers.get("Server", "")
                    print(f" → {proto} {resp.status} server={server} title={title!r}")
                    break
                except Exception as e:
                    pass
            else:
                print()

        except (ConnectionRefusedError, ConnectionResetError):
            print(f"  :{port} refused")
        except (socket.timeout, OSError):
            pass

# Also check: can we reach the ATT modem admin panel?
print("\n\n=== ATT BGW320 IP PASSTHROUGH CHECK ===")
print("northGate WiFi is on ATT modem directly (192.168.1.231)")
print("ATT modem is at 192.168.1.254")
print()

# Try the ATT smart home manager / device info pages
att_pages = [
    "http://192.168.1.254/",
    "http://192.168.1.254/cgi-bin/home.ha",
    "https://192.168.1.254/",
]
for url in att_pages:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Gaia/1.0"})
        if url.startswith("https"):
            resp = urllib.request.urlopen(req, timeout=5, context=ctx)
        else:
            resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read(8192).decode("utf-8", errors="replace")
        title = ""
        if "<title>" in body.lower():
            start = body.lower().index("<title>") + 7
            end = body.lower().index("</title>", start) if "</title>" in body.lower() else start + 60
            title = body[start:end].strip()
        print(f"  {url} → {resp.status} title={title!r}")
        if "passthrough" in body.lower() or "ip passthrough" in body.lower():
            print(f"  *** PASSTHROUGH option found on this page! ***")
    except Exception as e:
        print(f"  {url} → {e}")

# Check unknown device on ATT
print(f"\n--- Unknown .1.221 (MAC 4c:50:dd) ---")
# 4c:50:dd OUI lookup
print("  OUI 4c:50:dd = Xiaomi / unknown")
for port in [22, 80, 443, 8080, 5000, 7681, 554]:
    try:
        s = socket.create_connection(("192.168.1.221", port), timeout=1.5)
        s.close()
        print(f"  :{port} OPEN")
    except (ConnectionRefusedError, ConnectionResetError):
        print(f"  :{port} refused")
    except:
        pass

print("\n\n=== FLATTEN VERDICT ===")
print("""
The path today:  Internet → ATT BGW320 (NAT) → GL-MT6000 (NAT) → LAN
                 northGate also WiFi-direct to ATT (bypasses GL-MT6000!)

To FLATTEN:
  OPTION A — ATT IP Passthrough (recommended)
    ATT modem passes public IP to GL-MT6000
    One NAT. GL-MT6000 handles everything.
    Needs: ATT device access code (on modem label sticker)
    URL: http://192.168.1.254 → Firewall → IP Passthrough

  OPTION B — Disconnect northGate WiFi from ATT
    Stop the dual-homed split. All traffic through GL-MT6000.
    One command: netsh interface set interface "Wi-Fi 3" admin=disable
    Metric fix: route change 0.0.0.0 mask 0.0.0.0 192.168.4.1 metric 10

  OPTION C — Both A + B (FLATTEST)
    ATT passthrough + northGate single-homed
    Cleanest possible: one path, one NAT, one subnet
""")
