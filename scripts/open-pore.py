"""Open the pore — restart Tor with left eye ports, verify all services."""
import subprocess, socket, os, json

print("=" * 60)
print("OPENING THE PORE — Tor + Left Eye architecture")
print("=" * 60)

# ─── What's listening on northGate? ───
print("\n[1] Active listeners on northGate...\n")
ports_to_check = {
    8080: "data/RSS server",
    8888: "petalTongue API",
    8443: "gate thymus",
    9050: "Tor SOCKS",
    9100: "Tower Atomic",
    9878: "nestGate storage",
    21116: "RustDesk signaling",
    21117: "RustDesk relay",
    21118: "RustDesk direct",
    31415: "biomeOS",
    3000: "Forgejo (eastGate)",
    11434: "ollama local",
    55919: "barraCuda GPU",
}

for port, desc in sorted(ports_to_check.items()):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        status = "OPEN" if result == 0 else "closed"
        icon = "  *" if result == 0 else "   "
        print(f"{icon} :{port:>5}  {status:6s}  {desc}")
    except:
        print(f"    :{port:>5}  error   {desc}")

# ─── Restart Tor to pick up new config ───
print("\n[2] Restarting Tor with LEFT EYE ports...\n")

# Kill existing tor
r = subprocess.run(['taskkill', '/f', '/im', 'tor.exe'], capture_output=True, text=True, timeout=5)
print(f"  Kill: {r.stdout.strip()}")

import time
time.sleep(2)

# Start tor with our torrc
tor_exe = r"C:\Users\mokke\Desktop\Gaia\engine\tor\tor\tor.exe"
torrc = r"C:\Users\mokke\Desktop\Gaia\engine\tor\torrc"

if os.path.exists(tor_exe):
    proc = subprocess.Popen(
        [tor_exe, '-f', torrc],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=0x00000008  # DETACHED_PROCESS
    )
    print(f"  Tor started: PID {proc.pid}")
    time.sleep(5)
    
    # Check if it's running
    r = subprocess.run(['tasklist', '/fi', 'imagename eq tor.exe'], capture_output=True, text=True, timeout=5)
    if 'tor.exe' in r.stdout:
        print("  Tor is RUNNING")
    else:
        print("  Tor may have failed — checking log...")
        log_path = r"C:\Users\mokke\Desktop\Gaia\engine\tor\tor.log"
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(f"    {line.rstrip()}")
else:
    print(f"  tor.exe not found at {tor_exe}")

# Verify SOCKS is back
time.sleep(2)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    result = s.connect_ex(("127.0.0.1", 9050))
    s.close()
    print(f"\n  Tor SOCKS :9050: {'OPEN' if result == 0 else 'closed (still bootstrapping)'}")
except:
    print("  Tor SOCKS: checking...")

# ─── Print the dual-eye architecture ───
print("\n" + "=" * 60)
print("DUAL-EYE ARCHITECTURE")
print("=" * 60)
print()
print("  RIGHT EYE (Display 1 — RTX 5090 DisplayPort)")
print("  ├── Kevin's personal desktop")
print("  ├── Cursor IDE")
print("  ├── OUTER face — mitochondria pipeline")
print("  └── NOT shared — private power workspace")
print()
print("  LEFT EYE (Display 2 — iGPU HDMI)")
print("  ├── RustDesk/amoeba display")
print("  ├── INNER face — cell wall pipeline")
print("  ├── Shared with ALL gates via:")
print("  │   ├── LAN direct: 192.168.4.147:21118")
print("  │   ├── Tor onion: k3lubz...oaad.onion:21118")
print("  │   └── WAN: primals.eco (port forward)")
print("  └── Every gate sees through this eye")
print()
print("  .onion address:")
onion = open(r"C:\Users\mokke\Desktop\Gaia\engine\tor\hidden_service\hostname").read().strip()
print(f"  {onion}")
print()
print("  After reboot + BIOS UMA=512M:")
print("  1. Display 2 opens (iGPU live)")
print("  2. RustDesk starts on Display 2")
print("  3. Tor routes :21118 → RustDesk")
print("  4. ALL gates can see through the LEFT EYE")
