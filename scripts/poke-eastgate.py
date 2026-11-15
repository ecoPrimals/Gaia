import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)
print('SSH CONNECTED to eastGate!')

pokes = [
    ('services', 'systemctl list-units --type=service --state=running | grep -iE "gaia|ollama|rustdesk|gdm|tor|forgejo" | head -15'),
    ('ollama-count', 'curl -s http://localhost:11436/api/tags 2>/dev/null | grep -c \'"name"\''),
    ('gate-8443', 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8443/pulse'),
    ('data-8080', 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/'),
    ('forgejo-3000', 'curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/'),
    ('tor', 'systemctl is-active tor'),
    ('crons', 'crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l'),
    ('gpu', 'nvidia-smi --query-gpu=name,temperature.gpu,power.draw,utilization.gpu,memory.used --format=csv,noheader'),
    ('disk', 'df -h / | tail -1'),
    ('uptime', 'uptime'),
    ('connections', 'ss -tn state established | grep -v "127.0.0" | wc -l'),
    ('rustdesk', 'ss -tn | grep 21118'),
    ('network', 'ip -br addr show | grep -v lo | grep -v "DOWN"'),
    ('usb', 'lsusb 2>/dev/null | head -10'),
    ('display', 'DISPLAY=:0 xrandr --current 2>/dev/null | head -3'),
    ('biomeOS', 'systemctl is-active biomeOS 2>/dev/null || echo "not found"'),
    ('mushrooms', 'ls /opt/Gaia/mushrooms/ 2>/dev/null | wc -l'),
    ('git-status', 'cd /opt/Gaia && git log --oneline -3 2>/dev/null'),
]

for label, cmd in pokes:
    _, out, err = c.exec_command(cmd, timeout=8)
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    result = o if o else (e if e else '(empty)')
    # Truncate long output
    if len(result) > 200:
        result = result[:200] + '...'
    print(f'  {label:20s}: {result}')

c.close()
print('\neastGate FULLY POKED!')
