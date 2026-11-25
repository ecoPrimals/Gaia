import paramiko

def ssh(ip, user, pw, timeout=5):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username=user, password=pw, timeout=timeout, allow_agent=False, look_for_keys=False)
    return c

def run(c, cmd, t=5):
    _, out, err = c.exec_command(cmd, timeout=t)
    return out.read().decode().strip()

# === SOUTHGATE DEEP PROBE ===
print('='*60)
print('  SOUTHGATE (.148) — DEEP PROBE')
print('='*60)

sg = ssh('192.168.4.148', 'southgate', 'southgate')

print(f'\nHostname: {run(sg, "hostname")}')
print(f'Uptime: {run(sg, "uptime")}')
print(f'CPU: {run(sg, "lscpu | grep \"Model name\"")}')
print(f'RAM: {run(sg, "free -h | grep Mem")}')
print(f'Disk: {run(sg, "df -h / | tail -1")}')
print(f'GPU: {run(sg, "nvidia-smi --query-gpu=name,memory.total,temperature.gpu,power.draw --format=csv,noheader")}')
print(f'USB: {run(sg, "lsusb | head -10")}')
print(f'Net: {run(sg, "ip addr | grep \"inet \" | grep -v 127")}')
print(f'MAC: {run(sg, "ip link show enp4s0 | grep ether")}')

# Is Pixel tethered here via USB?
print(f'\nUSB tether: {run(sg, "ip link | grep usb")}')
print(f'USB net: {run(sg, "ip addr show usb0 2>/dev/null || echo no-usb0")}')

# Check for Pixel ADB
print(f'ADB: {run(sg, "which adb 2>/dev/null && adb devices 2>/dev/null || echo no-adb")}')

# Ollama models
print(f'\nOllama: {run(sg, "ollama list 2>/dev/null", 8)}')

# RustDesk config
print(f'\nRustDesk ID: {run(sg, "cat /root/.config/rustdesk/RustDesk.toml 2>/dev/null; cat /home/southgate/.config/rustdesk/RustDesk.toml 2>/dev/null | head -20")}')

# Services
print(f'\nServices: {run(sg, "systemctl list-units --type=service --state=running | grep -iE \"rust|ollama|gaia|steam|biome|docker\" 2>/dev/null")}')

# Physical hardware
print(f'\nCase: {run(sg, "cat /sys/class/dmi/id/product_name 2>/dev/null")}')
print(f'Chassis: {run(sg, "cat /sys/class/dmi/id/chassis_type 2>/dev/null")}')
print(f'Board: {run(sg, "cat /sys/class/dmi/id/board_name 2>/dev/null")}')

# Displays
print(f'\nDisplays: {run(sg, "xrandr --listmonitors 2>/dev/null || echo no-xrandr")}')
print(f'DRM: {run(sg, "ls -la /dev/dri/ 2>/dev/null")}')

# Check if Pixel is USB tethered HERE
print(f'\nUSB devices detailed: {run(sg, "lsusb -v 2>/dev/null | grep -iE \"google|pixel|android|rndis\" || echo none-found")}')

sg.close()

# === NOW FIND SWIFTGATE ===
print('\n' + '='*60)
print('  FINDING SWIFTGATE')
print('='*60)

# swiftGate should be at House 2
# If Pixel is USB-tethered to it, it might get internet from Pixel
# swiftGate was WiFi-only on Gaia WiFi (192.168.9.x)
# Check from eastGate if anything new on 192.168.9.x

east = ssh('192.168.4.244', 'eastgate', 'eastgate')

# Check router DHCP leases for swiftGate
print('\nRouter DHCP scan (via eastGate):')
result = run(east, 'curl -s http://192.168.4.1/cgi-bin/luci 2>/dev/null | head -5 || echo "router-ui not reachable"', 5)
print(f'  Router UI: {result[:100]}')

# Check for any device named swift
result = run(east, 'getent hosts swiftgate 2>/dev/null; avahi-resolve -n swiftgate.local 2>/dev/null; echo "---"; nslookup swiftgate.primals.local 192.168.4.1 2>/dev/null | tail -3', 5)
print(f'  DNS: {result[:200]}')

# Scan .9.x from eastGate (it can reach both subnets)  
# Quick check common IPs
print('\nLAN 2 scan:')
for ip in ['192.168.9.100', '192.168.9.150', '192.168.9.200', '192.168.9.210', '192.168.9.217', '192.168.9.203']:
    r = run(east, f'ping -c1 -W1 {ip} 2>/dev/null | grep -c "bytes from"', 3)
    if r == '1':
        print(f'  ALIVE: {ip}')
        # Try SSH
        r2 = run(east, f'sshpass -p "swiftgate" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 swiftgate@{ip} "hostname" 2>&1', 5)
        print(f'    SSH: {r2[:80]}')

# Check if .160, .212 might be swiftGate (appeared in ARP)
print('\nNew ARP entries:')
for ip in ['192.168.4.160', '192.168.4.212']:
    r = run(east, f'ping -c1 -W1 {ip} 2>/dev/null && echo ALIVE || echo DOWN', 3)
    print(f'  {ip}: {r}')

east.close()
print('\nDone!')
