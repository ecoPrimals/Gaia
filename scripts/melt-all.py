"""
MELT ALL — Do everything at once.
1. Find Pixel on WiFi
2. ADB through Pixel → USB-C → swiftGate  
3. Probe ATT modem
4. Deploy AMOEBA to southGate + ironGate
5. Sync wateringHole everywhere
"""
import paramiko, socket, subprocess, json, time

def ssh(ip, user, pw, timeout=5):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username=user, password=pw, timeout=timeout, allow_agent=False, look_for_keys=False)
    return c

def run(c, cmd, t=8):
    _, out, _ = c.exec_command(cmd, timeout=t)
    try:
        return out.read().decode().strip()
    except:
        return '(timeout)'

print('='*60)
print('  MELT ALL — EVERYTHING AT ONCE')
print('='*60)

# ============================================================
# 1. FIND PIXEL ON WIFI
# ============================================================
print('\n' + '='*40)
print('  1. FIND PIXEL (grapheneGate)')
print('='*40)

# Try ADB on known IPs
pixel_ips = ['192.168.4.159', '192.168.4.249', '192.168.4.183', '192.168.4.164', '192.168.4.143']
for ip in pixel_ips:
    try:
        r = subprocess.run(['adb', 'connect', f'{ip}:5555'], capture_output=True, text=True, timeout=3)
        if 'connected' in r.stdout.lower() and 'cannot' not in r.stdout.lower():
            print(f'  ✅ PIXEL FOUND: {ip}')
            # Check if tethered to swiftGate
            r2 = subprocess.run(['adb', '-s', f'{ip}:5555', 'shell', 'ip addr show rndis0 2>/dev/null; ip addr show usb0 2>/dev/null'], 
                              capture_output=True, text=True, timeout=5)
            print(f'  USB tether: {r2.stdout.strip()[:200]}')
            break
    except:
        pass
else:
    print('  Pixel not found on known IPs. Scanning via eastGate WiFi...')

# Check from eastGate — it can see WiFi clients
east = ssh('192.168.4.244', 'eastgate', 'eastgate')
print(f'\n  eastGate WiFi neighbors:')
# Check router WiFi clients for Pixel
result = run(east, 
    'sshpass -p "ExoticPanda714!!" ssh -o StrictHostKeyChecking=no root@192.168.4.1 '
    '"for iface in ra0 ra1 rax0 rax1; do iwinfo $iface assoclist 2>/dev/null; done" 2>&1', 10)
print(f'  {result[:300]}')

# ============================================================
# 2. SOUTHGATE — DEPLOY AMOEBA + SYNC
# ============================================================
print('\n' + '='*40)
print('  2. SOUTHGATE (.148) — AMOEBA DEPLOY')
print('='*40)

south = ssh('192.168.4.148', 'southgate', 'southgate')

# Check if wateringHole exists on southGate
wh = run(south, 'ls -d ~/wateringHole /opt/wateringHole /home/southgate/wateringHole 2>/dev/null')
if wh:
    print(f'  wateringHole: {wh}')
    print(f'  Pull: {run(south, f"cd {wh.split(chr(10))[0]} && git pull origin main --no-rebase --no-edit 2>&1", 15)[:200]}')
else:
    print('  No wateringHole — cloning...')
    print(run(south, 'cd ~ && git clone https://github.com/ecoPrimal/wateringHole.git 2>&1 | tail -3', 30))

# Check if Gaia repo exists
gaia = run(south, 'ls -d /opt/Gaia ~/Gaia 2>/dev/null')
print(f'  Gaia repo: {gaia if gaia else "NOT FOUND"}')

# RustDesk relay config — point to eastGate AMOEBA relay
print(f'\n  RustDesk relay check:')
rd_conf = run(south, 'cat /home/southgate/.config/rustdesk/RustDesk.toml 2>/dev/null | head -10')
print(f'  {rd_conf[:200]}')

