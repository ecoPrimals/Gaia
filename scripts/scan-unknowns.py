import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)
print('eastGate bridge\n')

def run(cmd, t=10):
    _, out, err = east.exec_command(cmd, timeout=t)
    return out.read().decode().strip()

# === .212 — suspect swiftGate (399ms WiFi, unnamed, no SSH) ===
print('='*50)
print('  .212 PORT SCAN (swiftGate?)')
print('='*50)
# SteamOS has SSH disabled by default!
# But might have: Steam Remote Play (27036-27037), RustDesk, Sunshine/Moonlight
ports_212 = run(
    'for p in 22 80 443 1714 3000 5900 8080 8384 8443 '
    '9090 11434 21115 21116 21117 21118 21119 '
    '27036 27037 27031 27032 47984 47989 47990 '
    '4443 5901 6900; do '
    '(echo >/dev/tcp/192.168.4.212/$p) 2>/dev/null && echo "PORT $p OPEN"; done', 20)
print(ports_212 if ports_212 else '  No ports open!')

# HTTP probe
print('\nHTTP probe:')
print(run('curl -s --connect-timeout 3 http://192.168.4.212:8080/ 2>&1 | head -5', 5))
print(run('curl -s --connect-timeout 3 http://192.168.4.212/ 2>&1 | head -5', 5))

# MAC lookup  
print('\n10:c7:53 = ??? (checking)')
# 10:c7:53 could be Quanta/Apple/Intel
print(run('ping -c1 -W2 192.168.4.212 && echo "ALIVE"', 5))

# === .181 — steamFRAME ===
print('\n' + '='*50)
print('  .181 PORT SCAN (steamFRAME)')
print('='*50)
ports_181 = run(
    'for p in 22 80 443 1714 3000 5900 8080 8384 8443 '
    '9090 11434 21115 21116 21117 21118 21119 '
    '27036 27037 27031 27032 47984 47989 47990; do '
    '(echo >/dev/tcp/192.168.4.181/$p) 2>/dev/null && echo "PORT $p OPEN"; done', 20)
print(ports_181 if ports_181 else '  No ports open!')

# Try SSH from eastGate with sshpass
print('\nSSH attempts:')
for user in ['deck', 'root', 'framegate']:
    for pw in ['framegate', 'deckgate', 'deck', 'eastgate', 'steam']:
        r = run(f'sshpass -p "{pw}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@192.168.4.181 "hostname; uname -a" 2>&1', 8)
        if 'Permission denied' not in r and 'Connection' not in r and 'banner' not in r.lower() and r:
            print(f'  ✅ {user}:{pw} → {r[:150]}')
            break
    else:
        continue
    break
else:
    print('  All combos failed')

# === .237 ironGate ===
print('\n' + '='*50)
print('  .237 PORT SCAN (ironGate)')
print('='*50)
ports_237 = run(
    'for p in 22 80 443 8080 8443 11434 21115; do '
    '(echo >/dev/tcp/192.168.4.237/$p) 2>/dev/null && echo "PORT $p OPEN"; done', 15)
print(ports_237 if ports_237 else '  No ports open!')

# Try SSH from eastGate
print('\nSSH attempts:')
for user in ['irongate', 'root', 'gaia']:
    for pw in ['irongate', 'eastgate', 'gaia']:
        r = run(f'sshpass -p "{pw}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {user}@192.168.4.237 "hostname; uname -a" 2>&1', 8)
        if 'Permission denied' not in r and 'Connection' not in r and r:
            print(f'  ✅ {user}:{pw} → {r[:150]}')
            break
    else:
        continue
    break
else:
    print('  All combos failed')

# === COMPLETE MAP ===
print('\n' + '='*50)
print('  FULL BODY MAP')
print('='*50)
print(run('cat /opt/Gaia/infra/hud/site/public/data/lan-mycelium-map.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -40', 8))

east.close()
