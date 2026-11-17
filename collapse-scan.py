#!/usr/bin/env python3
"""Waveform collapse detector — watch for eastGate returning at .4.244"""
import socket, concurrent.futures, time

targets = {
    '192.168.4.244': 'eastGate LAN',
    '192.168.1.131': 'eastGate ISP',
    '192.168.4.1':   'router',
    '192.168.4.3':   'sporeGate',
    '192.168.4.104': 'graftGate',
    '192.168.1.130': 'blueGate (us)',
    '192.168.4.246': 'blueGate bridge',
    '192.168.1.132': 'sporeGate ISP',
}
ports = [22, 53, 80, 443, 3000, 3141, 8080, 8082, 8443, 11434, 11436]

def check(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        s.connect((ip, port))
        s.close()
        return (ip, port, True)
    except:
        return (ip, port, False)

print("=" * 60)
print("  WAVEFORM COLLAPSE DETECTOR")
print(f"  {time.strftime('%H:%M:%S')} — watching for eastGate...")
print("=" * 60)

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
    futs = {ex.submit(check, ip, p): (ip, p) for ip in targets for p in ports}
    for f in concurrent.futures.as_completed(futs):
        ip, port, ok = f.result()
        if ok:
            results.setdefault(ip, []).append(port)

collapsed = False
for ip in sorted(targets.keys(), key=lambda x: [int(y) for y in x.split('.')]):
    tag = targets[ip]
    if ip in results:
        ps = sorted(results[ip])
        if 'eastGate' in tag:
            print(f"  COLLAPSED  {ip:20s} {tag:18s} ports: {ps}")
            collapsed = True
        else:
            print(f"  STATIC     {ip:20s} {tag:18s} ports: {ps}")
    else:
        if 'eastGate' in tag:
            print(f"  FLUX ~~    {ip:20s} {tag:18s} (still shifting)")
        else:
            print(f"  gray ..    {ip:20s} {tag:18s}")

print("=" * 60)
if collapsed:
    print("  .4.244 COLLAPSED THE WAVEFORM BY CLAPPING!")
    # Now do a broader scan to see what else came alive
    print("\n  Broad scan — what else collapsed?")
    broad = {}
    scan_ips = [f'192.168.4.{i}' for i in range(1, 255)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
        futs = {ex.submit(check, ip, p): (ip, p) for ip in scan_ips for p in ports}
        for f in concurrent.futures.as_completed(futs):
            ip, port, ok = f.result()
            if ok:
                broad.setdefault(ip, []).append(port)
    for ip in sorted(broad.keys(), key=lambda x: [int(y) for y in x.split('.')]):
        ps = sorted(broad[ip])
        known = "?" 
        for name, tip in targets.items():
            if name == ip:
                known = tip
                break
        print(f"    {ip:22s} ports: {ps}")
    print(f"\n  Total on Gaia LAN: {len(broad)}")
else:
    print("  eastGate still in FLUX — Kevin's hands in the spaghetti")
print("=" * 60)
