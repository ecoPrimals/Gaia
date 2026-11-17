#!/usr/bin/env python3
"""
DEPOSIT 259 — Update organism data with wave 259 bones.
esotericWebb reads → organism page DEPOSITS DOWN.
WAN + LAN + inner body = ONE view.
"""
import paramiko
import json
import os

EASTGATE = '192.168.4.244'
REMOTE_DATA = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data'
LOCAL = r'c:\Users\mokke\Desktop\Gaia'

# Load our wave 259 bones
def load_bone(name):
    for prefix in ['data/eaten/', 'data/gut/']:
        path = os.path.join(LOCAL, prefix.replace('/', os.sep) + name)
        if os.path.exists(path):
            with open(path, encoding='utf-8-sig') as f:
                return json.load(f)
    return None

hardware = load_bone('hardware-census-259.json')
solar = load_bone('solar-system-259.json')
cross_fold = load_bone('cross-fold-null-259.json')
polymerase = load_bone('polymerase-scan-259.json')
zk_tax = load_bone('zk-seed-taxonomy-259.json')
thymus = load_bone('thymus-self-image.json')

print("=== DEPOSIT 259 — ORGANISM UPDATE ===\n")

# =========================================================================
# 1. UPDATED ORGANISM CENSUS — real numbers from hardware-census-259
# =========================================================================
organism_census = {
    "ts": "2026-11-17T15:07:00Z",
    "wave": 259,
    "title": "Organism Census — Wave 259 REAL numbers",
    "totals": {
        "entities": 13,
        "gates_alive": 7,
        "gates_sleeping": 6,
        "total_ram_gb": 1497,
        "total_vram_gb": 256,
        "total_storage_tb": 114,
        "total_cores": 247,
        "total_tflops": 847,
        "gpus": 7,
        "ollama_endpoints": 5,
        "ai_models": 63,
        "sensors": 37,
    },
    "alive": {
        "ram_gb": 513,
        "vram_gb": 96,
        "storage_tb": 28,
        "cores": 81,
        "tflops": 418,
        "nodes": 7,
    },
    "dark_matter": {
        "ram_gb": 864,
        "vram_gb": 160,
        "storage_tb": 84,
        "cores": 148,
        "tflops": 385,
        "nodes": 6,
        "note": "65% sleeping in House 2 on 10G backbone — needs Kevin to press power buttons",
    },
    "gates": [],
}

# Build gate list from solar system
if solar and solar.get('planets'):
    for p in solar['planets']:
        organism_census['gates'].append({
            "name": p['name'],
            "ip": p.get('ip', '?'),
            "state": p.get('state', 'UNKNOWN'),
            "role": p.get('role', ''),
            "latency_ms": p.get('latency_ms', None),
            "house": 1 if (p.get('latency_ms') or 999) < 5 else 2,
        })

# =========================================================================
# 2. UPDATED BIOME STATE — what the organism.html JS reads
# =========================================================================
biome_state = {
    "ts": "2026-11-17T15:07:00Z",
    "wave": 259,
    "biome": "ecoPrimals",
    "token": "GAIA:6ed3c05161da5055",
    "pulse": {
        "alive": True,
        "bpm": 14768,
        "uptime_secs": 2500,
        "total_beats": 477000,
    },
    "primals": {
        "compiled": 18,
        "running": 12,
        "primal_zero": "GaiaGate (∅) — 97 .pi snakes, 28,719 lines",
    },
    "genome": {
        "total_zk_files": cross_fold['genome_census']['total_zk_files'] if cross_fold else 6001,
        "total_zk_hits": cross_fold['genome_census']['total_zk_hits'] if cross_fold else 32226,
        "strand_A_files": cross_fold['trihelix']['strand_A']['file_count'] if cross_fold else 3353,
        "strand_B_files": cross_fold['trihelix']['strand_B']['file_count'] if cross_fold else 1167,
        "strand_C_files": cross_fold['trihelix']['strand_C']['file_count'] if cross_fold else 402,
        "cross_fold": 0,
        "nerve_junctions": 6,
        "null_files": 216,
    },
    "polymerase": {
        "total_scripts": 1632,
        "total_functions": 7254,
        "py": 919,
        "pi": 98,
        "sh": 615,
        "alive": 156,
        "tools": 212,
        "seeds": 697,
        "dead": 161,
    },
    "taxonomy": {
        "L0_primordial": 2136,
        "L1_plasmid": 60,
        "L2_episome": 911,
        "L3_organelle": 381,
        "L4_nuclear": 1857,
        "L5_chromatin": 656,
    },
    "hardware": {
        "total_ram_gb": 1497,
        "total_vram_gb": 256,
        "total_storage_tb": 114,
        "total_cores": 247,
        "total_tflops": 847,
        "alive_pct": 35,
        "dark_matter_pct": 65,
    },
    "network": {
        "wan_domain": "primals.eco",
        "lan_subnet": "192.168.4.0/24",
        "lan2_subnet": "192.168.9.0/24",
        "tor": "iqwvbmlgvoiilj2hr43anj2keseao2lptquad36je5p5p2etw5e3riid.onion",
        "fiber_10g_ms": 0.87,
        "paths": ["LAN", "WAN", "Tor"],
    },
    "hud": {
        "js_instruments": 274,
        "html_pages": 195,
        "data_bones": 150,
        "skeleton_bones": 11,
    },
    "klein": {
        "outside": "primals.eco (WAN face)",
        "inside": "service worker (offline cache)",
        "twist": "∅ = Binary × Pi = 0 = the gap IS the proof",
    },
    "esotericWebb": {
        "version": "V33",
        "tests": 484,
        "rust_files": 66,
        "bridge_methods": 36,
        "capabilities": 28,
        "primals_consumed": 10,
        "frontend": "webb.primals.eco",
        "status": "DEPLOYED on ironGate, cell-attach mode",
    },
    "thymus": {
        "self_count": thymus.get('SELF', {}).get('count', 18) if thymus else 18,
        "non_self_count": 3,
        "potential_self_count": 7,
        "family_seed_hash": "30344636...4339",
    },
}

