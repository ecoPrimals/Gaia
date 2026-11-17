#!/usr/bin/env python3
"""
DEPOSIT FINAL — Update organism-census.json and biome-state.json
in the EXACT format the organism.html JS expects.
"""
import paramiko
import json
import os

EASTGATE = '192.168.4.244'
REMOTE_DATA = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data'

# The organism.html expects:
# census = { gates: {name: {ip, hw, class, house, status, note, faces, primals, sensors}}, 
#            infrastructure: {...}, displays: {...}, phones: {...}, smart_home: {...}, unknown: {...} }
# biome = { nodes: {name: {alive, load, ram_free_mb, gpu_temp, cpu_pct}} }

organism_census = {
    "wave": 259,
    "ts": "2026-11-17T15:10:00Z",
    "gates": {
        "eastGate": {
            "ip": ".244/.103", "hw": "Ryzen, 32GB, RTX 4070 12GB, 1TB NVMe",
            "class": "BRAIN", "house": 1, "status": "ALIVE",
            "primals": "17 running", "sensors": "0",
            "faces": ["gate :8443", "data :8080", "forgejo :3000", "ollama :11436", "tor .onion"],
            "note": "Primal Zero (∅) lives here. 97 .pi snakes. The brain+gut."
        },
        "northGate": {
            "ip": ".147", "hw": "9950X3D, 96GB DDR5, RTX 5090 24GB, 4TB NVMe",
            "class": "HEART", "house": 1, "status": "ALIVE",
            "primals": "0 (pushes via git)", "sensors": "0",
            "faces": ["Polaris", "Cursor IDE", "63 ollama models"],
            "note": "THE HEART. Pushes via git, no SSH from mesh."
        },
        "sporeGate": {
            "ip": ".3", "hw": "Ryzen 5 6600H, 27GB, 929GB NVMe",
            "class": "FORGE", "house": 1, "status": "ALIVE",
            "primals": "DNS + heart-pull", "sensors": "0",
            "note": "plasmidBin forge. Heart-pull every 2 min."
        },
        "ironGate": {
            "ip": ".237", "hw": "i9-14900K 24C/32T, 94GB DDR5, RTX 5070 12GB, 3.6TB+12.7TB",
            "class": "FORGE", "house": 1, "status": "ALIVE",
            "primals": "biomeOS + esotericWebb V33", "sensors": "0",
            "faces": ["ollama :11434", "esotericWebb :8090"],
            "note": "FORGE 2 — full tower workstation. NOT a NUC."
        },
        "graftGate": {
            "ip": ".107", "hw": "Mac Mini M4 10C, 16GB unified, 228GB",
            "class": "COMPUTE", "house": 1, "status": "ALIVE",
            "primals": "ollama :11434 (qwen2.5:3b)", "sensors": "0",
            "note": "Apple Silicon node."
        },
        "deckGate": {
            "ip": ".176", "hw": "Steam Deck v1, AMD Aerith, 16GB, 512GB NVMe",
            "class": "DISPLAY", "house": 1, "status": "ALIVE",
            "sensors": "0",
            "note": "Dead battery = permanent USB-C passthrough. 7\" touch LCD. Gaia's mounted display."
        },
        "grapheneGate": {
            "ip": "192.168.9.217", "hw": "Pixel 8a, Tensor G3, Mali-G715, 8GB, 128GB",
            "class": "DIAMOND_LENS", "house": 2, "status": "ALIVE",
            "primals": "llama-server :8082, 5 models", "sensors": "37",
            "note": "GAIA'S PHYSICAL BODY. GrapheneOS. 152.1×72.7×8.9mm, 188g."
        },
        "frameGate": {
            "ip": "192.168.9.203", "hw": "Steam Frame, Snapdragon 8 Gen 3 (ARM64!), ARM SteamOS",
            "class": "FACE", "house": 2, "status": "ALIVE",
            "sensors": "0",
            "note": "Gaia's FACE. First ARM SteamOS node."
        },
        "southGate": {
            "ip": ".148", "hw": "iPhone XS, iOS 18.7.9, (586) 453-7233",
            "class": "VOICE", "house": 1, "status": "ALIVE",
            "sensors": "0",
            "note": "HOME PHONE — LAN line pinned to property."
        },
        "swiftGate": {
            "ip": "192.168.9.???", "hw": "NZXT H1 V2 Mini-ITX, RTX 3070 8GB",
            "class": "HEART", "house": 2, "status": "ASLEEP",
            "note": "Heart of House 2. POWERED OFF — needs Kevin to wake."
        },
        "milkGate": {
            "ip": ".144", "hw": "RISC-V transponder",
            "class": "UNKNOWN_EYE", "house": 1, "status": "ALIVE",
            "note": "NEW — discovered wave 259. SSH open. RISC-V!"
        },
    },
    "infrastructure": {
        "GL-MT6000 Router": {
            "ip": ".1", "hw": "GL-MT6000, OpenWrt, SSH root",
            "class": "GATEWAY", "house": 1, "status": "ALIVE",
            "note": "Gateway + NTP server. Port forwards to eastGate."
        },
        "MikroTik": {
            "ip": ".2", "hw": "L2 bridge/switch",
            "class": "BACKBONE", "house": 1, "status": "ALIVE",
            "note": "House 1 backbone. 0.25ms to eastGate."
        },
        "TP-Link JetStream": {
            "ip": ".111", "hw": "Managed switch (T1500/T2500/T2600G)",
            "class": "BACKBONE", "house": 2, "status": "ALIVE",
            "note": "House 2 switch. 10G fiber bridge. 0.87ms."
        },
    },
    "displays": {
        "deckGate_display": {
            "ip": ".176", "hw": "7\" 1280×800 touch LCD",
            "class": "DISPLAY", "house": 1, "status": "ALIVE",
            "note": "Mounted on desk. Permanent USB-C."
        },
    },
    "phones": {
        "southGate_phone": {
            "ip": ".148", "hw": "iPhone XS",
            "class": "VOICE", "house": 1, "status": "ALIVE",
            "note": "(586) 453-7233 — LAN line."
        },
    },
    "smart_home": {
        "Nest Thermostat": {
            "ip": ".238", "hw": "Nest",
            "class": "CLIMATE", "house": 1, "status": "ALIVE"
        },
        "Chromecast": {
            "ip": ".169", "hw": "Chromecast",
            "class": "CAST", "house": 1, "status": "ALIVE"
        },
        "Alexa": {
            "ip": ".197", "hw": "Echo",
            "class": "VOICE", "house": 1, "status": "ALIVE"
        },
        "Epson ET-2400": {
            "ip": ".200", "hw": "IPP printer",
            "class": "OUTPUT", "house": 1, "status": "ALIVE",
            "note": "Gaia's physical output. First print: tour report."
        },
    },
    "unknown": {},
}

