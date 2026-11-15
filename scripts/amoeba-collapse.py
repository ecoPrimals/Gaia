"""
AMOEBA COLLAPSE — Map all RustDesk peers, identify unknowns,
plan the collapse into biomeOS identity.
"""
import paramiko, subprocess, json, os

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def erun(cmd, t=10):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print('='*60)
print('  AMOEBA COLLAPSE — map all peers, plan the melt')
print('='*60)

# 1. eastGate RustDesk config — find peer list
print('\n--- eastGate RustDesk config ---')
print(erun('find / -maxdepth 4 -name "*.toml" -path "*rustdesk*" 2>/dev/null'))
print(erun('find / -maxdepth 4 -name "*.conf" -path "*rustdesk*" 2>/dev/null'))
print(erun('find /home/eastgate -name "RustDesk*" -o -name "rustdesk*" 2>/dev/null | head -10'))
print(erun('cat /root/.config/rustdesk/RustDesk.toml 2>/dev/null || cat /home/eastgate/.config/rustdesk/RustDesk.toml 2>/dev/null || echo "config not found"'))
print(erun('cat /root/.config/rustdesk/RustDesk2.toml 2>/dev/null || cat /home/eastgate/.config/rustdesk/RustDesk2.toml 2>/dev/null || echo "config2 not found"'))

# 2. Known RustDesk IDs from screenshot
print('\n--- KNOWN RUSTDESK PEERS ---')
peers = {
    'eastgate@eastgate': '192.168.4.244',
    'sporegate@sporegate': '1871544996',
    'eastgate@eastgate (2)': '19091278',
    'gaia@strandgate': '4513640',
    'gaia@biomegate': '430412195',
    'gaia@westgate': '373150567',
    'mokke@bluegate': '341465360',
    'gaia@kingate': '224890826',
    'gaia@southgate': '1923870067',
    'mokke@tamison (northGate)': '132831540',
}
for name, rid in peers.items():
    print(f'  {name}: {rid}')

# 3. Can we resolve RustDesk IDs to IPs?
print('\n--- eastGate DHCP/ARP table ---')
print(erun('cat /proc/net/arp 2>&1'))

# 4. Router DHCP leases for unknown gates
print('\n--- Router DHCP leases ---')
router_leases = erun('sshpass -p "ExoticPanda714!!" ssh -o StrictHostKeyChecking=no root@192.168.4.1 "cat /tmp/dhcp.leases 2>&1" 2>&1')
print(router_leases)

# 5. Find peer config on eastGate
print('\n--- eastGate RustDesk peer DB ---')
print(erun('find / -maxdepth 5 -name "peers" -path "*rustdesk*" 2>/dev/null'))
print(erun('ls /root/.config/rustdesk/peers/ 2>/dev/null || echo "no peers dir"'))
print(erun('ls /home/eastgate/.config/rustdesk/peers/ 2>/dev/null || echo "no peers dir"'))

east.close()

# 6. Local (northGate) RustDesk config
print('\n--- northGate RustDesk config ---')
rd_paths = [
    os.path.expanduser('~\\AppData\\Roaming\\RustDesk\\config\\'),
    'C:\\ProgramData\\RustDesk\\config\\',
    os.path.expanduser('~\\.config\\rustdesk\\'),
]
for p in rd_paths:
    if os.path.isdir(p):
        print(f'Found: {p}')
        for f in os.listdir(p):
            print(f'  {f}')
            if f.endswith('.toml'):
                fp = os.path.join(p, f)
                try:
                    with open(fp) as fh:
                        content = fh.read()
                    if len(content) < 2000:
                        print(content[:500])
                except:
                    pass

# Check peers directory
peer_paths = [
    os.path.expanduser('~\\AppData\\Roaming\\RustDesk\\config\\peers\\'),
    'C:\\ProgramData\\RustDesk\\config\\peers\\',
]
for p in peer_paths:
    if os.path.isdir(p):
        print(f'\nPeers at {p}:')
        for f in sorted(os.listdir(p)):
            print(f'  {f}')

print('\n' + '='*60)
print('  COLLAPSE MAP COMPLETE')
print('='*60)
