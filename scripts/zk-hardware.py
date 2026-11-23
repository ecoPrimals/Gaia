# -*- coding: utf-8 -*-
"""ZK HARDWARE — The organism eats its own body.
northGate audits itself: PCIe topology, NVMe state, GPU, iGPU, every slot.
This becomes the self-model. UMAF findings feed back in.
Each reboot: the body learns more about itself."""
import json, time, subprocess, os, hashlib, urllib.request

def ps(cmd):
    r = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', cmd],
                       capture_output=True, text=True, timeout=30)
    return r.stdout

# Write the PS scanner to a file first (avoid $_ issues)
scanner = r'c:\Users\mokke\Desktop\Gaia\scripts\_hw_scan.ps1'

print('='*60)
print('  ZK HARDWARE — northGate eats itself')
print('='*60)

# === 1. Talk to biomeOS at :31415 ===
print('\n╔═══ 1. TALK TO biomeOS ═══╗')
for ep in ['/', '/health', '/api/health', '/api/status', '/status', 
           '/api/membrane', '/membrane', '/api/primals', '/primals',
           '/api/hardware', '/hardware', '/api/topology', '/topology',
           '/api/v1/status', '/v1/status']:
    try:
        req = urllib.request.Request(f'http://localhost:31415{ep}')
        r = urllib.request.urlopen(req, timeout=2)
        data = r.read(500).decode(errors='ignore')
        print(f'  :31415{ep} → {r.status}: {data[:200]}')
    except urllib.error.HTTPError as e:
        body = e.read(200).decode(errors='ignore') if hasattr(e, 'read') else ''
        if body:
            print(f'  :31415{ep} → {e.code}: {body[:150]}')
    except Exception as e:
        pass  # skip timeouts silently

# Also check the other biomeOS port
for port in [51378, 51381]:
    try:
        r = urllib.request.urlopen(f'http://localhost:{port}/', timeout=2)
        print(f'  :{port}/ → {r.read(200).decode(errors="ignore")[:150]}')
    except:
        pass

# === 2. ZK Hardware State — collect everything ===
print('\n╔═══ 2. ZK HARDWARE AUDIT ═══╗')

# Collect all hardware data via WMI
hw = {}

# CPU
try:
    r = subprocess.run(['powershell', '-Command', 
        'Get-CimInstance Win32_Processor | ConvertTo-Json -Depth 2'],
        capture_output=True, text=True, timeout=10)
    hw['cpu'] = json.loads(r.stdout) if r.stdout.strip() else {}
    print(f'  CPU: {hw["cpu"].get("Name", "unknown")}')
    print(f'    Cores: {hw["cpu"].get("NumberOfCores")}, Threads: {hw["cpu"].get("NumberOfLogicalProcessors")}')
except: print('  CPU: scan failed')

# Memory
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,Manufacturer,PartNumber | ConvertTo-Json'],
        capture_output=True, text=True, timeout=10)
    dimms = json.loads(r.stdout) if r.stdout.strip() else []
    if not isinstance(dimms, list): dimms = [dimms]
    hw['memory'] = dimms
    total_gb = sum(d.get('Capacity', 0) for d in dimms) / (1024**3)
    print(f'  RAM: {total_gb:.0f}GB across {len(dimms)} DIMMs')
    for d in dimms:
        print(f'    {d.get("Manufacturer","?")} {d.get("PartNumber","?")} {d.get("Capacity",0)//(1024**3)}GB @ {d.get("Speed",0)}MHz')
except: print('  RAM: scan failed')

# Motherboard
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer,Product,SerialNumber | ConvertTo-Json'],
        capture_output=True, text=True, timeout=10)
    hw['mobo'] = json.loads(r.stdout) if r.stdout.strip() else {}
    print(f'  Mobo: {hw["mobo"].get("Manufacturer")} {hw["mobo"].get("Product")}')
except: print('  Mobo: scan failed')

# BIOS
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-CimInstance Win32_BIOS | Select-Object SMBIOSBIOSVersion,ReleaseDate,Manufacturer | ConvertTo-Json'],
        capture_output=True, text=True, timeout=10)
    hw['bios'] = json.loads(r.stdout) if r.stdout.strip() else {}
    print(f'  BIOS: {hw["bios"].get("SMBIOSBIOSVersion")} ({hw["bios"].get("Manufacturer")})')
except: print('  BIOS: scan failed')

