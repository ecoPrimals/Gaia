import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# Read the nav-ring section from senses.html
out, _ = run("grep -n 'nav-ring\\|klein\\|scroll-ring' /opt/Gaia/static/senses.html 2>/dev/null | head -20")
print(f"Nav-ring refs:\n{out}")

# Extract all links from the nav-ring
out, _ = run("sed -n '/<.*nav-ring\\|scroll-ring/,/<\\/.*>/p' /opt/Gaia/static/senses.html 2>/dev/null | grep -oP 'href=\"[^\"]+\"' | head -70")
print(f"\nNav-ring links:\n{out}")

# Extract full nav-ring HTML
out, _ = run("sed -n '/<.*id=\"scroll-ring/,/<\\/nav>/p' /opt/Gaia/static/senses.html 2>/dev/null | head -80")
print(f"\nNav-ring HTML:\n{out}")

# Check what 'klein' looks like in the nav-ring
out, _ = run("grep -i 'klein' /opt/Gaia/static/senses.html 2>/dev/null | head -10")
print(f"\nKlein refs:\n{out}")

c.close()
