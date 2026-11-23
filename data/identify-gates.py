#!/usr/bin/env python3
"""Identify all NEW gates on the mesh"""
import paramiko, socket, urllib.request, ssl

NEW_GATES = {
    '192.168.4.138': 'ports 80,443 — web only',
    '192.168.4.183': 'port 22 — OpenSSH_10.2p1 Ubuntu',
    '192.168.4.215': 'ports 22,80,443 — Linux',
    '192.168.4.230': 'no ports — phone/IoT?',
    '192.168.4.248': 'SAME as eastGate — second NIC?',
    '192.168.8.246': 'SAME as northGate — second NIC?',
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("=" * 60)
print("  IDENTIFYING NEW GATES")
print("=" * 60)

for ip, desc in NEW_GATES.items():
    print(f"\n{'─' * 60}")
    print(f"  {ip} — {desc}")
    print(f"{'─' * 60}")
    
    # Try HTTP
    for port in [80, 443, 8080, 8443]:
        try:
            if port in [443, 8443]:
                r = urllib.request.urlopen(f'https://{ip}:{port}/', timeout=3, context=ctx)
            else:
                r = urllib.request.urlopen(f'http://{ip}:{port}/', timeout=3)
            server = r.headers.get('Server', '?')
            body = r.read(500).decode('utf-8', errors='replace')[:200]
            print(f"  HTTP {port}: {r.status} Server={server}")
            print(f"    {body[:150]}")
        except urllib.error.HTTPError as e:
            print(f"  HTTP {port}: {e.code} Server={e.headers.get('Server','?')}")
        except Exception as e:
            pass
    
    # Try SSH with various creds
    if ip in ['192.168.4.183', '192.168.4.215', '192.168.4.248', '192.168.8.246']:
        users = ['root', 'kevin', 'gaia', 'user']
        for user in users:
            try:
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                c.connect(ip, username=user, timeout=5, auth_timeout=8)
                _, o, _ = c.exec_command('hostname; uname -a; cat /etc/hostname 2>/dev/null', timeout=5)
                out = o.read().decode().strip()
                print(f"  SSH as {user}: {out}")
                
                # Get more info
                cmds = [
                    ('OS', 'cat /etc/os-release 2>/dev/null | head -3'),
                    ('CPU', 'lscpu 2>/dev/null | grep "Model name" || sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "?"'),
                    ('GPU', 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "no GPU driver"'),
                    ('RAM', 'free -h 2>/dev/null | head -2 || sysctl -n hw.memsize 2>/dev/null || echo "?"'),
                    ('IPs', 'ip -4 addr show 2>/dev/null | grep "inet " || ifconfig 2>/dev/null | grep "inet "'),
                    ('Ollama', 'ollama list 2>/dev/null | head -5 || echo "no ollama"'),
                    ('Uptime', 'uptime'),
                ]
                for label, cmd in cmds:
                    _, o2, _ = c.exec_command(cmd, timeout=5)
                    out2 = o2.read().decode().strip()
                    if out2:
                        print(f"  {label}: {out2}")
                c.close()
                break
            except paramiko.AuthenticationException:
                print(f"  SSH {user}: auth rejected")
            except Exception as e:
                print(f"  SSH {user}: {type(e).__name__}")

    # Try to identify phones by checking common phone ports  
    if ip in ['192.168.4.138', '192.168.4.230']:
        for p in [5353, 62078, 49152, 7000, 7100]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, p))
                s.close()
                print(f"  Port {p}: OPEN (phone marker)")
            except:
                pass

print(f"\n{'=' * 60}")
print("  IDENTIFICATION COMPLETE")
print(f"{'=' * 60}")
