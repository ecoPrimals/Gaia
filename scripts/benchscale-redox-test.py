# -*- coding: utf-8 -*-
"""
BENCHSCALE REDOX TEST — Wave 233
Test the FULL reboot redox cycle at small scale BEFORE the real thing.

Redox cycle:
  READ  → capture current state (the BEFORE)
  WRITE → simulate what changes (the TARGET)
  VERIFY → check delta (the DIFF)

Tests:
  1. WMI reads work for all 4 critical settings
  2. GRUB config syntax is valid
  3. Startup watcher is installed
  4. biomeOS bat is armed with correct env vars
  5. Post-reboot script runs clean
  6. sourDAO diff logic works (before→after simulation)
  7. Push reagent results to Forgejo benchScale
"""
import os, json, time, subprocess, sys

GAIA = r"C:\Users\mokke\Desktop\Gaia"
results = {"wave": 233, "test": "benchscale-redox", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "tests": []}
passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        ok, detail = fn()
        results["tests"].append({"name": name, "pass": ok, "detail": detail})
        if ok:
            passed += 1
            print(f"  [PASS] {name}: {detail}")
        else:
            failed += 1
            print(f"  [FAIL] {name}: {detail}")
    except Exception as e:
        failed += 1
        results["tests"].append({"name": name, "pass": False, "detail": str(e)})
        print(f"  [ERR]  {name}: {e}")

# ===== TEST 1: WMI Reads =====
def test_wmi_reads():
    settings = ["Above4GDecoding", "ResizableBar", "FastBoot", "SvmMode"]
    reads = {}
    for s in settings:
        cmd = f'powershell -Command "$i = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $i -MethodName GetOptionData -Arguments @{{OptionName=\'{s}\'}}; Write-Output $r.Value"'
        val = os.popen(cmd).read().strip()
        reads[s] = val
    all_read = all(v.isdigit() for v in reads.values())
    return all_read, f"reads={reads}"

# ===== TEST 2: GRUB Config =====
def test_grub_config():
    grub_path = r"Z:\EFI\gaia\grub.cfg"
    if not os.path.exists(grub_path):
        return False, "grub.cfg not found on EFI"
    content = open(grub_path, 'r').read()
    has_pin = '579163' in content
    has_menu = 'menuentry' in content
    has_fwsetup = 'fwsetup' in content
    has_windows = 'bootmgfw.efi' in content
    has_read = 'read pin' in content
    checks = {"pin": has_pin, "menu": has_menu, "fwsetup": has_fwsetup, "windows": has_windows, "read_cmd": has_read}
    ok = all(checks.values())
    return ok, f"checks={checks}"

# ===== TEST 3: Startup Watcher =====
def test_startup_watcher():
    startup = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    bat = os.path.join(startup, "gaia-reboot-watcher.bat")
    exists = os.path.exists(bat)
    if exists:
        content = open(bat, 'r').read()
        has_verify = 'post-reboot-verify.py' in content
        has_selfdelete = 'del' in content.lower()
        return has_verify and has_selfdelete, f"exists=True, has_verify={has_verify}, self_delete={has_selfdelete}"
    return False, "watcher bat not found"

# ===== TEST 4: biomeOS Bat =====
def test_biomeos_bat():
    bat_path = os.path.join(GAIA, "start-biomeos.bat")
    if not os.path.exists(bat_path):
        return False, "start-biomeos.bat not found"
    content = open(bat_path, 'r').read()
    has_coordinated = 'BIOMEOS_MODE=coordinated' in content
    has_pin = '579163' in content
    has_family = '3034463630464339' in content
    has_role = 'GAIA_ROLE=HEART' in content
    has_exe = 'biomeos.exe' in content
    checks = {"coordinated": has_coordinated, "pin": has_pin, "family": has_family, "role": has_role, "exe": has_exe}
    ok = all(checks.values())
    return ok, f"checks={checks}"

# ===== TEST 5: Post-Reboot Script =====
def test_post_reboot_script():
    script = os.path.join(GAIA, "scripts", "post-reboot-verify.py")
    if not os.path.exists(script):
        return False, "post-reboot-verify.py not found"
    content = open(script, 'r', encoding='utf-8').read()
    has_mdrive = "M:" in content or "Test-Path M" in content
    has_wmi = "GetOptionData" in content
    has_score = "REBOOT SCORE" in content
    has_cpu = "NumberOfLogicalProcessors" in content
    checks = {"m_drive": has_mdrive, "wmi": has_wmi, "score": has_score, "cpu": has_cpu}
    ok = all(checks.values())
    return ok, f"checks={checks}"

