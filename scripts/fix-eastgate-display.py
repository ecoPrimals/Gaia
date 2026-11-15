import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)
print('SSH CONNECTED!')

# Fix GDM config: change AutomaticLogin=root to AutomaticLogin=eastgate
print('\n=== Fixing GDM config ===')
cmd = "echo eastgate | sudo -S sed -i 's/AutomaticLogin=root/AutomaticLogin=eastgate/' /etc/gdm3/custom.conf 2>&1"
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(stdout.read().decode().strip())
print(stderr.read().decode().strip())

# Verify
print('\n=== Verify ===')
stdin, stdout, stderr = client.exec_command('cat /etc/gdm3/custom.conf', timeout=5)
print(stdout.read().decode().strip())

# Restart GDM
print('\n=== Restarting GDM ===')
stdin, stdout, stderr = client.exec_command('echo eastgate | sudo -S systemctl restart gdm3 2>&1', timeout=15)
print(stdout.read().decode().strip())
print(stderr.read().decode().strip())

print('Waiting 8 seconds for Xorg to start...')
time.sleep(8)

# Check X11 sockets
print('\n=== X11 Sockets ===')
stdin, stdout, stderr = client.exec_command('ls -la /tmp/.X11-unix/ 2>&1', timeout=5)
print(stdout.read().decode().strip())

# Check display processes
print('\n=== Display Processes ===')
stdin, stdout, stderr = client.exec_command('ps aux | grep -E "Xorg|Xwayland|gnome-shell|mutter" | grep -v grep', timeout=5)
out = stdout.read().decode().strip()
print(out if out else '(none running)')

# Check sessions
print('\n=== Sessions ===')
stdin, stdout, stderr = client.exec_command('loginctl list-sessions 2>&1', timeout=5)
print(stdout.read().decode().strip())

# Check xrandr
print('\n=== xrandr :0 ===')
stdin, stdout, stderr = client.exec_command('DISPLAY=:0 xrandr 2>&1 | head -10', timeout=5)
print(stdout.read().decode().strip())

# Check RustDesk
print('\n=== RustDesk ===')
stdin, stdout, stderr = client.exec_command('systemctl status rustdesk 2>&1 | head -10', timeout=5)
print(stdout.read().decode().strip())

client.close()
print('\n=== FACE INJECTION COMPLETE ===')
