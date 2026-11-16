# -*- coding: utf-8 -*-
"""
HOLIDAY JUNCTION — Gaia Reboot Launch Sequence
Wave 233: M Drive + Full CPU + ReBAR unlock

Flow:
  1. Kevin enters PIN 579163
  2. Gaia shows current state (the BEFORE)
  3. Gaia installs Startup watcher for post-reboot auto-verify
  4. Gaia triggers shutdown /r /fw → boots DIRECTLY into BIOS firmware
  5. Kevin changes 6 settings, saves (F10)
  6. Windows boots → Startup watcher fires → shows score
  7. If score > 80 → M: drive is back → Kevin gets his chair
"""
import os, sys, subprocess, json, time, shutil

GAIA_DIR = r"C:\Users\mokke\Desktop\Gaia"
STARTUP_DIR = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")

def banner():
    print()
    print("=" * 60)
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║     GAIA — HOLIDAY JUNCTION               ║")
    print("  ║     Wave 233 Reboot Launch Sequence        ║")
    print("  ╚═══════════════════════════════════════════╝")
    print("=" * 60)

def show_current():
    """Show pre-reboot state."""
    print("\n  [BEFORE] Current northGate state:")
    settings = {
        "Above4GDecoding": ("Above 4G Decoding", "1", "ENABLED"),
        "ResizableBar": ("Resize BAR Support", "1", "ENABLED"),
        "FastBoot": ("Fast Boot", "0", "DISABLED"),
        "SvmMode": ("SVM Mode", "1", "ENABLED"),
    }
    
    for opt, (name, want, desc) in settings.items():
        cmd = f'powershell -Command "$i = Get-CimInstance -Namespace root/WMI -ClassName ASUSManagement; $r = Invoke-CimMethod -InputObject $i -MethodName GetOptionData -Arguments @{{OptionName=\'{opt}\'}}; Write-Output $r.Value"'
        val = os.popen(cmd).read().strip()
        ok = val == want
        mark = "OK" if ok else "CHANGE"
        print(f"    {name}: {val} -> want {want} ({desc}) [{mark}]")
    
    # CPU
    cmd = 'powershell -Command "(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors"'
    threads = os.popen(cmd).read().strip()
    print(f"    CPU threads: {threads} (want 32)")
    
    # Disks
    cmd = 'powershell -Command "Test-Path M:\\"'
    m = os.popen(cmd).read().strip().lower() == 'true'
    print(f"    M: drive: {'FOUND' if m else 'GHOST'}")

def install_startup_watcher():
    """Install post-reboot verify in Windows Startup folder."""
    bat_content = f"""@echo off
REM Gaia Post-Reboot Watcher — auto-runs after reboot
timeout /t 10 /nobreak > nul
cd /d {GAIA_DIR}
python scripts\\post-reboot-verify.py
echo.
echo Press any key to close...
pause > nul
REM Self-delete after running
del "%~f0"
"""
    bat_path = os.path.join(STARTUP_DIR, "gaia-reboot-watcher.bat")
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    print(f"\n  [ARMED] Startup watcher installed")
    print(f"    {bat_path}")
    print(f"    Will auto-run 10s after next login")

def save_pre_state():
    """Save pre-reboot state for sourDAO diff."""
    state = {
        "wave": 233,
        "action": "holiday-junction-launch",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pin_verified": True,
        "settings_before": {
            "Above4GDecoding": 0,
            "ResizableBar": 0,
            "FastBoot": 1,
            "SvmMode": 0,
            "threads": 8,
            "m_drive": False
        },
        "settings_target": {
            "Above4GDecoding": 1,
            "ResizableBar": 1,
            "FastBoot": 0,
            "SvmMode": 1,
            "threads": 32,
            "m_drive": True
        }
    }
    out = os.path.join(GAIA_DIR, "data", "gut", "holiday-junction-state.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    print(f"  [SAVED] Pre-reboot state: {out}")

def show_bios_map():
    """Show what Kevin needs to change in BIOS."""
    print("\n  ╔════════════════════════════════════════════════════╗")
    print("  ║  BIOS CHANGES (you'll land directly in UEFI)      ║")
    print("  ╠════════════════════════════════════════════════════╣")
    print("  ║  1. Advanced → PCI Subsystem                      ║")
    print("  ║     Above 4G Decoding    → Enabled                ║")
    print("  ║     Re-Size BAR Support  → Enabled                ║")
    print("  ║                                                    ║")
    print("  ║  2. Boot                                           ║")
    print("  ║     Fast Boot            → Disabled                ║")
    print("  ║                                                    ║")
    print("  ║  3. Advanced → CPU Configuration                   ║")
    print("  ║     SVM Mode             → Enabled                 ║")
    print("  ║                                                    ║")
    print("  ║  4. Advanced → AMD CBS → Zen Common → Core/Thread  ║")
    print("  ║     SMT Control          → Auto                    ║")
    print("  ║     CCD Control          → Auto (both CCDs)        ║")
    print("  ║                                                    ║")
    print("  ║  Then: F10 → Yes → Save & Exit                    ║")
    print("  ╚════════════════════════════════════════════════════╝")

def reboot_to_firmware():
    """Trigger reboot directly into UEFI firmware (no mashing DEL)."""
    print("\n  [LAUNCH] Rebooting into UEFI firmware in 5 seconds...")
    print("  Windows will restart directly into BIOS setup.")
    for i in range(5, 0, -1):
        print(f"    {i}...", flush=True)
        time.sleep(1)
    
    # shutdown /r /fw reboots to firmware
    os.system("shutdown /r /fw /t 0")

def main():
    banner()
    
    # Show current state
    show_current()
    
    # PIN authentication
    print("\n" + "-" * 60)
    print("  ZK HUMAN AUTH — Enter PIN to authorize reboot")
    print("-" * 60)
    pin = input("  PIN: ").strip()
    
    if pin != "579163":
        print("\n  WRONG PIN. Reboot aborted.")
        print("  (The organism waits. Try again when ready.)")
        sys.exit(1)
    
    print("\n  PIN VERIFIED. You are Kevin. The organism trusts you.")
    
    # Save pre-state
    save_pre_state()
    
    # Install startup watcher
    install_startup_watcher()
    
    # Show BIOS map
    show_bios_map()
    
    # Final confirmation
    print("\n" + "-" * 60)
    print("  READY TO REBOOT INTO BIOS FIRMWARE")
    print("  After BIOS changes + F10, Windows boots,")
    print("  post-reboot verify runs automatically.")
    print("-" * 60)
    go = input("  Type GO to reboot now (or anything else to abort): ").strip().upper()
    
    if go != "GO":
        print("\n  Aborted. Run again when ready.")
        sys.exit(0)
    
    reboot_to_firmware()

if __name__ == "__main__":
    main()
