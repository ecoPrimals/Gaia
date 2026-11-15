import paramiko
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)
    print('SSH CONNECTED!')

    commands = [
        ('gdm3', 'systemctl status gdm3 2>&1 | head -15'),
        ('display-mgr', 'systemctl status display-manager 2>&1 | head -10'),
        ('sessions', 'loginctl list-sessions 2>&1'),
        ('x11-sockets', 'ls -la /tmp/.X11-unix/ 2>&1'),
        ('xdg-type', 'echo XDG=$XDG_SESSION_TYPE DISPLAY=$DISPLAY WAYLAND=$WAYLAND_DISPLAY'),
        ('default-dm', 'cat /etc/X11/default-display-manager 2>&1'),
        ('rustdesk-svc', 'systemctl is-active rustdesk 2>&1'),
        ('display-procs', 'ps aux | grep -E "Xorg|Xwayland|gdm|lightdm|rustdesk|wayland" | grep -v grep'),
        ('gpu', 'nvidia-smi --query-gpu=name,temperature.gpu,power.draw,display_active --format=csv,noheader 2>&1'),
        ('xrandr', 'DISPLAY=:0 xrandr 2>&1 | head -15'),
        ('xrandr1', 'DISPLAY=:1 xrandr 2>&1 | head -10'),
        ('drm', 'cat /sys/class/drm/card*/status 2>&1'),
        ('drm-modes', 'cat /sys/class/drm/card*-*/modes 2>&1 | head -10'),
        ('hdmi-state', 'cat /sys/class/drm/card*-HDMI*/status 2>&1'),
        ('dp-state', 'cat /sys/class/drm/card*-DP*/status 2>&1'),
    ]

    for label, cmd in commands:
        print(f'\n=== {label} ===')
        stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out:
            print(out)
        if err and not out:
            print(f'  (err: {err})')

    client.close()
    print('\n=== DONE ===')

except Exception as e:
    print(f'SSH FAILED: {e}')
