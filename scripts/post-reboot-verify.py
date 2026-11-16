# -*- coding: utf-8 -*-
"""POST-REBOOT VERIFY — Wave 233 M Drive Solve
Checks: M drive visibility, Above4G, ReBAR, FastBoot, disks, GPUs, biomeOS mode."""
import subprocess, os, json, sys

def wmi_read(option):
    """Read ASUS WMI BIOS setting."""
    cmd = f'powershell -Command "$inst = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $inst -MethodName GetOptionData -Arguments @{{OptionName=\'{option}\'}}; Write-Output $r.Value"'
    return os.popen(cmd).read().strip()

def run_ps(cmd):
    """Run PowerShell command, return output."""
    return os.popen(f'powershell -Command "{cmd}"').read().strip()

print("=" * 60)
print("  GAIA POST-REBOOT VERIFY — Wave 233")
print("  Target: M Drive + Above4G + ReBAR + Full CPU")
print("=" * 60)

# ===== 1. THE BIG ONE — Is M: drive visible? =====
print("\n[1] DISK ENUMERATION")
disks = run_ps("Get-Disk | Format-Table Number,FriendlyName,Size,PartitionStyle -AutoSize")
print(f"  Disks:\n{disks}")

volumes = run_ps("Get-Volume | Where-Object {$_.DriveLetter} | Format-Table DriveLetter,FileSystemLabel,Size,FileSystem -AutoSize")
print(f"\n  Volumes:\n{volumes}")

m_drive = run_ps("Test-Path M:\\")
m_found = m_drive.lower() == 'true'
print(f"\n  >>> M: DRIVE: {'FOUND!' if m_found else 'NOT FOUND'} <<<")

# ===== 2. CRITICAL BIOS SETTINGS =====
print("\n[2] BIOS SETTINGS (ASUS WMI)")
checks = {
    'Above4GDecoding': ('Above 4G Decoding', '1', 'ENABLED'),
    'ResizableBar': ('Resize BAR Support', '1', 'ENABLED'),
    'FastBoot': ('Fast Boot', '0', 'DISABLED'),
    'SvmMode': ('SVM Mode', '1', 'ENABLED'),
}

settings_ok = 0
for opt, (name, want, desc) in checks.items():
    val = wmi_read(opt)
    ok = val == want
    if ok:
        settings_ok += 1
    status = f"{'OK' if ok else 'WRONG'}"
    print(f"  {name}: {val} — want {want} ({desc}) [{status}]")

# ===== 3. CPU =====
print("\n[3] CPU")
cpu_name = run_ps("(Get-CimInstance Win32_Processor).Name")
cores = run_ps("(Get-CimInstance Win32_Processor).NumberOfCores")
threads = run_ps("(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors")
print(f"  {cpu_name}")
print(f"  Cores: {cores}, Threads: {threads}")
smt_ok = int(threads or 0) > int(cores or 1)
print(f"  SMT: {'ENABLED' if smt_ok else 'DISABLED or single-thread'}")

# ===== 4. GPU =====
print("\n[4] GPU")
gpus = run_ps("Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize")
print(f"  {gpus}")

# Check ReBAR via nvidia-smi
rebar = run_ps("nvidia-smi --query-gpu=bar1.total --format=csv,noheader 2>$null")
if rebar:
    print(f"  BAR1 size: {rebar}")
    rebar_on = False
    try:
        mb = int(rebar.replace(' MiB', '').replace(' GiB', '').strip())
        rebar_on = mb > 256
    except:
        pass
    print(f"  ReBAR: {'LIKELY ENABLED (BAR1 > 256MB)' if rebar_on else 'May be disabled'}")

# ===== 5. NVMe devices =====
print("\n[5] NVMe ENUMERATION")
nvme = run_ps("Get-PnpDevice | Where-Object {$_.FriendlyName -like '*NVMe*'} | Format-Table FriendlyName,Status -AutoSize")
print(f"  {nvme}")

# ===== 6. biomeOS mode =====
print("\n[6] biomeOS STATE")
mode = os.environ.get('BIOMEOS_MODE', 'NOT SET')
print(f"  BIOMEOS_MODE env: {mode}")
port_file = r'C:\Users\mokke\Desktop\Gaia\runtime\membrane\biomeos-api-gaia-pi.port'
if os.path.exists(port_file):
    port = open(port_file).read().strip()
    print(f"  biomeOS API port: {port}")
else:
    print("  biomeOS API port file: not found (biomeOS not running yet)")

# ===== SUMMARY =====
print("\n" + "=" * 60)
score = 0
results = []
if m_found:
    score += 40
    results.append("M: DRIVE VISIBLE (40pt)")
else:
    results.append("M: DRIVE MISSING (0pt)")

score += settings_ok * 10
results.append(f"BIOS settings: {settings_ok}/4 correct ({settings_ok*10}pt)")

if smt_ok:
    score += 10
    results.append("SMT ENABLED (10pt)")

print(f"  REBOOT SCORE: {score}/90")
for r in results:
    print(f"  - {r}")

if score >= 80:
    print("\n  REBOOT SUCCESS. northGate fully unlocked.")
    print("  Kevin — go get your chair. Steam awaits.")
elif score >= 50:
    print("\n  PARTIAL SUCCESS. M drive or some settings still need work.")
else:
    print("\n  SETTINGS NOT YET APPLIED. BIOS changes needed.")
print("=" * 60)
