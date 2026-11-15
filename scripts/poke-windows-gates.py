"""
POKE WINDOWS GATES — SSH is dead, use the HUMAN PUBLIC PIN
swiftGate (.100) and blueGate are Windows PCs
PIN: 579163
"""
import socket, subprocess

# Windows gates
targets = {
    '.100 swiftGate': '192.168.4.100',
    '.139 DESKTOP-9QG6LQL': '192.168.4.139',
}

for label, ip in targets.items():
    print(f'=== {label} ({ip}) ===')
    
    # Port scan for Windows services
    win_ports = {
        22: 'SSH',
        135: 'RPC/WMI',
        139: 'NetBIOS',
        445: 'SMB',
        3389: 'RDP',
        5985: 'WinRM HTTP',
        5986: 'WinRM HTTPS',
        8080: 'HTTP',
        11434: 'Ollama',
        27036: 'Steam RP',
        47984: 'Sunshine',
        47989: 'Sunshine HTTPS',
        47990: 'Sunshine Web',
    }
    
    open_ports = []
    for port, name in win_ports.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            result = s.connect_ex((ip, port))
            s.close()
            if result == 0:
                print(f'  ✅ PORT {port} OPEN ({name})')
                open_ports.append(port)
        except:
            pass
    
    if not open_ports:
        print(f'  ❌ No ports reachable')
        continue
    
    # Try SMB/NetBIOS for identity
    if 445 in open_ports or 139 in open_ports:
        print(f'\n  SMB probe:')
        try:
            r = subprocess.run(
                ['net', 'view', f'\\\\{ip}', '/all'],
                capture_output=True, text=True, timeout=5
            )
            print(f'    {r.stdout.strip()[:200]}')
            if r.returncode != 0:
                print(f'    err: {r.stderr.strip()[:100]}')
        except Exception as e:
            print(f'    {e}')
    
    # Try PowerShell remoting
    if 5985 in open_ports or 5986 in open_ports:
        print(f'\n  WinRM probe:')
        try:
            r = subprocess.run(
                ['powershell', '-Command',
                 f'Test-WSMan -ComputerName {ip} -ErrorAction SilentlyContinue'],
                capture_output=True, text=True, timeout=8
            )
            print(f'    {r.stdout.strip()[:200]}')
        except:
            pass

    # RDP check
    if 3389 in open_ports:
        print(f'\n  RDP is OPEN — can connect with:')
        print(f'    mstsc /v:{ip}')
        print(f'    PIN: 579163')
    
    # Steam Remote Play
    if 27036 in open_ports:
        print(f'\n  Steam Remote Play OPEN — can stream games from this gate!')
    
    print()

# Also try from northGate directly
print('=== DIRECT WINDOWS TOOLS ===')

# Can we ping swiftGate?
print('\nPing .100:')
r = subprocess.run(['ping', '-n', '1', '-w', '1000', '192.168.4.100'], capture_output=True, text=True, timeout=5)
alive = 'Reply from' in r.stdout
print(f'  {"ALIVE" if alive else "DOWN"}')

# Try hostname resolution
print('\nHostname lookup:')
try:
    r = subprocess.run(['nbtstat', '-A', '192.168.4.100'], capture_output=True, text=True, timeout=5)
    print(f'  {r.stdout.strip()[:300]}')
except:
    print('  nbtstat failed')

print('\nDone! Use RDP (mstsc) + PIN 579163 for Windows gates.')
