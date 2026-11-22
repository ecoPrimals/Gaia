#!/usr/bin/env python3
"""Deep probe of ironGate at 192.168.1.229"""
import socket, urllib.request

IP = '192.168.1.229'

# Wide port scan
ports = [21,22,25,53,80,111,139,443,445,631,1883,3000,3306,3389,
         4000,5432,5900,5901,6443,8000,8080,8443,9090,9100,
         11434,11435,11436,21115,21116,21117,21118,21119,27017]
open_p = []
for p in ports:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((IP, p))
        s.close()
        open_p.append(p)
        print(f"  Port {p}: OPEN")
    except:
        pass

print(f"\nOpen ports on {IP}: {open_p}")

# Check HTTP on open ports
for p in open_p:
    if p in [80, 443, 3000, 8000, 8080, 8443, 9090, 11434]:
        proto = 'https' if p == 443 else 'http'
        try:
            r = urllib.request.urlopen(f'{proto}://{IP}:{p}/', timeout=3)
            print(f"  HTTP {p}: {r.status} Server={r.headers.get('Server','?')}")
            body = r.read(500).decode('utf-8', errors='replace')
            print(f"    Body: {body[:200]}")
        except Exception as e:
            print(f"  HTTP {p}: {e}")

# Check ollama specifically
try:
    r = urllib.request.urlopen(f'http://{IP}:11434/api/tags', timeout=3)
    print(f"\n  OLLAMA at :11434 — {r.read(500).decode()[:300]}")
except Exception as e:
    print(f"\n  Ollama :11434: {e}")
