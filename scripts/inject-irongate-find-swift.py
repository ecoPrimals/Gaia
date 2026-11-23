import paramiko

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

# === IRONGATE — FRIEND ENTERED ===
print('='*60)
print('  IRONGATE (.237) — DEEP PROBE')
print('='*60)

ig = ssh('192.168.4.237', 'irongate', 'irongate')

print(f'Hostname: {run(ig, "hostname")}')
print(f'Uptime: {run(ig, "uptime")}')
print(f'CPU: {run(ig, "lscpu | grep \"Model name\"")}')
print(f'RAM: {run(ig, "free -h | grep Mem")}')
print(f'Disk: {run(ig, "df -h / | tail -1")}')
print(f'GPU: {run(ig, "nvidia-smi --query-gpu=name,memory.total,temperature.gpu,power.draw --format=csv,noheader")}')
print(f'Board: {run(ig, "cat /sys/class/dmi/id/board_name 2>/dev/null")}')
print(f'Case: {run(ig, "cat /sys/class/dmi/id/product_name 2>/dev/null")}')
print(f'Net: {run(ig, "ip addr | grep \"inet \" | grep -v 127")}')
print(f'OS: {run(ig, "lsb_release -d 2>/dev/null; cat /etc/os-release 2>/dev/null | head -2")}')

# USB — is Pixel tethered here?
print(f'\nUSB tether: {run(ig, "ip link | grep usb")}')
print(f'USB devices: {run(ig, "lsusb | head -10")}')
print(f'Pixel USB: {run(ig, "lsusb | grep -iE \"google|pixel|android\"")}')

# Ollama
print(f'\nOllama: {run(ig, "which ollama 2>/dev/null && ollama list 2>/dev/null | head -10 || echo no-ollama", 10)}')

# RustDesk
print(f'\nRustDesk: {run(ig, "systemctl is-active rustdesk 2>/dev/null; ls /usr/bin/rustdesk 2>/dev/null; cat /etc/rustdesk/RustDesk.toml 2>/dev/null | head -5")}')

# Docker
print(f'\nDocker: {run(ig, "docker ps 2>/dev/null | head -5 || echo no-docker")}')

# biomeOS
print(f'\nbiomeOS: {run(ig, "ls /opt/Gaia/bin/biomeOS 2>/dev/null; ls /usr/local/bin/biome* 2>/dev/null; which biomeOS 2>/dev/null")}')

# Disks
print(f'\nAll disks: {run(ig, "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | head -20")}')

# Services
print(f'\nKey services: {run(ig, "systemctl list-units --type=service --state=running | grep -iE \"rust|ollama|gaia|steam|biome|docker|ssh\" 2>/dev/null")}')

ig.close()

# === NOW: WHERE IS SWIFTGATE??? ===
print('\n' + '='*60)
print('  WHERE IS SWIFTGATE?')
print('='*60)

# swiftGate was "WiFi-only at 641 Samantha, NZXT H1 V2, RTX 3070"
# Kevin says Pixel is USB-C tethered to it
# But it's not showing in DHCP leases
# Check if router has a br-guest for LAN 2

east = ssh('192.168.4.244', 'eastgate', 'eastgate')

# Router guest network
print('\nRouter guest/LAN2 config:')
# SSH to router from eastGate
router_cmd = (
    'sshpass -p "***" ssh -o StrictHostKeyChecking=no root@192.168.4.1 '
    '"ip addr show br-guest 2>/dev/null; '
    'cat /etc/config/dhcp 2>/dev/null | grep -A5 guest; '
    'cat /tmp/dhcp.leases* 2>/dev/null; '
    'iwinfo 2>/dev/null | grep -A2 ESSID" 2>&1'
)
print(run(east, router_cmd, 10)[:600])

# Check southGate if it can see LAN 2
print('\n\nSouthGate LAN2 visibility:')
sg = ssh('192.168.4.148', 'southgate', 'southgate')
print(f'WiFi: {run(sg, "iwconfig 2>/dev/null | head -5")}')
print(f'All IPs: {run(sg, "ip addr | grep \"inet \" | grep -v 127")}')
# Can southGate see 192.168.9.x?
print(f'LAN2 ping: {run(sg, "ping -c1 -W1 192.168.9.1 2>/dev/null && echo 9.1-ALIVE || echo 9.1-DOWN", 3)}')
sg.close()

east.close()
print('\nDone!')
