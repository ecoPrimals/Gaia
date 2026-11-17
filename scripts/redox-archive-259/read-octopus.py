import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=20,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=30)

def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# Read the octopus invitation
path = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/sporeprint/outreach/octopus-invitation/index.html"
out, _ = run(f'cat {path} 2>/dev/null | head -300')
print("=== OCTOPUS INVITATION (first 300 lines) ===")
print(out)

# Count all outreach pages
out, _ = run('find /home/eastgate/Development/ecoPrimals/infra/hud/site/public/sporeprint/outreach -name "index.html" -type f 2>/dev/null | wc -l')
print(f"\nTotal outreach pages: {out}")

# List all outreach dirs
out, _ = run('ls -d /home/eastgate/Development/ecoPrimals/infra/hud/site/public/sporeprint/outreach/*/ 2>/dev/null')
print(f"\nOutreach topics:\n{out}")

# What port 8888 is serving
out, _ = run('sudo ss -tlnp sport eq 8888 2>/dev/null')
print(f"\nPort 8888:\n{out}")

# Check the USB tether
out, _ = run('ip addr show enx0200376af71b 2>/dev/null')
print(f"\nUSB tether interface:\n{out}")

c.close()
