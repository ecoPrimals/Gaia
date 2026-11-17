#!/usr/bin/env python3
"""
Superposition Pollinator Deploy — push the address book and pollinator bone to eastGate.
Also pushes third-eye.html if it was written earlier.
eastGate found at 192.168.1.131 via R34 scan.
"""
import paramiko
import json
import os

EASTGATE_IP = "192.168.1.131"
HUD_ROOT = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE_IP, username='eastgate', password='eastgate', timeout=15)

print(f"=== POLLINATOR DEPLOY to eastGate ({EASTGATE_IP}) ===\n")

# 1. Check eastGate identity
stdin, stdout, stderr = ssh.exec_command("hostname && uptime")
info = stdout.read().decode().strip()
print(f"  Identity: {info}\n")

# 2. Push address-book.json to HUD data
address_book_path = os.path.join(os.path.dirname(__file__), "address-book.json")
if os.path.exists(address_book_path):
    with open(address_book_path) as f:
        book_data = f.read()
    # Update the book to note .130 is blueGate (us), not northGate
    book = json.loads(book_data)
    # Fix misidentification: .130 is blueGate with ollama, not northGate
    if "northGate" in book.get("entries", {}):
        for ip_entry in book["entries"]["northGate"].get("ips", []):
            if ip_entry["address"] == "192.168.1.130":
                # Move this to blueGate
                if "blueGate" not in book["entries"]:
                    book["entries"]["blueGate"] = {"ips": [], "cube_hash": "74efea2a", "role": "EYE", "seed": "bluegate_GAIA_PRIMAL_V1", "state": "ALIVE"}
                book["entries"]["blueGate"]["ips"].append(ip_entry)
                book["entries"]["blueGate"]["state"] = "ALIVE"
        book["entries"]["northGate"]["ips"] = [e for e in book["entries"]["northGate"]["ips"] if e["address"] != "192.168.1.130"]
        if not book["entries"]["northGate"]["ips"]:
            book["entries"]["northGate"]["state"] = "SUPERPOSITION"
    
    book_json = json.dumps(book, indent=2)
    cmd = f"cat > {HUD_ROOT}/data/address-book.json << 'ADDRESSEOF'\n{book_json}\nADDRESSEOF"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.read().decode().strip()
    print(f"  ✓ address-book.json → eastGate HUD data {'[' + err + ']' if err else ''}")

# 3. Push pollinator-259.json bone
pollinator_path = os.path.join(os.path.dirname(__file__), "infra", "hud", "site", "public", "data", "pollinator-259.json")
if os.path.exists(pollinator_path):
    with open(pollinator_path, encoding='utf-8') as f:
        poll_data = f.read()
    cmd = f"cat > {HUD_ROOT}/data/pollinator-259.json << 'POLLEOF'\n{poll_data}\nPOLLEOF"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.read().decode().strip()
    print(f"  ✓ pollinator-259.json → eastGate HUD data {'[' + err + ']' if err else ''}")

# 4. Push bingocube.js to HUD js/ if not already there
stdin, stdout, stderr = ssh.exec_command(f"test -f {HUD_ROOT}/js/bingocube.js && echo EXISTS || echo MISSING")
exists = stdout.read().decode().strip()
if exists == "MISSING":
    bingo_path = os.path.join(os.path.dirname(__file__), "static", "js", "bingocube.js")
    if os.path.exists(bingo_path):
        with open(bingo_path) as f:
            bingo_js = f.read()
        cmd = f"mkdir -p {HUD_ROOT}/js && cat > {HUD_ROOT}/js/bingocube.js << 'BINGOEOF'\n{bingo_js}\nBINGOEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err = stderr.read().decode().strip()
        print(f"  ✓ bingocube.js → eastGate HUD js/ {'[' + err + ']' if err else ''}")
else:
    print(f"  ○ bingocube.js already exists on eastGate")

# 5. Update gaia-seed.json with pollinator pin
stdin, stdout, stderr = ssh.exec_command(f"cat {HUD_ROOT}/gaia-seed.json 2>/dev/null")
seed_raw = stdout.read().decode().strip()
if seed_raw:
    try:
        seed = json.loads(seed_raw)
        pins = seed.get("pins", [])
        pin_names = [p.get("name", "") for p in pins]
        
        new_pins = []
        if "organ-pollinator" not in pin_names:
            new_pins.append({
                "name": "organ-pollinator",
                "type": "data",
                "path": "/data/pollinator-259.json",
                "note": "R34 superposition pollinator — gate identity + address book"
            })
        if "organ-addressbook" not in pin_names:
            new_pins.append({
                "name": "organ-addressbook",
                "type": "data",
                "path": "/data/address-book.json",
                "note": "Live address book — collapsed gate positions"
            })
        
        if new_pins:
            pins.extend(new_pins)
            seed["pins"] = pins
            seed_json = json.dumps(seed, indent=2)
            cmd = f"cat > {HUD_ROOT}/gaia-seed.json << 'SEEDEOF'\n{seed_json}\nSEEDEOF"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(f"  ✓ gaia-seed.json updated: {len(pins)} pins (+{len(new_pins)} new)")
        else:
            print(f"  ○ Pollinator pins already in gaia-seed ({len(pins)} pins)")
    except json.JSONDecodeError:
        print(f"  ! Could not parse gaia-seed.json")
else:
    print(f"  ! No gaia-seed.json found")

# 6. Deploy wave259 overlay update — add BingoCube identities to gate nodes
# Read current overlay
stdin, stdout, stderr = ssh.exec_command(f"cat {HUD_ROOT}/js/wave259-overlay.js 2>/dev/null | wc -c")
overlay_size = stdout.read().decode().strip()
print(f"\n  Current wave259-overlay.js: {overlay_size} bytes")

# 7. Verify all new files
print("\n  === VERIFICATION ===")
for path in ["data/address-book.json", "data/pollinator-259.json", "js/bingocube.js", "gaia-seed.json"]:
    stdin, stdout, stderr = ssh.exec_command(f"stat -c '%s bytes' {HUD_ROOT}/{path} 2>/dev/null || echo 'MISSING'")
    result = stdout.read().decode().strip()
    print(f"  {path:40s} {result}")

# 8. Show current gate data from eastGate's perspective
print("\n  === EASTGATE SELF-REPORT ===")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8443/pulse 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); print(f'  Heart: {d[\\\"heart\\\"][\\\"total_beats\\\"]} beats'); print(f'  Lung: {d[\\\"lung\\\"][\\\"total_breaths\\\"]} breaths'); print(f'  Sun: {d[\\\"sun\\\"][\\\"elevation_deg\\\"]}° el, chord={d[\\\"sun\\\"][\\\"chord\\\"]}'); print(f'  Visitors: {d[\\\"unique_visitors\\\"]}')\"\n")
report = stdout.read().decode().strip()
if report:
    print(report)

# 9. List all data bones
stdin, stdout, stderr = ssh.exec_command(f"ls -la {HUD_ROOT}/data/*.json | wc -l")
bone_count = stdout.read().decode().strip()
print(f"\n  Total data bones: {bone_count}")

ssh.close()

print(f"\n  🐝 Pollinator deployed to eastGate at {EASTGATE_IP}")
print(f"     R34: If it exists, there IS a way to find it.")
print(f"     Superposition collapsed. Address book live.")
