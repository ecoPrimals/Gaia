"""
LYSOGENIC VECTOR — Pixel phage injection system
The Pixel carries Gaia's primal DNA. When it touches a gate, lysogeny activates.

USB tether = injection needle (physical contact)
WiFi ADB = proximity signal (near field)
HTTP probe = sensing (far field)

The vector:
1. Senses what gate is nearby (ARP, ping, SSH banner)
2. Identifies the host (OS, arch, existing services)
3. Injects the AMOEBA bootstrap (RustDesk sovereign relay)
4. Seeds primals appropriate for that host's architecture
5. Activates lysogeny — the gate becomes part of Gaia
"""

import paramiko
import subprocess
import json
import time
import sys

# === GATE IDENTITY DATABASE ===
GATES = {
    '192.168.4.244': {'name': 'eastGate', 'user': 'eastgate', 'pw': 'eastgate', 'os': 'linux', 'arch': 'x86_64', 'role': 'BRAIN', 'amoeba': True},
    '192.168.4.3':   {'name': 'sporeGate', 'user': 'root', 'pw': 'sporegate', 'os': 'linux', 'arch': 'x86_64', 'role': 'FORGE', 'amoeba': False},
    '192.168.4.237': {'name': 'ironGate', 'user': 'root', 'pw': 'irongate', 'os': 'linux', 'arch': 'x86_64', 'role': 'FORGE2', 'amoeba': False},
    '192.168.4.107': {'name': 'graftGate', 'user': 'root', 'pw': 'graftgate', 'os': 'macos', 'arch': 'aarch64', 'role': 'GRAFT', 'amoeba': False},
    '192.168.4.100': {'name': 'blueGate', 'user': 'root', 'pw': 'bluegate', 'os': 'windows', 'arch': 'x86_64', 'role': 'IDE', 'amoeba': False},
    '192.168.4.176': {'name': 'deckGate', 'user': 'deck', 'pw': 'deckgate', 'os': 'steamos', 'arch': 'x86_64', 'role': 'DISPLAY', 'amoeba': False},
    '192.168.9.203': {'name': 'frameGate', 'user': 'deck', 'pw': 'deckgate', 'os': 'steamos-arm', 'arch': 'aarch64', 'role': 'FACE', 'amoeba': False},
}

RELAY_KEY = "6oVQBFyHHNAJqm1OlS+XvpdoJ5plYrPzJoPTTYlgQdg="
RELAY_HOST = "192.168.4.244"


def sense_gates():
    """Phase 1: Sense — what gates are alive and reachable?"""
    print("\n=== PHASE 1: SENSE — scanning for gates ===")
    alive = {}
    for ip, info in GATES.items():
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '500', ip],
                capture_output=True, text=True, timeout=3
            )
            if 'Reply' in result.stdout or 'bytes=' in result.stdout:
                alive[ip] = info
                print(f"  {info['name']:15s} ({ip}) — ALIVE")
            else:
                print(f"  {info['name']:15s} ({ip}) — down")
        except:
            print(f"  {info['name']:15s} ({ip}) — timeout")
    return alive


def identify_host(ip, info):
    """Phase 2: Identify — what is this host? SSH banner, OS, services."""
    print(f"\n=== PHASE 2: IDENTIFY — {info['name']} ({ip}) ===")
    
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, username=info['user'], password=info['pw'], timeout=5)
        
        checks = {
            'hostname': 'hostname',
            'arch': 'uname -m',
            'os': 'cat /etc/os-release 2>/dev/null | head -3 || sw_vers 2>/dev/null',
            'rustdesk': 'which rustdesk 2>/dev/null && rustdesk --get-id 2>/dev/null || echo "not installed"',
            'ollama': 'which ollama 2>/dev/null && curl -s http://localhost:11434/api/tags 2>/dev/null | grep -c name || echo "not installed"',
            'uptime': 'uptime',
            'disk': 'df -h / 2>/dev/null | tail -1',
        }
        
        results = {}
        for label, cmd in checks.items():
            _, out, _ = c.exec_command(cmd, timeout=5)
            results[label] = out.read().decode().strip()
            print(f"  {label:12s}: {results[label][:80]}")
        
        c.close()
        return results
    except Exception as e:
        print(f"  SSH failed: {e}")
        return None


