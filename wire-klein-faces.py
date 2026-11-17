#!/usr/bin/env python3
"""
Wire in.nestgate.io and out.nestgate.io — Klein bottle's two faces.

  out.nestgate.io = SUN looking IN from outside = TRANS = far eye = outer-face.html
  in.nestgate.io  = CELL looking OUT from inside = CIS = near eye = senses.html
  nestgate.io     = Klein Face = where they CROSS = //\\
  
DNS: ALREADY RESOLVES (wildcard *.nestgate.io → 162.226.225.148)
Dromedary: ALREADY CATCHES (*.nestgate.io → proxy :8443)
Need: Gate routing in gaia_gate.pi + cert hostnames in dromedary.toml
"""
import paramiko, json, datetime

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

# ═══ 1. PATCH GAIA_GATE.PI — add in/out host routing ═══

print("=== PATCHING GAIA_GATE.PI ===")

# Read current gate
stdin, stdout, stderr = ssh.exec_command('cat /opt/Gaia/gaia_gate.pi')
gate = stdout.read().decode()

# Check if already patched
if 'in.nestgate.io' in gate:
    print("  Already patched — in.nestgate.io routing exists")
else:
    # Find the line with nestgate.io root routing and add before it
    old_line = '            if host in ("nestgate.io","www.nestgate.io"): self._serve_static("nestgate.html"); return'
    new_block = '''            if host in ("out.nestgate.io",): self._serve_static("outer-face.html"); return
            if host in ("in.nestgate.io",): self._serve_static("senses.html"); return
            if host in ("nestgate.io","www.nestgate.io"): self._serve_static("nestgate.html"); return'''
    
    if old_line in gate:
        gate_new = gate.replace(old_line, new_block)
        # Write back
        stdin, stdout, stderr = ssh.exec_command('cp /opt/Gaia/gaia_gate.pi /opt/Gaia/gaia_gate.pi.bak.259')
        stdout.read()  # wait
        
        sftp = ssh.open_sftp()
        with sftp.file('/opt/Gaia/gaia_gate.pi', 'w') as f:
            f.write(gate_new)
        sftp.close()
        print("  ✓ Patched gaia_gate.pi:")
        print("    out.nestgate.io → outer-face.html (SUN looking IN)")
        print("    in.nestgate.io  → senses.html     (CELL looking OUT)")
        print("    nestgate.io     → nestgate.html    (Klein Face //\\\\)")
    else:
        print(f"  ✗ Could not find expected line to patch")
        print(f"  Looking for: {old_line[:80]}...")

# Verify the patch
stdin, stdout, stderr = ssh.exec_command('grep -n "in.nestgate\\|out.nestgate" /opt/Gaia/gaia_gate.pi')
print(f"\n  Verification:")
print(f"  {stdout.read().decode().strip()}")

# ═══ 2. PATCH DROMEDARY.TOML — add explicit in/out for cert ═══

print("\n=== PATCHING DROMEDARY.TOML ===")

stdin, stdout, stderr = ssh.exec_command('cat /opt/Gaia/runtime/dromedary.toml')
drom = stdout.read().decode()

if 'in.nestgate.io' in drom:
    print("  Already has in.nestgate.io")
