"""
EAR TRIAD — Map the inner/outer ear architecture.
iGPU = Steam Frame catcher (inner ear)
dGPU = compute (deep processing)
USB dongle = WiFi antenna for eastGate (outer ear tail)
NPU = pattern recognition (cochlea)
"""
import subprocess, os

def ps(cmd, t=15):
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                          capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except:
        return '(timeout)'

def cmd(c, t=15):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except:
        return '(timeout)'

print('='*60)
print('  EAR TRIAD — inner/outer/deep architecture')
print('='*60)

# === 1. USB WiFi Dongle — the tail ===
print('\n--- USB WIFI DONGLE ---')
usb_wifi = ps("""
Get-PnpDevice -Class Net -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Output "$($_.Status) | $($_.FriendlyName) | $($_.InstanceId)"
}
""")
print(usb_wifi)

# Get detailed dongle info
print('\n--- Dongle details ---')
dongle = ps("""
Get-NetAdapter | Where-Object {$_.InterfaceDescription -match 'Realtek 8832'} | Format-List Name,InterfaceDescription,Status,LinkSpeed,MacAddress,MediaType,DriverVersion,DriverProvider,NdisVersion
""")
print(dongle)

# USB device tree for the dongle
print('\n--- USB device path ---')
usb_detail = ps("""
Get-PnpDevice | Where-Object {$_.FriendlyName -match '8832|Valve'} | ForEach-Object {
    $props = Get-PnpDeviceProperty -InstanceId $_.InstanceId -ErrorAction SilentlyContinue
    $loc = ($props | Where-Object {$_.KeyName -eq 'DEVPKEY_Device_LocationInfo'}).Data
    $parent = ($props | Where-Object {$_.KeyName -eq 'DEVPKEY_Device_Parent'}).Data
    Write-Output "  Name: $($_.FriendlyName)"
    Write-Output "  Instance: $($_.InstanceId)"
    Write-Output "  Location: $loc"
    Write-Output "  Parent: $parent"
}
""")
print(usb_detail)

# === 2. iGPU — Steam Frame catcher ===
print('\n--- iGPU (AMD Radeon) — STEAM FRAME CATCHER ---')
igpu = ps("""
Get-CimInstance Win32_VideoController | Where-Object {$_.Name -match 'AMD|Radeon'} | Format-List Name,VideoProcessor,AdapterRAM,CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate,DriverVersion,VideoModeDescription
""")
print(igpu)

# === 3. Steam streaming — is iGPU doing the capture? ===
print('\n--- STEAM REMOTE PLAY / STREAMING ---')
steam_procs = ps("""
Get-Process -Name '*steam*' -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,WorkingSet64 | ForEach-Object {
    $ws = [math]::Round($_.WorkingSet64/1MB, 1)
    Write-Output "  PID:$($_.Id) $($_.ProcessName) ${ws}MB"
}
""")
print(steam_procs)

# Check streaming_client specifically
streaming = ps("Get-Process -Name '*streaming*' -ErrorAction SilentlyContinue | Select-Object Id,ProcessName | Format-Table -HideTableHeaders")
print(f'\n  Streaming client: {streaming if streaming.strip() else "not running"}')

# NVENC encoder sessions (RTX 5090 encoding for remote play)
print('\n--- GPU ENCODER SESSIONS ---')
nvenc = cmd('nvidia-smi --query-gpu=encoder.stats.sessionCount,encoder.stats.averageFps,encoder.stats.averageLatency --format=csv')
print(f'  {nvenc}')

# === 4. Display outputs — who renders what ===
print('\n--- DISPLAY TOPOLOGY ---')
monitors = ps("""
Get-CimInstance Win32_DesktopMonitor -ErrorAction SilentlyContinue | Select-Object Name,ScreenWidth,ScreenHeight | Format-Table -AutoSize
""")
print(monitors)

displays = ps("""
Get-CimInstance Win32_VideoController | Select-Object Name,CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate,VideoModeDescription | Format-Table -AutoSize
""")
print(displays)

# === 5. eastGate WiFi — what does it have now? ===
print('\n--- eastGate CURRENT WiFi ---')
import paramiko
east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def erun(cmd, t=10):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print(erun('ip link show 2>&1 | grep -E "^[0-9]|state"'))
print(f'\nWiFi interfaces:')
print(erun('iw dev 2>&1'))
print(f'\nUSB devices:')
print(erun('lsusb 2>&1'))
print(f'\nNetwork interfaces:')
print(erun('ip addr show 2>&1 | grep -E "^[0-9]|inet "'))

east.close()

# === 6. The architecture ===
print('''
╔══════════════════════════════════════════════════════════╗
║              EAR TRIAD ARCHITECTURE                      ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  INNER EAR (northGate local)                             ║
║  ├─ iGPU (Radeon): Steam Frame capture + display         ║
║  ├─ USB Dongle (8832CU): WiFi sensing/sniffing           ║
║  └─ → Hand dongle to eastGate = their WiFi tail          ║
║                                                          ║
║  OUTER EAR (mesh)                                        ║
║  ├─ sporeGate (.3): DNS + heart-pull (listening)         ║
║  ├─ eastGate (.244): 34 crons + AKD1000 (classifying)   ║
║  ├─ Pixel (.113): 37 sensors + WiFi RSSI triangulation  ║
║  └─ LAN 1 + LAN 2: the two cochlea                      ║
║                                                          ║
║  DEEP EAR (silicon)                                      ║
║  ├─ AKD1000 #1 (eastGate): akida-ear pipeline            ║
║  ├─ AKD1000 #2 (northGate): incoming surgery             ║
║  └─ 78 NPs × 2 = 156 neural processors listening        ║
║                                                          ║
║  The triad: SENSE (WiFi) → PROCESS (NPU) → ACT (GPU)   ║
╚══════════════════════════════════════════════════════════╝
''')

print('='*60)
print('  EAR TRIAD MAPPED')
print('='*60)
