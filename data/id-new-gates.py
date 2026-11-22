#!/usr/bin/env python3
"""Identify the new gates .152, .178 and the unknowns"""
import socket, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

targets = {
    '192.168.4.152': 'ac:41:6a — 31ms WiFi hop — NEW',
    '192.168.4.178': 'e0:bb:9e — 4ms — NEW',
    '192.168.4.183': '50:0a:52 (Huiwan) — <1ms — SSH only',
    '192.168.4.230': '1c:1b:0d — <1ms — no ports',
}

KEY_PORTS = [22, 53, 80, 443, 548, 631, 3000, 3141, 3389, 5000, 5001,
             5353, 5900, 5901, 7000, 8080, 8082, 8443, 9090, 9100,
             11434, 11436, 21115, 21116, 27036, 49152, 62078]

for ip, desc in targets.items():
    print(f"\n{'='*55}")
    print(f"  {ip} — {desc}")
    print(f"{'='*55}")
    
    # Port scan
    open_ports = []
    for p in KEY_PORTS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, p))
            s.close()
            open_ports.append(p)
        except: pass
    print(f"  Ports: {open_ports if open_ports else 'NONE'}")
    
    # SSH banner
    if 22 in open_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((ip, 22))
            banner = s.recv(256).decode('utf-8', errors='replace').strip()
            s.close()
            print(f"  SSH: {banner}")
        except: pass
    
    # HTTP
    for p in [80, 443, 5000, 8080, 8443, 9090]:
        if p in open_ports or p in [80, 5000, 8080]:
            try:
                proto = 'https' if p in [443, 8443] else 'http'
                if proto == 'https':
                    r = urllib.request.urlopen(f'{proto}://{ip}:{p}/', timeout=2, context=ctx)
                else:
                    r = urllib.request.urlopen(f'{proto}://{ip}:{p}/', timeout=2)
                server = r.headers.get('Server', '?')
                body = r.read(500).decode('utf-8', errors='replace')
                title = ''
                if '<title>' in body.lower():
                    s_idx = body.lower().index('<title>') + 7
                    e_idx = body.lower().index('</title>', s_idx)
                    title = body[s_idx:e_idx].strip()
                print(f"  HTTP {p}: Server={server} Title='{title}'")
            except: pass
    
    # NetBIOS
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        query = (b'\x80\x94\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                 b'\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00'
                 b'\x00\x21\x00\x01')
        s.sendto(query, (ip, 137))
        data, addr = s.recvfrom(1024)
        if len(data) > 56:
            name = data[57:57+15].decode('ascii', errors='replace').strip()
            print(f"  NetBIOS: {name}")
        s.close()
    except:
        pass
    
    # Reverse DNS
    try:
        name = socket.gethostbyaddr(ip)
        print(f"  rDNS: {name[0]}")
    except:
        pass

    # Apple device check (port 62078 = lockdown)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, 62078))
        s.close()
        print(f"  ** Apple lockdownd (62078) OPEN — iPhone/iPad! **")
    except:
        pass

# Summary
print(f"\n{'='*55}")
print("  GATE MAPPING HYPOTHESIS:")
print(f"{'='*55}")
print("""
  CONFIRMED:
    .1   = Router (GL-MT6000)
    .2   = MikroTik CRS310
    .138 = Synology NAS 'SOUTHGATE_DATA'
    .147 = northGate (Polaris) — WE ARE HERE
    .215 = TP-Link JetStream SX3008F
    .244 = eastGate (WiFi)
    .248 = eastGate (wired eno1)
    
  HYPOTHESIS (Kevin: confirm/correct):
    .183 = ? (Huiwan mini PC, Ubuntu 25.x) — blueGate?? new device??
    .152 = ? (WiFi 31ms, ac:41:6a) — phone? milkyGate? southGate?
    .178 = ? (4ms, e0:bb:9e) — tower? ironGate? westGate?
    .230 = ? (stealth, 1c:1b:0d) — phone? milkyGate?
""")