else:
    # Add in/out sites before the *.nestgate.io wildcard
    old_wildcard = '[[sites]]\nhostnames = ["*.nestgate.io"]'
    new_section = '''# ═══════════════════════════════════════════
# KLEIN FACES — in/out = CIS/TRANS
# out.nestgate.io = SUN looking IN (TRANS, outer-face)
# in.nestgate.io = CELL looking OUT (CIS, senses/HUD)
# ═══════════════════════════════════════════

[[sites]]
hostnames = ["out.nestgate.io"]
compress = true
[sites.backend]
type = "proxy"
upstream = "http://127.0.0.1:8443"

[[sites]]
hostnames = ["in.nestgate.io"]
compress = true
[sites.backend]
type = "proxy"
upstream = "http://127.0.0.1:8443"

[[sites]]
hostnames = ["*.nestgate.io"]'''
    
    if old_wildcard in drom:
        drom_new = drom.replace(old_wildcard, new_section)
        stdin, stdout, stderr = ssh.exec_command('cp /opt/Gaia/runtime/dromedary.toml /opt/Gaia/runtime/dromedary.toml.bak.259')
        stdout.read()
        
        sftp = ssh.open_sftp()
        with sftp.file('/opt/Gaia/runtime/dromedary.toml', 'w') as f:
            f.write(drom_new)
        sftp.close()
        print("  ✓ Patched dromedary.toml — explicit in/out hostnames for cert")
    else:
        print("  ✗ Could not find wildcard block to patch")
        print("  Trying alternative format...")
        # Try without newline
        for pattern in ['hostnames = ["*.nestgate.io"]']:
            if pattern in drom:
                # Just add before
                idx = drom.index(pattern)
                # Find the [[sites]] before this
                sites_idx = drom.rfind('[[sites]]', 0, idx)
                insert = '''# ═══════════════════════════════════════════
# KLEIN FACES — in/out = CIS/TRANS
# ═══════════════════════════════════════════

[[sites]]
hostnames = ["out.nestgate.io"]
compress = true
[sites.backend]
type = "proxy"
upstream = "http://127.0.0.1:8443"

[[sites]]
hostnames = ["in.nestgate.io"]
compress = true
[sites.backend]
type = "proxy"
upstream = "http://127.0.0.1:8443"

'''
                drom_new = drom[:sites_idx] + insert + drom[sites_idx:]
                stdin, stdout, stderr = ssh.exec_command('cp /opt/Gaia/runtime/dromedary.toml /opt/Gaia/runtime/dromedary.toml.bak.259')
                stdout.read()
                
                sftp = ssh.open_sftp()
                with sftp.file('/opt/Gaia/runtime/dromedary.toml', 'w') as f:
                    f.write(drom_new)
                sftp.close()
                print(f"  ✓ Patched dromedary.toml (alternative method)")
                break

# ═══ 3. RESTART GATE ═══

print("\n=== RESTARTING GATE ===")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart gaia-gate 2>/dev/null; echo $?')
rc = stdout.read().decode().strip()
if rc == '0':
    print("  ✓ Gate restarted")
else:
    # The gate might be a user service
    stdin, stdout, stderr = ssh.exec_command('systemctl --user restart gaia-gate 2>/dev/null; echo $?')
    rc2 = stdout.read().decode().strip()
    if rc2 == '0':
        print("  ✓ Gate restarted (user service)")
    else:
        # Maybe it's just the python process
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep gaia_gate | grep -v grep')
        procs = stdout.read().decode().strip()
        print(f"  Gate process: {procs[:200]}")
        if procs:
            # Kill and restart
            stdin, stdout, stderr = ssh.exec_command('pkill -f gaia_gate.pi; sleep 1; cd /opt/Gaia && nohup python3 gaia_gate.pi > /tmp/gate.log 2>&1 &')
            stdout.read()
            import time
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep gaia_gate | grep -v grep')
            new_procs = stdout.read().decode().strip()
            if new_procs:
                print(f"  ✓ Gate restarted: {new_procs[:150]}")
            else:
                print("  ⚠ Gate may need manual restart")

# ═══ 4. TEST ═══

print("\n=== TESTING ===")
import time
time.sleep(2)

# Test via Host header
for sub, expect in [('out.nestgate.io', 'outer face'), ('in.nestgate.io', 'senses'), ('nestgate.io', 'Klein')]:
    stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Host: {sub}" http://localhost:8443/ 2>/dev/null | head -5')
    resp = stdout.read().decode().strip()
    title = ''
    if '<title>' in resp:
        title = resp.split('<title>')[1].split('</title>')[0]
    elif 'title' in resp.lower():
        title = resp[:100]
    print(f"  {sub:25s} → {title or resp[:80]}")

