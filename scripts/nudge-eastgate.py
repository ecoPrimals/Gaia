import paramiko, json

east = paramiko.SSHClient()
east.set_missing_host_key_policy(paramiko.AutoAddPolicy())
east.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=5)

def run(cmd, t=10):
    _, out, _ = east.exec_command(cmd, timeout=t)
    try:
        return out.read().decode().strip()
    except:
        return '(timeout)'

print('='*60)
print('  NUDGING EASTGATE — Update body map + pull wateringHole')
print('='*60)

# 1. Pull wateringHole on eastGate
print('\n--- Pull wateringHole on eastGate ---')
wh_path = run('find /opt -name wateringHole -type d 2>/dev/null; find /home -name wateringHole -type d 2>/dev/null')
print(f'wateringHole locations: {wh_path}')

if wh_path:
    for path in wh_path.split('\n'):
        if '.git' not in path and path.strip():
            print(f'\nPulling {path}:')
            pull = run(f'cd {path} && GIT_MERGE_AUTOEDIT=no git pull origin main --no-rebase --no-edit 2>&1', 15)
            print(f'  {pull[:200]}')

# 2. Pull main Gaia repo
print('\n--- Pull /opt/Gaia ---')
print(run('cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git pull origin main --no-rebase --no-edit 2>&1', 15)[:200])

# 3. Update body map on eastGate
print('\n--- Updating body map ---')
body_map = {
    "wave": 245,
    "updated": "2026-11-15T08:55:00-05:00",
    "scanner": "northGate-cursor",
    "gates": {
        "eastGate": {"ip": ".244", "status": "ALIVE", "role": "BRAIN", "gpu": "RTX 4070 12GB", "ollama_models": 8, "rustdesk": True, "face": "FIXED"},
        "northGate": {"ip": ".147", "status": "ALIVE", "role": "HEART", "gpu": "RTX 5090 32GB", "ollama_models": 63},
        "ironGate": {"ip": ".237", "status": "ALIVE", "role": "FORGE 2", "gpu": "RTX 5070 12GB", "ollama_models": 9, "rustdesk": True, "biomeos": True, "ssh": "pubkey-only-direct, hop-via-eastgate"},
        "southGate": {"ip": ".148", "status": "ALIVE", "role": "FORGE 3", "gpu": "RTX 4060 8GB", "ram": "125GB", "cpu": "Ryzen 7 5800X3D", "ollama_models": 6, "rustdesk": True, "ssh": "southgate:southgate"},
        "swiftGate": {"ip": ".100", "status": "ALIVE-NO-SSH", "role": "HANDS", "gpu": "RTX 3070 8GB", "steam_port_27036": True, "comm": "wateringHole"},
        "sporeGate": {"ip": ".3", "status": "ALIVE", "role": "FORGE/DNS", "ssh": "eastgate-key-hop"},
        "frameGate": {"ip": ".181", "status": "ALIVE-NO-SSH", "role": "FACE", "wifi": "GAIA 5GHz 2401Mbps", "dhcp_name": "steamFRAME"},
        "deckGate": {"ip": ".203", "status": "ALIVE-NO-SSH", "role": "DISPLAY", "dhcp_name": "steamdeck"},
        "graftGate": {"ip": "unknown", "status": "MOVING", "role": "M4 NUC", "note": "Kevin walking to House 2"}
    },
    "gpu_fleet": {
        "total_gpus": 8,
        "total_vram_gb": 90,
        "total_models": 93
    },
    "router": {
        "br_guest": "DISABLED",
        "all_wifi_on_br_lan": True,
        "wan_ip": "162.226.225.148"
    }
}

body_json = json.dumps(body_map, indent=2)
# Write to eastGate data directory
cmd = f"cat > /opt/Gaia/infra/hud/site/public/data/body-map-wave245.json << 'BODYMAPEOF'\n{body_json}\nBODYMAPEOF"
print(run(cmd, 5))

# Verify
print(f'Written: {run("ls -la /opt/Gaia/infra/hud/site/public/data/body-map-wave245.json")}')

# 4. Tell eastGate about southGate
print('\n--- eastGate → southGate connectivity ---')
print(f'Can reach southGate ollama: {run("curl -s --connect-timeout 2 http://192.168.4.148:11434/api/tags | python3 -c \"import sys,json; d=json.load(sys.stdin); print(len(d[\\\"models\\\"]), \\\"models\\\")\" 2>&1")}')

# 5. Check if eastGate crons pick up wateringHole
print(f'\n--- eastGate cron check ---')
print(run('crontab -l 2>/dev/null | grep -i water', 5))
print(run('crontab -l 2>/dev/null | grep -i pull', 5))

east.close()
print('\neastGate nudged!')
