import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)
print('eastGate bridge\n')

# Deep probe .148 (swiftGate?) — scan ports and try every combo
ip = '192.168.4.148'

# Port scan key services
print(f'=== Port scan {ip} ===')
ports = [22, 80, 443, 1714, 3000, 3141, 5900, 8080, 8443, 11434, 21115, 21116, 21117, 21118, 21119, 8082, 8384]
port_str = ' '.join(str(p) for p in ports)
_, out, _ = east.exec_command(
    f'for p in {port_str}; do (echo >/dev/tcp/{ip}/$p) 2>/dev/null && echo "PORT $p OPEN" || echo "PORT $p closed"; done',
    timeout=30
)
print(out.read().decode())

# Try SSH banners to identify
print('=== SSH Banner ===')
_, out, _ = east.exec_command(f'timeout 3 ssh -v -o StrictHostKeyChecking=no -o BatchMode=yes root@{ip} 2>&1 | head -20', timeout=8)
banner = out.read().decode()
print(banner[:500])

# Try nmap if available
print('=== Service detection ===')
_, out, _ = east.exec_command(f'nmap -sV -p 22 {ip} 2>/dev/null | grep "22/tcp"', timeout=10)
print(out.read().decode())

# Check MAC vendor - 1c:86:0b
print('=== MAC lookup 1c:86:0b ===')
print('1c:86:0b = ASUS or similar (10G NIC)')
print('Same prefix as .237 (ironGate) and .244 (eastGate)')
print()

# Try SSH with ALL possible combos
users = ['root', 'deck', 'steam', 'swiftgate', 'gaia', 'eastgate', 'northgate']
passwords = ['swiftgate', 'northgate', 'deckgate', 'southgate', 'eastgate', 'deck', 'steam', '']

print('=== SSH brute (from northGate) ===')
import socket
for user in users:
    for pw in passwords:
        try:
            t = paramiko.SSHClient()
            t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            t.connect(ip, username=user, password=pw, timeout=2)
            _, out, _ = t.exec_command('hostname; uname -a', timeout=3)
            h = out.read().decode().strip()
            print(f'  ✅ {user}:{pw} → {h}')
            t.close()
            break
        except paramiko.AuthenticationException:
            pass
        except socket.timeout:
            break
        except Exception as e:
            if 'timed out' in str(e) or 'Connection refused' in str(e):
                break
    else:
        continue
    break
else:
    print('  All combos failed')

# Also probe .181 (graftGate Apple)
print('\n=== .181 graftGate port scan ===')
ports_181 = [22, 80, 5900, 11434, 8080, 3141, 8443]
for p in ports_181:
    _, out, _ = east.exec_command(f'(echo >/dev/tcp/192.168.4.181/{p}) 2>/dev/null && echo "PORT {p} OPEN" || echo "PORT {p} closed"', timeout=3)
    r = out.read().decode().strip()
    if 'OPEN' in r:
        print(f'  {r}')

# Try graftGate SSH
print('\n=== graftGate SSH ===')
for user in ['root', 'graftgate', 'gaia', 'kevin']:
    for pw in ['graftgate', 'eastgate', 'gaia']:
        try:
            t = paramiko.SSHClient()
            t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            t.connect('192.168.4.181', username=user, password=pw, timeout=2)
            _, out, _ = t.exec_command('hostname; uname -a', timeout=3)
            print(f'  ✅ {user}:{pw} → {out.read().decode().strip()[:100]}')
            t.close()
            break
        except:
            pass

east.close()
