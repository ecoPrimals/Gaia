"""Scan the rewired LAN — find the new body map"""
import subprocess, concurrent.futures

def ping(ip):
    try:
        r = subprocess.run(['ping','-n','1','-w','500',ip], capture_output=True, text=True, timeout=3)
        if 'Reply from ' + ip in r.stdout:
            # Get the time
            for line in r.stdout.split('\n'):
                if 'time' in line.lower() and 'Reply' in line:
                    return f"{ip} ALIVE — {line.strip()}"
            return f"{ip} ALIVE"
    except:
        pass
    return None

print("=== SCANNING 192.168.4.0/24 ===")
ips = [f"192.168.4.{i}" for i in range(1, 255)]

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
    results = list(ex.map(ping, ips))

alive = [r for r in results if r]
print(f"\nFound {len(alive)} devices:\n")
for a in alive:
    print(f"  {a}")

# Also check LAN 2
print("\n=== SCANNING 192.168.9.0/24 (LAN 2 — legs/tail) ===")
ips2 = [f"192.168.9.{i}" for i in range(1, 255)]
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
    results2 = list(ex.map(ping, ips2))

alive2 = [r for r in results2 if r]
print(f"\nFound {len(alive2)} devices:\n")
for a in alive2:
    print(f"  {a}")
