import paramiko

def ssh(ip, user, pw, timeout=5):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username=user, password=pw, timeout=timeout, allow_agent=False, look_for_keys=False)
    return c

def run(c, cmd, t=8):
    _, out, err = c.exec_command(cmd, timeout=t)
    return out.read().decode().strip()

# === CHECK ROUTER DHCP LEASES ===
print('=== ROUTER (GL-MT6000) DHCP LEASES ===')
try:
    router = ssh('192.168.4.1', 'root', 'ExoticPanda714!!', timeout=5)
    
    # DHCP leases file
    print('\nDHCP leases (LAN 1):')
    leases = run(router, 'cat /tmp/dhcp.leases 2>/dev/null')
    print(leases if leases else '(empty)')
    
    # Guest/LAN 2 leases
    print('\nDHCP leases (LAN 2 / Guest):')
    leases2 = run(router, 'cat /tmp/dhcp.leases.guest 2>/dev/null; cat /var/dhcpd/var/db/dhcpd.leases 2>/dev/null | head -30')
    print(leases2 if leases2 else '(checking dnsmasq...)')
    
    # dnsmasq leases (OpenWrt style)
    print('\nAll dnsmasq leases:')
    dm = run(router, 'cat /tmp/dhcp.leases* 2>/dev/null; ls /tmp/dhcp* 2>/dev/null')
    print(dm if dm else '(no dnsmasq leases)')
    
    # ARP from router
    print('\nRouter ARP (sees ALL devices):')
    arp = run(router, 'cat /proc/net/arp')
    print(arp)
    
    # Interfaces  
    print('\nRouter interfaces:')
    ifaces = run(router, 'ip addr | grep "inet " | grep -v 127')
    print(ifaces)
    
    # Find anything named swift
    print('\nHostname lookups:')
    dns = run(router, 'grep -i swift /tmp/dhcp.leases 2>/dev/null; grep -i swift /etc/hosts 2>/dev/null; grep -i swift /tmp/hosts/* 2>/dev/null', 3)
    print(dns if dns else '(none)')
    
    # All connected WiFi clients
    print('\nWiFi clients:')
    wifi = run(router, 'iwinfo | head -5; for iface in $(iwinfo | grep ESSID | cut -d\" \" -f1); do echo "--- $iface ---"; iwinfo $iface assoclist 2>/dev/null; done', 8)
    print(wifi[:500])
    
    router.close()
except Exception as e:
    print(f'Router connection failed: {e}')

# === CHECK EASTGATE WiFi ===
print('\n=== EASTGATE WiFi SCAN ===')
east = ssh('192.168.4.244', 'eastgate', 'eastgate')

# eastGate WiFi interface
print('\neastGate WiFi:')
print(run(east, 'iwconfig 2>/dev/null | head -10'))
print(run(east, 'ip addr show wlp0s20f3 2>/dev/null | grep inet'))

# Scan for devices on WiFi subnet
print('\neastGate WiFi ARP:')
print(run(east, 'arp -a | grep -v enp5s0'))

# Can eastGate ping 192.168.9.x?
print('\nCross-subnet check:')
print(run(east, 'ping -c1 -W1 192.168.9.1 2>/dev/null && echo "9.1 ALIVE" || echo "9.1 DOWN"', 3))
print(run(east, 'ping -c1 -W1 192.168.9.217 2>/dev/null && echo "9.217 ALIVE (Pixel)" || echo "9.217 DOWN"', 3))

# Check .160 and .212 identity
print('\n=== UNKNOWN DEVICES ===')
for ip in ['192.168.4.160', '192.168.4.212']:
    r = run(east, f'ping -c1 -W1 {ip} 2>/dev/null && echo ALIVE || echo DOWN', 3)
    print(f'{ip}: {r}')

east.close()
print('\nDone!')
