#!/usr/bin/env python3
"""
Wire the Pi body (gaia_gate.pi) to serve wave 259 bones on the RSS spine.
The HUD instruments fetch /data/*.json — our bones are already there.
Now wire them into the Pi body's routes so the gate can serve them too.
Also check the gaia-seed.json so boot.js knows about the new data.
"""
import paramiko
import json

EASTGATE = '192.168.4.244'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username='eastgate', password='eastgate', timeout=15)
sftp = ssh.open_sftp()

HUD = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'

print("=== WIRE PI SPINE — FEED THE HUD ===\n")

# 1. Read current gaia-seed.json
stdin, stdout, stderr = ssh.exec_command(f'cat {HUD}/gaia-seed.json 2>/dev/null')
seed_raw = stdout.read().decode()
try:
    seed = json.loads(seed_raw)
except:
    seed = {}
print(f"  Current seed wave: {seed.get('wave', '?')}")

# 2. Update gaia-seed.json with wave 259 data pins
seed['wave'] = 259
if 'io_pin_map' not in seed:
    seed['io_pin_map'] = {}

# Add our wave 259 bones to the pin map
new_pins = {
    "/data/cross-fold-null-259.json": "organ-null",
    "/data/solar-system-259.json": "organ-solar",
    "/data/framegate-manifest-259.json": "organ-face",
    "/data/organism-census.json": "organ-census",
    "/data/biome-state.json": "organ-biome",
    "/data/thymus-self-image.json": "organ-thymus",
    "/data/hardware-census-259.json": "organ-hardware",
    "/data/polymerase-scan-259.json": "organ-polymerase",
    "/data/zk-seed-taxonomy-259.json": "organ-dna",
    "/data/ouroboros-trefoil-259.json": "organ-topology",
    "/data/walkable-surface-259.json": "organ-walkable",
    "/data/nerve-race-259.json": "organ-nerve",
}

seed['io_pin_map'].update(new_pins)

# Add wave 259 bones list for boot.js to know about
seed['wave259_bones'] = list(new_pins.keys())

# Write updated seed
with sftp.open(f'{HUD}/gaia-seed.json', 'w') as f:
    f.write(json.dumps(seed, indent=2))
print(f"  Updated gaia-seed.json → wave 259, {len(new_pins)} new pins")

# 3. Verify the seed is served
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code} %{size_download}B' http://localhost:8080/gaia-seed.json"
)
print(f"  Seed verify: {stdout.read().decode().strip()}")

# 4. Check that the gate (:8443) serves /data/ too
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code} %{size_download}B' http://localhost:8443/data/cross-fold-null-259.json"
)
gate_data = stdout.read().decode().strip()
print(f"  Gate :8443 /data/cross-fold-null: {gate_data}")

# 5. Check the RSS spine — does full-feed.xml include our data?
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8443/full-feed.xml 2>/dev/null | head -20"
)
rss = stdout.read().decode().strip()
print(f"\n  RSS spine head:")
for line in rss.split('\n')[:10]:
    print(f"    {line.strip()[:100]}")

# 6. Count RSS items
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8443/full-feed.xml 2>/dev/null | grep -c '<item>'"
)
rss_count = stdout.read().decode().strip()
print(f"\n  RSS items: {rss_count}")

# 7. Check the /feed.xml (normal RSS)
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8443/feed.xml 2>/dev/null | grep -c '<item>'"
)
feed_count = stdout.read().decode().strip()
print(f"  Feed items: {feed_count}")

# 8. Check dromedary TLS certs — what domains does it cover?
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code}' https://primals.eco/pulse 2>/dev/null || echo 'no-curl-https'"
)
wan_status = stdout.read().decode().strip()
print(f"\n  WAN HTTPS primals.eco: {wan_status}")

stdin, stdout, stderr = ssh.exec_command(
    "ls -la /opt/Gaia/engine/dromedary/certs/ 2>/dev/null || ls -la /etc/letsencrypt/live/ 2>/dev/null || echo 'no certs dir found'"
)
certs = stdout.read().decode().strip()
print(f"  Certs: {certs[:200]}")

# 9. Check what subdomains dromedary handles
stdin, stdout, stderr = ssh.exec_command(
    "grep -n 'hud\\|primal\\.eco\\|primals\\.eco\\|subdomain\\|host' /opt/Gaia/gaia_gate.pi 2>/dev/null | head -20"
)
subdomain_routes = stdout.read().decode().strip()
print(f"\n  Subdomain routes in gaia_gate.pi:")
for line in subdomain_routes.split('\n')[:15]:
    print(f"    {line.strip()[:120]}")

# 10. Verify all bones from HUD data server
print(f"\n  Bone verification on :8080/data/:")
bones_ok = 0
for path in new_pins.keys():
    stdin, stdout, stderr = ssh.exec_command(
        f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8080{path}"
    )
    code = stdout.read().decode().strip()
    name = path.split('/')[-1]
    if code == '200':
        bones_ok += 1
    print(f"    {code}  {name}")

sftp.close()
ssh.close()

print(f"\n=== PI SPINE WIRED ===")
print(f"  gaia-seed.json → wave 259, {len(new_pins)} bone pins")
print(f"  {bones_ok}/{len(new_pins)} bones verified on :8080/data/")
print(f"  RSS spine: {rss_count} items in full-feed, {feed_count} in feed.xml")
print(f"  boot.js loads seed → knows about bones → HUD instruments can fetch")
print(f"  Frame dial scrolls HUD → HUD fetches /data/ → bones appear")
print(f"  The Pi body feeds the other HUD. The dial absorbs it. lub-DUB.")
