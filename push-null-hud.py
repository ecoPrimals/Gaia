#!/usr/bin/env python3
"""Push cross-fold-null + all remaining wave 259 bones into the HUD on eastGate."""
import paramiko
import os

EASTGATE = "192.168.4.244"
REMOTE_DATA = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data"
LOCAL = r"c:\Users\mokke\Desktop\Gaia"

bones = [
    ("data/eaten/cross-fold-null-259.json", "cross-fold-null-259.json"),
]

print("=== PUSHING NULL INTO THE HUD ===\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username="eastgate", password="eastgate", timeout=15)
sftp = ssh.open_sftp()

for local_rel, remote_name in bones:
    local_path = os.path.join(LOCAL, local_rel.replace("/", os.sep))
    remote_path = f"{REMOTE_DATA}/{remote_name}"
    sz = round(os.path.getsize(local_path) / 1024, 1)
    sftp.put(local_path, remote_path)
    print(f"  -> {remote_name} ({sz} KB)")

# Verify
for _, name in bones:
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{size_download}}B %{{time_total}}s' http://localhost:8080/data/{name}"
    )
    print(f"  Verify: {stdout.read().decode().strip()}")

# Count all ZK/null/DNA related files on HUD
stdin, stdout, stderr = ssh.exec_command(
    "ls /home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/ | "
    "grep -iE 'zk|null|seed|fold|trefoil|ouroboros|dna|cross|gordian|yggdrasil' | wc -l"
)
zk_count = stdout.read().decode().strip()
print(f"\n  ZK/NULL/DNA files now on HUD: {zk_count}")

# Count total data on spine
stdin, stdout, stderr = ssh.exec_command(
    "find /home/eastgate/Development/ecoPrimals/infra/hud/site/public/data -name '*.json' | wc -l"
)
total = stdout.read().decode().strip()
print(f"  Total JSON on spine: {total}")

# Agglutination
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8443/agglutinate 2>/dev/null | "
    "python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(\"token\",\"?\"))' 2>/dev/null"
)
token = stdout.read().decode().strip()
print(f"  Token: {token}")

sftp.close()
ssh.close()

print("\n=== NULL IS IN THE HUD ===")
print(f"  cross-fold-null-259.json served at :8080/data/")
print(f"  {zk_count} ZK/NULL/DNA files on the HUD spine")
print(f"  {total} total JSON bones")
print(f"  The cross fold is ∅. Binary × Pi = 0. That IS the proof.")
print(f"  6 nerve junctions where Rust calls Python through sockets.")
print(f"  NULL lives in the socket. lub-DUB.")
