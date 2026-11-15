"""
SOURDOUGH — Do work while northGate reboots.
eastGate keeps learning. We ferment what we know.
"""
import paramiko, json, time

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def run(cmd, t=15):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try: return out.read().decode().strip()
    except: return '(timeout)'

print('='*60)
print('  SOURDOUGH — fermenting while northGate reboots')
print('='*60)

# 1. eastGate's Akida chip — deep dive since we know it's at 08:00.0
print('\n--- eastGate AKD1000 DEEP PROBE ---')
print(run('lspci -d 1e7c: -vvv 2>&1'))

print('\n--- Akida IOMMU group ---')
print(run('find /sys/kernel/iommu_groups/23/ -type l 2>/dev/null'))

print('\n--- Akida BAR regions ---')
print(run('cat /sys/bus/pci/devices/0000:08:00.0/resource 2>&1'))

print('\n--- Akida driver binding ---')
print(run('ls -la /sys/bus/pci/devices/0000:08:00.0/driver 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:08:00.0/driver_override 2>&1'))

print('\n--- Akida current_link_speed ---')
print(run('cat /sys/bus/pci/devices/0000:08:00.0/current_link_speed 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:08:00.0/current_link_width 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:08:00.0/max_link_speed 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:08:00.0/max_link_width 2>&1'))

print('\n--- eastGate GPU PCIe link for comparison ---')
print(run('cat /sys/bus/pci/devices/0000:01:00.0/current_link_speed 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:01:00.0/current_link_width 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:01:00.0/max_link_speed 2>&1'))
print(run('cat /sys/bus/pci/devices/0000:01:00.0/max_link_width 2>&1'))

print('\n--- eastGate full PCIe tree ---')
print(run('lspci -tv 2>&1'))

# 2. Check rustChip on eastGate
print('\n--- rustChip on eastGate ---')
print(run('find /home/eastgate /opt -maxdepth 4 -name "rustChip" -o -name "akida*" 2>/dev/null'))
print(run('ls /home/eastgate/rustChip/ 2>/dev/null || echo "not found at ~/rustChip"'))

# 3. Pull wateringHole on eastGate
print('\n--- eastGate: pulling wateringHole ---')
wh_pull = run('cd /home/eastgate/wateringHole 2>/dev/null && git pull origin main --no-rebase --no-edit 2>&1 || echo "wateringHole not cloned"')
print(wh_pull)

# 4. ironGate PCIe — does it have slots for chip #3?
print('\n--- ironGate PCIe scan (via eastGate hop) ---')
iron_pcie = run('ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "lspci -nn 2>&1" 2>&1', 15)
print(iron_pcie[:1000] if iron_pcie else '(could not reach)')

# 5. ironGate Akida check
print('\n--- ironGate: BrainChip check ---')
iron_akida = run('ssh -o StrictHostKeyChecking=no irongate@192.168.4.237 "lspci -d 1e7c: 2>&1" 2>&1', 10)
print(iron_akida if iron_akida else '(no BrainChip in ironGate)')

# 6. southGate PCIe check
print('\n--- southGate PCIe scan ---')
south_cmd = 'sshpass -p southgate ssh -o StrictHostKeyChecking=no southgate@192.168.4.148'
south_pcie = run(f'{south_cmd} "lspci -nn 2>&1 | head -20" 2>&1', 15)
print(south_pcie[:800] if south_pcie else '(could not reach)')

print('\n--- southGate: BrainChip check ---')
south_akida = run(f'{south_cmd} "lspci -d 1e7c: 2>&1" 2>&1', 10)
print(south_akida if south_akida else '(no BrainChip in southGate)')

# 7. Organism pulse
print('\n--- ORGANISM PULSE ---')
print(f'eastGate uptime: {run("uptime")}')
print(f'eastGate ollama: {run("systemctl is-active ollama")}')
print(f'eastGate crons: {run("crontab -l 2>/dev/null | grep -v ^# | grep -v ^$ | wc -l")}')
gate = run('curl -s -o /dev/null -w "%{http_code}" http://localhost:8443/pulse')
print(f'eastGate gate: HTTP {gate}')

east.close()

print('\n' + '='*60)
print('  SOURDOUGH COMPLETE — knowledge fermenting')
print('='*60)
