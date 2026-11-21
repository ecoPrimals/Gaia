#!/usr/bin/env python3
"""
TRAVELING SALESMAN — Back-triangulate all gates from membrane topology + live scan.
Kevin is the honey bee. We are the traveling salesman. 
Predict which new IP = which old gate, then Kevin goes and wires.
"""
import json, subprocess, socket, concurrent.futures
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# PRE-REWIRE TOPOLOGY (Wave 259, Nov 17)
# ═══════════════════════════════════════════════════════════════
PRE_REWIRE = {
    'eastGate':     {'old_ip': '.244', 'os': 'Pop!_OS 22.04', 'ssh': 'OpenSSH_8.9p1 Ubuntu', 'ttl': 64, 'role': 'BRAIN', 'services': ['ssh','http','dromedary','forgejo','ollama','rustdesk']},
    'northGate':    {'old_ip': '.147', 'os': 'Windows', 'ssh': 'OpenSSH_for_Windows_9.5', 'ttl': 128, 'role': 'HEART', 'services': ['ssh','http','ollama']},
    'ironGate':     {'old_ip': '.237', 'os': 'Pop!_OS 22.04', 'ssh': 'OpenSSH_8.9p1 Ubuntu', 'ttl': 64, 'role': 'FORGE 2', 'hw': 'i9-14900K, RTX 5070, 94GB DDR5', 'services': ['ssh','http','ollama']},
    'southGate':    {'old_ip': '.148', 'os': 'Dual boot', 'ssh': '?', 'ttl': 64, 'role': 'SOUTH POLE', 'hw': '5800X3D, RTX 4060, 128GB', 'services': ['ssh','ollama']},
    'sporeGate':    {'old_ip': '.3',   'os': 'Pop!_OS 22.04', 'ssh': 'OpenSSH_8.9p1 Ubuntu', 'ttl': 64, 'role': 'FORGE', 'hw': 'Ryzen 5 6600H, 27GB'},
    'milkGate':     {'old_ip': '.144', 'os': 'Ubuntu (RISC-V)', 'ssh': '?', 'ttl': 64, 'role': 'MILKY WAY — RISC-V', 'hw': 'SpacemiT K3 RVA23, 32GB'},
    'deckGate':     {'old_ip': '.176', 'os': 'SteamOS', 'ttl': 64, 'role': 'DISPLAY'},
    'blueGate':     {'old_ip': '.100', 'os': 'Windows', 'ssh': 'OpenSSH_for_Windows', 'ttl': 128, 'role': 'EXPANSION', 'hw': '128GB DDR4, 2TB'},
    'westGate':     {'old_ip': '—',    'os': '?', 'ttl': 64, 'role': 'COLD STORAGE NAS', 'hw': 'Ryzen 7 5700X, RTX 3070, 64GB, 50.7TB ZFS'},
    'graftGate':    {'old_ip': '.107', 'os': 'macOS', 'ssh': 'OpenSSH macOS', 'ttl': 64, 'role': 'Mac Mini M4'},
    'frameGate':    {'old_ip': '.181', 'os': 'ARM SteamOS', 'ttl': 64, 'role': 'FACE'},
    'grapheneGate': {'old_ip': '.202', 'os': 'GrapheneOS', 'ttl': 64, 'role': 'Diamond Lens'},
    'strandGate':   {'old_ip': '—',    'os': 'Pop!_OS', 'ttl': 64, 'role': 'HPC', 'hw': 'Dual EPYC 7452, RTX 3090 + RX 6950 XT, 256GB ECC'},
    'biomeGate':    {'old_ip': '—',    'os': '?', 'ttl': 64, 'role': 'HBM2 Fortress', 'hw': 'Threadripper 3970X, 256GB'},
    'kinGate':      {'old_ip': '—',    'os': 'Pop!_OS', 'ttl': 64, 'role': 'Staging', 'hw': 'i7-6700K, RTX 3070, 32GB'},
}

