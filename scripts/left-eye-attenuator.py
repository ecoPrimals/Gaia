"""LEFT EYE ATTENUATOR — Pulse the iGPU display awake after boot.
Inverse of right eye: RTX wakes naturally, iGPU needs a kick.
Runs on login, detects new display, extends desktop, wakes RustDesk."""
import subprocess, time, os, json, ctypes, sys

print("=" * 60)
print("LEFT EYE ATTENUATOR — Wake pulse for Display 2")
print("=" * 60)

def check_displays():
    """Get current display state."""
    cmd = '''
    Add-Type -AssemblyName System.Windows.Forms
    $screens = [System.Windows.Forms.Screen]::AllScreens
    foreach ($s in $screens) {
        Write-Output ("DISPLAY: " + $s.DeviceName + " Primary=" + $s.Primary + " Bounds=" + $s.Bounds.Width + "x" + $s.Bounds.Height + " Working=" + $s.WorkingArea.Width + "x" + $s.WorkingArea.Height)
    }
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
    return r.stdout.strip()

def check_monitors():
    """Get PnP monitor state."""
    cmd = 'Get-PnpDevice -Class Monitor | Select-Object FriendlyName,Status | Format-Table -AutoSize'
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=5)
    return r.stdout.strip()

def extend_display():
    """Try to extend desktop to second display."""
    # displayswitch.exe /extend is the Windows built-in
    subprocess.run(['displayswitch.exe', '/extend'], capture_output=True, timeout=5)

def wake_monitor_ddcci():
    """Send DDC/CI wake command to monitors."""
    cmd = '''
    # Try to wake all monitors via PowerShell
    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class MonitorWake {
        [DllImport("user32.dll")]
        public static extern int SendMessage(int hWnd, int Msg, int wParam, int lParam);
        
        [DllImport("user32.dll")]
        public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
        
        public const int HWND_BROADCAST = 0xffff;
        public const int SC_MONITORPOWER = 0xF170;
        public const int WM_SYSCOMMAND = 0x0112;
        public const int MONITOR_ON = -1;
        
        public static void WakeMonitors() {
            // Send monitor ON to all
            SendMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_ON);
            // Also jiggle mouse to ensure wake
            mouse_event(0x0001, 1, 1, 0, 0);
            System.Threading.Thread.Sleep(100);
            mouse_event(0x0001, -1, -1, 0, 0);
        }
    }
"@
    [MonitorWake]::WakeMonitors()
    Write-Output "Monitor wake signal sent"
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

def enable_igpu_display():
    """Try to enable the iGPU display device."""
    cmd = '''
    # Find disabled LG monitor on BasicDisplay and try to enable
    $monitors = Get-PnpDevice -Class Monitor | Where-Object { $_.Status -eq "Unknown" -and $_.FriendlyName -like "*LG*" }
    foreach ($m in $monitors) {
        Write-Output ("Found sleeping LG: " + $m.InstanceId)
        try {
            Enable-PnpDevice -InstanceId $m.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Output ("  Enabled!")
        } catch {
            Write-Output ("  Enable attempt: " + $_.Exception.Message)
        }
    }
    
    # Also try enabling the iGPU audio (proves silicon wake)
    $igpu_audio = Get-PnpDevice | Where-Object { $_.InstanceId -like "*1002*1640*" -and $_.Status -eq "Unknown" }
    foreach ($d in $igpu_audio) {
        try {
            Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Output ("  iGPU audio enabled!")
        } catch {}
    }
    '''
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

# ─── ATTENUATOR LOOP ───
print("\n[1] Pre-state...")
print(check_displays())
print(check_monitors())

print("\n[2] Pulsing wake signal...")
print(wake_monitor_ddcci())

print("\n[3] Enabling iGPU devices...")
print(enable_igpu_display())

print("\n[4] Extending desktop...")
extend_display()
time.sleep(2)

print("\n[5] Post-state...")
displays_after = check_displays()
monitors_after = check_monitors()
print(displays_after)
print(monitors_after)

# Count displays
display_count = displays_after.count("DISPLAY:")
print(f"\n  Active displays: {display_count}")

if display_count >= 2:
    print("\n  *** LEFT EYE IS OPEN! Display 2 detected! ***")
    print("  RustDesk will auto-detect the new display.")
    print("  Connect from any gate → select Display 2")
else:
    print("\n  Left eye not yet visible as active display.")
    print("  This is normal if UMA hasn't been set yet.")
    print("  After modGRUBShell sets UMA → reboot → run this again.")

# ─── SCHEDULE FOR AUTO-RUN ───
print("\n[6] Scheduling attenuator for next login...")
script_path = os.path.abspath(__file__)
# The task has no PATH to find a bare "python" (it failed with file-not-found at every logon after this
# line re-registered it), so it is registered with the interpreter that is running this script.
cmd_sched = f'schtasks /Create /TN "GaiaLeftEyeWake" /TR "\\"{sys.executable}\\" \\"{script_path}\\"" /SC ONLOGON /RL HIGHEST /F'
r_sched = subprocess.run(cmd_sched, shell=True, capture_output=True, text=True, timeout=10)
if 'SUCCESS' in r_sched.stdout.upper():
    print("  Scheduled: GaiaLeftEyeWake runs on every login")
else:
    print(f"  Schedule: {r_sched.stdout.strip() or r_sched.stderr.strip()}")

# Save state
state = {
    "attenuator": "left-eye",
    "displays_before": check_displays(),
    "displays_after": displays_after,
    "display_count": display_count,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
}
with open(r'c:\Users\mokke\Desktop\Gaia\data\uefi-sniffs\attenuator-state.json', 'w') as f:
    json.dump(state, f, indent=2)

print("\n" + "=" * 60)
print("ATTENUATOR READY — will pulse on every boot")
print("  Right eye: RTX wakes → EI322QUR (natural)")
print("  Left eye:  iGPU → LG (PULSED by attenuator)")
print("  Inverted pattern: one wakes, other is kicked")
print("=" * 60)
