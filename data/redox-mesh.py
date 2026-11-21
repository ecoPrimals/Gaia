#!/usr/bin/env python3
"""REDOX MESH — cross-reference HARDWARE.md with ARP to ID every gate"""
import subprocess, socket, struct

# === ARP TABLE (from scan) ===
ARP = {
    '192.168.4.1':   ('94-83-c4-e0-63-5a', 'Router GL-MT6000'),
    '192.168.4.2':   ('04-f4-1c-e6-7c-e8', 'MikroTik CRS310'),
    '192.168.4.138': ('90-09-d0-75-2a-1e', '?'),
    '192.168.4.147': ('BC-FC-E7-EA-D9-34', 'northGate (US)'),
    '192.168.4.183': ('50-0a-52-0b-87-81', '?'),
    '192.168.4.195': ('84-47-09-38-97-54', '?'),
    '192.168.4.215': ('ec-75-0c-4c-98-08', '?'),
    '192.168.4.230': ('1c-1b-0d-67-8f-ca', '?'),
    '192.168.4.244': ('c8-5e-a9-c9-6f-80', 'eastGate WiFi'),
    '192.168.4.248': ('c8-5e-a9-c9-6f-80', 'eastGate 2nd lease'),
}

# === KNOWN MACS from ecosystem docs ===
KNOWN_MACS = {
    '04:f4:1c:e6:7c:e8': 'MikroTik CRS310',
    '84:47:09:38:97:55': 'sporeGate (known NIC)',
    '84:47:09:38:97:54': 'sporeGate (2nd NIC, seq MAC)',
    'ec:75:0c:4c:98:08': 'TP-Link JetStream SX3008F',
    '94:83:c4:e0:62:b0': 'GL-MT6000 (enp5s0)',
    '94:83:c4:e0:63:5a': 'GL-MT6000 (br-lan)',
    '14:13:33:d6:96:09': 'frameGate (Steam Frame)',
    'd4:80:8b:1b:9f:01': 'EPSON ET-2400',
    'c8:5e:a9:c9:6f:80': 'eastGate (WiFi)',
}

# === OUI DATABASE (first 3 bytes → manufacturer) ===
OUI = {
    '90:09:d0': 'Synology Inc.',
    '50:0a:52': '??? (check below)',
    '1c:1b:0d': '??? (check below)',
    'bc:fc:e7': 'Realtek (northGate NIC)',
    '84:47:09': 'Lenovo / GMKtec',
    'ec:75:0c': 'TP-Link',
    '94:83:c4': 'GL-iNet / MediaTek',
    'c8:5e:a9': 'Intel WiFi',
    '14:13:33': 'Valve (Steam)',
    'd4:80:8b': 'Seiko Epson',
    '1c:86:0b': 'Intel Ethernet',
}

# === HARDWARE.MD GATES (OS + expected banner) ===
GATES = {
    'ironGate':       {'os': 'Pop!_OS 22.04', 'ssh': 'OpenSSH_8.9p1 Ubuntu', 'cpu': 'i9-14900K', 'gpu': 'RTX 5070'},
    'blueGate':       {'os': 'Windows', 'ssh': 'OpenSSH_for_Windows', 'cpu': 'TBD', 'gpu': 'None'},
    'westGate':       {'os': '? (was listed with RTX 2070 Super + ZFS)', 'ssh': '?', 'cpu': 'Ryzen 7 5700X or i7-4771', 'gpu': 'RTX 3070 or RTX 2070S'},
    'southGate-tower':{'os': 'Dual boot Win/Linux', 'ssh': '?', 'cpu': 'Ryzen 5800X3D', 'gpu': 'RTX 4060'},
    'strandGate':     {'os': 'Pop!_OS', 'ssh': 'OpenSSH Ubuntu', 'cpu': 'Dual EPYC 7452', 'gpu': 'RTX 3090 + RX 6950 XT'},
    'biomeGate':      {'os': '? (Threadripper)', 'ssh': '?', 'cpu': 'Threadripper 3970X', 'gpu': 'RTX 5060 + Titan V'},
    'kinGate':        {'os': 'Pop!_OS', 'ssh': 'OpenSSH Ubuntu', 'cpu': 'i7-6700K', 'gpu': 'RTX 3070'},
}

print("=" * 70)
print("  REDOX MESH — Gate Identification by MAC + Banner + Hardware")
print("=" * 70)

print("\n--- KNOWN (confirmed) ---")
confirmed = {
    '.1':   'Router (GL-MT6000)',
    '.2':   'MikroTik CRS310',
    '.138': 'Synology NAS (Southgate_Data) — OUI 90:09:d0 = Synology',
    '.147': 'northGate (Polaris, 9950X3D) — WE ARE HERE',
    '.195': 'sporeGate — MAC 84:47:09:38:97:54 is sequential to known 84:47:09:38:97:55',
    '.215': 'TP-Link JetStream SX3008F — MAC ec:75:0c:4c:98:08 exact match',
    '.244': 'eastGate (WiFi) — MAC c8:5e:a9:c9:6f:80',
    '.248': 'eastGate (2nd DHCP lease, same MAC as .244)',
}
for ip, name in confirmed.items():
    print(f"  192.168.4{ip:10s} = {name}")

