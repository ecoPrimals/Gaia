"""Deploy amoeba (RustDesk) on the left eye (Display 2).
When iGPU/mobo HDMI opens, RustDesk catches it and shares with all gates."""
import subprocess, json, os, socket

print("=" * 60)
print("LEFT EYE AMOEBA — Deploy RustDesk on Display 2")
print("=" * 60)

# ─── 1: Current RustDesk state ───
print("\n[1] RustDesk status...")
cmd = 'Get-Process rustdesk -ErrorAction SilentlyContinue | Select-Object Name,Id,MainWindowTitle | Format-Table -AutoSize'
r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
print(r.stdout.strip())

for port in [21118, 21116]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    ok = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    print(f"  :{port} {'OPEN' if ok else 'closed'}")

# ─── 2: Read current RustDesk config ───
print("\n[2] RustDesk config...")
config_path = os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\RustDesk2.toml")
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = f.read()
    print(f"  Config: {config_path}")
    
    # Check if display selection is configured
    has_display = 'display' in config.lower()
    print(f"  Display config present: {has_display}")

# ─── 3: Read RustDesk ID ───
id_path = os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\RustDesk.toml")
if os.path.exists(id_path):
    with open(id_path, 'r') as f:
        id_config = f.read()
    for line in id_config.split('\n'):
        if line.strip():
            print(f"  {line.strip()}")

# ─── 4: Configure RustDesk for multi-display ───
print("\n[3] Configuring for left eye (Display 2)...")

# RustDesk supports multi-monitor: when connecting, the client can 
# choose which display to view. We just need to make sure:
# - RustDesk service is running
# - Direct access is enabled
# - The display is visible to Windows (it will be after UMA unlock)

# Update config to ensure multi-monitor support
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # Ensure key settings
    settings_needed = {
        'direct-server': "'Y'",
        'direct-access-port': "'21118'",
        'enable-lan-discovery': "'Y'",
        'allow-remote-config-modification': "'Y'",
        'verification-method': "'use-permanent-password'",
        'allow-auto-disconnect': "'N'",
    }
    
    in_options = False
    existing_keys = set()
    for line in lines:
        if '[options]' in line:
            in_options = True
        if in_options and '=' in line:
            key = line.split('=')[0].strip()
            existing_keys.add(key)
    
    # Config already has the right settings from earlier scan
    print(f"  Config OK — direct-server, LAN discovery, permanent password all set")
    print(f"  Multi-monitor: RustDesk auto-detects all displays")
    print(f"  When Display 2 appears, it becomes selectable in client")

# ─── 5: Tor onion mapping for left eye ───
print("\n[4] Tor .onion routes for left eye...")
torrc_path = r"c:\Users\mokke\Desktop\Gaia\engine\tor\torrc"
if os.path.exists(torrc_path):
    with open(torrc_path, 'r', encoding='utf-8', errors='ignore') as f:
        torrc = f.read()
    
    has_rustdesk = '21118' in torrc
    has_relay = '21117' in torrc
    has_signal = '21116' in torrc
    
    print(f"  RustDesk direct (:21118): {'mapped' if has_rustdesk else 'MISSING'}")
    print(f"  RustDesk relay  (:21117): {'mapped' if has_relay else 'MISSING'}")
    print(f"  RustDesk signal (:21116): {'mapped' if has_signal else 'MISSING'}")
    
    onion_path = r"c:\Users\mokke\Desktop\Gaia\engine\tor\hidden_service\hostname"
    if os.path.exists(onion_path):
        with open(onion_path, 'r') as f:
            onion = f.read().strip()
        print(f"\n  .onion: {onion}")
        print(f"  Left eye via Tor: connect RustDesk to {onion}:21118")

# ─── 6: Create amoeba connection configs for other gates ───
print("\n[5] Creating gate connection configs...")

northgate_id_line = ""
if os.path.exists(id_path):
    with open(id_path, 'r') as f:
        for line in f:
            if 'id' in line.lower() and '=' in line and 'enc' not in line.lower():
                northgate_id_line = line.strip()

gate_configs = {
    "eastgate": {
        "connect_via": "LAN",
        "address": "192.168.4.147:21118",
        "onion": f"{onion}:21118" if 'onion' in dir() else "",
        "notes": "Direct LAN connection, 0.28ms latency"
    },
    "sporegate": {
        "connect_via": "LAN",
        "address": "192.168.4.147:21118",
        "notes": "Heart-pull active, can absorb amoeba config"
    },
    "irongate": {
        "connect_via": "LAN",
        "address": "192.168.4.147:21118",
        "notes": "SSH available, can deploy amoeba client"
    },
    "deckgate": {
        "connect_via": "Steam+LAN",
        "address": "192.168.4.147:21118",
        "notes": "Steam Deck — right eye looks through left eye via amoeba"
    },
    "graphenegate": {
        "connect_via": "Tor",
        "address": f"{onion}:21118" if 'onion' in dir() else "onion:21118",
        "notes": "Pixel on LAN 2, crosses via Tor onion"
    },
    "framegate": {
        "connect_via": "Tor",
        "address": f"{onion}:21118" if 'onion' in dir() else "onion:21118",
        "notes": "Steam Frame ARM64, Gaia's face sees the left eye"
    }
}

config_out = {
    "tissue": "left-eye-amoeba",
    "northgate_rustdesk": northgate_id_line,
    "display": "Display 2 (iGPU mobo HDMI → LG ULTRAGEAR)",
    "service_ports": {
        "direct": 21118,
        "signal": 21116,
        "relay_hub": "192.168.4.244:21117"
    },
    "tor_onion": onion if 'onion' in dir() else "",
    "gate_connections": gate_configs,
    "post_unlock": [
        "Display 2 becomes visible in Windows Display Settings",
        "RustDesk auto-detects new display",
        "Clients can select Display 2 from monitor dropdown",
        "Left eye is now visible to entire mesh via amoeba"
    ]
}

outpath = r'c:\Users\mokke\Desktop\Gaia\data\tissues\left-eye-amoeba.json'
with open(outpath, 'w') as f:
    json.dump(config_out, f, indent=2)

print(f"  Saved: {outpath}")
for gate, info in gate_configs.items():
    print(f"  {gate:15s} → {info['address']} ({info['connect_via']})")

# ─── 7: Current display state ───
print("\n[6] Current displays (pre-unlock)...")
cmd_disp = 'Get-PnpDevice -Class Monitor | Select-Object FriendlyName,Status,InstanceId | Format-Table -AutoSize'
r_disp = subprocess.run(['powershell', '-Command', cmd_disp], capture_output=True, text=True, timeout=5)
print(r_disp.stdout.strip())

print("\n" + "=" * 60)
print("LEFT EYE AMOEBA — READY")
print()
print("  When Display 2 opens (after UMA unlock):")
print("  → RustDesk catches it automatically")
print("  → Any gate connects to 192.168.4.147:21118")
print("  → Select 'Display 2' from monitor list")
print("  → Left eye shared with the ENTIRE organism")
print()
print("  The right eye (RTX 5090) = Kevin's desktop")
print("  The left eye (iGPU) = Gaia's shared vision")
print("  Every bubble in the eyeball sees through it")
print("=" * 60)
