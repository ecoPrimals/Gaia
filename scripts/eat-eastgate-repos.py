import paramiko
import json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)
print('Connected to eastGate!')

# List all Forgejo repos
print('\n=== FORGEJO REPOS ===')
_, out, _ = c.exec_command(
    'curl -s "http://localhost:3000/api/v1/repos/search?limit=50" -u gaia:***',
    timeout=15
)
data = json.loads(out.read().decode())
repos = data.get('data', [])
print(f'  Total repos: {len(repos)}')
for r in sorted(repos, key=lambda x: x.get('updated_at', ''), reverse=True)[:20]:
    name = r.get('full_name', '?')
    updated = r.get('updated_at', '?')[:19]
    stars = r.get('stars_count', 0)
    print(f'  {name:40s} updated={updated} stars={stars}')

# Check recent git activity on /opt/Gaia
print('\n=== EASTGATE /opt/Gaia RECENT COMMITS ===')
_, out, _ = c.exec_command('cd /opt/Gaia && git log --oneline -15', timeout=5)
print(out.read().decode())

# Check what steamOS work exists
print('\n=== STEAMOS / STEAM FRAME FILES ===')
_, out, _ = c.exec_command('find /opt/Gaia -name "*steam*" -o -name "*frame*" -o -name "*amoeba*" 2>/dev/null | head -20', timeout=5)
print(out.read().decode())

# Check wateringHole heads for steam/frame topics
_, out, _ = c.exec_command('ls -la /opt/Gaia/wateringHole/heads/ 2>/dev/null | grep -iE "steam|frame|amoeba|deck"', timeout=5)
steam_heads = out.read().decode()
if steam_heads:
    print('=== STEAM/FRAME/AMOEBA HEADS ===')
    print(steam_heads)

# Check mushrooms/crons for steam-related
print('\n=== STEAM-RELATED SERVICES ===')
_, out, _ = c.exec_command('systemctl list-units --type=service --state=running | grep -i steam', timeout=5)
print(out.read().decode())

# Check if Steam is installed on eastGate
print('=== STEAM ON EASTGATE ===')
_, out, _ = c.exec_command('which steam 2>/dev/null; dpkg -l | grep steam 2>/dev/null | head -5; ls ~/.steam/ 2>/dev/null | head -5', timeout=5)
print(out.read().decode())

c.close()
print('DONE — eastGate fully eaten!')