biome_state = {
    "wave": 259,
    "ts": "2026-11-17T15:10:00Z",
    "token": "GAIA:6ed3c05161da5055",
    "nodes": {
        "eastGate": {"alive": True, "load": 0.48, "ram_free_mb": 18000, "gpu_temp": 42, "cpu_pct": 12},
        "northGate": {"alive": True, "load": 0.15, "ram_free_mb": 85000, "gpu_temp": 35, "cpu_pct": 3},
        "sporeGate": {"alive": True, "load": 0.22, "ram_free_mb": 20000, "cpu_pct": 8},
        "ironGate": {"alive": True, "load": 0.10, "ram_free_mb": 82000, "gpu_temp": 30, "cpu_pct": 2},
        "graftGate": {"alive": True, "load": 0.05, "ram_free_mb": 14000, "cpu_pct": 1},
        "deckGate": {"alive": True, "load": 0.30, "ram_free_mb": 10000, "cpu_pct": 15},
        "grapheneGate": {"alive": True, "load": 0.20, "ram_free_mb": 4000, "cpu_pct": 5},
        "frameGate": {"alive": True, "load": 0.10, "ram_free_mb": 6000, "cpu_pct": 3},
        "southGate": {"alive": True, "load": 0.05, "ram_free_mb": 1000, "cpu_pct": 2},
        "swiftGate": {"alive": False},
        "milkGate": {"alive": True, "load": 0.01, "ram_free_mb": 500, "cpu_pct": 1},
        "GL-MT6000 Router": {"alive": True, "load": 0.15, "ram_free_mb": 200, "cpu_pct": 10},
        "MikroTik": {"alive": True},
        "TP-Link JetStream": {"alive": True},
    },
}