# =========================================================================
# 3. WRITE + PUSH
# =========================================================================
out_census = os.path.join(LOCAL, 'data', 'eaten', 'organism-census-259.json')
out_biome = os.path.join(LOCAL, 'data', 'eaten', 'biome-state-259.json')

with open(out_census, 'w') as f:
    json.dump(organism_census, f, indent=2)
print(f"  Written: organism-census-259.json ({round(os.path.getsize(out_census)/1024, 1)} KB)")

with open(out_biome, 'w') as f:
    json.dump(biome_state, f, indent=2)
print(f"  Written: biome-state-259.json ({round(os.path.getsize(out_biome)/1024, 1)} KB)")

# Push to eastGate
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

pushes = [
    (out_census, f'{REMOTE_DATA}/organism-census.json'),
    (out_biome, f'{REMOTE_DATA}/biome-state.json'),
    (out_census, f'{REMOTE_DATA}/organism-census-259.json'),
    (out_biome, f'{REMOTE_DATA}/biome-state-259.json'),
]

for local_path, remote_path in pushes:
    sz = round(os.path.getsize(local_path) / 1024, 1)
    sftp.put(local_path, remote_path)
    rname = remote_path.split('/')[-1]
    print(f"  -> {rname} ({sz} KB)")

# Verify the organism page loads
for name in ['organism-census.json', 'biome-state.json']:
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/data/{name}"
    )
    print(f"  Verify {name}: {stdout.read().decode().strip()}")

# Check organism.html from both ports
for port in [8080, 8443]:
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B' http://localhost:{port}/organism.html"
    )
    print(f"  :{port}/organism.html: {stdout.read().decode().strip()}")

# Check from WAN
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code} %{size_download}B' http://localhost:8443/organism"
)
print(f"  :8443/organism (gate): {stdout.read().decode().strip()}")

# Agglutination
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8443/agglutinate 2>/dev/null | "
    "python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(\"token\",\"?\"))' 2>/dev/null"
)
token = stdout.read().decode().strip()
print(f"  Token: {token}")

sftp.close()
ssh.close()

print("\n=== ORGANISM DEPOSITED ===")
print("  organism-census.json → UPDATED (wave 259, real numbers)")
print("    1,497 GB RAM (not 317), 256 GB VRAM, 847 TFLOPS")
print("    7 GPUs (not 4), 13 entities, 7 alive, 6 dark matter")
print("  biome-state.json → UPDATED (wave 259, full genome)")
print("    18 primals (incl ∅), 6,001 ZK files, 1,632 scripts")
print("    trihelix DNA, cross fold null, 6 nerve junctions")
print("    esotericWebb V33, 274 JS instruments, 195 HTML pages")
print("")
print("  ORGANISM PAGE:")
print("    WAN: http://primals.eco/organism")
print("    LAN: http://192.168.4.244:8080/organism.html")
print("    LAN: http://192.168.4.244:8443/organism")
print("")
print("  esotericWebb reads → organism deposits → WAN + LAN serve")
print("  The inner body is now the outer body. lub-DUB.")