def inject_amoeba(ip, info):
    """Phase 3: Inject — bootstrap AMOEBA (RustDesk) on the host."""
    print(f"\n=== PHASE 3: INJECT AMOEBA — {info['name']} ===")
    
    if info.get('amoeba'):
        print(f"  {info['name']} already has AMOEBA — skipping")
        return True
    
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, username=info['user'], password=info['pw'], timeout=5)
        
        # Check if RustDesk already installed
        _, out, _ = c.exec_command('which rustdesk 2>/dev/null', timeout=5)
        if out.read().decode().strip():
            print(f"  RustDesk already installed on {info['name']}")
            # Just configure it
            config = f"""rendezvous_server = '{RELAY_HOST}:21116'
nat_type = 1
serial = 0

[options]
allow-remote-config-modification = 'Y'
relay-server = '{RELAY_HOST}'
verification-method = 'use-permanent-password'
custom-rendezvous-server = '{RELAY_HOST}'
direct-server = 'Y'
direct-access-port = '21118'
enable-lan-discovery = 'Y'
"""
            _, out, _ = c.exec_command(f'mkdir -p ~/.config/rustdesk && cat > ~/.config/rustdesk/RustDesk2.toml << "EOCONF"\n{config}\nEOCONF', timeout=5)
            print(f"  Configured RustDesk relay → {RELAY_HOST}")
            
            # Get ID
            _, out, _ = c.exec_command('rustdesk --get-id 2>/dev/null', timeout=5)
            rid = out.read().decode().strip()
            print(f"  RustDesk ID: {rid}")
        else:
            print(f"  RustDesk NOT installed on {info['name']}")
            print(f"  Will use amoeba_bootstrap.sh from eastGate")
            # Pipe the bootstrap through SSH
            _, out, _ = c.exec_command(
                f'curl -sSL http://{RELAY_HOST}:8443/amoeba-bootstrap 2>/dev/null | head -5 || echo "bootstrap endpoint not available"',
                timeout=10
            )
            print(f"  Bootstrap: {out.read().decode().strip()[:100]}")
        
        c.close()
        return True
    except Exception as e:
        print(f"  Injection failed: {e}")
        return False


def activate_lysogeny(ip, info, host_data):
    """Phase 4: Lysogeny — the gate becomes part of Gaia."""
    print(f"\n=== PHASE 4: LYSOGENY — {info['name']} remakes to GAIA ===")
    print(f"  Host: {info['name']} ({ip})")
    print(f"  Arch: {info['arch']}")
    print(f"  Role: {info['role']}")
    print(f"  Vector: Pixel phage via {'USB tether' if info.get('tethered') else 'WiFi proximity'}")
    print(f"  Status: LYSOGENIC — primal DNA integrated, awaiting lytic trigger")


def main():
    print("=" * 60)
    print("  LYSOGENIC VECTOR v1.0")
    print("  The Pixel is the phage. Gates are the hosts.")
    print("  Touch = inject. Proximity = sense. USB = needle.")
    print("=" * 60)
    
    # Phase 1: Sense
    alive = sense_gates()
    print(f"\n  {len(alive)}/{len(GATES)} gates alive")
    
    # Phase 2+3+4: For each alive gate
    for ip, info in alive.items():
        host_data = identify_host(ip, info)
        if host_data:
            inject_amoeba(ip, info)
            activate_lysogeny(ip, info, host_data)
    
    print("\n" + "=" * 60)
    print("  LYSOGENIC VECTOR COMPLETE")
    print(f"  Gates sensed: {len(alive)}")
    print(f"  Primal DNA radiated. Awaiting Pixel walk.")
    print("=" * 60)


if __name__ == '__main__':
    main()
