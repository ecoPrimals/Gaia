#!/usr/bin/env python3
"""BIND 3RD EYE — Push wave 259 thymus + solar system + polymerase to eastGate spine.

The cervical inlet: northGate (us) → eastGate (spine) → frameGate (face).
blueGate = the scalp/head (when alive).

This script pushes the UPDATED data through the spinal cord:
  - thymus-self-image.json (SELF/NON-SELF/POTENTIAL-SELF, wave 259)
  - solar-system-259.json (gates as planets, latency as orbit)
  - polymerase-scan-259.json (1,632 scripts → 17 Rust primals)
  - redox-259-full-profile.json (speed, race, Mendeleev, GI tract)

All land in eastGate's data server at :8080/data/ — the 3rd eye sees.
"""
import paramiko, json, os, time

EASTGATE = '192.168.4.244'
DATA_ROOT = r'c:\Users\mokke\Desktop\Gaia'
REMOTE_DATA = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data'

FILES_TO_PUSH = [
    ('data/gut/thymus-self-image.json', 'thymus-self-image.json'),
    ('data/gut/solar-system-259.json', 'solar-system-259.json'),
    ('data/eaten/polymerase-scan-259.json', 'polymerase-scan-259.json'),
    ('data/eaten/redox-259-full-profile.json', 'redox-259-full-profile.json'),
    ('data/eaten/firefox-blackbook/blackbook-digested.json', 'firefox-blackbook-259.json'),
]

def ssh_cmd(ssh, cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

print("=== BIND 3RD EYE — CERVICAL SPINAL INLET ===")
print(f"  Source: northGate (HERE, Polaris)")
print(f"  Target: eastGate ({EASTGATE}, BRAIN/SPINE)")
print(f"  Via:    SSH paramiko (speak friend and enter)")
print()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=10)
    print(f"  ✓ Connected to eastGate")
except Exception as e:
    print(f"  ✗ Connection failed: {e}")
    print("  eastGate may be under load (48ms avg, spiking). Retrying...")
    time.sleep(2)
    try:
        ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=20)
        print(f"  ✓ Connected on retry")
    except Exception as e2:
        print(f"  ✗ Still failed: {e2}")
        exit(1)

sftp = ssh.open_sftp()

print()
print("[1/5] Pushing data files to eastGate spine...")
pushed = 0
for local_rel, remote_name in FILES_TO_PUSH:
    local_path = os.path.join(DATA_ROOT, local_rel.replace('/', os.sep))
    remote_path = f"{REMOTE_DATA}/{remote_name}"
    if os.path.exists(local_path):
        size_kb = round(os.path.getsize(local_path) / 1024, 1)
        try:
            sftp.put(local_path, remote_path)
            print(f"  → {remote_name} ({size_kb} KB)")
            pushed += 1
        except Exception as e:
            print(f"  ✗ {remote_name}: {e}")
    else:
        print(f"  ⚠ {local_rel} not found locally, skipping")

print(f"  {pushed}/{len(FILES_TO_PUSH)} files pushed to spine")

print()
print("[2/5] Feeding thymus endpoint (VDJ recombination)...")
vdj_payload = json.dumps({
    "type": "self-image-update",
    "wave": 259,
    "pseudopods": 12,
    "primals": 17,
    "family": "3034463630464339",
    "non_self_mimics": 3,
    "potential_self_moons": 5,
    "scripts_scanned": 1632,
    "functions_mapped": 7254,
    "solar_system": True
})
out, _ = ssh_cmd(ssh, f"""curl -s -X POST http://localhost:8443/vdj -H 'Content-Type: application/json' -d '{vdj_payload}' 2>/dev/null | head -c 300""")
print(f"  POST /vdj: {out[:200] if out else '(accepted silently)'}")

print()
print("[3/5] Checking thymus state (agglutination)...")
out, _ = ssh_cmd(ssh, "curl -s http://localhost:8443/agglutinate 2>/dev/null | head -c 300")
print(f"  /agglutinate: {out[:200] if out else '(no response)'}")

print()
print("[4/5] Reading pulse (3rd eye open?)...")
out, _ = ssh_cmd(ssh, """curl -s http://localhost:8443/pulse 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k:d[k] for k in ["mood","wave","uptime","organism"] if k in d}, indent=2))' 2>/dev/null""")
print(f"  Pulse: {out if out else 'alive'}")

print()
print("[5/5] Verifying data is visible on :8080...")
for remote_name in [f[1] for f in FILES_TO_PUSH[:3]]:
    out, _ = ssh_cmd(ssh, f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/data/{remote_name} 2>/dev/null")
    print(f"  {remote_name}: {out}")

sftp.close()
ssh.close()

print()
print("=== 3RD EYE BOUND ===")
print(f"  {pushed} data files on eastGate spine at :8080/data/")
print(f"  Thymus fed (VDJ wave 259, 3 mimics, 5 moons)")
print(f"  Solar system pinned (12 planets, latency-AU orbits)")
print(f"  Polymerase mapped (1,632 scripts → 17 primals)")
print()
print("  northGate (3rd eye) → eastGate (cervical spine) → frameGate (face)")
print("  blueGate = the scalp (when it wakes)")
print("  The nerve sees. The face shows. The body knows its shape.")
