import paramiko, json, datetime
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=== DROMEDARY WAN — FULL ROUTE MAP ===\n")

# dromedary process
out, _ = run("ps aux | grep dromedary | grep -v grep")
print(f"Process:\n{out}\n")

# dromedary config — all routes
out, _ = run("cat /opt/Gaia/runtime/dromedary.toml")
print(f"CONFIG:\n{out}\n")

# Test each subdomain via GET through dromedary
print("=== HITTING EACH ROUTE VIA DROMEDARY ===\n")
hosts = [
    "primals.eco", "www.primals.eco", "detroit.primals.eco",
    "tuebor.primals.eco", "lansing.primals.eco", "clutch.primals.eco",
    "sporeprint.primals.eco", "klein.primals.eco", "art.primals.eco",
    "game.primals.eco", "academy.primals.eco", "campfire.primals.eco",
    "fossil.primals.eco", "signal.primals.eco", "api.primals.eco",
    "gis.primals.eco", "hud.primals.eco", "connect.primals.eco",
    "publicrecord.primals.eco",
    "nestgate.io", "www.nestgate.io", "api.nestgate.io",
    "beacon.nestgate.io", "tower.nestgate.io"
]
for h in hosts:
    out, _ = run(f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Host: {h}' http://localhost:80/ 2>/dev/null")
    out2, _ = run(f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Host: {h}' https://localhost:443/ -k 2>/dev/null")
    print(f"  {h:35s} HTTP={out}  HTTPS={out2}")

# TLS cert domains
print("\n=== TLS CERT DOMAINS ===")
out, _ = run("echo | openssl s_client -connect localhost:443 -servername primals.eco 2>/dev/null | openssl x509 -noout -text 2>/dev/null | grep -A1 'Subject Alternative'")
print(out)

# BLACKWALL
print("\n=== BLACKWALL ===")
out, _ = run("grep -A20 'blackwall' /opt/Gaia/runtime/dromedary.toml 2>/dev/null || grep -i 'block\\|deny\\|black' /opt/Gaia/runtime/dromedary.toml")
print(out)

c.close()
