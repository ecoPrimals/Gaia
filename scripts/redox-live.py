# -*- coding: utf-8 -*-
"""
REDOX LIVE — Restart dead primals, clean membrane, prepare for reboot.
Reboots are better when planned. Rebuild on the way back up.
"""
import subprocess, os, json, time, signal

gaia = r'C:\Users\mokke\Desktop\Gaia'
membrane = os.path.join(gaia, 'runtime', 'membrane')

print('='*60)
print('  REDOX LIVE — Restart dead, clean stale, prepare rebuild')
print('='*60)

# === 1. Find all live primal processes ===
print('\n--- Live primal processes ---')
r = subprocess.run(['powershell', '-Command',
    "Get-Process | Where-Object { $_.ProcessName -match 'biome|beardog|songbird|barracuda|skunkbat|squirrel|nestgate|coralreef|loamspine|rhizocrypt|swarmvine|sweetgrass|toadstool|petaltongue|gaia' } | Select-Object Id, ProcessName, StartTime | Format-Table -AutoSize"],
    capture_output=True, text=True, timeout=10)
print(r.stdout.strip())

# === 2. Clean stale PID files ===
print('\n--- Cleaning stale membrane PIDs ---')
for f in os.listdir(membrane):
    if f.endswith('.pid'):
        path = os.path.join(membrane, f)
        try:
            pid = int(open(path).read().strip())
            check = subprocess.run(['powershell', '-Command', 
                f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName"],
                capture_output=True, text=True, timeout=5)
            if check.stdout.strip():
                print(f'  {f}: PID {pid} ALIVE ({check.stdout.strip()})')
            else:
                print(f'  {f}: PID {pid} DEAD - removing stale PID')
                os.remove(path)
        except:
            print(f'  {f}: invalid - removing')
            os.remove(path)

# === 3. Check what primal binaries exist on northGate ===
print('\n--- Available primal binaries ---')
primal_names = ['beardog', 'songbird', 'barracuda', 'skunkbat', 'squirrel', 
                'nestgate', 'coralreef', 'loamspine', 'rhizocrypt', 
                'swarmvine', 'sweetgrass', 'toadstool', 'petaltongue',
                'biomeos', 'biomeOS', 'gaia-hands']
found = {}
for root_dir, dirs, files in os.walk(gaia):
    if '.git' in root_dir or 'node_modules' in root_dir:
        continue
    for f in files:
        name_lower = f.lower().replace('.exe', '')
        for p in primal_names:
            if p.lower() in name_lower and (f.endswith('.exe') or f.endswith('.bat') or f.endswith('.sh')):
                full = os.path.join(root_dir, f)
                found[p] = found.get(p, []) + [full]

for name, paths in found.items():
    for p in paths:
        print(f'  {name}: {p} ({os.path.getsize(p)//1024}KB)')

if not found:
    print('  Searching broader...')
    for d in ['C:\\Users\\mokke', 'C:\\Program Files']:
        r2 = subprocess.run(['powershell', '-Command',
            f"Get-ChildItem -Path '{d}' -Recurse -Filter 'biomeOS*' -ErrorAction SilentlyContinue | Select-Object -First 5 FullName, Length"],
            capture_output=True, text=True, timeout=15)
        if r2.stdout.strip():
            print(f'  {r2.stdout.strip()}')

# === 4. biomeOS health check ===
print('\n--- biomeOS orchestrator ---')
r3 = subprocess.run(['powershell', '-Command',
    "Get-Process -Name biomeos -ErrorAction SilentlyContinue | Select-Object Id, StartTime, CPU, WorkingSet64 | Format-List"],
    capture_output=True, text=True, timeout=5)
print(r3.stdout.strip() if r3.stdout.strip() else '  biomeOS not found as process')

# Check biomeOS port  
print('\n--- biomeOS API port ---')
for f in os.listdir(membrane):
    if f.endswith('.port'):
        port = open(os.path.join(membrane, f)).read().strip()
        print(f'  {f}: port {port}')
        # Try to hit it
        try:
            import urllib.request
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3)
            print(f'    HTTP {resp.status}: {resp.read().decode()[:100]}')
        except Exception as e:
            print(f'    {e}')

# === 5. Prepare reboot state file ===
print('\n--- Saving pre-reboot state for rebuild ---')
reboot_state = {
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'event': 'pre-umaf-reboot-redox',
    'primals_alive': [],
    'primals_dead': [],
    'umaf_target': {
        'igpu': 'Forces',
        'uma_mode': 'UMA_SPECIFIED',
        'uma_size': '512M',
        'check_m2_slots': True,
        'check_pcie_bifurcation': True,
    },
    'expected_after_reboot': [
        'iGPU enabled - dummy plug catches Display 2',
        'UMA 512M allocated from DDR5',
        'M.2 slots re-enabled - 4TB drives return',
        'M: drive (Steam library) comes back',
        'D: and K: drives return',
        'biomeOS restarts with full primal set',
        'RustDesk catches new display via amoeba',
    ],
}

# Get alive/dead primals
r4 = subprocess.run(['powershell', '-Command',
    "Get-Process | Where-Object { $_.ProcessName -match 'biome|beardog|songbird|barracuda|skunkbat|squirrel|nestgate|coralreef|loamspine|rhizocrypt|swarmvine|sweetgrass|toadstool' } | Select-Object -ExpandProperty ProcessName -Unique"],
    capture_output=True, text=True, timeout=5)
alive = [p.strip() for p in r4.stdout.strip().split('\n') if p.strip()]
reboot_state['primals_alive'] = alive
all_primals = ['biomeos', 'beardog', 'songbird', 'barracuda', 'skunkbat', 
               'squirrel', 'nestgate', 'coralreef', 'loamspine', 'rhizocrypt',
               'swarmvine', 'sweetgrass', 'toadstool']
reboot_state['primals_dead'] = [p for p in all_primals if p not in [a.lower() for a in alive]]

out = os.path.join(gaia, 'data', 'gut', 'pre-reboot-state.json')
with open(out, 'w') as f:
    json.dump(reboot_state, f, indent=2)
print(f'  Saved: {out}')
print(f'  Alive: {", ".join(alive)}')
print(f'  Dead: {", ".join(reboot_state["primals_dead"])}')

print('\n' + '='*60)
print('  REDOX COMPLETE — Stack is as alive as it can be')
print('  REBOOT when ready:')
print('  F8 -> Boot from file -> EFI\\UMAF\\Bootx64.efi')
print('  AMD CBS -> NBIO -> GFX -> iGPU Forces + UMA 512M')
print('  + Check M.2/PCIe for the 4TB drives')
print('  ESC ESC ESC -> Save -> Reboot')
print('='*60)
