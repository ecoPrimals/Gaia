"""
SOURDOUGH REBOOT — Graceful up/down for northGate hardware surgery.
Run BEFORE powering off: saves state, verifies organism survives without us.
Run AFTER powering on: verifies everything came back healthy.

Usage:
  python sourdough-reboot.py down   # Pre-shutdown checklist
  python sourdough-reboot.py up     # Post-boot health verify
  python sourdough-reboot.py        # Just show current health
"""
import subprocess, sys, json, time, os
from datetime import datetime

STATE_FILE = os.path.expanduser('~/sourdough-state.json')

def run(cmd, t=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
        return (r.stdout + r.stderr).strip()
    except:
        return ''

def get_health():
    """Capture current system health as a dict"""
    h = {}
    h['timestamp'] = datetime.now().isoformat()
    h['hostname'] = run('hostname')
    h['uptime'] = run('uptime -p')

    # GPU
    gpu = run('nvidia-smi --query-gpu=name,temperature.gpu,power.draw,memory.used,memory.total --format=csv,noheader')
    h['gpu'] = gpu if gpu else 'NO GPU DETECTED'
    h['gpu_alive'] = 'NVIDIA' in gpu if gpu else False

    # Ollama
    h['ollama_active'] = run('systemctl is-active ollama 2>/dev/null') == 'active'
    model_count = run('ollama list 2>&1 | tail -n +2 | wc -l')
    h['ollama_models'] = int(model_count) if model_count.isdigit() else 0

    # Network
    h['can_reach_east'] = '0% packet loss' in run('ping -c 1 -W 1 192.168.4.244 2>&1')
    h['can_reach_wan'] = '0% packet loss' in run('ping -c 1 -W 1 8.8.8.8 2>&1')
    h['can_reach_south'] = '0% packet loss' in run('ping -c 1 -W 1 192.168.4.148 2>&1')
    h['can_reach_iron'] = '0% packet loss' in run('ping -c 1 -W 1 192.168.4.237 2>&1')

    # Services
    for svc in ['ollama', 'sshd', 'NetworkManager']:
        h[f'svc_{svc}'] = run(f'systemctl is-active {svc} 2>/dev/null')

    # Failed units
    h['failed_units'] = run('systemctl --failed --plain --no-pager 2>&1 | grep -c "failed"')

    # Memory
    mem = run("free -m | awk '/Mem:/ {print $2, $3, $7}'")
    if mem:
        parts = mem.split()
        if len(parts) == 3:
            h['mem_total_mb'] = int(parts[0])
            h['mem_used_mb'] = int(parts[1])
            h['mem_available_mb'] = int(parts[2])

    # Disk
    disk = run("df -BG / | awk 'NR==2 {print $2, $3, $4}'")
    if disk:
        h['disk'] = disk

    # Crons
    crons = run('crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l')
    h['cron_count'] = int(crons) if crons.isdigit() else 0

    return h

def show_health(h, label='CURRENT'):
    """Pretty print health"""
    print(f'\n{"="*55}')
    print(f'  SOURDOUGH — {label} HEALTH')
    print(f'{"="*55}')
    print(f'  Host:     {h.get("hostname", "?")}')
    print(f'  Uptime:   {h.get("uptime", "?")}')
    print(f'  Time:     {h.get("timestamp", "?")}')

    gpu_ok = '✅' if h.get('gpu_alive') else '❌'
    print(f'\n  GPU:      {gpu_ok} {h.get("gpu", "?")}')

    oll = '✅' if h.get('ollama_active') else '❌'
    print(f'  Ollama:   {oll} ({h.get("ollama_models", 0)} models)')

    east = '✅' if h.get('can_reach_east') else '❌'
    wan = '✅' if h.get('can_reach_wan') else '❌'
    south = '✅' if h.get('can_reach_south') else '❌'
    iron = '✅' if h.get('can_reach_iron') else '❌'
    print(f'\n  Network:')
    print(f'    eastGate:  {east}')
    print(f'    WAN:       {wan}')
    print(f'    southGate: {south}')
    print(f'    ironGate:  {iron}')

    for svc in ['ollama', 'sshd', 'NetworkManager']:
        s = h.get(f'svc_{svc}', '?')
        ok = '✅' if s == 'active' else '❌'
        print(f'    {svc}: {ok} {s}')

    fail = h.get('failed_units', '0')
    print(f'\n  Failed units: {fail}')
    print(f'  Cron jobs:    {h.get("cron_count", "?")}')

    mem_t = h.get('mem_total_mb', 0)
    mem_a = h.get('mem_available_mb', 0)
    if mem_t:
        pct = round((mem_t - mem_a) / mem_t * 100, 1)
        print(f'  Memory:       {mem_a}MB free / {mem_t}MB ({pct}% used)')
    print(f'  Disk:         {h.get("disk", "?")}')

def cmd_down():
    """Pre-shutdown: save state, verify organism survives"""
    print('\n🔧 SOURDOUGH DOWN — Preparing for hardware surgery...\n')

    h = get_health()
    show_health(h, 'PRE-SURGERY BASELINE')

    # Save state
    with open(STATE_FILE, 'w') as f:
        json.dump(h, f, indent=2)
    print(f'\n  💾 Baseline saved to {STATE_FILE}')

    # Stop ollama gracefully
    print('\n  Stopping ollama gracefully...')
    print(f'  {run("systemctl stop ollama 2>&1")}')
    time.sleep(1)
    print(f'  ollama: {run("systemctl is-active ollama 2>/dev/null")}')

    # Sync disks
    print('  Syncing disks...')
    run('sync')

    # Verify organism survives without us
    print('\n  Verifying organism survives without northGate...')
    import paramiko
    try:
        east = paramiko.SSHClient()
        east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)
        _, out, _ = east.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8443/pulse', timeout=5)
        code = out.read().decode().strip()
        east.close()
        print(f'  eastGate pulse: {code} {"✅" if code == "200" else "❌"}')
    except Exception as e:
        print(f'  eastGate: {e}')

    print(f'\n{"="*55}')
    print(f'  ✅ READY FOR SHUTDOWN')
    print(f'  Run: sudo poweroff')
    print(f'  After surgery: python sourdough-reboot.py up')
    print(f'{"="*55}')

