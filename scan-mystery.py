#!/usr/bin/env python3
"""Deep port scan mystery IPs from eastGate WiFi bridge to identify moved gates."""
import paramiko
import json

EAST_HOST = "192.168.1.131"
EAST_USER = "eastgate"
EAST_PASS = "eastgate"

MYSTERY_IPS = ["192.168.4.189", "192.168.4.213", "192.168.4.243", "192.168.4.3"]

GATE_PORTS = [22, 53, 80, 443, 3000, 3141, 5900, 8080, 8082, 8443, 9090, 11434, 11436]

GATE_SIGS = {
    "northGate": {22, 11434},
    "ironGate": {22, 11434},
    "blueGate": {22, 3141},
    "deckGate": {22},
    "sporeGate": {22, 53},
    "swiftGate": {22, 11434},
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EAST_HOST, username=EAST_USER, password=EAST_PASS, timeout=10)

for ip in MYSTERY_IPS:
    print(f"\n=== DEEP SCAN {ip} ===")

    # Port scan
    open_ports = []
    for port in GATE_PORTS:
        cmd = f"timeout 3 bash -c 'echo >/dev/tcp/{ip}/{port}' 2>/dev/null && echo OPEN || echo CLOSED"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=5)
        result = stdout.read().decode().strip()
        if result == "OPEN":
            open_ports.append(port)
            print(f"  PORT {port}: OPEN")

    # Try to get MAC address
    cmd = f"ping -c 1 -W 1 {ip} >/dev/null 2>&1; arp -n {ip} 2>/dev/null"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=5)
    arp_out = stdout.read().decode().strip()
    print(f"  ARP: {arp_out}")

    # Try SSH banner grab
    if 22 in open_ports:
        cmd = f"timeout 3 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 -o BatchMode=yes {ip} 2>&1 | head -5"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=8)
        ssh_out = stdout.read().decode().strip()
        print(f"  SSH banner: {ssh_out}")

    # Try ollama if port 11434 open
    if 11434 in open_ports:
        cmd = f"curl -s --connect-timeout 3 http://{ip}:11434/api/tags 2>/dev/null | head -c 500"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=8)
        ollama_out = stdout.read().decode().strip()
        print(f"  OLLAMA: {ollama_out}")

    # Try HTTP endpoints
    for port in [8080, 8443, 3000, 3141]:
        if port in open_ports:
            cmd = f"curl -sk --connect-timeout 3 http://{ip}:{port}/ 2>/dev/null | head -c 300"
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=8)
            http_out = stdout.read().decode().strip()
            print(f"  HTTP {port}: {http_out[:200]}")

    # Try hostname
    cmd = f"timeout 2 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 -o PreferredAuthentications=none {ip} 2>&1 || true"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=8)
    hostname_out = stdout.read().decode().strip()
    if hostname_out:
        print(f"  SSH attempt: {hostname_out[:200]}")

    # Identify
    port_set = set(open_ports)
    matched = None
    for gate, sig in GATE_SIGS.items():
        if sig.issubset(port_set):
            matched = gate
            break
    
    if open_ports:
        print(f"  OPEN PORTS: {open_ports}")
        print(f"  MATCH: {matched or 'UNKNOWN - needs manual identification'}")
    else:
        print(f"  NO PORTS OPEN - likely smart home device")

# Also scan the MISSING gate old IPs to confirm they're truly gone
print("\n=== CHECKING OLD GATE IPs ===")
old_ips = {
    ".147 (northGate)": "192.168.4.147",
    ".237 (ironGate)": "192.168.4.237",
    ".100 (blueGate)": "192.168.4.100",
    ".176 (deckGate)": "192.168.4.176",
    ".2 (MikroTik)": "192.168.4.2",
    ".148 (southGate)": "192.168.4.148",
}
for name, ip in old_ips.items():
    cmd = f"ping -c 1 -W 2 {ip} >/dev/null 2>&1 && echo ALIVE || echo DEAD"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=5)
    result = stdout.read().decode().strip()
    print(f"  {name}: {result}")

ssh.close()
print("\n=== SCAN COMPLETE ===")
