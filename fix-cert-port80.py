#!/usr/bin/env python3
"""Fix port 80 binding + expand cert."""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

# What's on port 80?
print("=== PORT 80 ===")
stdin, stdout, stderr = ssh.exec_command('sudo ss -tlnp | grep ":80 "')
print(stdout.read().decode().strip())

stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :80 2>/dev/null | head -10')
print(stdout.read().decode().strip())

# What's on port 443?
print("\n=== PORT 443 ===")
stdin, stdout, stderr = ssh.exec_command('sudo ss -tlnp | grep ":443 "')
print(stdout.read().decode().strip())

# Full stop of everything that might use 80/443
print("\n=== STOPPING SERVICES ===")
for svc in ['dromedary', 'gaia-gate', 'nginx', 'apache2', 'caddy']:
    stdin, stdout, stderr = ssh.exec_command(f'sudo systemctl stop {svc} 2>/dev/null; echo "{svc}: $?"')
    print(f"  {stdout.read().decode().strip()}")
    # Also user services
    stdin, stdout, stderr = ssh.exec_command(f'systemctl --user stop {svc} 2>/dev/null')
    stdout.read()

time.sleep(2)

# Check again
stdin, stdout, stderr = ssh.exec_command('sudo ss -tlnp | grep ":80\\|:443"')
ports = stdout.read().decode().strip()
print(f"\n  After stop: {ports or 'PORTS FREE'}")

if ports:
    # Kill whatever's left
    stdin, stdout, stderr = ssh.exec_command('sudo fuser -k 80/tcp 2>/dev/null; sudo fuser -k 443/tcp 2>/dev/null')
    stdout.read()
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('sudo ss -tlnp | grep ":80\\|:443"')
    print(f"  After fuser kill: {stdout.read().decode().strip() or 'PORTS FREE'}")

# Build domain list
all_domains = [
    "primals.eco", "academy.primals.eco", "api.primals.eco", "art.primals.eco",
    "campfire.primals.eco", "clutch.primals.eco", "detroit.primals.eco",
    "fossil.primals.eco", "game.primals.eco", "gis.primals.eco",
    "hud.nestgate.io", "hud.primals.eco", "klein.primals.eco",
    "lansing.primals.eco", "nestgate.io", "publicrecord.primals.eco",
    "record.primals.eco", "signal.primals.eco", "sporeprint.primals.eco",
    "tuebor.primals.eco", "water.primals.eco", "www.nestgate.io", "www.primals.eco",
    "in.nestgate.io", "out.nestgate.io",
    "primal.eco", "www.primal.eco", "hud.primal.eco"
]
domain_args = " ".join([f"-d {d}" for d in all_domains])

# Run certbot
print(f"\n=== RUNNING CERTBOT ({len(all_domains)} domains) ===")
cmd = f'sudo certbot certonly --standalone --cert-name nestgate.io --expand --non-interactive --agree-tos -m gaia@primals.eco {domain_args} 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
result = stdout.read().decode()
print(result[:2000])

# Restart everything
print("\n=== RESTARTING SERVICES ===")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl start dromedary')
stdout.read()
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('sudo systemctl start gaia-gate 2>/dev/null; systemctl --user start gaia-gate 2>/dev/null')
stdout.read()
time.sleep(3)

# Verify new cert
print("=== VERIFY CERT ===")
stdin, stdout, stderr = ssh.exec_command('sudo openssl x509 -in /etc/letsencrypt/live/nestgate.io/cert.pem -noout -text 2>/dev/null | grep "DNS:"')
sans = stdout.read().decode().strip()
print(sans[:500])

has_in = 'in.nestgate.io' in sans
has_out = 'out.nestgate.io' in sans
has_primal = 'primal.eco' in sans
print(f"\n  in.nestgate.io:  {'✓' if has_in else '✗'}")
print(f"  out.nestgate.io: {'✓' if has_out else '✗'}")
print(f"  primal.eco:      {'✓' if has_primal else '✗'}")

# Final test — real HTTPS (not insecure)
print("\n=== FINAL HTTPS TEST ===")
time.sleep(2)
for domain in ['in.nestgate.io', 'out.nestgate.io', 'primals.eco', 'nestgate.io', 'hud.primals.eco']:
    stdin, stdout, stderr = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" --max-time 5 https://{domain}/ 2>/dev/null')
    code = stdout.read().decode().strip()
    icon = '✓' if code == '200' else ('→' if code.startswith('3') else '✗')
    print(f"  {icon} https://{domain:25s} → {code}")

ssh.close()
