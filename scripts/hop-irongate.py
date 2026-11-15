import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def hop(cmd, t=10):
    """Run command on ironGate via eastGate SSH hop"""
    full = f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 irongate@192.168.4.237 "{cmd}" 2>&1'
    _, out, _ = east.exec_command(full, timeout=t)
    try:
        return out.read().decode().strip()
    except:
        return '(timeout)'

print('='*60)
print('  IRONGATE VIA EASTGATE HOP')
print('='*60)

print(f'Hostname: {hop("hostname")}')
print(f'Uptime: {hop("uptime")}')
print(f'CPU: {hop("lscpu | grep Model\\ name")}')
print(f'RAM: {hop("free -h | grep Mem")}')
print(f'Disk: {hop("df -h / | tail -1")}')
print(f'GPU: {hop("nvidia-smi --query-gpu=name,memory.total,temperature.gpu,power.draw --format=csv,noheader")}')
print(f'Board: {hop("cat /sys/class/dmi/id/board_name")}')
print(f'Case: {hop("cat /sys/class/dmi/id/product_name")}')
print(f'OS: {hop("cat /etc/os-release | head -3")}')
print(f'Kernel: {hop("uname -r")}')

# Network
print(f'\nNet: {hop("ip addr | grep inet\\ | grep -v 127")}')

# USB — PIXEL TETHERED?
print(f'\nUSB tether: {hop("ip link | grep -i usb")}')
print(f'USB devices: {hop("lsusb")}')
print(f'Pixel USB: {hop("lsusb | grep -iE google\\ pixel\\ android")}')

# Ollama
print(f'\nOllama: {hop("which ollama && ollama list | head -10", 15)}')

# RustDesk  
print(f'\nRustDesk: {hop("systemctl is-active rustdesk; which rustdesk")}')
rd_conf = hop("cat /etc/rustdesk/RustDesk.toml 2>/dev/null; cat /root/.config/rustdesk/RustDesk.toml 2>/dev/null; cat /home/irongate/.config/rustdesk/RustDesk.toml 2>/dev/null | head -15")
print(f'RustDesk config: {rd_conf[:200]}')

# Docker
print(f'\nDocker: {hop("docker ps 2>/dev/null | head -5")}')

# All disks
print(f'\nDisks: {hop("lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | head -20")}')

# Services
print(f'\nServices: {hop("systemctl list-units --type=service --state=running | grep -iE rust\\ ollama\\ gaia\\ steam\\ biome\\ docker\\ ssh")}')

# biomeOS
print(f'\nbiomeOS: {hop("ls /opt/Gaia/ 2>/dev/null | head -10; ls /usr/local/bin/biome* 2>/dev/null")}')

# === FIND SWIFTGATE FROM IRONGATE ===
# Maybe ironGate at House 2 can see swiftGate?
print(f'\n{"="*60}')
print(f'  IRONGATE → SWIFTGATE SEARCH')
print(f'{"="*60}')
print(f'WiFi: {hop("iwconfig 2>/dev/null | head -8")}')
print(f'ARP: {hop("arp -a | grep -v incomplete")}')
print(f'Route: {hop("ip route | head -5")}')

east.close()
print('\nDone!')
