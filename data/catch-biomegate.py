"""catch-biomegate.py — Catch biomegate during its boot loop up-phase.
Pings every 2 seconds. When UP: immediately probes for services, grabs everything we can.
Tracks boot loop timing to predict next window."""
import subprocess
import socket
import time
import datetime

IP = "192.168.1.233"
IP2 = "192.168.1.232"

print("=" * 70)
print("  CATCHING BIOMEGATE — Waiting for next boot cycle")
print(f"  Target: {IP} (b4:2e:99:a7:91:a5)")
print("  Polling every 2s for 5 minutes...")
print("=" * 70)

cycles = []
current_state = None
state_start = None
last_up_time = None
attempt = 0

start = time.time()
while time.time() - start < 300:  # 5 minutes
    attempt += 1
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Fast ping
    r = subprocess.run(f"ping -n 1 -w 400 {IP}", capture_output=True, text=True, shell=True, timeout=3)
    alive = "TTL=" in r.stdout
    
    # Also check .232 (other NIC)
    r2 = subprocess.run(f"ping -n 1 -w 400 {IP2}", capture_output=True, text=True, shell=True, timeout=3)
    alive2 = "TTL=" in r2.stdout
    
    state = "UP" if alive else ("UP2" if alive2 else "DOWN")
    
    # Detect state transition
    if state != current_state:
        if current_state is not None:
            duration = time.time() - state_start
            cycles.append((current_state, duration))
            print(f"  [{ts}] *** {current_state} → {state} *** (was {current_state} for {duration:.1f}s)")
            
            if state in ("UP", "UP2"):
                target_ip = IP if state == "UP" else IP2
                print(f"  [{ts}] BIOMEGATE IS UP! Quick-probing {target_ip}...")
                last_up_time = time.time()
                
                # Try SSH immediately
                try:
                    s = socket.create_connection((target_ip, 22), timeout=1)
                    banner = s.recv(256)
                    s.close()
                    print(f"  [{ts}] *** SSH OPEN! Banner: {banner.decode(errors='replace').strip()} ***")
                except ConnectionRefusedError:
                    print(f"  [{ts}] SSH refused (sshd not running yet)")
                except (socket.timeout, OSError):
                    print(f"  [{ts}] SSH filtered (firewall)")
                
                # Try HTTP
                for port in [80, 8080, 443]:
                    try:
                        s = socket.create_connection((target_ip, port), timeout=0.5)
                        s.close()
                        print(f"  [{ts}] *** HTTP :{port} OPEN! ***")
                    except:
                        pass
                
                # Check ARP for MAC
                r3 = subprocess.run("arp -a", capture_output=True, text=True, shell=True)
                for line in r3.stdout.split("\n"):
                    if "b4-2e-99" in line.lower():
                        print(f"  [{ts}] ARP: {line.strip()}")
        else:
            print(f"  [{ts}] Initial state: {state}")
        
        current_state = state
        state_start = time.time()
    elif attempt % 15 == 0:  # Every ~30 seconds, print a heartbeat
        elapsed = time.time() - state_start
        total = time.time() - start
        print(f"  [{ts}] ...{state} for {elapsed:.0f}s (total watch: {total:.0f}s)")
    
    time.sleep(2)

# Summary
print(f"\n{'=' * 70}")
print(f"  BOOT LOOP ANALYSIS")
print(f"{'=' * 70}")
if cycles:
    up_times = [d for s, d in cycles if s in ("UP", "UP2")]
    down_times = [d for s, d in cycles if s == "DOWN"]
    print(f"  Cycles observed: {len(cycles)}")
    if up_times:
        print(f"  UP durations: {[f'{d:.1f}s' for d in up_times]}")
        print(f"  Avg UP time: {sum(up_times)/len(up_times):.1f}s")
    if down_times:
        print(f"  DOWN durations: {[f'{d:.1f}s' for d in down_times]}")
        print(f"  Avg DOWN time: {sum(down_times)/len(down_times):.1f}s")
    total_cycle = sum(d for _, d in cycles)
    if up_times and down_times:
        print(f"  Estimated cycle: ~{total_cycle/max(len(up_times),1):.0f}s")
        print(f"\n  DIAGNOSIS: Boot loop with {sum(up_times)/len(up_times):.0f}s up, {sum(down_times)/len(down_times):.0f}s down")
        print(f"  Likely cause: kernel panic, service crash, or watchdog reboot")
else:
    print(f"  No state transitions in 5 minutes")
    print(f"  biomegate stayed {current_state} the entire time")
    if current_state == "DOWN":
        print(f"  → Boot loop cycle may be >5 minutes, or device is off")
        print(f"  → Kevin: check if biomegate has power and check its display")
    elif current_state in ("UP", "UP2"):
        print(f"  → biomegate is STABLE! Not in boot loop anymore!")