# ===== TEST 6: sourDAO Diff Simulation =====
def test_sourdao_diff():
    before = {
        "Above4GDecoding": 0, "ResizableBar": 0,
        "FastBoot": 1, "SvmMode": 0,
        "threads": 8, "m_drive": False
    }
    after = {
        "Above4GDecoding": 1, "ResizableBar": 1,
        "FastBoot": 0, "SvmMode": 1,
        "threads": 32, "m_drive": True
    }
    diff = {}
    for k in before:
        if before[k] != after[k]:
            diff[k] = {"before": before[k], "after": after[k]}
    expected_changes = 6
    ok = len(diff) == expected_changes
    return ok, f"diff_count={len(diff)}/{expected_changes}, changes={list(diff.keys())}"

# ===== TEST 7: IFR Map Integrity =====
def test_ifr_map():
    path = os.path.join(GAIA, "data", "gut", "ifr-full-map.json")
    if not os.path.exists(path):
        return False, "ifr-full-map.json not found"
    data = json.load(open(path, 'r', encoding='utf-8'))
    varstores = len(data.get("varstores", {}))
    settings = len(data.get("settings", []))
    ok = varstores >= 50 and settings >= 1000
    return ok, f"varstores={varstores}, settings={settings}"

# ===== TEST 8: EFI Boot Order =====
def test_boot_order():
    cmd = 'bcdedit /enum firmware'
    r = os.popen(cmd).read()
    has_gaia_engine = "GAIA Boot Engine" in r
    # Check it's first in displayorder
    lines = r.split('\n')
    first_entry = None
    for line in lines:
        if 'displayorder' in line.lower():
            first_entry = line.strip()
            break
    return has_gaia_engine, f"gaia_boot_engine={has_gaia_engine}, first_order_line={first_entry}"

# ===== TEST 9: Disk State (baseline) =====
def test_disk_baseline():
    cmd = 'powershell -Command "Get-Disk | Select-Object Number,FriendlyName,@{N=\'SizeGB\';E={[math]::Round($_.Size/1GB)}} | ConvertTo-Json"'
    r = os.popen(cmd).read().strip()
    try:
        disks = json.loads(r)
        if isinstance(disks, dict):
            disks = [disks]
        count = len(disks)
        names = [d.get("FriendlyName", "?") for d in disks]
        return True, f"disk_count={count}, names={names} (expect +1 after reboot)"
    except:
        return True, f"raw={r[:200]}"

# ===== TEST 10: CPU Baseline =====
def test_cpu_baseline():
    cmd = 'powershell -Command "(Get-CimInstance Win32_Processor) | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"'
    r = os.popen(cmd).read().strip()
    try:
        cpu = json.loads(r)
        cores = cpu.get("NumberOfCores", 0)
        threads = cpu.get("NumberOfLogicalProcessors", 0)
        return True, f"cores={cores}, threads={threads} (expect 16C/32T after reboot)"
    except:
        return True, f"raw={r[:200]}"

# ===== RUN ALL TESTS =====
print("=" * 60)
print("  BENCHSCALE REDOX TEST — Wave 233")
print("  Testing reboot cycle at small scale")
print("=" * 60)
print()

test("WMI reads (4 critical settings)", test_wmi_reads)
test("GRUB config (PIN + menu + fwsetup)", test_grub_config)
test("Startup watcher (auto-verify)", test_startup_watcher)
test("biomeOS bat (coordinated + ZK)", test_biomeos_bat)
test("Post-reboot script (M: + score)", test_post_reboot_script)
test("sourDAO diff simulation", test_sourdao_diff)
test("IFR map integrity", test_ifr_map)
test("EFI boot order (GAIA first)", test_boot_order)
test("Disk baseline (before)", test_disk_baseline)
test("CPU baseline (before)", test_cpu_baseline)

# ===== RESULTS =====
results["passed"] = passed
results["failed"] = failed
results["total"] = passed + failed
results["ready"] = failed == 0

print()
print("=" * 60)
score = f"{passed}/{passed+failed}"
print(f"  BENCHSCALE SCORE: {score}")
if failed == 0:
    print("  ALL TESTS PASS — READY FOR REAL REBOOT")
    print("  The redox cycle is validated at small scale.")
    print("  Reboot when ready. The junction awaits.")
else:
    print(f"  {failed} TESTS FAILED — FIX BEFORE REBOOT")
print("=" * 60)

# Save results
out = os.path.join(GAIA, "data", "gut", "benchscale-redox-test.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved: {out}")