print("\n--- UNKNOWN (need identification) ---")
unknowns = {
    '.183': {
        'mac': '50:0a:52:0b:87:81',
        'ssh_banner': 'OpenSSH_10.2p1 Ubuntu-2ubuntu3',
        'ports': [22],
        'ttl': 64,
        'notes': 'Linux, SSH only, VERY new Ubuntu (10.2p1 = Ubuntu 25.04+)',
    },
    '.230': {
        'mac': '1c:1b:0d:67:8f:ca',
        'ssh_banner': None,
        'ports': [],
        'ttl': 64,
        'notes': 'Linux TTL, zero ports open. Phone or IoT.',
    },
}

for ip, info in unknowns.items():
    mac = info['mac']
    oui = mac[:8]
    print(f"\n  192.168.4{ip}")
    print(f"    MAC: {mac} (OUI: {oui})")
    print(f"    SSH: {info['ssh_banner']}")
    print(f"    Ports: {info['ports']}")
    print(f"    Notes: {info['notes']}")
    
    # Cross-reference with hardware
    if ip == '.183':
        print(f"\n    ANALYSIS:")
        print(f"    - OpenSSH 10.2p1 = Ubuntu 25.04 or Pop!_OS 25.04")
        print(f"    - ironGate was Pop!_OS 22.04 (SSH 8.9p1) → MISMATCH unless reinstalled")
        print(f"    - Could be: ANY tower Kevin reinstalled with fresh Ubuntu")
        print(f"    - Candidates: ironGate (reinstall?), westGate, southGate-tower,")
        print(f"                  strandGate, biomeGate, kinGate, blueGate (if switched to Linux)")
        print(f"    - ONLY port 22 → fresh install, no services yet")
        
    if ip == '.230':
        print(f"\n    ANALYSIS:")
        print(f"    - Zero ports = phone, IoT, or stealth device")
        print(f"    - OUI 1c:1b:0d — need lookup")
        print(f"    - Kevin mentioned milkyGate (Mint Mobile phone)")
        print(f"    - Also southGate-phone (iPhone XS) could appear portless")
        print(f"    - Candidates: milkyGate, southGate-phone, smart device")

# === Try NetBIOS / mDNS for hostnames ===
print("\n\n--- HOSTNAME DISCOVERY (NetBIOS/mDNS) ---")

for ip in ['192.168.4.183', '192.168.4.230', '192.168.4.138', '192.168.4.195']:
    # Try NetBIOS name query
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        # NetBIOS name query packet
        query = (b'\x80\x94\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                 b'\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00'
                 b'\x00\x21\x00\x01')
        s.sendto(query, (ip, 137))
        data, addr = s.recvfrom(1024)
        if len(data) > 56:
            name = data[57:57+15].decode('ascii', errors='replace').strip()
            print(f"  {ip} NetBIOS: {name}")
        s.close()
    except:
        print(f"  {ip} NetBIOS: no response")

    # Try reverse DNS
    try:
        name = socket.gethostbyaddr(ip)
        print(f"  {ip} rDNS: {name[0]}")
    except:
        pass

# === Try nmap-style service detection on .183 ===
print("\n--- SSH DEEPER PROBE on .183 ---")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(('192.168.4.183', 22))
    banner = s.recv(512)
    print(f"  Full banner: {banner}")
    
    # Send our banner and see what key types are offered
    s.send(b'SSH-2.0-GaiaProbe_1.0\r\n')
    response = s.recv(4096)
    print(f"  Response length: {len(response)} bytes")
    # Parse for host key algorithms (tells us about the OS/config)
    if b'ssh-ed25519' in response:
        print(f"  Has ed25519 key")
    if b'ssh-rsa' in response:
        print(f"  Has RSA key")
    if b'ecdsa' in response:
        print(f"  Has ECDSA key")
    s.close()
except Exception as e:
    print(f"  Error: {e}")

# === Check for mDNS on .230 (common on phones) ===
print("\n--- mDNS PROBE .230 ---")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    # mDNS query for _services._dns-sd._udp.local
    mdns_query = (b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                  b'\x09_services\x07_dns-sd\x04_udp\x05local\x00'
                  b'\x00\x0c\x00\x01')
    s.sendto(mdns_query, ('192.168.4.230', 5353))
    data, addr = s.recvfrom(4096)
    print(f"  mDNS response from {addr}: {len(data)} bytes")
    print(f"  Raw: {data[:100]}")
    s.close()
except Exception as e:
    print(f"  mDNS: {e}")

print("\n" + "=" * 70)
print("  SUMMARY — Kevin, here's what I need from you:")
print("=" * 70)
print("""
  .183 (50:0a:52, Ubuntu 25.x, SSH only) = WHICH GATE?
  .230 (1c:1b:0d, no ports) = milkyGate? southGate? 
  
  When you plug in via ADB, I can reach through eastGate
  to feel more of the mesh from the inside.
  
  Also found: Synology NAS 'Southgate_Data' at .138!
""")