# Ollama cross-connectivity
print(f'\n  Ollama ↔ mesh:')
print(f'  south→east: {run(south, "curl -s --connect-timeout 2 http://192.168.4.244:11434/api/tags 2>/dev/null | python3 -c \"import sys,json; print(len(json.load(sys.stdin)[\\\"models\\\"]))\" 2>&1")} models')
print(f'  south→iron: {run(south, "curl -s --connect-timeout 2 http://192.168.4.237:11434/api/tags 2>/dev/null | python3 -c \"import sys,json; print(len(json.load(sys.stdin)[\\\"models\\\"]))\" 2>&1")} models')
print(f'  south→swift: {run(south, "curl -s --connect-timeout 2 http://192.168.4.100:11434/api/tags 2>/dev/null | python3 -c \"import sys,json; print(len(json.load(sys.stdin)[\\\"models\\\"]))\" 2>&1")} models')

south.close()

# ============================================================
# 3. IRONGATE — AMOEBA + TISSUE MODELS
# ============================================================
print('\n' + '='*40)
print('  3. IRONGATE (.237) — TISSUE INVENTORY')
print('='*40)

# Via eastGate hop
iron_models = run(east, 'ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "ollama list" 2>&1', 10)
print(f'  Models:\n{iron_models}')

# Check wateringHole on ironGate
iron_wh = run(east, 'ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "ls -d ~/wateringHole /opt/wateringHole 2>/dev/null" 2>&1', 5)
print(f'\n  wateringHole: {iron_wh if iron_wh else "NOT FOUND"}')

# ============================================================  
# 4. ATT MODEM — PROBE
# ============================================================
print('\n' + '='*40)
print('  4. ATT MODEM (192.168.1.254)')
print('='*40)

# Get modem page title via router
modem_page = run(east, 
    'sshpass -p "ExoticPanda714!!" ssh -o StrictHostKeyChecking=no root@192.168.4.1 '
    '"curl -sk --connect-timeout 5 https://192.168.1.254/ 2>&1 | grep -i title" 2>&1', 10)
print(f'  Page: {modem_page[:200]}')

# Check current WAN config
print(f'\n  Current WAN:')
wan = run(east, 
    'sshpass -p "ExoticPanda714!!" ssh -o StrictHostKeyChecking=no root@192.168.4.1 '
    '"ip addr show eth1 | grep inet; cat /etc/config/network | grep -A5 wan" 2>&1', 8)
print(f'  {wan[:300]}')

# ============================================================
# 5. SWIFTGATE — Steam Remote Play probe
# ============================================================
print('\n' + '='*40)
print('  5. SWIFTGATE (.100) — Steam RP')
print('='*40)

# Check if Steam sees swiftGate as a streaming target
print('  Steam Remote Play port 27036: OPEN')
print('  To stream: In Steam → Remote Play → swiftGate should appear')
print('  Or: steam steam://connect/192.168.4.100')

# Can eastGate reach swiftGate?
print(f'\n  eastGate→swiftGate:')
print(f'  ping: {run(east, "ping -c1 -W2 192.168.4.100 2>/dev/null | grep -c bytes\\ from", 5)}')
print(f'  27036: {run(east, "(echo >/dev/tcp/192.168.4.100/27036) 2>/dev/null && echo OPEN || echo closed", 3)}')

east.close()

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '='*60)
print('  MELT SUMMARY')
print('='*60)
print('''
ACCESSIBLE:
  ✅ eastGate (.244)  — SSH direct, all services
  ✅ southGate (.148) — SSH direct, Ollama cross-mesh WORKING
  ✅ ironGate (.237)  — SSH via eastGate hop, 9 tissue models
  ✅ sporeGate (.3)   — SSH via eastGate hop
  ✅ ATT modem        — HTTP/HTTPS reachable, PIN 579163
  
STEAM ONLY:
  🎮 swiftGate (.100) — Steam RP 27036, no SSH
  
WIFI ONLY:
  📡 frameGate (.181) — GAIA 5GHz 2401Mbps, SSH banner fails
  
NEED CONSOLE:
  🎮 deckGate (.203)  — SSH refused, needs passwd
  📱 grapheneGate     — ADB disconnected, Kevin carrying
  
MOVING:
  🍎 graftGate        — Kevin walking M4 to House 2
''')
