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

# Use nmap for fast scanning
print('=== .212 nmap ===')
r = run('nmap -sT -T4 --top-ports 100 192.168.4.212 2>/dev/null', 30)
if 'nmap' not in r.lower() and r != '(timeout)':
    # nmap not installed, try nc
    print('nmap not available, trying nc...')
    for p in [22, 80, 443, 8080, 11434, 27036, 47984]:
        r2 = run(f'nc -z -w1 192.168.4.212 {p} 2>&1 && echo "PORT {p} OPEN" || echo "PORT {p} closed"', 3)
        if 'OPEN' in r2:
            print(f'  {r2}')
else:
    print(r[:800])

print('\n=== .181 (steamFRAME) nmap ===')
r = run('nmap -sT -T4 --top-ports 50 192.168.4.181 2>/dev/null', 20)
if 'nmap' not in r.lower() and r != '(timeout)':
    for p in [22, 80, 443, 8080, 11434, 27036, 47984]:
        r2 = run(f'nc -z -w1 192.168.4.181 {p} 2>&1 && echo "PORT {p} OPEN" || echo "PORT {p} closed"', 3)
        if 'OPEN' in r2:
            print(f'  {r2}')
else:
    print(r[:800])

print('\n=== .237 (ironGate) nmap ===')
r = run('nmap -sT -T4 --top-ports 50 192.168.4.237 2>/dev/null', 20)
if 'nmap' not in r.lower() and r != '(timeout)':
    for p in [22, 80, 443, 8080, 11434]:
        r2 = run(f'nc -z -w1 192.168.4.237 {p} 2>&1 && echo "PORT {p} OPEN" || echo "PORT {p} closed"', 3)
        if 'OPEN' in r2:
            print(f'  {r2}')
else:
    print(r[:800])

# Also: try sshpass ironGate from eastGate  
print('\n=== ironGate SSH via eastGate sshpass ===')
for user, pw in [('irongate','irongate'), ('root','irongate'), ('irongate','eastgate')]:
    r = run(f'sshpass -p "{pw}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@192.168.4.237 "hostname" 2>&1', 6)
    print(f'  {user}:{pw} → {r[:100]}')

# Check if eastGate knows about swiftGate
print('\n=== eastGate body knowledge ===')
print(run('grep -ri swift /opt/Gaia/data/ 2>/dev/null | head -10', 8))
print()
print(run('cat /opt/Gaia/data/amoeba-mesh.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\\"  {k}: {v.get(\'ip\',\'?\')  } {v.get(\'status\',\'?\')}\\" ) for k,v in d.get(\'gates\',d).items()]" 2>&1', 8))

east.close()
print('\nDone!')
