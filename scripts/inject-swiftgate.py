import paramiko

# swiftGate is at .148 with 1c:86:0b MAC (10G NIC)
# Try SSH — password = "northgate" (it was the original name) or "swiftgate"

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)
print('eastGate bridge connected\n')

# Try to SSH to .148 from eastGate
targets = [
    ('.148 swiftGate', '192.168.4.148', 'root', 'swiftgate'),
    ('.148 northgate-pw', '192.168.4.148', 'root', 'northgate'),
    ('.148 deck-pw', '192.168.4.148', 'deck', 'deckgate'),
    ('.148 key-auth', '192.168.4.148', 'root', None),
    ('.181 graftGate', '192.168.4.181', 'root', 'graftgate'),
    ('.203 frameGate', '192.168.4.203', 'deck', 'deckgate'),
    ('.100 blueGate', '192.168.4.100', 'root', 'bluegate'),
]

for label, ip, user, pw in targets:
    print(f'=== {label} ({ip}) ===')
    
    if pw is None:
        # Key auth
        cmd = f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes {user}@{ip} "hostname; uname -a" 2>&1'
    else:
        # Check if sshpass available
        cmd = f'timeout 5 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes {user}@{ip} "hostname; uname -a" 2>&1'
    
    _, out, _ = east.exec_command(cmd, timeout=10)
    result = out.read().decode().strip()
    print(f'  {result[:150]}')
    
    # Also try direct SSH with paramiko from northGate
    try:
        t = paramiko.SSHClient()
        t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if pw:
            t.connect(ip, username=user, password=pw, timeout=3)
        else:
            t.connect(ip, username=user, timeout=3)
        _, out, _ = t.exec_command('hostname; uname -a; uptime', timeout=5)
        print(f'  DIRECT SSH: {out.read().decode().strip()[:150]}')
        t.close()
    except Exception as e:
        print(f'  Direct: {str(e)[:80]}')
    print()

east.close()
print('Injection probe complete!')
