"""Find deckGate + Steam devices on LAN 1 — scan for the mounted display."""
import subprocess, socket, urllib.request, ssl, json

print("=" * 60)
print("FINDING DECKGATE + STEAM DEVICES ON LAN 1")
print("=" * 60)

# ─── Ping deckGate ───
print("\n[1] Reaching deckGate (.176)...\n")
r = subprocess.run(['ping', '-n', '2', '-w', '1000', '192.168.4.176'], capture_output=True, text=True, timeout=5)
alive = 'Reply from' in r.stdout and 'TTL=' in r.stdout
print(f"  deckGate (.176): {'ALIVE!' if alive else 'DOWN'}")
if alive:
    for line in r.stdout.split('\n'):
        if 'Reply' in line:
            print(f"    {line.strip()}")

# ─── Scan nearby IPs for Steam devices ───
print("\n[2] Scanning LAN 1 for Steam/game devices...\n")
# Steam uses ports: 27036-27037 (Remote Play), 27031-27036 (streaming), 8443, 27015
steam_ports = [27036, 27037, 27031, 8443, 22, 80]

# Check known device IPs and nearby
targets = {
    "deckGate (.176)": "192.168.4.176",
    "Chromecast (.169)": "192.168.4.169",
    "Nest (.238)": "192.168.4.238",
    "Epson (.200)": "192.168.4.200",
}

# Also scan .170-.180 range for deckGate
for i in range(170, 185):
    ip = f"192.168.4.{i}"
    if ip not in targets.values():
        targets[f"scan .{i}"] = ip

for name, ip in sorted(targets.items(), key=lambda x: x[1]):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        result = s.connect_ex((ip, 22))
        s.close()
        if result == 0:
            # Check Steam port too
            open_ports = [22]
            for sp in [27036, 27037, 8080, 80]:
                try:
                    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s2.settimeout(0.2)
                    if s2.connect_ex((ip, sp)) == 0:
                        open_ports.append(sp)
                    s2.close()
                except:
                    pass
            print(f"  * {name:25s} {ip:16s} SSH OPEN  ports: {open_ports}")
        else:
            # Try ping instead
            rp = subprocess.run(['ping', '-n', '1', '-w', '200', ip], capture_output=True, text=True, timeout=2)
            if 'Reply from' in rp.stdout and 'TTL=' in rp.stdout:
                print(f"  * {name:25s} {ip:16s} PING OK (no SSH)")
    except:
        pass

# ─── Check Steam streaming on northGate ───
print("\n[3] Steam Remote Play status on northGate...\n")
r3 = subprocess.run(['powershell', '-Command', 
    'Get-Process steam* -ErrorAction SilentlyContinue | Select-Object Name,Id; '
    'Get-NetTCPConnection -LocalPort 27036 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State; '
    'Get-NetTCPConnection -LocalPort 27037 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State'
], capture_output=True, text=True, timeout=10)
print(r3.stdout if r3.stdout.strip() else "  No Steam processes / streaming ports found")

# ─── Check Steam Link devices ───
print("\n[4] Looking for Steam Link on LAN...\n")
# Steam Link announces on UDP 27036
# Check ARP table for known Steam device MACs
r4 = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
for line in r4.stdout.split('\n'):
    line = line.strip()
    if not line or 'Interface' in line or 'Address' in line or 'static' in line:
        continue
    # Look for .176 or Steam-related MACs
    if '.176 ' in line or '.169' in line or '.152' in line:
        print(f"  {line}")
    # Valve MAC prefixes: d4:61:da, 10:f6:0a
    if 'd4-61-da' in line.lower() or '10-f6-0a' in line.lower() or 'd4-61' in line.lower():
        print(f"  STEAM! {line}")

# ─── eastGate SSH check for Steam Link ───
print("\n[5] What northGate knows about displays + HDMI...\n")
cmd5 = '''
nvidia-smi --query-gpu=name --format=csv,noheader
Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue | ForEach-Object { Write-Output "$($_.FriendlyName): $($_.Status)" }
Get-CimInstance -ClassName Win32_VideoController | ForEach-Object { Write-Output "GPU: $($_.Name) Outputs=$($_.VideoModeDescription)" }
'''
r5 = subprocess.run(['powershell', '-Command', cmd5], capture_output=True, text=True, timeout=10)
print(r5.stdout)

print("\n" + "=" * 60)
