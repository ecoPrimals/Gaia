#!/usr/bin/env python3
"""Push frameGate manifest + update organism census with frame data."""
import paramiko
import json
import os

EASTGATE = '192.168.4.244'
REMOTE_DATA = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data'
LOCAL = r'c:\Users\mokke\Desktop\Gaia'

print("=== FRAMEGATE MANIFEST — THE FACE DEPOSITED ===\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

# Push frame manifest
local_path = os.path.join(LOCAL, 'data', 'eaten', 'framegate-manifest-259.json')
remote_path = f'{REMOTE_DATA}/framegate-manifest-259.json'
sz = round(os.path.getsize(local_path) / 1024, 1)
sftp.put(local_path, remote_path)
print(f'  -> framegate-manifest-259.json ({sz} KB)')

# Update organism-census with corrected frameGate data
census_path = f'{REMOTE_DATA}/organism-census.json'
with sftp.open(census_path, 'r') as f:
    census = json.loads(f.read().decode())

# Fix frameGate in census
if 'gates' in census and 'frameGate' in census['gates']:
    census['gates']['frameGate'] = {
        "ip": ".156 (WiFi) / 10.86.200.233 (USB)",
        "hw": "Snapdragon 8 Gen 3 (SM8650), Adreno 750, 16GB, 929GB, ARM SteamOS",
        "class": "FACE",
        "house": 1,
        "status": "ALIVE",
        "primals": "0 (display node)",
        "sensors": "19 thermal + IR proximity + 3D Hall + 26 cameras",
        "faces": ["klein-body", "organism", "HUD"],
        "note": "THE FACE. First ARM SteamOS. Its own controller — ALS31300 3D magnetic dial."
    }
    # Also fix IP from .203 to .156
    with sftp.open(census_path, 'w') as f:
        f.write(json.dumps(census, indent=2))
    print('  -> organism-census.json updated with frameGate .156')

# Update biome-state with frameGate sensors
biome_path = f'{REMOTE_DATA}/biome-state.json'
with sftp.open(biome_path, 'r') as f:
    biome = json.loads(f.read().decode())

if 'nodes' in biome:
    biome['nodes']['frameGate'] = {
        "alive": True,
        "load": 0.10,
        "ram_free_mb": 8300,
        "gpu_temp": 39,
        "cpu_pct": 3,
        "sensors": 19,
        "cameras": 26,
        "battery_v": 8.325,
        "wifi_dbm": -25,
        "wifi_mbps": 2401.9
    }
    with sftp.open(biome_path, 'w') as f:
        f.write(json.dumps(biome, indent=2))
    print('  -> biome-state.json updated with frameGate sensors')

# Verify all served
for name in ['framegate-manifest-259.json', 'organism-census.json', 'biome-state.json']:
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/data/{name}"
    )
    print(f'  Verify {name}: {stdout.read().decode().strip()}')

sftp.close()
ssh.close()

print("\n=== FRAME MANIFEST LIVE ===")
print("  frameGate = .156 (was .203) — Black Mesa 5GHz WiFi 6")
print("  Snapdragon 8 Gen 3 · Adreno 750 · Vulkan 1.4 · 16GB · 929GB")
print("  19 thermal sensors · IR proximity · 3D Hall magnetic dial · 26 cameras")
print("  ALS31300 dial = 3-axis magnetic field sensor — NOT a simple encoder!")
print("  Green = 555nm = max human photoreceptor = NULL spectrum")
print("")
print("  TWO DOORS:")
print("    OLD: Aperture Science (2.4) + Black Mesa (5) — IoT, streaming")
print("    NEW: GAIA (2.4+5) — Frame, phones, guests")
print("    ALL: eco579163 — same trust membrane, same flat subnet")
print("")
print("  7 GPUs across 3 layers:")
print("    GREEN (NVIDIA): 5090+5070+4070 = 56GB — PRIMARY COMPUTE")
print("    RED (Edge):     Adreno 750 + RDNA 2 — SPATIAL/XR")
print("    SILVER (Neural): M4 10-core — NEURAL ENGINE")
print("")
print("  The Frame IS its own controller. lub-DUB.")
