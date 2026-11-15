import paramiko

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)
print('Connected to eastGate (bridge)\n')

gates = [
    ('sporeGate', '192.168.4.3'),
    ('ironGate', '192.168.4.237'),
]

for name, ip in gates:
    print(f'=== {name} ({ip}) via eastGate hop ===')
    
    # Try SSH key auth (eastGate may have keys to other gates)
    cmds = [
        ('banner', f'echo "" | timeout 2 nc {ip} 22 2>/dev/null | head -1'),
        ('key-ssh', f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@{ip} "hostname; uname -m; uptime" 2>&1'),
        ('rustdesk', f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@{ip} "which rustdesk 2>/dev/null; rustdesk --get-id 2>/dev/null" 2>&1'),
        ('ollama', f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes root@{ip} "curl -s http://localhost:11434/api/tags 2>/dev/null | grep -c name" 2>&1'),
        ('http-8443', f'curl -s -o /dev/null -w "%{{http_code}}" http://{ip}:8443/pulse 2>/dev/null'),
        ('http-8080', f'curl -s -o /dev/null -w "%{{http_code}}" http://{ip}:8080/ 2>/dev/null'),
        ('http-9800', f'curl -s -o /dev/null -w "%{{http_code}}" http://{ip}:9800/ 2>/dev/null'),
    ]
    
    for label, cmd in cmds:
        _, out, err = east.exec_command(cmd, timeout=8)
        o = out.read().decode().strip()
        e = err.read().decode().strip()
        result = o if o else e
        if len(result) > 120:
            result = result[:120] + '...'
        print(f'  {label:12s}: {result}')
    print()

east.close()
print('Hop injection complete!')
