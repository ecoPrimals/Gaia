"""
DETANGLE WINDOWS — Post-reboot health scan for northGate (Windows).
Finds all issues before hardware surgery.
"""
import subprocess, os, json, socket

def run(cmd, t=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return '(timeout)'
    except Exception as e:
        return f'(error: {e})'

def ps(cmd):
    """Run PowerShell command"""
    return run(f'powershell -NoProfile -Command "{cmd}"', 15)

print('='*60)
print('  DETANGLE WINDOWS — northGate post-reboot scan')
print('='*60)

# 1. System info
print('\n--- SYSTEM ---')
print(f'Hostname: {socket.gethostname()}')
print(ps('(Get-CimInstance Win32_OperatingSystem).LastBootUpTime'))
print(ps('(Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory).TotalPhysicalMemory / 1GB'))

# 2. GPU
print('\n--- GPU (RTX 5090) ---')
print(run('nvidia-smi --query-gpu=name,temperature.gpu,power.draw,power.limit,memory.used,memory.total,fan.speed,clocks.gr,clocks.mem --format=csv,noheader'))

# 3. Ollama
print('\n--- OLLAMA ---')
# Check if ollama is running
ollama_proc = ps('Get-Process ollama* -ErrorAction SilentlyContinue | Select-Object -First 1 Id,ProcessName | Format-List')
print(f'Process: {ollama_proc if ollama_proc else "NOT RUNNING"}')

# Check models directory
models_paths = [
    os.path.expanduser('~\\.ollama\\models'),
    'D:\\ollama\\models',
    'E:\\ollama\\models',
    'C:\\ollama\\models',
]
for p in models_paths:
    if os.path.isdir(p):
        print(f'Models dir FOUND: {p}')
        manifests = os.path.join(p, 'manifests')
        if os.path.isdir(manifests):
            count = sum(1 for _ in os.walk(manifests))
            print(f'  Manifests dir entries: {count}')
    else:
        print(f'Models dir missing: {p}')

# Check OLLAMA_MODELS env var
ollama_env = os.environ.get('OLLAMA_MODELS', '(not set)')
print(f'OLLAMA_MODELS env: {ollama_env}')
ollama_env_sys = ps('[System.Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "Machine")')
print(f'OLLAMA_MODELS (system): {ollama_env_sys if ollama_env_sys else "(not set)"}')
ollama_env_user = ps('[System.Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "User")')
print(f'OLLAMA_MODELS (user): {ollama_env_user if ollama_env_user else "(not set)"}')

# Ollama list
print('\n  Models:')
print(run('ollama list 2>&1'))

# 4. Network
print('\n--- NETWORK ---')
gates = {
    'eastGate': '192.168.4.244',
    'router': '192.168.4.1',
    'southGate': '192.168.4.148',
    'ironGate': '192.168.4.237',
    'sporeGate': '192.168.4.3',
    'WAN': '8.8.8.8',
}
for name, ip in gates.items():
    result = run(f'ping -n 1 -w 1000 {ip}')
    alive = 'TTL=' in result or 'time=' in result.lower()
    ms = ''
    if alive:
        for part in result.split():
            if part.lower().startswith('time'):
                ms = part
    print(f'  {name} ({ip}): {"✅ " + ms if alive else "❌ UNREACHABLE"}')

# 5. eastGate services
print('\n--- eastGate SERVICES ---')
import urllib.request
for port, svc in [(8443, 'gate'), (8080, 'data'), (3000, 'forgejo'), (11436, 'ollama')]:
    try:
        r = urllib.request.urlopen(f'http://192.168.4.244:{port}/', timeout=2)
        print(f'  :{port} ({svc}): HTTP {r.status} ✅')
    except Exception as e:
        print(f'  :{port} ({svc}): ❌ {e}')

# 6. Windows services
print('\n--- WINDOWS SERVICES ---')
services = ['OllamaDaemon', 'Ollama', 'sshd', 'RustDesk', 'Docker Desktop Service', 'Steam Client Service']
for svc in services:
    status = ps(f'(Get-Service -Name "{svc}" -ErrorAction SilentlyContinue).Status')
    print(f'  {svc}: {status if status else "NOT FOUND"}')

# 7. Startup apps
print('\n--- KEY PROCESSES ---')
procs = ['ollama', 'rustdesk', 'steam', 'barracuda', 'biomeOS', 'cursor', 'firefox', 'nginx']
for p in procs:
    found = ps(f'Get-Process -Name "*{p}*" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count')
    print(f'  {p}: {found + " running" if found and found != "0" else "not found"}')

# 8. Disk
print('\n--- DISKS ---')
disks = ps('Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | Format-Table Name,@{N="UsedGB";E={[math]::Round($_.Used/1GB,1)}},@{N="FreeGB";E={[math]::Round($_.Free/1GB,1)}},@{N="TotalGB";E={[math]::Round(($_.Used+$_.Free)/1GB,1)}} -AutoSize | Out-String')
print(disks)

# 9. Memory
print('\n--- MEMORY ---')
mem = ps('$os = Get-CimInstance Win32_OperatingSystem; $total = [math]::Round($os.TotalVisibleMemorySize/1MB,1); $free = [math]::Round($os.FreePhysicalMemory/1MB,1); $used = $total - $free; Write-Output "${used}GB used / ${total}GB total (${free}GB free)"')
print(f'  {mem}')

# 10. Gaia repos
print('\n--- GIT REPOS ---')
repos = [
    os.path.expanduser('~\\Desktop\\Gaia'),
    os.path.expanduser('~\\Desktop\\wateringHole'),
    os.path.expanduser('~\\Desktop\\KenshiReborn'),
    os.path.expanduser('~\\wateringHole'),
]
for repo in repos:
    if os.path.isdir(os.path.join(repo, '.git')):
        branch = run(f'cd /d {repo} && git branch --show-current')
        print(f'  {repo}: branch={branch} ✅')
    elif os.path.isdir(repo):
        print(f'  {repo}: exists but NOT a git repo')
    else:
        print(f'  {repo}: NOT FOUND')

# 11. Primals
print('\n--- PRIMALS ---')
primal_dir = os.path.expanduser('~\\Desktop\\Gaia\\primals\\biomeOS\\plasmidBin\\primals')
if os.path.isdir(primal_dir):
    for f in os.listdir(primal_dir):
        fp = os.path.join(primal_dir, f)
        if os.path.isfile(fp):
            sz = os.path.getsize(fp)
            print(f'  {f}: {sz/1024/1024:.1f}MB')
else:
    print(f'  Primals dir not found: {primal_dir}')

# 12. Boot errors (Windows Event Log)
print('\n--- RECENT ERRORS (Event Log) ---')
errors = ps('Get-EventLog -LogName System -EntryType Error -Newest 5 -ErrorAction SilentlyContinue | Format-Table TimeGenerated,Source,Message -Wrap -AutoSize | Out-String')
if errors:
    print(errors[:500])
else:
    print('  (no recent errors or access denied)')

print('\n' + '='*60)
print('  DETANGLE COMPLETE')
print('='*60)
