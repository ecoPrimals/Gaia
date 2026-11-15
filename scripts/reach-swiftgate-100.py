import paramiko, socket, time

# wateringHole says swiftGate is at .100!
# DHCP says .100 = DESKTOP-BLOV2LR (MAC 68:54:5a:d0:69:a2)
# swiftGate = Ryzen 7 5800X + RTX 3070 + 16GB

ip = '192.168.4.100'

print('='*60)
print(f'  REACHING swiftGate at {ip}')
print('='*60)

# Port check first
print('\nPort scan:')
for port in [22, 80, 443, 1714, 3000, 3141, 3389, 5900, 8080, 8443, 11434, 21115, 21116, 21117, 21118, 27036, 47984]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        result = s.connect_ex((ip, port))
        s.close()
        if result == 0:
            print(f'  PORT {port} OPEN!')
    except:
        pass

# Try SSH with all combos
print('\nSSH attempts (SPEAK FRIEND):')
combos = [
    ('swiftgate', 'swiftgate'),
    ('root', 'swiftgate'),
    ('deck', 'swiftgate'),
    ('gaia', 'swiftgate'),
    ('swiftgate', 'eastgate'),
    ('kevin', 'swiftgate'),
    ('mokke', 'swiftgate'),
    # blueGate was Windows - maybe it's now Linux
    ('bluegate', 'bluegate'),
    ('root', 'bluegate'),
]

for user, pw in combos:
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, username=user, password=pw, timeout=5, allow_agent=False, look_for_keys=False)
        _, out, _ = c.exec_command('hostname; uname -a; uptime', timeout=5)
        ident = out.read().decode().strip()
        print(f'  ✅ FRIEND ENTERED! {user}:{pw}')
        print(f'  {ident}')
        
        # Deep probe
        _, out, _ = c.exec_command('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "no-gpu"', timeout=5)
        print(f'  GPU: {out.read().decode().strip()}')
        
        _, out, _ = c.exec_command('ollama list 2>/dev/null | head -8 || echo "no-ollama"', timeout=8)
        print(f'  Ollama: {out.read().decode().strip()[:200]}')
        
        _, out, _ = c.exec_command('ip addr | grep "inet " | grep -v 127', timeout=3)
        print(f'  IPs: {out.read().decode().strip()}')
        
        _, out, _ = c.exec_command('ls /opt/Gaia 2>/dev/null | head -5; which biomeos 2>/dev/null; ls *.exe 2>/dev/null', timeout=3)
        print(f'  Gaia: {out.read().decode().strip()}')
        
        c.close()
        break
    except paramiko.AuthenticationException:
        pass
    except paramiko.ssh_exception.SSHException as e:
        if 'publickey' in str(e).lower() or 'Bad authentication' in str(e):
            print(f'  {user}:{pw} → pubkey only!')
            break
        print(f'  {user}:{pw} → SSH error: {str(e)[:60]}')
        break
    except socket.timeout:
        print(f'  {user}:{pw} → timeout')
        break
    except Exception as e:
        print(f'  {user}:{pw} → {str(e)[:60]}')
        break

# Also try via eastGate hop
print('\n--- Via eastGate hop ---')
east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

for user in ['swiftgate', 'root', 'deck']:
    for pw in ['swiftgate', 'bluegate']:
        _, out, _ = east.exec_command(
            f'sshpass -p "{pw}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@{ip} "hostname; uname -a" 2>&1',
            timeout=8
        )
        result = out.read().decode().strip()
        if 'Permission denied' not in result and 'Connection' not in result and 'timed out' not in result.lower() and result:
            print(f'  ✅ HOP: {user}:{pw} → {result[:150]}')
            break
    else:
        continue
    break
else:
    # Key auth
    _, out, _ = east.exec_command(
        f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes root@{ip} "hostname" 2>&1',
        timeout=10
    )
    print(f'  Key auth: {out.read().decode().strip()[:100]}')

# Check if it's reachable via HTTP
print('\n--- HTTP probe ---')
_, out, _ = east.exec_command(f'curl -s --connect-timeout 3 http://{ip}:8080/ 2>&1 | head -3', timeout=8)
print(f'  :8080: {out.read().decode().strip()[:100]}')
_, out, _ = east.exec_command(f'curl -s --connect-timeout 3 http://{ip}:3141/ 2>&1 | head -3', timeout=8)
print(f'  :3141: {out.read().decode().strip()[:100]}')
_, out, _ = east.exec_command(f'curl -s --connect-timeout 3 http://{ip}:11434/api/tags 2>&1 | head -1', timeout=8)
print(f'  :11434: {out.read().decode().strip()[:100]}')

east.close()
print('\nDone!')
