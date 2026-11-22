#!/usr/bin/env python3
"""Try SSH to candidate IPs that might be ironGate"""
import paramiko, socket

candidates = [
    '192.168.1.229',   # ATT subnet, port 22 open
    '192.168.4.237',   # original IP (timeout but try anyway)
]

users = ['root', 'kevin', 'gaia', 'user', 'irongate', 'pop']
passwords = ['', 'gaia', 'irongate', 'password']

for ip in candidates:
    print(f"\n=== Trying {ip} ===")
    
    # First check if port 22 is even open
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, 22))
        s.close()
        print(f"  Port 22: OPEN")
    except Exception as e:
        print(f"  Port 22: CLOSED ({e})")
        continue
    
    # Get SSH banner
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, 22))
        banner = s.recv(256).decode('utf-8', errors='replace').strip()
        s.close()
        print(f"  Banner: {banner}")
    except Exception as e:
        print(f"  Banner grab failed: {e}")
    
    # Try each user/pass combo
    for user in users:
        for pw in passwords:
            try:
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                c.connect(ip, username=user, password=pw, timeout=5, auth_timeout=5,
                         look_for_keys=False, allow_agent=False)
                _, o, _ = c.exec_command('hostname; uname -a; lscpu | head -5', timeout=5)
                out = o.read().decode().strip()
                print(f"  SUCCESS as {user}/{pw}:")
                print(f"    {out}")
                c.close()
                break
            except paramiko.AuthenticationException:
                pass
            except Exception as e:
                print(f"  {user}/{pw}: {type(e).__name__}: {e}")
                break
        else:
            continue
        break

# Also try key-based auth
print("\n=== Key-based auth attempts ===")
for ip in ['192.168.1.229']:
    for user in ['root', 'kevin', 'gaia']:
        try:
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(ip, username=user, timeout=5, auth_timeout=5)
            _, o, _ = c.exec_command('hostname; uname -a', timeout=5)
            out = o.read().decode().strip()
            print(f"  {ip} as {user} (key): {out}")
            c.close()
        except Exception as e:
            print(f"  {ip} as {user} (key): {type(e).__name__}")

print("\nDone.")
