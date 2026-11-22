"""watch-wire.py — Continuous monitoring for boot-looping biomegate + full mesh state."""
import subprocess
import socket
import time
import datetime

BIOMEGATE_ATT_MAC = "b4:2e:99:a7:91:a3"
MYSTERY_MAC = "c8:5e:a9:c9:6f:80"
TARGETS = [
    "192.168.4.248",    # .248 appeared then vanished (boot loop?)
    "192.168.4.232",    # biomegate's last ATT IP transposed to .4
    "192.168.4.3",      # sporeGate
    "192.168.4.2",      # MikroTik
    "192.168.1.81",     # eastGate on ATT
    "192.168.1.232",    # biomegate's ATT IP
]

print("=" * 70)
print("  WIRE WATCH — monitoring for biomegate boot loop")
print(f"  Known biomegate MAC: {BIOMEGATE_ATT_MAC}")
print(f"  Mystery .248 MAC:    {MYSTERY_MAC}")
print("  Watching all subnets for 60 seconds...")
print("=" * 70)
print()

start = time.time()
cycle = 0
events = []

while time.time() - start < 60:
    cycle += 1
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Ping all targets
    results = {}
    for ip in TARGETS:
        r = subprocess.run(f"ping -n 1 -w 300 {ip}", capture_output=True, text=True, shell=True, timeout=3)
        alive = "TTL=" in r.stdout
        results[ip] = alive
    
    # Quick ARP check
    r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
    arp_macs = {}
    for line in r.stdout.split("\n"):
        l = line.strip()
        if "dynamic" in l.lower() and "192.168" in l:
            parts = l.split()
            if len(parts) >= 2:
                arp_macs[parts[0]] = parts[1]
    
    # Format output
    status_line = f"[{ts}] cycle={cycle:2d}  "
    for ip in TARGETS:
        short = ip.split(".")[-1]
        subnet = ip.split(".")[2]
        label = f"{subnet}.{short}"
        if results.get(ip):
            mac = arp_macs.get(ip, "???")
            status_line += f" {label}:UP({mac})"
            events.append(f"{ts}: {ip} UP mac={mac}")
        else:
            status_line += f" {label}:--"
    
    # Check for ANY new devices in ARP
    for ip, mac in arp_macs.items():
        if ip not in [t for t in TARGETS] and ip != "192.168.4.147":  # not us, not targets
            if BIOMEGATE_ATT_MAC.replace(":", "-") in mac.lower() or MYSTERY_MAC.replace(":", "-") in mac.lower():
                events.append(f"*** {ts}: BIOMEGATE MAC seen at {ip}! ({mac}) ***")
                status_line += f" !!!{ip}={mac}"
    
    print(status_line)
    time.sleep(5)

print(f"\n--- 60 SECONDS COMPLETE ---")
print(f"Total events: {len(events)}")
for e in events:
    print(f"  {e}")

# Final ARP dump
print(f"\n--- FINAL ARP STATE ---")
r = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
for line in r.stdout.split("\n"):
    l = line.strip()
    if "dynamic" in l.lower() and "192.168" in l:
        print(f"  {l}")

# Check WHAT is on the MikroTik — it's alive with SSH!
print(f"\n--- MikroTik (.4.2) is ALIVE — checking if it knows about biomegate ---")
print("  MikroTik has SSH on port 22 — if we could query its ARP/MAC table,")
print("  we'd see every device on the L2 backbone, including boot-looping ones.")
print("  (Need MikroTik credentials to query its switching table)")

# Check if anything ELSE popped up on .4.x during our monitoring
print(f"\n--- QUICK SWEEP .4.x (1-10, 95-105, 240-254) ---")
from concurrent.futures import ThreadPoolExecutor
def ping_fast(ip):
    try:
        r = subprocess.run(f"ping -n 1 -w 200 {ip}", capture_output=True, text=True, shell=True, timeout=2)
        return ip if "TTL=" in r.stdout else None
    except: return None

sweep_range = list(range(1,11)) + list(range(95,106)) + list(range(240,255))
targets = [f"192.168.4.{i}" for i in sweep_range]
with ThreadPoolExecutor(30) as ex:
    alive = [ip for ip in ex.map(ping_fast, targets) if ip]
print(f"  Alive: {alive}")
