#!/usr/bin/env python3
"""
EXPAND THE CERT — add in/out.nestgate.io + primal.eco to Let's Encrypt cert.

Current nestgate.io cert SANs (23):
  primals.eco, academy/api/art/campfire/clutch/detroit/fossil/game/gis.primals.eco,
  hud.nestgate.io, hud/klein/lansing/publicrecord/record/signal/sporeprint/tuebor/water.primals.eco,
  nestgate.io, www.nestgate.io, www.primals.eco

Missing: in.nestgate.io, out.nestgate.io, primal.eco, www.primal.eco, hud.primal.eco
"""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15)

# Check how certbot was originally run
print("=== CERTBOT RENEWAL CONFIG ===")
stdin, stdout, stderr = ssh.exec_command('sudo cat /etc/letsencrypt/renewal/nestgate.io.conf 2>/dev/null')
print(stdout.read().decode().strip()[:2000])

print("\n=== CERTBOT RENEWAL CONFIG (primals.eco) ===")
stdin, stdout, stderr = ssh.exec_command('sudo cat /etc/letsencrypt/renewal/primals.eco.conf 2>/dev/null')
print(stdout.read().decode().strip()[:2000])

# Build the full domain list — existing + new
existing_nestgate = [
    "primals.eco", "academy.primals.eco", "api.primals.eco", "art.primals.eco",
    "campfire.primals.eco", "clutch.primals.eco", "detroit.primals.eco",
    "fossil.primals.eco", "game.primals.eco", "gis.primals.eco",
    "hud.nestgate.io", "hud.primals.eco", "klein.primals.eco",
    "lansing.primals.eco", "nestgate.io", "publicrecord.primals.eco",
    "record.primals.eco", "signal.primals.eco", "sporeprint.primals.eco",
    "tuebor.primals.eco", "water.primals.eco", "www.nestgate.io", "www.primals.eco"
]

new_domains = [
    "in.nestgate.io", "out.nestgate.io",
    "primal.eco", "www.primal.eco", "hud.primal.eco"
]

all_domains = existing_nestgate + new_domains
domain_args = " ".join([f"-d {d}" for d in all_domains])

print(f"\n=== EXPANDING CERT ===")
print(f"  Existing: {len(existing_nestgate)} domains")
print(f"  New: {', '.join(new_domains)}")
print(f"  Total: {len(all_domains)} domains")

# Stop dromedary briefly so certbot can use port 80
print("\n  Stopping dromedary for certbot challenge...")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl stop dromedary')
stdout.read()
time.sleep(2)

# Run certbot expand
cmd = f'sudo certbot certonly --standalone --cert-name nestgate.io --expand --non-interactive --agree-tos -m gaia@primals.eco {domain_args} 2>&1'
print(f"\n  Running certbot...")
stdin, stdout, stderr = ssh.exec_command(cmd)
result = stdout.read().decode()
err = stderr.read().decode()
print(result[:2000])
if err:
    print(f"  stderr: {err[:500]}")

# Restart dromedary
print("\n  Restarting dromedary...")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl start dromedary')
stdout.read()
time.sleep(3)

# Verify the new cert
print("\n=== VERIFY NEW CERT ===")
stdin, stdout, stderr = ssh.exec_command('sudo openssl x509 -in /etc/letsencrypt/live/nestgate.io/cert.pem -noout -text 2>/dev/null | grep "DNS:" | head -3')
print(stdout.read().decode().strip())

# Test HTTPS with the new domains
print("\n=== HTTPS TEST ===")
time.sleep(2)
for domain in ['in.nestgate.io', 'out.nestgate.io', 'nestgate.io', 'hud.primals.eco', 'primals.eco', 'primal.eco']:
    stdin, stdout, stderr = ssh.exec_command(f'curl -sk -o /dev/null -w "%{{http_code}} %{{size_download}}" https://{domain}/ 2>/dev/null')
    result = stdout.read().decode().strip()
    print(f"  https://{domain:25s} → {result}")

ssh.close()