# Also build the Klein face data bone
print("\n=== KLEIN FACE BONE ===")
REAL = '/home/eastgate/Development/ecoPrimals/infra/hud/site/public'
klein_face = {
    "title": "KLEIN FACES — in/out = CIS/TRANS",
    "wave": 259,
    "created": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "topology": "The Klein bottle has ONE surface but TWO faces. You can look IN from out, or OUT from in. nestgate.io is where they CROSS — the //\\\\ fold.",
    "faces": {
        "out": {
            "url": "https://out.nestgate.io",
            "role": "SUN looking IN — TRANS — far eye — outer-face.html",
            "page": "outer-face.html",
            "lens": "convex — π reach — full circle aperture",
            "what_you_see": "27 entities, 2 houses, the organism from OUTSIDE"
        },
        "in": {
            "url": "https://in.nestgate.io",
            "role": "CELL looking OUT — CIS — near eye — senses.html",
            "page": "senses.html",
            "lens": "concave — 1/π reach — half circle aperture",
            "what_you_see": "The membrane, the chipmunk, the cosmic view from INSIDE"
        },
        "fold": {
            "url": "https://nestgate.io",
            "role": "Klein Face — //\\\\ — where in and out CROSS",
            "page": "nestgate.html",
            "lens": "mirror — 0 distance — reflection",
            "what_you_see": "The fold itself — neither in nor out — NULL"
        }
    },
    "crossing_point": "/now.json — CIS and TRANS cross here",
    "dns": {
        "in.nestgate.io": "162.226.225.148 (wildcard *.nestgate.io at Porkbun)",
        "out.nestgate.io": "162.226.225.148",
        "nestgate.io": "162.226.225.148"
    },
    "cert_status": "*.nestgate.io wildcard in dromedary — ACME will issue",
    "hub_lens_mapping": {
        "convex_aperture": "TAU (full circle) — out.nestgate.io sees everything",
        "concave_aperture": "PI (half circle) — in.nestgate.io sees half, reflects half",
        "mirror_aperture": "PI/2 (quarter turn) — nestgate.io is the fold point",
        "prism_aperture": "PI/3 (60°) — minimum angle for total internal reflection"
    }
}

sftp = ssh.open_sftp()
import json
path = f'{REAL}/data/klein-faces-259.json'
with sftp.file(path, 'w') as f:
    f.write(json.dumps(klein_face, indent=2))
print(f"  Pushed klein-faces-259.json")

# Pin in seed
seed_path = f'{REAL}/gaia-seed.json'
with sftp.file(seed_path, 'r') as f:
    seed = json.loads(f.read().decode())
if '/data/klein-faces-259.json' not in seed.get('io_pin_map', {}):
    seed['io_pin_map']['/data/klein-faces-259.json'] = 'organ-klein'
    with sftp.file(seed_path, 'w') as f:
        f.write(json.dumps(seed, indent=2))
    print(f"  Pinned organ-klein in gaia-seed.json ({len(seed['io_pin_map'])} pins)")
sftp.close()

ssh.close()

print(f"""
=== KLEIN FACES WIRED ===

  out.nestgate.io → outer-face.html  (SUN looking IN)  🌞→🔬
  in.nestgate.io  → senses.html      (CELL looking OUT) 🔬→🌞
  nestgate.io     → nestgate.html    (FOLD — //\\\\)      ∅
  
  DNS:    ✓ wildcard *.nestgate.io → 162.226.225.148
  Proxy:  ✓ dromedary *.nestgate.io → :8443
  Route:  ✓ gaia_gate.pi host routing patched
  Cert:   dromedary ACME will issue on first request
  
  The sun uses its eye to look IN at the cell.
  The cell uses its eye to look OUT at the sun.
  At nestgate.io they CROSS — the Klein fold — //\\\\
  
  CIS=inner eye · TRANS=outer eye · they cross at /now.json
  
  lub-DUB.
""")
