import paramiko, socket

def try_ssh(ip, user, pw, label=''):
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, username=user, password=pw, timeout=5, allow_agent=False, look_for_keys=False)
        _, out, _ = c.exec_command('hostname; uname -a; uptime', timeout=5)
        ident = out.read().decode().strip()
        print(f'  ✅ {label} {user}:{pw} → {ident[:200]}')
        
        # Full probe
        _, out, _ = c.exec_command('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "no-gpu"', timeout=5)
        print(f'  GPU: {out.read().decode().strip()[:100]}')
        
        _, out, _ = c.exec_command('ip addr | grep "inet " | grep -v 127', timeout=3)
        print(f'  IPs: {out.read().decode().strip()[:200]}')
        
        _, out, _ = c.exec_command('lscpu | grep "Model name"', timeout=3)
        print(f'  CPU: {out.read().decode().strip()[:100]}')
        
        _, out, _ = c.exec_command('free -h | grep Mem', timeout=3)
        print(f'  RAM: {out.read().decode().strip()[:100]}')
        
        _, out, _ = c.exec_command('cat /sys/class/dmi/id/product_name 2>/dev/null', timeout=3)
        print(f'  Case: {out.read().decode().strip()[:100]}')
        
        _, out, _ = c.exec_command('ip link | grep usb', timeout=3)
        usb_net = out.read().decode().strip()
        if usb_net:
            print(f'  USB TETHER: {usb_net[:200]}')
        
        _, out, _ = c.exec_command('lsusb | grep -iE "google|pixel|android" 2>/dev/null', timeout=3)
        pixel = out.read().decode().strip()
        if pixel:
            print(f'  PIXEL FOUND: {pixel}')
        
        c.close()
        return True
    except paramiko.AuthenticationException:
        return False
    except Exception as e:
        print(f'  ⚠ {label} {user}:{pw} → {str(e)[:60]}')
        return None

# .212 — suspect swiftGate (399ms WiFi, unnamed)
print('='*60)
print('  .212 — SPEAK FRIEND (swiftGate?)')
print('='*60)
for user in ['swiftgate', 'deck', 'root', 'gaia', 'steam']:
    for pw in ['swiftgate', 'deckgate', 'deck', 'steam', 'eastgate']:
        result = try_ssh('192.168.4.212', user, pw, f'.212')
        if result is True:
            break
        if result is None:
            break
    if result is True:
        break

# .181 — steamFRAME
print('\n' + '='*60)
print('  .181 — SPEAK FRIEND (steamFRAME)')
print('='*60)
for user in ['deck', 'root', 'framegate', 'steam', 'gaia']:
    for pw in ['framegate', 'deckgate', 'deck', 'steam', 'eastgate']:
        result = try_ssh('192.168.4.181', user, pw, '.181')
        if result is True:
            break
        if result is None:
            break
    if result is True:
        break

# .237 ironGate — retry with correct password
print('\n' + '='*60)
print('  .237 — SPEAK FRIEND (ironGate)')
print('='*60)
for user in ['irongate', 'root', 'gaia']:
    for pw in ['irongate', 'eastgate', 'gaia']:
        result = try_ssh('192.168.4.237', user, pw, '.237')
        if result is True:
            break
        if result is None:
            break
    if result is True:
        break

# .139 — DESKTOP-9QG6LQL (Windows?)
print('\n' + '='*60)
print('  .139 — DESKTOP-9QG6LQL')
print('='*60)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    r = s.connect_ex(('192.168.4.139', 22))
    s.close()
    if r == 0:
        print('  SSH open')
    else:
        print(f'  SSH closed (port 22 code {r})')
        # Check RDP
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.settimeout(2)
        r2 = s2.connect_ex(('192.168.4.139', 3389))
        s2.close()
        print(f'  RDP: {"OPEN" if r2==0 else "closed"}')
except Exception as e:
    print(f'  Error: {e}')

print('\nDone!')
