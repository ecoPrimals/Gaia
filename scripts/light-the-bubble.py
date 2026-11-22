"""LIGHT THE BUBBLE — Install IDD virtual display, extend desktop, fire up the left eye prototype."""
import subprocess, os, time, socket

print("=" * 60)
print("LIGHT THE BUBBLE — Virtual left eye on right eye")
print("=" * 60)

# ─── 1: Install IDD virtual display driver ───
print("\n[1] Installing RustDesk IDD virtual display driver...")

idd_path = r"C:\Program Files\RustDesk\usbmmidd_v2"
idd_inf = os.path.join(idd_path, "usbmmIdd.inf")

if os.path.exists(idd_inf):
    print(f"  Driver found: {idd_inf}")
    
    # Install using pnputil
    r = subprocess.run(['pnputil', '/add-driver', idd_inf, '/install'],
                      capture_output=True, text=True, timeout=30)
    print(f"  pnputil: {r.stdout.strip()}")
    if r.stderr.strip():
        print(f"  stderr: {r.stderr.strip()}")
    
    # Also try devcon-style install via PowerShell
    if 'failed' in r.stdout.lower() or r.returncode != 0:
        print("  Trying alternate install method...")
        cmd_alt = f'''
        $inf = "{idd_inf}"
        $setupapi = Add-Type -Name SetupAPI -PassThru -MemberDefinition @"
            [DllImport("newdev.dll", SetLastError = true)]
            public static extern bool DiInstallDriver(
                IntPtr hwndParent,
                [MarshalAs(UnmanagedType.LPWStr)] string DriverPackageInfPath,
                uint Flags,
                out bool NeedReboot);
"@
        $needReboot = $false
        $result = [SetupAPI]::DiInstallDriver([IntPtr]::Zero, $inf, 0x04, [ref]$needReboot)
        Write-Output "DiInstallDriver: Result=$result NeedReboot=$needReboot LastError=$([System.Runtime.InteropServices.Marshal]::GetLastWin32Error())"
        '''
        r2 = subprocess.run(['powershell', '-Command', cmd_alt], capture_output=True, text=True, timeout=30)
        print(f"  {r2.stdout.strip()}")
else:
    print(f"  IDD driver NOT found at {idd_inf}")
    # Try the dylib approach instead
    print("  Trying RustDesk dylib_virtual_display...")

# ─── 2: Check if virtual display appeared ───
print("\n[2] Checking displays after driver install...")
time.sleep(3)

cmd_displays = '''
Add-Type -AssemblyName System.Windows.Forms
$screens = [System.Windows.Forms.Screen]::AllScreens
foreach ($s in $screens) {
    Write-Output ("SCREEN: " + $s.DeviceName + " Primary=" + $s.Primary + " " + $s.Bounds.Width + "x" + $s.Bounds.Height)
}
Write-Output ""
Get-PnpDevice -Class Display | Format-Table FriendlyName,Status -AutoSize
Write-Output ""
Get-PnpDevice -Class Monitor | Format-Table FriendlyName,Status -AutoSize
'''
r3 = subprocess.run(['powershell', '-Command', cmd_displays], capture_output=True, text=True, timeout=10)
print(r3.stdout.strip())

# ─── 3: If no virtual display, try RustDesk's built-in virtual display ───
screen_count = r3.stdout.count("SCREEN:")
print(f"\n  Active screens: {screen_count}")

if screen_count < 2:
    print("\n[3] Activating RustDesk virtual display via config...")
    
    # RustDesk 1.5+ supports virtual display via settings
    config_path = os.path.expanduser(r"~\AppData\Roaming\RustDesk\config\RustDesk2.toml")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = f.read()
        
        # Add virtual display settings if not present
        if 'allow-virtual-display' not in config:
            # Find [options] section and add setting
            if '[options]' in config:
                config = config.replace('[options]', "[options]\nallow-virtual-display = 'Y'")
            else:
                config += "\n[options]\nallow-virtual-display = 'Y'\n"
            
            with open(config_path, 'w') as f:
                f.write(config)
            print("  Added allow-virtual-display = Y")
            
            # Restart RustDesk to pick up config
            print("  Restarting RustDesk...")
            subprocess.run(['powershell', '-Command', 'Stop-Process -Name rustdesk -Force -ErrorAction SilentlyContinue'], 
                         capture_output=True, timeout=5)
            time.sleep(2)
            
            # Start RustDesk
            rd_exe = r"C:\Program Files\RustDesk\rustdesk.exe"
            if os.path.exists(rd_exe):
                subprocess.Popen([rd_exe], creationflags=0x00000008)  # DETACHED_PROCESS
                print("  RustDesk restarted")
                time.sleep(3)
    
    # Also try the devcon approach to add virtual display
    print("\n  Trying devcon-style virtual display creation...")
    cmd_vdisp = '''
    # Check if IDD device exists
    $idd = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*USB Mobile Monitor*" -or $_.FriendlyName -like "*IDD*" -or $_.FriendlyName -like "*Virtual*Display*" }
    if ($idd) {
        Write-Output ("Found IDD: " + $idd.FriendlyName + " Status=" + $idd.Status)
        if ($idd.Status -ne "OK") {
            Enable-PnpDevice -InstanceId $idd.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
            Write-Output "Enabled!"
        }
    } else {
        Write-Output "No IDD virtual display device found"
        
        # List ALL display adapters to see what we have
        Write-Output "`nAll display-related devices:"
        Get-PnpDevice | Where-Object { $_.Class -eq "Display" -or $_.Class -eq "Monitor" -or $_.FriendlyName -like "*display*" } | Format-Table FriendlyName,Status,Class -AutoSize
    }
    '''
    r4 = subprocess.run(['powershell', '-Command', cmd_vdisp], capture_output=True, text=True, timeout=10)
    print(r4.stdout.strip())

# ─── 4: Extend desktop ───
print("\n[4] Extending desktop...")
subprocess.run(['displayswitch.exe', '/extend'], capture_output=True, timeout=5)
time.sleep(2)

# Recheck
r5 = subprocess.run(['powershell', '-Command', 
    'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::AllScreens | ForEach-Object { Write-Output ($_.DeviceName + " " + $_.Bounds.Width + "x" + $_.Bounds.Height + " Primary=" + $_.Primary) }'],
    capture_output=True, text=True, timeout=5)
print(r5.stdout.strip())
final_count = r5.stdout.strip().count("\\")

# ─── 5: RustDesk status ───  
print(f"\n[5] RustDesk amoeba check...")
for port in [21118, 21116]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    ok = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    print(f"  :{port} {'OPEN' if ok else 'closed'}")

# ─── 6: Steam Deck connection ───
print(f"\n[6] Steam Deck (right eye → bubble)...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.5)
deck_ok = s.connect_ex(("192.168.4.176", 27036)) == 0
s.close()
print(f"  deckGate:27036 {'OPEN — can stream!' if deck_ok else 'closed'}")

# ─── Summary ───
print("\n" + "=" * 60)
print("BUBBLE STATUS")
print("=" * 60)
