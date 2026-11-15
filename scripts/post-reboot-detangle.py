"""
POST-REBOOT DETANGLE — Find all startup issues on northGate before hardware surgery.
Check services, GPU, ollama, network, crons, processes, errors.
Build a health baseline so we know what "good" looks like.
"""
import subprocess, json, os, time

def run(cmd, t=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return '(timeout)'
    except Exception as e:
        return f'(error: {e})'

print('='*60)
print('  POST-REBOOT DETANGLE — northGate health scan')
print('='*60)

# 1. Uptime + boot time
print('\n--- UPTIME ---')
print(run('uptime'))

# 2. GPU status
print('\n--- GPU (RTX 5090) ---')
gpu = run('nvidia-smi --query-gpu=name,temperature.gpu,power.draw,memory.used,memory.total,driver_version --format=csv,noheader 2>&1')
print(gpu)
gpu_procs = run('nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv,noheader 2>&1')
if gpu_procs and 'No running' not in gpu_procs:
    print(f'GPU processes: {gpu_procs}')
else:
    print('GPU processes: (none)')

# 3. Ollama
print('\n--- OLLAMA ---')
ollama_status = run('systemctl is-active ollama 2>/dev/null || echo "not systemd"')
print(f'Service: {ollama_status}')
ollama_list = run('ollama list 2>&1 | head -5')
print(ollama_list)
model_count = run('ollama list 2>&1 | tail -n +2 | wc -l')
print(f'Total models: {model_count}')

# 4. Key services
print('\n--- SERVICES ---')
services = ['ollama', 'rustdesk', 'sshd', 'docker', 'NetworkManager']
for svc in services:
    status = run(f'systemctl is-active {svc} 2>/dev/null')
    enabled = run(f'systemctl is-enabled {svc} 2>/dev/null')
    print(f'  {svc}: {status} (enabled: {enabled})')

# 5. Failed systemd units
print('\n--- FAILED UNITS ---')
failed = run('systemctl --failed --no-pager 2>&1')
print(failed)

# 6. Network — can we reach all gates?
print('\n--- NETWORK REACH ---')
gates = {
    'eastGate': '192.168.4.244',
    'router': '192.168.4.1',
    'southGate': '192.168.4.148',
    'ironGate': '192.168.4.237',
    'sporeGate': '192.168.4.3',
    'WAN (google)': '8.8.8.8',
}
for name, ip in gates.items():
    ping = run(f'ping -c 1 -W 1 {ip} 2>&1 | grep -oP "time=\\S+"')
    print(f'  {name} ({ip}): {ping if ping else "UNREACHABLE"}')

# 7. eastGate services reachable?
print('\n--- eastGate SERVICES ---')
for port, svc in [(8443, 'gate'), (8080, 'data'), (3000, 'forgejo'), (11436, 'ollama')]:
    code = run(f'curl -s -o /dev/null -w "%{{http_code}}" --connect-timeout 2 http://192.168.4.244:{port}/ 2>&1')
    print(f'  :{port} ({svc}): HTTP {code}')

# 8. Disk
print('\n--- DISK ---')
print(run('df -h / /home 2>&1 | grep -v Filesystem'))

# 9. Memory
print('\n--- MEMORY ---')
print(run('free -h | head -2'))

# 10. Recent boot errors
print('\n--- BOOT ERRORS (last 50 lines of journalctl priority err+) ---')
errors = run('journalctl -b -p err --no-pager -n 20 2>&1')
print(errors)

# 11. Crontab
print('\n--- CRONTAB ---')
cron = run('crontab -l 2>&1 | grep -v "^#" | grep -v "^$" | wc -l')
print(f'Active cron jobs: {cron}')

# 12. Git repos status
print('\n--- GIT REPOS ---')
for repo in ['/opt/Gaia', os.path.expanduser('~/wateringHole'), os.path.expanduser('~/KenshiReborn')]:
    if os.path.isdir(repo):
        branch = run(f'cd {repo} && git branch --show-current 2>&1')
        status = run(f'cd {repo} && git status --short 2>&1 | wc -l')
        print(f'  {repo}: branch={branch}, dirty={status} files')
    else:
        print(f'  {repo}: NOT FOUND')

# 13. Processes eating resources
print('\n--- TOP CPU PROCESSES ---')
print(run('ps aux --sort=-%cpu | head -8'))

print('\n--- TOP MEMORY PROCESSES ---')
print(run('ps aux --sort=-%mem | head -8'))

print('\n' + '='*60)
print('  DETANGLE COMPLETE — baseline captured')
print('='*60)