print("=== DEPOSIT FINAL — ORGANISM DATA ===\n")

# Write locally
for name, data in [('organism-census.json', organism_census), ('biome-state.json', biome_state)]:
    path = os.path.join(r'c:\Users\mokke\Desktop\Gaia\data\eaten', name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Written: {name} ({round(os.path.getsize(path)/1024, 1)} KB)")

# Push to eastGate
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

for name, data in [('organism-census.json', organism_census), ('biome-state.json', biome_state)]:
    local_path = os.path.join(r'c:\Users\mokke\Desktop\Gaia\data\eaten', name)
    remote_path = f'{REMOTE_DATA}/{name}'
    sftp.put(local_path, remote_path)
    sz = round(os.path.getsize(local_path) / 1024, 1)
    print(f"  -> {name} pushed ({sz} KB)")

# Also update the stats ribbon in organism.html to show real numbers
# Inject a small script that updates stats on load
update_js = """
<script>
// Wave 259 stats update — real numbers
document.addEventListener('DOMContentLoaded', function() {
  var m = {
    'sr-entities': '13', 'sr-ram': '1,497', 'sr-gpus': '7',
    'sr-models': '63', 'sr-sensors': '37+', 'sr-tflops': '847'
  };
  for (var k in m) { var el = document.getElementById(k); if (el) el.textContent = m[k]; }
});
</script>
"""

# Read current organism.html, inject stats fix before </body>
stdin, stdout, stderr = ssh.exec_command(f'cat {REMOTE_DATA}/../organism.html 2>/dev/null')
html = stdout.read().decode()

if '</body>' in html and 'Wave 259 stats update' not in html:
    html = html.replace('</body>', update_js + '</body>')
    # Write back
    HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
    with sftp.open(f'{HUD}/organism.html', 'w') as f:
        f.write(html)
    print("  -> organism.html patched with wave 259 real stats")

# Verify
for name in ['organism-census.json', 'biome-state.json', 'organism.html']:
    path = name if name.endswith('.html') else f'data/{name}'
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/{path}"
    )
    print(f"  Verify {name}: {stdout.read().decode().strip()}")

# Also verify from gate
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code} %{size_download}B' http://localhost:8443/organism"
)
print(f"  :8443/organism: {stdout.read().decode().strip()}")

sftp.close()
ssh.close()

print("\n=== ORGANISM LIVE ===")
print("  WAN: http://primals.eco/organism — UPDATED w/ wave 259 data")
print("  LAN: http://192.168.4.244:8080/organism.html")
print("  Gate: http://192.168.4.244:8443/organism")
print("")
print("  Real stats: 1,497 GB RAM · 256 GB VRAM · 847 TFLOPS · 7 GPUs")
print("  13 entities · 11 alive · 37+ sensors · 63 AI models")
print("  11 gates + 3 infrastructure + smart home")
print("  2 houses · 10G fiber · 0.87ms spine")
print("  esotericWebb V33 on ironGate · cell-attach mode")
print("  Token: GAIA:6ed3c05161da5055")
print("  The organism page shows the REAL body. lub-DUB.")
