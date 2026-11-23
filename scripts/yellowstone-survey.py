"""
YELLOWSTONE SURVEY — Map the hairpin NAT blind spot.
WHY did we miss it? What will we see BEFORE we wire?

The geology:
  Yellowstone = the ATT BGW320 (hot magma beneath the surface)
  Grand Canyon = the layers of routing exposed by failure
  Explore = probe from every gate's perspective
  Return = tally what we found
  Resolve = wire dromedary as the inner solve
"""
import paramiko, json

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def erun(cmd, t=15):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print('='*60)
print('  YELLOWSTONE SURVEY — hairpin NAT geology')
print('='*60)

# === 1. THE GEOLOGY: Why we were blind ===
print('''
╔══════════════════════════════════════════════════╗
║  WHY WE MISSED IT                                ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  eastGate (.244) ←→ northGate (.147)             ║
║       Same subnet. Direct L2. No hairpin.        ║
║       They NEVER needed the WAN path.            ║
║                                                  ║
║  swiftGate (.100) → nestgate.io (WAN IP)         ║
║       FIRST gate to try reaching itself           ║
║       through the public IP. BGW320 DROPS it.     ║
║                                                  ║
║  The hot springs were always there.               ║
║  We just never stepped on them.                   ║
╚══════════════════════════════════════════════════╝
''')

# === 2. THE LAYERS: Grand Canyon cross-section ===
print('--- LAYER 1: DNS Resolution (what names resolve to) ---')
for domain in ['primals.eco', 'primal.eco', 'nestgate.io']:
    result = erun(f'dig +short {domain} A 2>&1 | head -3')
    result6 = erun(f'dig +short {domain} AAAA 2>&1 | head -1')
    print(f'  {domain}:')
    print(f'    A:    {result}')
    print(f'    AAAA: {result6 if result6 else "(none)"}')

print('\n--- LAYER 2: From eastGate — can we reach ourselves via WAN? ---')
wan_ip = erun('curl -s --connect-timeout 3 ifconfig.me 2>&1')
print(f'  Our WAN IP: {wan_ip}')

# Try to reach ourselves through the WAN IP
for port, svc in [(80, 'HTTP'), (443, 'HTTPS'), (8443, 'gate'), (8080, 'data'), (3000, 'forgejo')]:
    result = erun(f'curl -s -o /dev/null -w "%{{http_code}}" --connect-timeout 3 http://{wan_ip}:{port}/ 2>&1')
    print(f'  WAN:{port} ({svc}): {result} {"← HAIRPIN!" if result == "000" else ""}')

print('\n--- LAYER 3: From eastGate — reach by domain name ---')
for domain in ['primals.eco', 'primal.eco', 'nestgate.io']:
    result = erun(f'curl -s -o /dev/null -w "%{{http_code}}" --connect-timeout 3 http://{domain}/ 2>&1')
    print(f'  http://{domain}/: {result}')
    result_s = erun(f'curl -sk -o /dev/null -w "%{{http_code}}" --connect-timeout 3 https://{domain}/ 2>&1')
    print(f'  https://{domain}/: {result_s}')

print('\n--- LAYER 4: From eastGate — reach localhost (should always work) ---')
for port, svc in [(8443, 'gate'), (8080, 'data'), (3000, 'forgejo'), (11436, 'ollama')]:
    result = erun(f'curl -s -o /dev/null -w "%{{http_code}}" --connect-timeout 2 http://localhost:{port}/ 2>&1')
    print(f'  localhost:{port} ({svc}): {result}')

print('\n--- LAYER 5: From eastGate — reach by LAN IP (should work) ---')
for port, svc in [(8443, 'gate'), (8080, 'data'), (3000, 'forgejo')]:
    result = erun(f'curl -s -o /dev/null -w "%{{http_code}}" --connect-timeout 2 http://192.168.4.244:{port}/ 2>&1')
    print(f'  .244:{port} ({svc}): {result}')

print('\n--- LAYER 6: Router port forwards (what ATT BGW320 routes) ---')
router_fwd = erun('sshpass -p "***" ssh -o StrictHostKeyChecking=no root@192.168.4.1 "uci show firewall 2>&1 | grep -i redirect | head -20" 2>&1')
print(f'  {router_fwd[:600]}')

print('\n--- LAYER 7: ATT BGW320 — the Yellowstone caldera ---')
att_reach = erun('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://192.168.1.254/ 2>&1')
print(f'  BGW320 web UI: HTTP {att_reach}')
# What does the BGW320 think our public IP is?
print(f'  BGW320 is at: 192.168.1.254 (above our router)')
print(f'  Router WAN interface: {erun("sshpass -p *** ssh -o StrictHostKeyChecking=no root@192.168.4.1 ip addr show eth1 2>&1 | grep inet | head -1")}')

# === 3. Cross-gate hairpin test ===
print('\n--- LAYER 8: Cross-gate hairpin test ---')
# From southGate — try to reach WAN IP
south_test = erun(f'sshpass -p southgate ssh -o StrictHostKeyChecking=no southgate@192.168.4.148 "curl -s -o /dev/null -w %{{http_code}} --connect-timeout 3 http://{wan_ip}:8080/ 2>&1" 2>&1', 15)
print(f'  southGate → WAN:8080: {south_test} {"← HAIRPIN FAIL" if "000" in str(south_test) else ""}')

# From ironGate
iron_test = erun(f'ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "curl -s -o /dev/null -w %{{http_code}} --connect-timeout 3 http://{wan_ip}:8080/ 2>&1" 2>&1', 15)
print(f'  ironGate → WAN:8080: {iron_test} {"← HAIRPIN FAIL" if "000" in str(iron_test) else ""}')

# === 4. dromedary current state ===
print('\n--- DROMEDARY (the inner solve) ---')
drom = erun('which dromedary 2>/dev/null || find /opt /home/eastgate -maxdepth 4 -name dromedary -type f 2>/dev/null')
print(f'  Binary: {drom}')
drom_svc = erun('systemctl is-active dromedary 2>/dev/null')
print(f'  Service: {drom_svc}')
drom_conf = erun('find /etc /opt /home/eastgate -maxdepth 4 -name "dromedary*" -name "*.toml" -o -name "dromedary*" -name "*.conf" 2>/dev/null')
print(f'  Config: {drom_conf}')
drom_port = erun('ss -tlnp 2>/dev/null | grep -E ":443|:80 " | head -5')
print(f'  Ports 80/443: {drom_port if drom_port else "(not listening)"}')

# === 5. What dromedary WOULD fix ===
print('''
╔══════════════════════════════════════════════════╗
║  WHAT WE WILL SEE AFTER WIRING DROMEDARY        ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  BEFORE (broken):                                ║
║    gate(.4.x) → primals.eco → WAN → BGW320      ║
║    → DROPPED (no hairpin)                        ║
║                                                  ║
║  AFTER (dromedary on eastGate):                  ║
║    gate(.4.x) → DNS → 192.168.4.244:443         ║
║    → dromedary → localhost:8443                  ║
║    → WORKS (never leaves LAN)                    ║
║                                                  ║
║  The solve: dromedary IS the inner caldera.      ║
║  Traffic stays local. The hot spring cools.      ║
║  The WAN path is for OUTSIDE visitors only.      ║
╚══════════════════════════════════════════════════╝
''')

east.close()

print('='*60)
print('  YELLOWSTONE SURVEY COMPLETE')
print('  We see the layers. Now we explore.')
print('='*60)
