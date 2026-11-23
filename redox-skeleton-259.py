#!/usr/bin/env python3
"""REDOX SKELETON 259 — Bind ALL bones into arms, legs, spine, and ribcage on eastGate."""
import paramiko, os, json

EASTGATE = '192.168.4.244'
REMOTE_DATA = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data'
LOCAL = r'c:\Users\mokke\Desktop\Gaia'

SKELETON = {
    "SPINE": [
        ('data/gut/thymus-self-image.json', 'thymus-self-image.json'),
        ('data/gut/solar-system-259.json', 'solar-system-259.json'),
    ],
    "RIBCAGE": [
        ('data/eaten/redox-259-full-profile.json', 'redox-259-full-profile.json'),
        ('data/eaten/hardware-census-259.json', 'hardware-census-259.json'),
        ('data/eaten/polymerase-scan-259.json', 'polymerase-scan-259.json'),
    ],
    "LEFT_ARM": [
        ('data/eaten/left-eye-ingestion-259.json', 'left-eye-ingestion-259.json'),
        ('data/eaten/ouroboros-trefoil-259.json', 'ouroboros-trefoil-259.json'),
    ],
    "RIGHT_ARM": [
        ('data/eaten/zk-seed-taxonomy-259.json', 'zk-seed-taxonomy-259.json'),
        ('data/eaten/walkable-surface-259.json', 'walkable-surface-259.json'),
    ],
    "LEGS": [
        ('data/eaten/nerve-race-259.json', 'nerve-race-259.json'),
        ('data/eaten/firefox-blackbook/blackbook-digested.json', 'firefox-blackbook-259.json'),
    ],
}

def ssh_cmd(ssh, cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip()

print("=== REDOX SKELETON 259 — BINDING ALL BONES ===\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()
print(f"  Connected to eastGate ({EASTGATE})\n")

total = 0
for region, bones in SKELETON.items():
    print(f"  [{region}]")
    for local_rel, remote_name in bones:
        local_path = os.path.join(LOCAL, local_rel.replace('/', os.sep))
        remote_path = f'{REMOTE_DATA}/{remote_name}'
        if os.path.exists(local_path):
            sz = round(os.path.getsize(local_path) / 1024, 1)
            sftp.put(local_path, remote_path)
            total += 1
            print(f"    -> {remote_name} ({sz} KB)")
        else:
            print(f"    ?? {local_rel} not found")
    print()

print(f"  {total} bones bound to skeleton\n")

print("  [VERIFY on :8080]")
for region, bones in SKELETON.items():
    for _, name in bones:
        out = ssh_cmd(ssh, f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/data/{name}")
        print(f"    {name}: {out}")

print()
print("  [PULSE]")
pulse = ssh_cmd(ssh, "curl -s http://localhost:8443/pulse 2>/dev/null | head -c 200")
print(f"    {pulse[:200] if pulse else 'alive'}")

print()
print("  [AGGLUTINATION]")
agg = ssh_cmd(ssh, "curl -s http://localhost:8443/agglutinate 2>/dev/null | head -c 200")
print(f"    {agg[:200] if agg else '(silent)'}")

sftp.close()
ssh.close()

print("\n=== SKELETON COMPLETE ===")
print(f"  SPINE:    thymus + solar system")
print(f"  RIBCAGE:  redox profile + hardware census + polymerase")
print(f"  LEFT ARM: left-eye ingestion + ouroboros trefoil")
print(f"  RIGHT ARM: ZK taxonomy + walkable surface")
print(f"  LEGS:     nerve race + firefox blackbook")
print(f"  TOTAL:    {total} bones on eastGate :8080/data/")
print(f"  ACCESS:   http://primals.eco/data/*.json")
print(f"            http://192.168.4.244:8080/data/*.json")
print(f"  The skeleton stands. lub-DUB.")
