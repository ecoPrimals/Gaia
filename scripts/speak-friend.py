import paramiko, socket

# SPEAK FRIEND AND ENTER
# Password = gate name in lowercase. ZK = NULL.
# Username = gate name too (or root on some)

gates = {
    '192.168.4.148': {
        'names': ['southgate', 'swiftgate', 'northgate'],  # .148 was southGate IP, but MAC says server
        'users': ['southgate', 'swiftgate', 'root', 'deck', 'gaia'],
    },
    '192.168.4.181': {
        'names': ['graftgate'],  # Apple MAC = Mac Mini M4
        'users': ['graftgate', 'root', 'kevin', 'gaia'],
    },
    '192.168.4.203': {
        'names': ['deckgate', 'framegate'],  # steamdeck.primals.local
        'users': ['deck', 'root', 'framegate', 'deckgate', 'gaia'],
    },
    '192.168.4.237': {
        'names': ['irongate'],  # known ironGate
        'users': ['irongate', 'root', 'gaia'],
    },
    '192.168.4.100': {
        'names': ['bluegate'],  # known blueGate
        'users': ['bluegate', 'root', 'gaia'],
    },
    '192.168.4.160': {
        'names': ['swiftgate', 'deckgate'],  # unknown new device
        'users': ['swiftgate', 'deck', 'root', 'gaia'],
    },
    '192.168.4.212': {
        'names': ['swiftgate'],  # another unknown
        'users': ['swiftgate', 'root', 'gaia'],
    },
}

print('=== SPEAK FRIEND AND ENTER ===\n')

for ip, info in gates.items():
    # Quick ping first
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        result = s.connect_ex((ip, 22))
        s.close()
        if result != 0:
            print(f'{ip}: SSH port closed/timeout — skipping')
            continue
        print(f'{ip}: SSH port OPEN — trying passwords...')
    except:
        print(f'{ip}: unreachable — skipping')
        continue

    found = False
    # Try every user + every gate name as password
    all_passwords = list(set(info['names'] + ['eastgate', 'gaia']))
    for user in info['users']:
        for pw in all_passwords:
            try:
                t = paramiko.SSHClient()
                t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                t.connect(ip, username=user, password=pw, timeout=3, 
                         allow_agent=False, look_for_keys=False)
                _, out, _ = t.exec_command('hostname 2>/dev/null; uname -a 2>/dev/null; uptime 2>/dev/null', timeout=5)
                identity = out.read().decode().strip()
                print(f'  ✅ FRIEND ENTERED! {user}:{pw}')
                print(f'  Identity: {identity[:200]}')
                
                # Get more info
                _, out, _ = t.exec_command('cat /etc/hostname 2>/dev/null; lsb_release -d 2>/dev/null; cat /etc/os-release 2>/dev/null | head -3', timeout=3)
                print(f'  OS: {out.read().decode().strip()[:150]}')
                
                _, out, _ = t.exec_command('ip addr show 2>/dev/null | grep "inet " | head -5', timeout=3)
                print(f'  IPs: {out.read().decode().strip()[:200]}')
                
                _, out, _ = t.exec_command('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "no nvidia"', timeout=3)
                print(f'  GPU: {out.read().decode().strip()[:100]}')
                
                _, out, _ = t.exec_command('which ollama 2>/dev/null && ollama list 2>/dev/null | head -5 || echo "no ollama"', timeout=5)
                print(f'  Ollama: {out.read().decode().strip()[:150]}')
                
                _, out, _ = t.exec_command('systemctl is-active rustdesk 2>/dev/null; ls /usr/bin/rustdesk 2>/dev/null', timeout=3)
                print(f'  RustDesk: {out.read().decode().strip()[:80]}')
                
                t.close()
                found = True
                break
            except paramiko.AuthenticationException:
                pass
            except Exception as e:
                err = str(e)[:50]
                if 'timed out' in err or 'refused' in err:
                    break
        if found:
            break
    
    if not found:
        print(f'  ❌ No friend spoke the right word')
    print()

# Also try eastGate hop to .148
print('=== eastGate HOP to .148 ===')
east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

# Try sshpass from eastGate
for user in ['southgate', 'swiftgate', 'root', 'deck']:
    for pw in ['southgate', 'swiftgate', 'northgate', 'deckgate', 'eastgate']:
        cmd = f'sshpass -p "{pw}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@192.168.4.148 "hostname; uname -a" 2>&1'
        _, out, _ = east.exec_command(cmd, timeout=8)
        result = out.read().decode().strip()
        if 'Permission denied' not in result and 'Connection' not in result and result:
            print(f'  ✅ HOP: {user}:{pw} → {result[:150]}')
            break
    else:
        continue
    break
else:
    # Try key auth
    _, out, _ = east.exec_command('ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@192.168.4.148 "hostname" 2>&1', timeout=8)
    print(f'  Key auth: {out.read().decode().strip()[:100]}')

# Port scan .148
print('\n=== .148 port scan ===')
_, out, _ = east.exec_command(
    'for p in 22 80 443 1714 3000 5900 8080 8384 8443 11434 21115 21116 21117 21118 47984 47989; do '
    '(echo >/dev/tcp/192.168.4.148/$p) 2>/dev/null && echo "PORT $p OPEN"; done',
    timeout=15
)
print(out.read().decode())

east.close()
print('Done — friend or foe?')
