import paramiko

# SSH directly to router
router = paramiko.SSHClient()
router.set_missing_host_key_policy(paramiko.AutoAddPolicy())
router.connect('192.168.4.1', username='root', password='***', timeout=5, allow_agent=False, look_for_keys=False)

def run(cmd, t=8):
    _, out, _ = router.exec_command(cmd, timeout=t)
    try:
        return out.read().decode().strip()
    except:
        return '(timeout)'

print('='*60)
print('  GL-MT6000 ROUTER — FULL WIFI & NETWORK STATE')
print('='*60)

# All interfaces
print('\nInterfaces:')
print(run('ip addr show | grep -E "^[0-9]|inet "'))

# Bridge config
print('\nBridges:')
print(run('brctl show 2>/dev/null || ip link show type bridge'))

# WiFi SSIDs and clients
print('\nWiFi SSIDs:')
print(run('iwinfo 2>/dev/null | grep -E "ESSID|Mode|Channel"'))

# All WiFi associated clients
print('\nAll WiFi clients:')
print(run('for iface in $(iwinfo 2>/dev/null | grep ESSID | cut -f1); do echo "=== $iface ==="; iwinfo $iface assoclist 2>/dev/null | head -5; done'))

# Is br-guest active?
print('\nbr-guest status:')
print(run('ip link show br-guest 2>/dev/null || echo "br-guest NOT FOUND"'))

# Guest network config
print('\nGuest/LAN2 config:')
print(run('uci show network.guest 2>/dev/null; uci show network.guest_dev 2>/dev/null'))

# DHCP config for guest
print('\nGuest DHCP:')
print(run('uci show dhcp.guest 2>/dev/null'))

# All DHCP leases
print('\nAll leases:')
print(run('cat /tmp/dhcp.leases'))

# Firewall zones
print('\nFirewall zones:')
print(run('uci show firewall | grep zone | head -20'))

# Check if Guest WiFi exists but is disabled
print('\nWireless config:')
print(run('uci show wireless 2>/dev/null | grep -iE "ssid|disabled|network|mode"'))

# Connected devices
print('\nConnected devices count:')
print(run('cat /proc/net/arp | wc -l'))

# Port forwards
print('\nPort forwards:')
print(run('iptables -t nat -L PREROUTING 2>/dev/null | head -15'))

router.close()
print('\nDone!')