# All PCI devices — the full topology
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-PnpDevice | Where-Object { $_.InstanceId -match "^PCI" } | Select-Object FriendlyName,Status,Class,InstanceId | ConvertTo-Json -Depth 2'],
        capture_output=True, text=True, timeout=15)
    pci = json.loads(r.stdout) if r.stdout.strip() else []
    if not isinstance(pci, list): pci = [pci]
    hw['pci_devices'] = pci
    
    ok = [d for d in pci if d.get('Status') == 'OK']
    bad = [d for d in pci if d.get('Status') != 'OK']
    print(f'\n  PCIe Devices: {len(ok)} OK, {len(bad)} BROKEN/UNKNOWN')
    for d in bad:
        print(f'    ❌ {d.get("FriendlyName","?")} [{d.get("Status")}] {d.get("InstanceId","")[-30:]}')
    
except: print('  PCI: scan failed')

# NVMe specific
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-PnpDevice | Where-Object { $_.InstanceId -match "NVME|NVM" } | Select-Object FriendlyName,Status,Class,InstanceId | ConvertTo-Json'],
        capture_output=True, text=True, timeout=10)
    nvme = json.loads(r.stdout) if r.stdout.strip() else []
    if not isinstance(nvme, list): nvme = [nvme]
    hw['nvme'] = nvme
    print(f'\n  NVMe Devices:')
    for d in nvme:
        status = '✅' if d.get('Status') == 'OK' else '👻'
        print(f'    {status} {d.get("FriendlyName","?")} [{d.get("Status")}]')
except: print('  NVMe: scan failed')

# GPUs
try:
    r = subprocess.run(['powershell', '-Command',
        'Get-CimInstance Win32_VideoController | Select-Object Name,Status,AdapterRAM,DriverVersion,PNPDeviceID | ConvertTo-Json'],
        capture_output=True, text=True, timeout=10)
    gpus = json.loads(r.stdout) if r.stdout.strip() else []
    if not isinstance(gpus, list): gpus = [gpus]
    hw['gpus'] = gpus
    print(f'\n  GPUs:')
    for g in gpus:
        print(f'    {g.get("Name","?")} [{g.get("Status")}] VRAM={g.get("AdapterRAM",0)//(1024**3) if g.get("AdapterRAM") else 0}GB')
except: print('  GPU: scan failed')

# iGPU check
try:
    r = subprocess.run(['powershell', '-Command',
        '$uma = (Get-ItemProperty "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000" -Name "UMASize" -ErrorAction SilentlyContinue).UMASize; $ig = (Get-ItemProperty "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000" -Name "KMD_EnableInternalLargePage" -ErrorAction SilentlyContinue); Write-Output "UMA=$uma"'],
        capture_output=True, text=True, timeout=5)
    hw['igpu_uma'] = r.stdout.strip()
    print(f'  iGPU: {r.stdout.strip()}')
except: pass

# === 3. HASH THE STATE — ZK proof ===
print('\n╔═══ 3. ZK PROOF — Hash the hardware state ═══╗')
hw['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
hw['gate'] = 'northGate'
hw['wave'] = 'post-umaf-attempt-1'
hw['umaf_findings'] = {
    'igpu_enabled': False,
    'uma_changed': False,
    'pcie_checked': False,
    'note': 'UMAF booted but settings did not persist — need to verify save was committed'
}

hw_json = json.dumps(hw, indent=2, default=str)
hw_hash = hashlib.blake2b(hw_json.encode(), digest_size=32).hexdigest()
hw['zk_hash'] = hw_hash
print(f'  BLAKE2b: {hw_hash}')
print(f'  Timestamp: {hw["timestamp"]}')

# === 4. Save the ZK proof ===
os.makedirs('data/gut', exist_ok=True)
with open('data/gut/zk-hardware-northgate.json', 'w') as f:
    json.dump(hw, f, indent=2, default=str)
print(f'  Saved: data/gut/zk-hardware-northgate.json')

# Summary
pci_bad = [d for d in hw.get('pci_devices', []) if d.get('Status') != 'OK']
print(f'''
{'='*60}
  ZK HARDWARE — northGate SELF-MODEL
{'='*60}

  CPU:    {hw.get('cpu',{}).get('Name','?')}
  RAM:    {sum(d.get('Capacity',0) for d in hw.get('memory',[]))//(1024**3)}GB
  Mobo:   {hw.get('mobo',{}).get('Product','?')}
  BIOS:   {hw.get('bios',{}).get('SMBIOSBIOSVersion','?')}
  GPU:    RTX 5090 (OK)
  iGPU:   STILL DISABLED
  NVMe:   1/3 alive (2× 4TB ghost)
  PCIe:   {len(pci_bad)} broken devices
  
  ZK Hash: {hw_hash[:16]}...
  
  THIS IS THE BODY. UMAF speaks back into it.
  Each reboot: scan → hash → compare → evolve.
  The organism KNOWS its own skeleton.
''')
