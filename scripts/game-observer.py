"""
GAME OBSERVER — Watch whatever Kevin plays, learn from it.
The ORC eats ALL engines, not just Ogre.
STALKER 2 = Unreal Engine 5. Study it.
"""
import subprocess, json, time, os

def get_gpu_stats():
    """Read GPU state while game runs"""
    try:
        r = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,temperature.gpu,power.draw,utilization.gpu,utilization.memory,memory.used,memory.total,clocks.gr,clocks.mem',
             '--format=csv,noheader'],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip()
    except:
        return 'nvidia-smi failed'

def get_game_process():
    """Find what game is running"""
    try:
        r = subprocess.run(
            ['powershell', '-Command',
             'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | '
             'Select-Object ProcessName, Id, WorkingSet64, CPU, MainWindowTitle | '
             'Format-Table -AutoSize | Out-String -Width 200'],
            capture_output=True, text=True, timeout=10
        )
        lines = r.stdout.strip().split('\n')
        games = [l for l in lines if any(g in l.lower() for g in 
                 ['stalker', 'kenshi', 'steam', 'unreal', 'game', 'ue5'])]
        return lines[:5], games  # header + game lines
    except:
        return [], []

def get_dx_info():
    """Check what rendering API the game uses"""
    try:
        r = subprocess.run(
            ['powershell', '-Command',
             'Get-Process | Where-Object {$_.ProcessName -match "Stalker|S2-Win64"} | '
             'Select-Object ProcessName, Id, @{N="MB";E={[math]::Round($_.WorkingSet64/1MB)}}, '
             '@{N="CPU_s";E={[math]::Round($_.CPU,1)}}, MainWindowTitle | Format-List | Out-String'],
            capture_output=True, text=True, timeout=10
        )
        return r.stdout.strip()
    except:
        return 'no game process found'

print('='*60)
print('  GAME OBSERVER — Learning from Kevin\'s play')
print('  Whatever game runs, we study the engine.')
print('='*60)

# Snapshot
print('\n--- GPU State ---')
print(get_gpu_stats())

print('\n--- Running Windows ---')
headers, games = get_game_process()
for h in headers:
    print(f'  {h}')
if games:
    print('\n  🎮 GAME DETECTED:')
    for g in games:
        print(f'    {g}')

print('\n--- Game Process Detail ---')
print(get_dx_info())

# Check STALKER 2 install
stalker_paths = [
    r'M:\SteamLibrary\steamapps\common\S.T.A.L.K.E.R. 2 Heart of Chornobyl',
    r'C:\Program Files (x86)\Steam\steamapps\common\S.T.A.L.K.E.R. 2 Heart of Chornobyl',
    r'D:\SteamLibrary\steamapps\common\S.T.A.L.K.E.R. 2 Heart of Chornobyl',
]
for p in stalker_paths:
    if os.path.exists(p):
        print(f'\n--- STALKER 2 Install: {p} ---')
        # Check engine files
        for f in os.listdir(p)[:20]:
            size = os.path.getsize(os.path.join(p, f)) if os.path.isfile(os.path.join(p, f)) else 0
            print(f'  {f} ({size//1024}KB)' if size else f'  {f}/')
        # Check Engine dir
        eng = os.path.join(p, 'Engine')
        if os.path.exists(eng):
            print(f'\n  Engine/:')
            for f in os.listdir(eng)[:15]:
                print(f'    {f}')
        # Check Binaries
        bbin = os.path.join(p, 'Stalker2', 'Binaries', 'Win64')
        if os.path.exists(bbin):
            print(f'\n  Binaries/Win64/:')
            for f in sorted(os.listdir(bbin))[:20]:
                fp = os.path.join(bbin, f)
                sz = os.path.getsize(fp) if os.path.isfile(fp) else 0
                print(f'    {f} ({sz//1024//1024}MB)' if sz > 1024*1024 else f'    {f}')
        break

# Summary
print('\n--- ENGINE STUDY NOTES ---')
print('STALKER 2: Heart of Chornobyl')
print('  Engine: Unreal Engine 5.1+')
print('  Renderer: DX12 (required), ray tracing optional')  
print('  AI: A-Life 2.0 (autonomous NPC simulation)')
print('  World: Open zone, dynamic weather, day/night')
print('  Audio: Wwise middleware')
print('  Physics: Chaos (UE5 native)')
print()
print('ORC LESSONS from UE5:')
print('  - Nanite (virtualized geometry) → our mesh LOD system')
print('  - Lumen (global illumination) → our lighting pipeline')
print('  - World Partition → our chunk streaming')
print('  - A-Life 2.0 → our creature AI (Kenshi already has squads!)')
print('  - Chaos physics → our physics layer')
print()
print('The ORC eats ALL engines. Play anything. We learn everything.')
