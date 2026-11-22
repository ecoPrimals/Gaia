#!/usr/bin/env python3
"""Deep ID — get HTTP page titles, grab more banners, identify every new device"""
import urllib.request, ssl, socket

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

targets = [
    ('192.168.4.138', [80, 443, 5000]),
    ('192.168.4.183', [22, 80, 443, 5000, 8080, 8443, 9090]),
    ('192.168.4.215', [22, 80, 443]),
    ('192.168.4.230', [80, 443, 548, 5353, 62078, 7000, 49152, 8082]),
    ('192.168.4.248', [80, 8080]),
]

for ip, ports in targets:
    print(f"\n{'─'*50}")
    print(f"  {ip}")
    print(f"{'─'*50}")
    
    # Try HTTP — get full title and more body
    for p in ports:
        for proto in ['http', 'https']:
            if proto == 'https' and p not in [443, 8443, 5001]:
                continue
            if proto == 'http' and p in [443]:
                continue
            try:
                if proto == 'https':
                    r = urllib.request.urlopen(f'{proto}://{ip}:{p}/', timeout=3, context=ctx)
                else:
                    r = urllib.request.urlopen(f'{proto}://{ip}:{p}/', timeout=3)
                server = r.headers.get('Server', '?')
                body = r.read(2000).decode('utf-8', errors='replace')
                # Extract title
                title = ''
                if '<title>' in body.lower():
                    start = body.lower().index('<title>') + 7
                    end = body.lower().index('</title>', start)
                    title = body[start:end].strip()
                print(f"  {proto}://{ip}:{p}")
                print(f"    Server: {server}")
                print(f"    Title: {title}")
                # Look for identifying info
                for keyword in ['Synology', 'TP-Link', 'MikroTik', 'iPhone', 'Android', 
                                'Pop!_OS', 'Ubuntu', 'GL-', 'Gaia', 'biome', 'QNAP',
                                'Netgear', 'Ubiquiti', 'hostname', 'model']:
                    if keyword.lower() in body.lower():
                        idx = body.lower().index(keyword.lower())
                        snippet = body[max(0,idx-20):idx+50]
                        print(f"    Found '{keyword}': ...{snippet}...")
            except:
                pass

    # Wider port scan
    extra_ports = [139, 445, 548, 631, 1883, 3000, 3306, 3389, 
                   5353, 5432, 5900, 5901, 6443, 8082, 9100,
                   11434, 11436, 21115, 21116, 62078]
    open_extra = []
    for p in extra_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, p))
            s.close()
            open_extra.append(p)
        except:
            pass
    if open_extra:
        print(f"  Extra ports: {open_extra}")

# Also grab .138 full page to see what device it is
print(f"\n{'='*50}")
print("  FULL PAGE: .138")
print(f"{'='*50}")
try:
    r = urllib.request.urlopen('http://192.168.4.138/', timeout=3)
    body = r.read(3000).decode('utf-8', errors='replace')
    print(body[:1500])
except Exception as e:
    print(f"  Error: {e}")

# .215 "Web Switch" full page
print(f"\n{'='*50}")
print("  FULL PAGE: .215 Web Switch")
print(f"{'='*50}")
try:
    r = urllib.request.urlopen('http://192.168.4.215/', timeout=3)
    body = r.read(3000).decode('utf-8', errors='replace')
    print(body[:1500])
except Exception as e:
    print(f"  Error: {e}")