def cmd_up():
    """Post-boot: verify everything came back healthy"""
    print('\n🫀 SOURDOUGH UP — Post-surgery health check...\n')

    h = get_health()
    show_health(h, 'POST-SURGERY')

    # Compare with baseline
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            baseline = json.load(f)

        print(f'\n  📊 Comparing with pre-surgery baseline...')

        diffs = []
        if baseline.get('gpu_alive') and not h.get('gpu_alive'):
            diffs.append('❌ GPU was alive, now DEAD')
        if baseline.get('ollama_models', 0) != h.get('ollama_models', 0):
            diffs.append(f'⚠️  Ollama models: {baseline.get("ollama_models")} → {h.get("ollama_models")}')
        if baseline.get('cron_count', 0) != h.get('cron_count', 0):
            diffs.append(f'⚠️  Cron jobs: {baseline.get("cron_count")} → {h.get("cron_count")}')
        for gate in ['east', 'south', 'iron']:
            key = f'can_reach_{gate}'
            if baseline.get(key) and not h.get(key):
                diffs.append(f'❌ Lost reach to {gate}Gate')

        if diffs:
            print('  DIFFERENCES FOUND:')
            for d in diffs:
                print(f'    {d}')
        else:
            print('  ✅ All systems match baseline — surgery successful!')
    else:
        print('  (no baseline found — run "down" before next shutdown)')

    print(f'\n{"="*55}')
    print(f'  SOURDOUGH FERMENTATION COMPLETE')
    print(f'{"="*55}')

# Main
mode = sys.argv[1] if len(sys.argv) > 1 else 'status'

if mode == 'down':
    cmd_down()
elif mode == 'up':
    cmd_up()
else:
    h = get_health()
    show_health(h)
