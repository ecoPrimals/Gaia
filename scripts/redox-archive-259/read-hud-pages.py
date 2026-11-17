import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# water.html — the page Kevin is looking at
print("=== water.html (first 150 lines) ===")
out, _ = run("head -150 /opt/Gaia/static/water.html")
print(out)

print("\n\n=== water.html (last 80 lines) ===")
out, _ = run("tail -80 /opt/Gaia/static/water.html")
print(out)

print("\n\n=== water.html line count ===")
out, _ = run("wc -l /opt/Gaia/static/water.html")
print(out)

# senses.html — the HUD main page
print("\n\n=== senses.html line count ===")
out, _ = run("wc -l /opt/Gaia/static/senses.html")
print(out)

# What data does the HUD fetch?
print("\n\n=== JS that builds the HUD ===")
out, _ = run("grep -n 'fetch\\|ajax\\|XMLHttp\\|\.json\\|/data/' /opt/Gaia/static/water.html | head -20")
print(out)

# body.html — the organism body map
print("\n\n=== body.html lines ===")
out, _ = run("wc -l /opt/Gaia/static/body.html 2>/dev/null")
print(out)
out, _ = run("grep -n 'northGate\\|sourDough\\|skin\\|membrane\\|pituitary\\|pancreas' /opt/Gaia/static/water.html | head -20")
print(f"\nExisting body refs in water.html:\n{out}")

# What does senses.html reference?
out, _ = run("grep -n 'northGate\\|sourDough\\|polaris\\|skin\\|membrane\\|gate' /opt/Gaia/static/senses.html | head -20")
print(f"\nExisting refs in senses.html:\n{out}")

c.close()