# ═══════════════════════════════════════════════════════════════
# POST-REWIRE SCAN (Now, Nov 21)
# ═══════════════════════════════════════════════════════════════
POST_REWIRE = {
    '.1':   {'mac': '94:83:c4:e0:63:5a', 'ttl': 64, 'ms': '<1', 'ports': [22,80,443], 'ssh': 'dropbear', 'id': 'Router'},
    '.2':   {'mac': '04:f4:1c:e6:7c:e8', 'ttl': 64, 'ms': '<1', 'ports': [22,80], 'ssh': 'ROSSSH', 'id': 'MikroTik'},
    '.138': {'mac': '90:09:d0:75:2a:1e', 'ttl': 64, 'ms': '<1', 'ports': [80,443,139,445,5000], 'oui': 'Synology', 'id': 'Synology NAS'},
    '.147': {'mac': 'BC:FC:E7:EA:D9:34', 'ttl': 128, 'ms': '<1', 'ports': [22,80,443,11434], 'ssh': 'OpenSSH_for_Windows_9.5', 'id': 'northGate'},
    '.152': {'mac': 'ac:41:6a:5c:b4:cf', 'ttl': 64, 'ms': '31', 'ports': [], 'oui': '?', 'id': '?'},
    '.178': {'mac': 'e0:bb:9e:d5:30:5a', 'ttl': 64, 'ms': '4', 'ports': [80,443,631,9100], 'id': 'EPSON printer'},
    '.183': {'mac': '50:0a:52:0b:87:81', 'ttl': 64, 'ms': '<1', 'ports': [22], 'ssh': 'OpenSSH_10.2p1 Ubuntu-2ubuntu3', 'oui': 'Huiwan Technologies', 'id': '?'},
    '.195': {'mac': '84:47:09:38:97:54', 'ttl': 64, 'ms': '<1', 'ports': [], 'id': 'sporeGate (offline now)', 'note': 'MAC sequential to known sporeGate'},
    '.215': {'mac': 'ec:75:0c:4c:98:08', 'ttl': 64, 'ms': '<1', 'ports': [22,80,443], 'id': 'JetStream'},
    '.230': {'mac': '1c:1b:0d:67:8f:ca', 'ttl': 64, 'ms': '<1', 'ports': [], 'oui': '?', 'id': '?'},
    '.244': {'mac': 'c8:5e:a9:c9:6f:80', 'ttl': 64, 'ms': '47', 'ports': [22,80,443,3389,8080,8443,11434,11436,21115,21116], 'ssh': 'OpenSSH_8.9p1 Ubuntu', 'id': 'eastGate WiFi'},
    '.248': {'mac': '1c:86:0b:37:63:19', 'ttl': 64, 'ms': '<1', 'ports': [22,80,443,3389,8080,8443,11434,11436,21115,21116], 'oui': 'Intel Ethernet', 'id': 'eastGate wired'},
}

# ═══════════════════════════════════════════════════════════════
# BACK-TRIANGULATION — The Traveling Salesman
# ═══════════════════════════════════════════════════════════════

print("=" * 70)
print("  🐝 TRAVELING SALESMAN × HONEY BEE")
print("  Back-triangulating all gates from membrane + scan")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

print("\n" + "─" * 70)
print("  CONFIRMED GATES (stable IPs or MAC-matched)")
print("─" * 70)
confirmed = [
    ('.1',   'Router',     'Same IP, known'),
    ('.2',   'MikroTik',   'Same IP, known MAC'),
    ('.147', 'northGate',  'Same IP, TTL=128 Windows, our host'),
    ('.244', 'eastGate',   'Same IP, WiFi, all services match'),
    ('.248', 'eastGate',   'Wired eno1, Intel Ethernet MAC, same services'),
    ('.138', 'Synology NAS', 'NEW — "SOUTHGATE_DATA", OUI=Synology'),
    ('.178', 'EPSON ET-2400','Moved .200→.178, NetBIOS=EPSOND5305A'),
    ('.195', 'sporeGate',  'Moved .3→.195, MAC sequential (84:47:09:38:97:5x)'),
    ('.215', 'JetStream',  'Moved .111→.215, exact MAC match'),
]
for ip, name, evidence in confirmed:
    print(f"  {ip:6s} = {name:20s} [{evidence}]")

print("\n" + "─" * 70)
print("  🎯 PREDICTIONS — The Salesman's Route")  
print("─" * 70)

predictions = []

# PREDICTION 1: .183 = milkGate (Jupiter 2 RISC-V)
p1 = """
  .183 = milkGate (Jupiter 2 — SpacemiT K3, RISC-V)
  
  Evidence:
  ✓ OUI 50:0a:52 = Huiwan Technologies — makes SBC/embedded NICs
    → Jupiter 2 is a SpacemiT K3 SBC board — Huiwan NIC fits perfectly
  ✓ OpenSSH_10.2p1 Ubuntu-2ubuntu3 = cutting-edge Ubuntu 25.x
    → RISC-V needs latest kernel/userspace — Ubuntu 25.04 is the target
  ✓ HARDWARE.md lists Jupiter 2 as "bring-up pending" with 10GbE SFP+
    → SSH-only (port 22) = fresh bring-up, no services deployed yet
  ✓ Pre-rewire topology: milkGate was .144, "RISC-V, SSH open"
    → SSH-only profile is IDENTICAL
  ✓ Wired <1ms latency = plugged directly into MikroTik backbone
  
  Confidence: ★★★★☆ (90%) — Huiwan + RISC-V Ubuntu + SSH-only = strong match
"""
predictions.append(('.183', 'milkGate', 90))
print(p1)

