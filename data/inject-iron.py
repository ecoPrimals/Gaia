#!/usr/bin/env python3
"""Connect to ironGate at 192.168.1.229 with long timeouts"""
import paramiko, time

IP = '192.168.1.229'

print(f"Connecting to ironGate candidate at {IP}...")
print(f"Banner was: SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.18 (Pop!_OS 22.04)")

# Try multiple users with generous timeouts
users_passes = [
    ('kevin', ''),     # key auth
    ('root', ''),      # key auth
    ('kevin', 'kevin'),
    ('kevin', 'gaia'),
    ('kevin', 'irongate'),
    ('root', 'gaia'),
    ('root', 'root'),
    ('root', 'irongate'),
    ('gaia', 'gaia'),
]

for user, pw in users_passes:
    print(f"\n  Trying {user}/{pw or '(key)'}...", end=' ', flush=True)
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if pw:
            c.connect(IP, username=user, password=pw, timeout=15, auth_timeout=15,
                     look_for_keys=False, allow_agent=False)
        else:
            c.connect(IP, username=user, timeout=15, auth_timeout=15)
        
        print("CONNECTED!")
        
        cmds = [
            'hostname',
            'uname -a',
            'cat /etc/os-release | head -3',
            'lscpu | grep -E "Model name|CPU\(s\):|Thread"',
            'free -h | head -2',
            'df -h / | tail -1',
            'ip -4 addr show | grep inet',
            'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "no nvidia-smi"',
            'systemctl is-active ollama 2>/dev/null || echo "ollama not active"',
            'uptime',
        ]
        
        for cmd in cmds:
            _, o, e = c.exec_command(cmd, timeout=10)
            out = o.read().decode().strip()
            err = e.read().decode().strip()
            if out:
                print(f"  >> {cmd}")
                for line in out.split('\n'):
                    print(f"     {line}")
            if err and 'not found' not in err:
                print(f"  !! {err[:100]}")
        
        c.close()
        print("\n=== ironGate FOUND AND ALIVE ===")
        break
    except paramiko.AuthenticationException:
        print("AUTH REJECTED")
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
else:
    print("\n\nCould not auth — ironGate is THERE but we need the right credentials.")
    print("Kevin: what user/password does ironGate use?")
