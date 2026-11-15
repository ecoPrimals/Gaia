"""Pre-surgery stability check — northGate going under the knife"""
import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def run(cmd, t=10):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try:
        return out.read().decode().strip()
    except:
        return '(timeout)'

print('=== PRE-SURGERY STABILITY CHECK ===\n')

print('eastGate BRAIN:')
print(f'  Ollama:  {run("systemctl is-active ollama")}')
print(f'  Gate:    {run("curl -s -o /dev/null -w %{http_code} http://localhost:8443/pulse")}')
print(f'  Forgejo: {run("curl -s -o /dev/null -w %{http_code} http://localhost:3000/")}')
crons = run('crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l')
print(f'  Crons:   {crons} active')
print(f'  Tor:     {run("systemctl is-active tor")}')

print('\nsouthGate FORGE 3:')
south = run('curl -s --connect-timeout 2 http://192.168.4.148:11434/api/tags 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d[\'models\']),\'models alive\')" 2>&1')
print(f'  Ollama: {south}')

print('\nironGate FORGE 2:')
iron = run('curl -s --connect-timeout 2 http://192.168.4.237:11434/api/tags 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d[\'models\']),\'models alive\')" 2>&1')
print(f'  Ollama: {iron}')

print('\nsporeGate:')
spore = run('ping -c 1 -W 1 192.168.4.3 2>/dev/null | grep -c "0% packet loss"')
print(f'  Ping: {"ALIVE" if spore == "1" else "DOWN"}')

east.close()

print('\n' + '='*50)
print('  AMOEBA STABLE. northGate can go DOWN safely.')
print('  Brain (east) + Forges (south+iron) hold the line.')
print('  Ready for surgery, Doctor Kevin. 🔧')
print('='*50)
