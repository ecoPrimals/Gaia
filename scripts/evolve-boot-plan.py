#!/usr/bin/env python3
"""EVOLVE BOOT PLAN — Download BIOS, extract IFR, build full mobo map.
Then push evolved plan to benchScale + agentReagents.
Redox = Rust as reduction-oxidation. The organism metabolizes silicon.
"""
import paramiko, json, time, base64, urllib.request

def ssh_cmd(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

def forgejo_api(path, method="GET", data=None):
    url = f"http://192.168.4.244:3000/api/v1{path}"
    creds = base64.b64encode(b"gaia:***").decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)[:100]}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

print("=== EVOLVE BOOT PLAN — REDOX CYCLE ===\n")

# 1. Download BIOS 1401 to eastGate for IFR extraction
print("--- Phase 1: Download BIOS 1401 ---")
out, err = ssh_cmd(ssh, """
mkdir -p /tmp/gaia-mobo
cd /tmp/gaia-mobo
if [ ! -f ROG-STRIX-X870E-E-GAMING-WIFI-ASUS-1401.zip ]; then
    wget -q "https://dlcdnets.asus.com/pub/ASUS/mb/BIOS/ROG-STRIX-X870E-E-GAMING-WIFI-ASUS-1401.zip" -O bios-1401.zip 2>&1 || echo "wget failed"
    ls -la bios-1401.zip 2>/dev/null
else
    echo "already downloaded"
    ls -la *.zip *.CAP 2>/dev/null
fi
""", timeout=60)
print(f"  {out}")

# Try alternate URL pattern
if "failed" in out or "404" in out:
    print("  Trying alternate download...")
    out, err = ssh_cmd(ssh, """
    cd /tmp/gaia-mobo
    # ASUS BIOS downloads use specific naming
    wget -q "https://dlcdnets.asus.com/pub/ASUS/mb/BIOS/A5557-ASUS-1401.zip" -O bios-1401.zip 2>&1
    ls -la bios-1401.zip 2>/dev/null
    """, timeout=60)
    print(f"  {out}")

# Extract
print("\n--- Phase 2: Extract BIOS ---")
out, err = ssh_cmd(ssh, """
cd /tmp/gaia-mobo
if [ -f bios-1401.zip ]; then
    unzip -o bios-1401.zip 2>&1 | head -10
    ls -la *.CAP *.cap *.ROM *.rom 2>/dev/null
fi
""")
print(f"  {out}")

# 2. Download UEFITool + IFRExtractor
print("\n--- Phase 3: Get extraction tools ---")
out, err = ssh_cmd(ssh, """
cd /tmp/gaia-mobo
# IFRExtractor-RS Linux
if [ ! -f ifrextractor ]; then
    wget -q "https://github.com/LongSoft/IFRExtractor-RS/releases/download/v1.5.1/ifrextractor_v1.5.1_Linux.zip" -O ifr.zip 2>&1
    unzip -o ifr.zip 2>&1
    chmod +x ifrextractor 2>/dev/null
fi
ls -la ifrextractor 2>/dev/null

# UEFITool NE (for extraction from CAP)
if [ ! -f UEFIExtract ]; then
    wget -q "https://github.com/LongSoft/UEFITool/releases/download/A68/UEFITool_NE_A68_linux_x86_64.zip" -O uefitool.zip 2>&1
    unzip -o uefitool.zip 2>&1
fi
ls -la UEFIExtract 2>/dev/null
""", timeout=60)
print(f"  {out}")

# 3. Extract IFR from BIOS
print("\n--- Phase 4: Extract IFR ---")
out, err = ssh_cmd(ssh, """
cd /tmp/gaia-mobo
CAP=$(ls *.CAP *.cap 2>/dev/null | head -1)
if [ -z "$CAP" ]; then
    echo "No CAP file found"
    exit 1
fi
echo "BIOS file: $CAP ($(stat -c%s $CAP 2>/dev/null) bytes)"

# UEFIExtract dumps all sections
if [ -f UEFIExtract ]; then
    ./UEFIExtract "$CAP" all 2>&1 | tail -5
    
    # Find Setup PE32 sections for IFR extraction
    find "${CAP}.dump" -name "*.sct" -o -name "*.bin" 2>/dev/null | head -20
    
    # Look for Setup/CbsSetup sections specifically
    find "${CAP}.dump" -path "*Setup*PE32*" -o -path "*CbsSetup*" -o -path "*AmdCbs*" 2>/dev/null | head -10
fi
""", timeout=120)
print(f"  {out[:500]}")

