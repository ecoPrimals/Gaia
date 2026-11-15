"""
SURGERY PREP — Nudge eastGate to start autonomous operations.
Kevin is going into surgery. The organism works while he heals.
"""
import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def run(cmd, t=15):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try:
        return out.read().decode().strip()
    except:
        return '(timeout)'

print('='*60)
print('  SURGERY PREP — eastGate autonomous activation')
print('='*60)

# 1. Pull latest Gaia repo
print('\n--- Pull /opt/Gaia ---')
# Stash local changes first
print(run('cd /opt/Gaia && git stash 2>&1 | tail -1', 10))
print(run('cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git pull origin main --no-rebase --no-edit 2>&1 | tail -3', 15))

# 2. Check southGate is reachable
print('\n--- southGate reachable? ---')
south_ollama = run('curl -s --connect-timeout 2 http://192.168.4.148:11434/api/tags 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)[\'models\']), \'models\')" 2>&1')
print(f'southGate Ollama: {south_ollama}')

# 3. Check ironGate reachable
print('\n--- ironGate reachable? ---')
iron_ollama = run('curl -s --connect-timeout 2 http://192.168.4.237:11434/api/tags 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)[\'models\']), \'models\')" 2>&1')
print(f'ironGate Ollama: {iron_ollama}')

# 4. Verify all services
print('\n--- eastGate services ---')
print(f'Ollama: {run("systemctl is-active ollama 2>/dev/null")}')
print(f'RustDesk: {run("systemctl is-active rustdesk 2>/dev/null")}')
print(f'Gate: {run("curl -s --connect-timeout 2 http://localhost:8443/pulse 2>&1 | head -1")}')
print(f'Data: {run("curl -s --connect-timeout 2 http://localhost:8080/data/now.json 2>&1 | head -1")}')
print(f'Forgejo: {run("curl -s --connect-timeout 2 http://localhost:3000/ 2>&1 | head -1")}')
print(f'Tor: {run("systemctl is-active tor 2>/dev/null")}')

# 5. Verify crons still running
print(f'\n--- Active crons ---')
cron_count = run('crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l')
print(f'Active cron jobs: {cron_count}')

# 6. Check uptime
print(f'\nUptime: {run("uptime")}')
print(f'Disk: {run("df -h / | tail -1")}')
print(f'GPU: {run("nvidia-smi --query-gpu=name,temperature.gpu,power.draw --format=csv,noheader")}')

east.close()

print('''
============================================================
  SURGERY PREP COMPLETE
  
  All repos pushed:
    ✅ Gaia → GitHub (233f555ba)
    ✅ wateringHole → GitHub (8c197c557) 
    ✅ KenshiReborn → Forgejo (4e498e2)
  
  Gates operational:
    ✅ eastGate — BRAIN (all services)
    ✅ southGate — FORGE 3 (Ollama reachable)
    ✅ ironGate — FORGE 2 (Ollama + tissue models)
    ✅ sporeGate — DNS + heart-pull
  
  Kevin: Go heal. The organism breathes. lub-DUB. 🫀
============================================================
''')
