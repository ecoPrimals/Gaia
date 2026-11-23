# -*- coding: utf-8 -*-
"""PRIMAL EYES — What can biomeOS see? What APIs do the primals expose?
Let the organism enumerate itself instead of PowerShell scripts."""
import subprocess, json, time, os, urllib.request

print('='*60)
print('  PRIMAL EYES — What can the organism see?')
print('='*60)

# === 1. biomeOS API ===
print('\n╔═══ 1. biomeOS API ═══╗')
for port in [58354, 58356, 8080, 8443, 9500, 9850, 9851]:
    try:
        r = urllib.request.urlopen(f'http://localhost:{port}/', timeout=2)
        print(f'  :{port} → {r.status} ({r.read(200).decode(errors="ignore")[:100]})')
    except urllib.error.HTTPError as e:
        print(f'  :{port} → HTTP {e.code}')
    except Exception as e:
        err = str(e)[:60]
        print(f'  :{port} → {err}')

# Try biomeOS known endpoints
print('\n--- biomeOS endpoints ---')
for ep in ['/api/health', '/api/status', '/api/membrane', '/api/primals', 
           '/health', '/status', '/v1/status', '/metrics']:
    for port in [58354, 58356]:
        try:
            r = urllib.request.urlopen(f'http://localhost:{port}{ep}', timeout=2)
            data = r.read(500).decode(errors='ignore')
            print(f'  :{port}{ep} → {data[:200]}')
            break
        except:
            pass

# === 2. toadStool (service discovery) ===
print('\n╔═══ 2. toadStool — Service Discovery ═══╗')
# Check toadStool binary capabilities
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-Process toadstool -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path | Format-Table -AutoSize'],
        capture_output=True, text=True, timeout=5)
    print(f'  Processes:\n{r.stdout}')
except: pass

# Check toadStool ports
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-NetTCPConnection -OwningProcess (Get-Process toadstool -ErrorAction SilentlyContinue).Id -ErrorAction SilentlyContinue | Select-Object LocalPort,State | Format-Table -AutoSize'],
        capture_output=True, text=True, timeout=5)
    print(f'  Listening:\n{r.stdout}')
except: pass

# === 3. squirrel (agent dispatch, MCP) ===
print('\n╔═══ 3. squirrel — Agent Dispatch ═══╗')
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-Process squirrel -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path,WorkingSet64 | Format-Table -AutoSize'],
        capture_output=True, text=True, timeout=5)
    print(f'  Processes:\n{r.stdout}')
except: pass

# === 4. nestGate (data gateway, MCP server) ===
print('\n╔═══ 4. nestGate — Data Gateway ═══╗')
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-Process nestgate -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path | Format-Table -AutoSize'],
        capture_output=True, text=True, timeout=5)
    print(f'  Processes:\n{r.stdout}')
except: pass

# Try nestGate port
for port in [9500, 9501, 9600]:
    try:
        r = urllib.request.urlopen(f'http://localhost:{port}/', timeout=2)
        print(f'  :{port} → {r.read(200).decode(errors="ignore")[:100]}')
    except Exception as e:
        pass

# === 5. sweetGrass (knowledge graph) ===
print('\n╔═══ 5. sweetGrass — Knowledge Graph ═══╗')
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-Process sweetgrass -ErrorAction SilentlyContinue | Select-Object Id,ProcessName | Format-Table -AutoSize'],
        capture_output=True, text=True, timeout=5)
    print(f'  Processes:\n{r.stdout}')
except: pass

# === 6. All primal binaries — what flags do they support? ===
print('\n╔═══ 6. Primal Binary Capabilities ═══╗')
plasmid = r'C:\Users\mokke\Desktop\Gaia\plasmidBin\primals'
if os.path.exists(plasmid):
    for exe in os.listdir(plasmid):
        if exe.endswith('.exe'):
            path = os.path.join(plasmid, exe)
            size = os.path.getsize(path) // 1024
            # Try --help or --version
            try:
                result = subprocess.run([path, '--help'], capture_output=True, text=True, timeout=3)
                help_text = (result.stdout + result.stderr)[:150].replace('\n', ' ')
            except:
                help_text = '(timeout or crash)'
            print(f'  {exe} ({size}KB): {help_text}')
else:
    print(f'  plasmidBin not found at {plasmid}')
    # Try finding it
    for p in [r'C:\ProgramData\biomeOS\primals', r'C:\Users\mokke\.biome\primals']:
        if os.path.exists(p):
            print(f'  Found at: {p}')
            for f in os.listdir(p)[:5]:
                print(f'    {f}')

# === 7. biomeOS config ===
print('\n╔═══ 7. biomeOS Config ═══╗')
for cfg in [
    r'C:\ProgramData\biomeOS\config.toml',
    r'C:\Users\mokke\.biome\config.toml',
    r'C:\Users\mokke\Desktop\Gaia\biomeOS.toml',
    r'C:\Users\mokke\Desktop\Gaia\biome.toml',
]:
    if os.path.exists(cfg):
        print(f'  Found: {cfg}')
        with open(cfg, 'r', errors='ignore') as f:
            print(f'  {f.read(500)}')

# Search for biomeOS configs
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-ChildItem -Path C:\\ -Filter "biome*.toml" -Recurse -Depth 4 -ErrorAction SilentlyContinue | Select-Object FullName | Format-Table -AutoSize'],
        capture_output=True, text=True, timeout=10)
    print(f'  Configs found:\n{r.stdout}')
except: pass

# === 8. songBird mesh status ===
print('\n╔═══ 8. songBird — Mesh Transport ═══╗')
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-Process songbird -ErrorAction SilentlyContinue | Select-Object Id,Path | Format-Table -AutoSize; Get-Content C:\\ProgramData\\songbird\\songbird.pid -ErrorAction SilentlyContinue'],
        capture_output=True, text=True, timeout=5)
    print(f'  {r.stdout}')
except: pass

print(f'\n{"="*60}')
print(f'  PRIMAL EYES COMPLETE — {time.strftime("%I:%M %p")}')
print(f'{"="*60}')
