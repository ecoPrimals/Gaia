# -*- coding: utf-8 -*-
"""
Prep Smokeless_UMAF USB — download and extract to FAT32 USB stick.
Phase 2 fallback: only needed if BIOS hunt (Phase 1) fails.
"""
import subprocess, os, zipfile, shutil, ctypes, string

print('='*60)
print('  SMOKELESS_UMAF USB PREP')
print('='*60)

# Step 1: Check for USB drives
print('\n--- Scanning for USB drives ---')
r = subprocess.run(['powershell', '-Command',
    'Get-Disk | Where-Object { $_.BusType -eq "USB" } | Select-Object Number, FriendlyName, @{N="SizeGB";E={[math]::Round($_.Size/1GB,1)}}, PartitionStyle | Format-Table -AutoSize'],
    capture_output=True, text=True, timeout=10)
print(r.stdout.strip() if r.stdout.strip() else '  No USB drives detected!')

# Step 2: Check for FAT32 USB volumes
r2 = subprocess.run(['powershell', '-Command',
    'Get-Volume | Where-Object { $_.DriveType -eq "Removable" -or $_.FileSystemLabel -match "USB|BOOT|EFI" } | Select-Object DriveLetter, FileSystemLabel, FileSystem, @{N="SizeGB";E={[math]::Round($_.Size/1GB,2)}}, @{N="FreeGB";E={[math]::Round($_.SizeRemaining/1GB,2)}} | Format-Table -AutoSize'],
    capture_output=True, text=True, timeout=10)
print('\n--- Removable volumes ---')
print(r2.stdout.strip() if r2.stdout.strip() else '  No removable volumes found')

# Step 3: Find all drive letters and check for removable
print('\n--- All drive letters ---')
removable = []
for letter in string.ascii_uppercase:
    drive = f'{letter}:\\'
    dtype = ctypes.windll.kernel32.GetDriveTypeW(drive)
    # 2 = REMOVABLE, 3 = FIXED, 4 = NETWORK, 5 = CDROM
    if dtype == 2:
        removable.append(letter)
        free = shutil.disk_usage(drive)
        print(f'  {drive} REMOVABLE  Total={free.total//1024//1024}MB  Free={free.free//1024//1024}MB')

if not removable:
    print('  No removable drives found. Plug in a USB stick!')
    print('  It needs to be FAT32 formatted, any size >= 64MB')

# Step 4: Download location
dl_dir = r'C:\Users\mokke\Desktop\Gaia\data\tools'
os.makedirs(dl_dir, exist_ok=True)
umaf_zip = os.path.join(dl_dir, 'UniversalAMDFormBrowser.zip')
umaf_url = 'https://github.com/DavidS95/Smokeless_UMAF/releases/latest/download/UniversalAMDFormBrowser.zip'

print(f'\n--- Download URL ---')
print(f'  {umaf_url}')
print(f'  Save to: {umaf_zip}')

# Step 5: Try to download
if not os.path.exists(umaf_zip):
    print('\n--- Downloading Smokeless_UMAF ---')
    r3 = subprocess.run(['powershell', '-Command',
        f'Invoke-WebRequest -Uri "{umaf_url}" -OutFile "{umaf_zip}" -UseBasicParsing'],
        capture_output=True, text=True, timeout=60)
    if os.path.exists(umaf_zip):
        sz = os.path.getsize(umaf_zip)
        print(f'  Downloaded! Size: {sz} bytes')
    else:
        print(f'  Download failed: {r3.stderr}')
        print('  Manual download: https://github.com/DavidS95/Smokeless_UMAF/releases')
else:
    print(f'\n  Already downloaded: {umaf_zip} ({os.path.getsize(umaf_zip)} bytes)')

# Step 6: Extract and show contents
if os.path.exists(umaf_zip):
    extract_dir = os.path.join(dl_dir, 'UMAF')
    if not os.path.exists(extract_dir):
        print('\n--- Extracting ---')
        with zipfile.ZipFile(umaf_zip, 'r') as z:
            z.extractall(extract_dir)
            print(f'  Extracted to: {extract_dir}')
    
    print('\n--- UMAF contents ---')
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            fp = os.path.join(root, f)
            print(f'  {os.path.relpath(fp, extract_dir)} ({os.path.getsize(fp)} bytes)')

    # Step 7: Instructions
    if removable:
        usb = removable[0]
        print(f'\n--- READY TO COPY to {usb}:\\ ---')
        print(f'  When ready, run:')
        print(f'    xcopy /E /Y "{extract_dir}\\*" "{usb}:\\"')
        print(f'  Then reboot, F8/F12 boot menu, select USB, UMAF launches')
    else:
        print('\n--- INSERT USB STICK ---')
        print('  Format as FAT32, then copy UMAF contents to root')

print('\n' + '='*60)
print('  Phase 1: Reboot, hunt BIOS for AMD CBS/PBS/NB Config')
print('  Phase 2: If not found, boot USB with UMAF')
print('='*60)
