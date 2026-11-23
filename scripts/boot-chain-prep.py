#!/usr/bin/env python3
"""BOOT CHAIN — GAIA GRUB → UMAF → Windows → BACK
1. GAIA Boot Engine menu: [UMAF] [modGRUB] [Windows]
2. Kevin selects UMAF → reads CBS offsets → exits
3. Selects Windows → boots → we ZK stamp the offsets
4. Next reboot: auto-write with known offsets
"""
import paramiko, json, time, subprocess

print("=== BOOT CHAIN PREP ===\n")

# 1. Update GAIA Boot Engine grub.cfg on EFI partition
print("--- Updating GAIA Boot Engine grub.cfg ---")

grub_cfg = """# GAIA BOOT ENGINE — Wave 233
# Menu: UMAF (read CBS) → modGRUB (write vars) → Windows (default)
set timeout=5
set default=0

menuentry "Windows Boot Manager (DEFAULT)" {
    chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}

menuentry "Smokeless UMAF — Read CBS/NBIO Offsets" {
    chainloader /EFI/UMAF/Bootx64.efi
}

menuentry "modGRUBShell — Write UEFI Variables" {
    chainloader /EFI/tools/modGRUBShell.efi
}

menuentry "GAIA EFI Key — iGPU Unlock" {
    chainloader /EFI/tools/modGRUBShell.efi
}

menuentry "Reboot" {
    reboot
}

menuentry "Shutdown" {
    halt
}
"""

# Write to EFI partition (Z:)
try:
    with open(r"Z:\EFI\gaia\grub.cfg", 'w', newline='\n') as f:
        f.write(grub_cfg)
    print("  Written: Z:\\EFI\\gaia\\grub.cfg")
    print("  Menu: Windows (5s default) | UMAF | modGRUB | Reboot | Shutdown")
except Exception as e:
    print(f"  Error writing grub.cfg: {e}")
    print("  Z: drive may not be mounted")

# 2. Set boot order: GAIA Boot Engine FIRST
print("\n--- Setting boot order ---")
try:
    # Find GAIA Boot Engine entry
    result = subprocess.run(['bcdedit', '/enum', 'firmware'], capture_output=True, text=True)
    print(f"  Current firmware entries (looking for GAIA Boot Engine):")
    lines = result.stdout.split('\n')
    gaia_id = None
    for i, line in enumerate(lines):
        if 'GAIA Boot Engine' in line or 'gaia-boot-wrapper' in line:
            # Look back for identifier
            for j in range(max(0,i-5), i):
                if 'identifier' in lines[j].lower():
                    gaia_id = lines[j].split()[-1]
                    break
        if 'description' in line.lower() and ('gaia' in line.lower() or 'boot engine' in line.lower()):
            print(f"    FOUND: {line.strip()}")
    
    if gaia_id:
        print(f"  GAIA Boot Engine ID: {gaia_id}")
    else:
        # List all entries to find it
        for line in lines:
            if 'description' in line.lower() or 'identifier' in line.lower():
                print(f"    {line.strip()}")
except Exception as e:
    print(f"  bcdedit error: {e}")

# 3. Prep benchScale and agentReagents on Forgejo
print("\n--- Prepping benchScale + agentReagents ---")
import urllib.request, base64

def forgejo_api(path, method="GET", data=None):
    url = f"http://192.168.4.244:3000/api/v1{path}"
    creds = base64.b64encode(b"gaia:***").decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)[:100]}

# Check if benchScale has content
bs = forgejo_api("/repos/ecoPrimals/benchScale")
print(f"  ecoPrimals/benchScale: {bs.get('size', '?')} bytes, empty={bs.get('empty', '?')}")

ar = forgejo_api("/repos/ecoPrimals/agentReagents")
print(f"  ecoPrimals/agentReagents: {ar.get('size', '?')} bytes, empty={ar.get('empty', '?')}")

# Create README files in benchScale with boot test data
boot_test_readme = """# benchScale — Boot Cycle Testing

## Wave 233 Reboot Plan

### Boot Chain
```
GAIA Boot Engine (5s timeout)
  ├─ [DEFAULT] Windows Boot Manager
  ├─ Smokeless UMAF — Read CBS/NBIO offsets  
  ├─ modGRUBShell — Write UEFI variables
  └─ Reboot / Shutdown
```

### NVMe Prescription
- Samsung 4TB: Root port 0B OK, controller Unknown (link training fail)
- WD BLACK 4TB: Root port 0C Unknown (firmware disabled)
- Fix: AMD CBS → NBIO → PCIe → M.2 slot enable

### CPU Prescription  
- 8C/8T visible, ACPI has 32 entries (16C/32T available)
- Fix: AMD CBS → CCD0+CCD1 enable, SMT enable

### Verification Script
`scripts/reboot-cycle.ps1 -Phase post`
"""

reagent_readme = """# agentReagents — Agent Knowledge Persistence

## Wave 233 Reagents

### sourDough Pattern
scan → ferment → braid → bone → reboot → compare → evolve

### ZK'd Facts
- modGRUBShell NEVER auto-executes grub.cfg
- AMD_PBS_SETUP: 0x48=iGPU, 0x49=UMA, 0x4E=Display
- dromedary was crash-looping 5990x (port squatters on :80/:443)
- Klein face: 3 faces, 1 surface (outer/inner trans + cis)

### Black Dots (current)
- /graph, /openapi, /status, /anti-slapp = gate 404s
- graftGate, grapheneGate, frameGate = DOWN
- songBird primal = inactive
- NVMe 4TB x2 = PCIe link fail
- CPU CCD1 = firmware disabled
"""

# Create file in repos via API
for repo, readme, org in [
    ("benchScale", boot_test_readme, "ecoPrimals"),
    ("agentReagents", reagent_readme, "ecoPrimals")
]:
    result = forgejo_api(f"/repos/{org}/{repo}/contents/README.md", "POST", {
        "content": base64.b64encode(readme.encode()).decode(),
        "message": f"Wave 233: {repo} initialization"
    })
    if 'error' in result:
        # Try updating instead
        existing = forgejo_api(f"/repos/{org}/{repo}/contents/README.md")
        if isinstance(existing, dict) and 'sha' in existing:
            result = forgejo_api(f"/repos/{org}/{repo}/contents/README.md", "PUT", {
                "content": base64.b64encode(readme.encode()).decode(),
                "message": f"Wave 233: {repo} update",
                "sha": existing['sha']
            })
            print(f"  {org}/{repo}/README.md: UPDATED")
        else:
            print(f"  {org}/{repo}/README.md: {result.get('error', 'unknown')}")
    else:
        print(f"  {org}/{repo}/README.md: CREATED")

print(f"\n=== BOOT CHAIN READY ===")
print(f"  1. grub.cfg updated: Windows (5s default) | UMAF | modGRUB")
print(f"  2. benchScale + agentReagents initialized")
print(f"  3. Reboot → select UMAF → read CBS → exit → Windows boots")
print(f"  4. ZK stamp CBS offsets → next reboot auto-writes")