# 4. Run IFRExtractor on found sections
print("\n--- Phase 5: IFR Extraction ---")
out, err = ssh_cmd(ssh, """
cd /tmp/gaia-mobo
CAP=$(ls *.CAP *.cap 2>/dev/null | head -1)

if [ -f ifrextractor ] && [ -d "${CAP}.dump" ]; then
    # Find all PE32 sections and try IFR extraction
    count=0
    for sct in $(find "${CAP}.dump" -name "*.sct" 2>/dev/null); do
        result=$(./ifrextractor "$sct" "${sct}.ifr.txt" 2>&1)
        if [ -f "${sct}.ifr.txt" ] && [ -s "${sct}.ifr.txt" ]; then
            size=$(stat -c%s "${sct}.ifr.txt")
            if [ "$size" -gt 1000 ]; then
                count=$((count+1))
                echo "IFR $count: $sct -> ${size} bytes"
                # Check if it has AMD CBS
                if grep -q "AMD CBS\|Above 4G\|SMT Control\|CCD\|iGPU\|UMA\|Resizable" "${sct}.ifr.txt" 2>/dev/null; then
                    echo "  *** CONTAINS AMD CBS/SETUP SETTINGS! ***"
                    grep -c "VarOffset" "${sct}.ifr.txt" | xargs -I{} echo "  Total settings: {}"
                    grep "Above 4G\|SMT Control\|CCD\|iGPU\|UMA.*Frame\|Resizable.*BAR\|Fast Boot\|IOMMU\|SVM" "${sct}.ifr.txt" | head -20
                fi
            fi
        fi
    done
    echo "Total IFR sections with data: $count"
fi
""", timeout=120)
print(f"  {out[:1000]}")

# 5. Build the evolved plan
plan = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "wave": 233,
    "phase": "evolve-boot-plan",
    
    "redox_principle": {
        "oxidation": "UEFI hides settings, strips capability, sells you half a machine",
        "reduction": "IFR extraction reduces the hidden to visible, setup_var.efi writes it back",
        "rust": "setup_var.efi is Rust. Redox IS Rust. The chemical and the code.",
        "cycle": "Each reboot is a redox cycle — oxidize (read), reduce (write), verify"
    },
    
    "mobo_enumeration": {
        "target": "ASUS ROG STRIX X870E-E GAMING WIFI",
        "bios": "1401 (2025-05-06)",
        "method": "UEFITool extract → IFRExtractor-RS → full offset map",
        "goal": "Like Akida — enumerate every bell and whistle the silicon supports",
        "varstores": ["Setup", "AmdSetup", "AMD_PBS_SETUP", "CbsSetupData", "AmdCbsConfig"],
        "expected": "1000+ hidden settings, full PCIe/NVMe/CPU/GPU control"
    },
    
    "boot_evolution": {
        "manual_transmission": "Current: Kevin picks UMAF/modGRUB, manually changes settings",
        "semi_auto": "Next: setup_var.efi with known offsets, PIN 579163 authenticates",
        "pi_clutch": "Future: Gaia reads IFR map, decides what to change, writes on reboot",
        "full_auto": "Eventually: biomeOS + toadStool discover mobo capabilities, sourDough optimizes across reboot cycles"
    },

    "testing": {
        "benchScale": "Boot cycle testing, pre/post comparison, performance benchmarks",
        "agentReagents": "sourDough persistence, ZK facts, IFR offset catalog",
        "ci_cd": "Each boot cycle = CI run. Pre-reboot = commit. Post-reboot = verify. Diff = test results.",
        "bingoCube": "Coordinate across gates — northGate writes, eastGate verifies, sporeGate absorbs"
    },

    "io_trainer": {
        "pattern": "Each reboot trains the IO subsystem",
        "inputs": "UEFI settings (58 WMI + N IFR hidden)",
        "outputs": "Hardware state (cores, threads, NVMe, GPU, ReBAR)",
        "loss_function": "diff(expected, actual) → sourDough evolve",
        "epochs": "reboot cycles"
    }
}

