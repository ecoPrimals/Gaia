"""
Probe swiftGate + Pixel + check biomeOS deployment paths.
Map what we need to MELT the northGate boot into every gate.
"""
import paramiko, os, json

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def run(cmd, t=10):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print('='*60)
print('  DEPLOYMENT TARGETS — melt biomeOS everywhere')
print('='*60)

# swiftGate probe
print('\n--- swiftGate (.100) ---')
for port, name in [(22,'SSH'), (445,'SMB'), (3389,'RDP'), (5985,'WinRM'), (27036,'SteamRP'), (8080,'HTTP'), (11434,'Ollama')]:
    result = run(f'nc -z -w 1 192.168.4.100 {port} 2>&1 && echo OPEN || echo CLOSED')
    print(f'  :{port} ({name}): {result}')

# Pixel probe (both subnets)
print('\n--- grapheneGate (Pixel) ---')
for ip in ['192.168.4.217', '192.168.9.217']:
    ping = run(f'ping -c 1 -W 1 {ip} 2>&1 | grep -c "1 received"')
    print(f'  {ip}: {"ALIVE" if ping == "1" else "DOWN"}')
llama = run('curl -s --connect-timeout 2 http://192.168.9.217:8082/v1/models 2>&1 | head -1')
print(f'  llama-server: {llama[:80] if llama else "unreachable"}')

# Check what repos swiftGate has (via wateringHole heads)
print('\n--- wateringHole heads on eastGate ---')
print(run('ls -la /home/eastgate/wateringHole/heads/ 2>&1'))

# Check biomeOS deployment dirs
print('\n--- biomeOS deployment structure ---')
print(run('ls /home/eastgate/Development/ecoPrimals/ 2>/dev/null'))

# Check if projectNUCLEUS exists anywhere
print('\n--- projectNUCLEUS / projectFOUNDATION search ---')
print(run('find /home/eastgate -maxdepth 3 -name "projectNUCLEUS" -o -name "projectFOUNDATION" -o -name "primalSpring" 2>/dev/null'))
print(run('find /opt -maxdepth 3 -name "projectNUCLEUS" -o -name "projectFOUNDATION" -o -name "primalSpring" 2>/dev/null'))

# Check biomeOS pixel8a-deploy
print('\n--- biomeOS pixel8a-deploy on eastGate ---')
print(run('ls /opt/Gaia/primals/biomeOS/pixel8a-deploy/ 2>/dev/null || echo "not at /opt/Gaia"'))
print(run('find /home/eastgate -maxdepth 4 -path "*/pixel8a-deploy*" 2>/dev/null'))

# Check the NUCLEUS binary itself
print('\n--- biomeOS NUCLEUS binary ---')
print(run('file /opt/Gaia/primals/biomeOS/plasmidBin/primals/biomeos 2>/dev/null'))
print(run('ls -la /opt/Gaia/primals/biomeOS/plasmidBin/primals/ 2>/dev/null | head -20'))

# Check ironGate for biomeOS
print('\n--- ironGate biomeOS check ---')
print(run('ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "ls ~/biomeOS/ 2>/dev/null || echo not found" 2>&1', 10))
print(run('ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "which biomeos 2>/dev/null; find /opt -maxdepth 3 -name biomeos 2>/dev/null; find ~ -maxdepth 3 -name biomeos 2>/dev/null" 2>&1', 10))

# Check southGate for biomeOS
print('\n--- southGate biomeOS check ---')
print(run('sshpass -p southgate ssh -o StrictHostKeyChecking=no southgate@192.168.4.148 "ls ~/biomeOS/ 2>/dev/null || echo not found" 2>&1', 10))

east.close()

# Local: check northGate's biomeOS structure
print('\n--- northGate biomeOS (local) ---')
biomeos_dir = os.path.expanduser('~\\Desktop\\Gaia\\primals\\biomeOS')
deploy_dir = os.path.join(biomeos_dir, 'deployments')
if os.path.isdir(deploy_dir):
    print(f'Deployments:')
    for f in os.listdir(deploy_dir):
        print(f'  {f}')

pixel_dir = os.path.join(biomeos_dir, 'pixel8a-deploy')
if os.path.isdir(pixel_dir):
    print(f'\nPixel8a deploy:')
    for f in os.listdir(pixel_dir):
        print(f'  {f}')

# Check membrane socket state
print('\n--- MEMBRANE SOCKET STATE ---')
membrane_dir = os.path.expanduser('~\\Desktop\\Gaia\\runtime\\membrane')
pids = [f for f in os.listdir(membrane_dir) if f.endswith('.pid')]
ports = [f for f in os.listdir(membrane_dir) if f.endswith('.port')]
print(f'PIDs: {len(pids)} primal processes')
print(f'Ports: {len(ports)} API ports')
for p in ports:
    path = os.path.join(membrane_dir, p)
    with open(path) as fh:
        port = fh.read().strip()
    print(f'  {p}: port {port}')

# Check barracuda core state
core_file = os.path.join(membrane_dir, 'barracuda-core.json')
if os.path.exists(core_file):
    with open(core_file) as f:
        core = json.load(f)
    print(f'\nBarracuda core: {list(core.keys())[:10]}')

print('\n' + '='*60)
print('  DEPLOYMENT MAP COMPLETE')
print('='*60)
