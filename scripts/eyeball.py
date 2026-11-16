"""EYEBALL — Map all amoeba/RustDesk bubbles across the organism."""
import subprocess, socket, json, os

print("=" * 60)
print("EYEBALL — Amoeba bubbles across the organism")
print("=" * 60)

# ─── 1: Local RustDesk/amoeba status ───
print("\n[1] northGate amoeba (local)...\n")
cmd1 = 'Get-Process rustdesk -ErrorAction SilentlyContinue | Format-Table Name,Id,WorkingSet64 -AutoSize'
r1 = subprocess.run(['powershell', '-Command', cmd1], capture_output=True, text=True, timeout=5)
print(r1.stdout.strip())

# RustDesk config
config_paths = [
    os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\RustDesk2.toml"),
    os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\RustDesk.toml"),
    r"C:\Users\mokke\RustDesk2_from_server.toml",
]
for cp in config_paths:
    if os.path.exists(cp):
        print(f"\n  Config: {cp}")
        with open(cp, 'r') as f:
            content = f.read()
        for line in content.split('\n')[:20]:
            if line.strip() and not line.strip().startswith('#'):
                print(f"    {line.strip()}")
        break

# RustDesk ID
id_path = os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\RustDesk.toml")
if os.path.exists(id_path):
    with open(id_path, 'r') as f:
        for line in f:
            if 'id' in line.lower() and '=' in line:
                print(f"\n  {line.strip()}")

# ─── 2: Scan all gates for RustDesk/amoeba ───
print("\n[2] Scanning gates for amoeba bubbles...\n")
gates = {
    "northGate (.147)": "192.168.4.147",
    "eastGate (.244)": "192.168.4.244",
    "sporeGate (.3)": "192.168.4.3",
    "ironGate (.237)": "192.168.4.237",
    "deckGate (.176)": "192.168.4.176",
    "graftGate (.107)": "192.168.4.107",
}

for name, ip in gates.items():
    # Check RustDesk ports: 21118 (direct), 21116 (signaling), 21117 (relay)
    bubbles = []
    for port in [21118, 21116, 21117]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.4)
            result = s.connect_ex((ip, port))
            s.close()
            if result == 0:
                bubbles.append(str(port))
        except:
            pass
    
    # Also check SSH and Steam
    extras = []
    for port, svc in [(22, "SSH"), (27036, "Steam"), (11434, "ollama")]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            if s.connect_ex((ip, port)) == 0:
                extras.append(svc)
            s.close()
        except:
            pass
    
    if bubbles or extras:
        bubble_str = f"amoeba:[{','.join(bubbles)}]" if bubbles else ""
        extra_str = f" + {','.join(extras)}" if extras else ""
        print(f"  * {name:25s} {bubble_str}{extra_str}")
    else:
        # Ping check
        rp = subprocess.run(['ping', '-n', '1', '-w', '200', ip], capture_output=True, text=True, timeout=2)
        alive = 'Reply from' in rp.stdout
        status = "ALIVE (no amoeba)" if alive else "DOWN"
        print(f"    {name:25s} {status}")

# ─── 3: RustDesk peers (known connections) ───
print("\n[3] Known RustDesk peers...\n")
peers_path = os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\peers")
if os.path.exists(peers_path):
    for f in os.listdir(peers_path):
        if f.endswith('.toml'):
            fp = os.path.join(peers_path, f)
            with open(fp, 'r') as fh:
                content = fh.read()
            peer_id = f.replace('.toml', '')
            # Extract key info
            alias = ""
            for line in content.split('\n'):
                if 'alias' in line.lower() or 'hostname' in line.lower():
                    alias = line.strip()
            print(f"  Peer {peer_id}: {alias}")
else:
    print("  No peers directory found")
    # Check alternate location
    alt = os.path.expanduser(r"~\AppData\Roaming\RustDesk\config")
    if os.path.exists(alt):
        print(f"  Config dir: {alt}")
        for f in os.listdir(alt):
            print(f"    {f}")

# ─── 4: Gaia's known peers ───
print("\n[4] Gaia's peer config...\n")
gaia_config = r"C:\Users\mokke\Desktop\Gaia\data\rustdesk-northgate-config.json"
if os.path.exists(gaia_config):
    with open(gaia_config, 'r') as f:
        data = json.load(f)
    if 'peers' in data:
        for name, info in data['peers'].items():
            print(f"  {name}: ID={info.get('id')} IP={info.get('ip')} — {info.get('note', '')}")
    if 'RustDesk2.toml' in data:
        opts = data['RustDesk2.toml'].get('[options]', {})
        print(f"\n  Relay: {opts.get('relay-server', '?')}")
        print(f"  Rendezvous: {opts.get('custom-rendezvous-server', '?')}")

# ─── 5: The eyeball architecture ───
print("\n" + "=" * 60)
print("EYEBALL ARCHITECTURE — Amoeba bubbles\n")
print("  Each gate running amoeba = one bubble")
print("  All bubbles together = the eyeball")
print("  RustDesk streams each gate's display")
print("  Tor routes them through .onion")
print()
print("  Current bubbles:")
print("    northGate: AMOEBA LIVE (:21118)")
print("    eastGate:  relay server (ID: 19091278)")
print("    sporeGate: ID: 1871544996 (Xorg :0)")
print("    deckGate:  Steam streaming (.176)")
print()
print("  Missing bubbles (need amoeba installed):")
print("    ironGate:  ollama running, no amoeba yet")
print("    graftGate: Mac Mini, need amoeba")
print()
print("  The eyeball sees through ALL bubbles at once")
print("  Like compound vision — each bubble = one facet")
print("=" * 60)