# 6. Push to benchScale + agentReagents
print("\n--- Phase 6: Push to Forgejo ---")

# benchScale — boot cycle testing
bs_content = json.dumps(plan, indent=2)
existing = forgejo_api("/repos/ecoPrimals/benchScale/contents/data/boot-plan-wave233.json")
if isinstance(existing, dict) and 'sha' in existing:
    result = forgejo_api("/repos/ecoPrimals/benchScale/contents/data/boot-plan-wave233.json", "PUT", {
        "content": base64.b64encode(bs_content.encode()).decode(),
        "message": "wave 233: evolved boot plan — redox cycle + IFR extraction",
        "sha": existing['sha']
    })
else:
    result = forgejo_api("/repos/ecoPrimals/benchScale/contents/data/boot-plan-wave233.json", "POST", {
        "content": base64.b64encode(bs_content.encode()).decode(),
        "message": "wave 233: evolved boot plan — redox cycle + IFR extraction"
    })
print(f"  benchScale/data/boot-plan-wave233.json: {result.get('content', {}).get('name', result.get('error', 'done'))}")

# agentReagents — IFR knowledge
reagent_content = json.dumps({
    "wave": 233,
    "known_varstores": {
        "AMD_PBS_SETUP": {"guid": "A339D746-F678-49B3-9FC7-54CE0F9DF226", "size": 256, "known_offsets": {
            "0x48": "iGPU (0=Disabled, 1=Forces)",
            "0x49": "UMA Frame Buffer (0x06=512M, 0xFF=Auto)",
            "0x4E": "Primary Video (0x02=PCIe)"
        }},
        "AmdSetupRPL_0x5000": {"offsets_from_osint": {
            "0x21": "Platform First Error Handling",
            "0x22": "Core Performance Boost",
            "0x23": "Global C-state Control",
            "0x15C": "FCLK Frequency",
            "0x35": "OC Mode"
        }},
        "Setup_EC87D643": {"guid": "EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9", "note": "Standard AMI Setup GUID"}
    },
    "tools": {
        "setup_var_efi": "Z:\\EFI\\gaia\\setup_var.efi (101KB, Rust, standalone)",
        "modGRUBShell": "Z:\\EFI\\tools\\modGRUBShell.efi (5.5MB, GRUB+setup_var)",
        "smokeless_umaf": "Z:\\EFI\\UMAF\\Bootx64.efi (9KB, AMD CBS browser)",
        "asus_wmi": "ASUSManagement WMI (58/58 read, 0 write — error 14/26)"
    },
    "pin": "579163 — human ZK authentication, NOT 'normal'"
}, indent=2)

existing2 = forgejo_api("/repos/ecoPrimals/agentReagents/contents/data/uefi-reagents-wave233.json")
if isinstance(existing2, dict) and 'sha' in existing2:
    result2 = forgejo_api("/repos/ecoPrimals/agentReagents/contents/data/uefi-reagents-wave233.json", "PUT", {
        "content": base64.b64encode(reagent_content.encode()).decode(),
        "message": "wave 233: UEFI reagents — VarStore offsets + tools + ZK",
        "sha": existing2['sha']
    })
else:
    result2 = forgejo_api("/repos/ecoPrimals/agentReagents/contents/data/uefi-reagents-wave233.json", "POST", {
        "content": base64.b64encode(reagent_content.encode()).decode(),
        "message": "wave 233: UEFI reagents — VarStore offsets + tools + ZK"
    })
print(f"  agentReagents/data/uefi-reagents-wave233.json: {result2.get('content', {}).get('name', result2.get('error', 'done'))}")

ssh.close()

# Save locally
with open(r"c:\Users\mokke\Desktop\Gaia\data\gut\evolved-boot-plan.json", 'w') as f:
    json.dump(plan, f, indent=2)

print(f"\n=== BOOT PLAN EVOLVED ===")
print(f"  IFR extraction: BIOS 1401 download attempted")
print(f"  benchScale: boot-plan-wave233.json pushed")
print(f"  agentReagents: uefi-reagents-wave233.json pushed")
print(f"  Redox: Rust is the chemistry. Each reboot is an epoch.")
print(f"  Manual → Semi-auto → piClutch → Full auto")