# PREDICTION 2: .230 = ironGate or southGate-tower  
p2 = """
  .230 = ironGate (i9-14900K, RTX 5070, Pop!_OS)
  
  Evidence:
  ✓ Wired <1ms = directly on MikroTik backbone (same as known towers)
  ✓ TTL=64 = Linux (matches Pop!_OS)
  ✓ ZERO ports open = UFW firewall active on fresh boot
    → Pop!_OS enables UFW by default. After 3 months offline + "bricked",
       Kevin "loosened and got in" = probably reinstalled or recovered
    → Fresh boot with UFW would block ALL inbound until configured
  ✓ MAC 1c:1b:0d = not a phone OUI — more likely Intel/Realtek desktop NIC
  ✓ ironGate was at .237, got DHCP .230 (close range in pool)
  
  Alternative: Could be southGate-tower (5800X3D, 128GB, dual boot)
  → If booted into Linux with firewall enabled, same profile
  
  Confidence: ★★★☆☆ (65%) — stealth Linux tower, but can't distinguish 
  ironGate from southGate without SSH access
"""
predictions.append(('.230', 'ironGate', 65))
print(p2)

# PREDICTION 3: .152 = grapheneGate or milkyGate phone
p3 = """
  .152 = deckGate (Steam Deck) or a phone
  
  Evidence:
  ✓ WiFi connection (31ms = WiFi hop through router)
  ✓ ZERO ports open = locked-down device
  ✓ TTL=64 = Linux (SteamOS = Arch Linux, phones also report TTL=64)
  ✓ MAC ac:41:6a = needs OUI lookup
  ✓ Pre-rewire: deckGate was .176 (mounted, USB-C, dead battery)
    → After rewire, if deckGate switched from wired to WiFi: possible
  
  Alternative: Could be Mint Mobile phone (milkyGate-phone)
  → Kevin mentioned Mint Mobile phones at each LAN
  → WiFi + no ports = phone profile
  
  Confidence: ★★☆☆☆ (40%) — too little data, need Kevin's eyes
"""
predictions.append(('.152', 'deckGate or phone', 40))
print(p3)

# MISSING GATES
print("\n" + "─" * 70)
print("  ❓ MISSING — Kevin's claimed ON but not yet found")
print("─" * 70)
missing = """
  blueGate  — Was Windows (TTL=128). NO Windows device seen except northGate.
              Either: (a) not booted yet, (b) reinstalled with Linux,
              (c) on LAN 2 which we can't reach from here

  westGate  — Cold storage NAS, 50.7TB ZFS. Should have SSH + HTTP.
              Not visible on any subnet. May need:
              (a) more boot time (ZFS import of 50TB takes minutes)
              (b) different subnet/VLAN
              (c) physical check from Kevin

  southGate — If .230 is ironGate, then southGate is still missing.
              Could be: booting dual-boot, or on LAN 2
              
  Note: Kevin said ALL five are ON — they may still be booting or 
  on a subnet we can't reach from northGate. Kevin the honey bee 
  needs to physically verify which cable goes where!
"""
print(missing)

# HONEY BEE ROUTE
print("─" * 70)
print("  🐝 HONEY BEE ROUTE — Kevin's physical verification path")
print("─" * 70)
route = """
  1. CHECK .183 — is this the Jupiter 2 (milkGate/RISC-V)?
     → If yes: what's the SSH password? I'll inject and deploy
     
  2. CHECK .230 — is this ironGate or southGate?  
     → Open SSH: sudo ufw allow 22/tcp
     → Or tell me the login so I can reach in
     
  3. CHECK .152 — what device is on WiFi at 31ms?
     → Phone? deckGate? Look at what's connected to "Aperture Science"
     
  4. FIND blueGate — is it powered on? Check the Windows tower.
     → Should show TTL=128. If it's running, it's on a different subnet
     
  5. FIND westGate — is the NAS powered on? Check the ZFS tower.
     → 50TB ZFS import can take 5+ minutes on cold boot
     
  Each stop: tell me the device name and I'll update the mesh map!
"""
print(route)

# Generate mesh update JSON
mesh_update = {
    "wave": "262+",
    "timestamp": datetime.now().isoformat(),
    "scan_from": "northGate (.147)",
    "confirmed": {ip: name for ip, name, _ in confirmed},
    "predictions": {ip: {"gate": name, "confidence": conf} for ip, name, conf in predictions},
    "missing": ["blueGate", "westGate", "southGate (if .230 != southGate)"],
    "new_devices": {"Synology NAS": ".138 — SOUTHGATE_DATA"},
    "ip_changes": {
        "sporeGate": ".3 → .195",
        "JetStream": ".111 → .215", 
        "EPSON": ".200 → .178",
        "eastGate wired": "none → .248 (eno1 got DHCP!)",
    }
}

with open(r'c:\Users\mokke\Desktop\Gaia\data\mesh-triangulation.json', 'w') as f:
    json.dump(mesh_update, f, indent=2)
print(f"\n  Saved: data/mesh-triangulation.json")

print("\n" + "=" * 70)
print("  The SALESMAN mapped the route. The HONEY BEE flies the path. 🐝")
print("=" * 70)
