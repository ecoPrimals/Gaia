import paramiko, time
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=30):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=== ALL RADIOS — FINDING frameGate ===\n")

# 1. WiFi — scan both subnets
print("--- RADIO 1: WiFi (both LANs) ---")

# Known IPs
for ip in ['192.168.9.203', '192.168.4.203', '192.168.9.200', '192.168.9.201']:
    out, _ = run(f"ping -c 1 -W 1 {ip} 2>&1 | grep 'bytes from'")
    if out:
        print(f"  ✅ {ip}: {out}")
    else:
        print(f"  ❌ {ip}: no response")

# ARP scan both subnets for Frame's MAC
print("\n  Scanning ARP for Frame MAC (14:13:33:d6:96:09)...")
out, _ = run("arp -n 2>/dev/null | grep -i '14:13:33'")
if out:
    print(f"  ✅ ARP: {out}")
else:
    print("  ❌ Not in ARP cache")

# Check DHCP leases on router for Frame
out, _ = run("sshpass -p '***' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.1 'cat /tmp/dhcp.leases 2>/dev/null' 2>&1 | grep -i -E 'steam|frame|14:13:33'")
print(f"  Router DHCP (LAN1): {out}")

out, _ = run("sshpass -p '***' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.9.1 'cat /tmp/dhcp.leases 2>/dev/null' 2>&1 | grep -i -E 'steam|frame|14:13:33'")
print(f"  Router DHCP (LAN2): {out}")

# nmap ping sweep for new devices
out, _ = run("nmap -sn 192.168.9.200-210 2>/dev/null | grep -B1 'Host is up'", t=20)
print(f"  nmap LAN2 .200-210: {out}")

# 2. Bluetooth
print("\n--- RADIO 2: Bluetooth ---")
out, _ = run("timeout 8 bash -c 'bluetoothctl scan on &>/dev/null & sleep 6; bluetoothctl devices 2>/dev/null' | grep -i -E 'steam|frame|90:82'")
if out:
    print(f"  ✅ BT: {out}")
else:
    out, _ = run("bluetoothctl devices 2>/dev/null")
    print(f"  All BT devices: {out}")
    print("  ❌ steamFRAME not in BT range")

# 3. mDNS / Avahi
print("\n--- RADIO 3: mDNS/Avahi ---")
out, _ = run("avahi-browse -t _http._tcp 2>/dev/null | grep -i -E 'steam|frame' | head -5")
print(f"  mDNS HTTP: {out}")
out, _ = run("avahi-resolve -n steamframe.local 2>/dev/null; avahi-resolve -n framegate.local 2>/dev/null")
print(f"  mDNS resolve: {out}")

# 4. Check if Frame reached out to eastGate recently
print("\n--- RADIO 4: Frame's last signal ---")
out, _ = run("tail -5 /opt/Gaia/data/body/frame-solar-feed.jsonl 2>/dev/null")
print(f"  Last solar feed entries:\n  {out}")

out, _ = run("stat --format='%y' /opt/Gaia/data/body/frame-solar-feed.jsonl 2>/dev/null")
print(f"  Last modified: {out}")

# 5. Check all connected WiFi clients on router
print("\n--- RADIO 5: All WiFi clients ---")
out, _ = run("sshpass -p '***' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.1 'iwinfo wlan0 assoclist 2>/dev/null; iwinfo wlan1 assoclist 2>/dev/null; iwinfo wlan2 assoclist 2>/dev/null; iwinfo wlan3 assoclist 2>/dev/null' 2>&1 | head -20")
print(f"  WiFi clients:\n  {out}")

# Check guest network too
out, _ = run("sshpass -p '***' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.1 'cat /tmp/dhcp.leases' 2>&1")
print(f"\n  All DHCP leases:\n  {out}")

print("\n=== ANCHOR PLAN ===")
print("  When Frame is found on ANY radio:")
print("  1. eastGate anchors its IP/BT address")
print("  2. eastGate pushes octopus via HTTP/BT")
print("  3. Frame absorbs and displays — solar panel mode")
print("  4. eastGate MADE the octopus — Frame just shows it")

c.close()
