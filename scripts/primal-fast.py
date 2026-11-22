# -*- coding: utf-8 -*-
"""PRIMAL EYES FAST — What can biomeOS see? Skip the hanging binary probes."""
import subprocess, json, time, os, urllib.request

print('='*60)
print('  PRIMAL EYES — Fast scan')
print('='*60)

# 1. biomeOS API endpoints
print('\n--- biomeOS API scan ---')
for port in [58354, 58356]:
    for ep in ['/', '/api/health', '/health', '/status', '/api/status', '/api/membrane']:
        try:
            r = urllib.request.urlopen(f'http://localhost:{port}{ep}', timeout=2)
            data = r.read(300).decode(errors='ignore')
            print(f'  :{port}{ep} → {data[:200]}')
        except urllib.error.HTTPError as e:
            body = e.read(200).decode(errors='ignore') if e.readable() else ''
            if body:
                print(f'  :{port}{ep} → HTTP {e.code}: {body[:100]}')
        except:
            pass

# 2. All primal processes with their ports
print('\n--- All primal processes ---')
r = subprocess.run(['powershell', '-Command',
    '''$primals = Get-Process | Where-Object { $_.ProcessName -match 'biomeos|songbird|squirrel|beardog|nestgate|sweetgrass|barracuda|coralreef|loamspine|skunkbat|sourdough|swarmvine|bingocube|toadstool|rhizocrypt|petaltongue|dromedary' }
    $primals | Group-Object ProcessName | ForEach-Object { Write-Host ("  " + $_.Name + ": " + $_.Count + " instances, PIDs: " + ($_.Group.Id -join ",")) }
    Write-Host ("`n  Total: " + $primals.Count + " primal processes")'''],
    capture_output=True, text=True, timeout=10)
print(r.stdout)

# 3. All listening TCP ports from primals
print('\n--- Primal listening ports ---')
r = subprocess.run(['powershell', '-Command',
    '''Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
        $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        if ($proc.ProcessName -match 'biomeos|songbird|squirrel|beardog|nestgate|sweetgrass|barracuda|coralreef|loamspine|skunkbat|sourdough|swarmvine|bingocube|toadstool|rhizocrypt|petaltongue') {
            Write-Host ("  :" + $_.LocalPort + " ← " + $proc.ProcessName + " (PID " + $_.OwningProcess + ")")
        }
    }'''],
    capture_output=True, text=True, timeout=10)
print(r.stdout)

# 4. biomeOS binary location and config
print('\n--- biomeOS binary + config ---')
r = subprocess.run(['powershell', '-Command',
    '''$bio = Get-Process biomeos -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($bio) { Write-Host ("  Path: " + $bio.Path) }
    # Find configs
    @("C:\\ProgramData\\biomeOS", "C:\\ProgramData\\songbird", "C:\\Users\\mokke\\.biome") | ForEach-Object {
        if (Test-Path $_) {
            Write-Host ("  Config dir: " + $_)
            Get-ChildItem $_ -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("    " + $_.Name + " (" + $_.Length + " bytes)") }
        }
    }'''],
    capture_output=True, text=True, timeout=10)
print(r.stdout)

# 5. plasmidBin inventory (just list, don't run)
print('\n--- plasmidBin inventory ---')
for p in [r'C:\Users\mokke\Desktop\Gaia\plasmidBin\primals',
          r'C:\ProgramData\biomeOS\primals',
          r'C:\Users\mokke\.biome\primals']:
    if os.path.exists(p):
        print(f'  Found: {p}')
        for f in sorted(os.listdir(p)):
            size = os.path.getsize(os.path.join(p, f)) // 1024
            print(f'    {f}: {size}KB')

# 6. songBird mesh
print('\n--- songBird mesh ---')
r = subprocess.run(['powershell', '-Command',
    '''$sb = Get-Process songbird -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($sb) { Write-Host ("  PID: " + $sb.Id + " Path: " + $sb.Path) }
    $pid_file = "C:\\ProgramData\\songbird\\songbird.pid"
    if (Test-Path $pid_file) { Write-Host ("  PID file: " + (Get-Content $pid_file)) }'''],
    capture_output=True, text=True, timeout=5)
print(r.stdout)

# 7. UMAF research — what the menu looks like for X870E
print('\n--- UMAF NAVIGATION for X870E + 9950X3D ---')
print('''
  KNOWN UMAF PATH (from OSINT):
  
  Device Manager
  └─ AMD CBS
     ├─ CPU Common Options
     │  └─ (CPU settings, CCD config, 3D V-Cache)
     ├─ DF Common Options  
     │  └─ (Data Fabric, memory interleaving)
     ├─ NBIO Common Options
     │  ├─ GFX Configuration        ← iGPU IS HERE
     │  │  ├─ iGPU Configuration    → "Auto" / "Disabled" / "Forces"
     │  │  ├─ UMA Mode              → "Auto" / "UMA_SPECIFIED" / "UMA_GAME_OPTIMIZED"  
     │  │  ├─ UMA Frame Buffer Size → 64M / 128M / 256M / 512M / 1G / 2G
     │  │  └─ Primary Video         → "PCIE" / "IGFX"
     │  ├─ PCIe Configuration       ← M.2 SLOTS HERE
     │  │  ├─ PCIe Slot Settings
     │  │  ├─ PCIe Link Speed
     │  │  └─ Bifurcation           ← KEY for missing drives!
     │  └─ NB Configuration
     └─ FCH Common Options
        └─ (USB, SATA, etc.)
  
  FOR iGPU:   NBIO → GFX Config → iGPU = "Forces"
  FOR DRIVES: NBIO → PCIe Config → check slot enable/bifurcation
''')

print(f'\n{"="*60}')
print(f'  DONE — {time.strftime("%I:%M %p")}')
print(f'{"="*60}')
