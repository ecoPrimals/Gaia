import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# Find the ecosystem network section and the area around it
out, _ = run("grep -n 'Ecosystem\\|network\\|hud-grid\\|hud-dash\\|membrane-geo\\|null\\|globe\\|jellyfish\\|overflow' /opt/Gaia/static/senses.html | head -30")
print(f"Key landmarks:\n{out}\n")

# Find where the 8 tentacle boxes are rendered
out, _ = run("grep -n 'tuebor.*detroit\\|primals.eco network\\|Ecosystem' /opt/Gaia/static/senses.html")
print(f"Ecosystem section:\n{out}\n")

# Read around those lines
out, _ = run("sed -n '1590,1680p' /opt/Gaia/static/senses.html")
print(f"Lines 1590-1680:\n{out}\n")

# The footer area where the bottom bar is
out, _ = run("grep -n 'membrane.*footer\\|bottom-bar\\|footer\\|membrane-bar' /opt/Gaia/static/senses.html | head -10")
print(f"Footer:\n{out}\n")

# The section with the green lines / SVG
out, _ = run("grep -n 'svg\\|<svg\\|viewBox\\|stroke.*green\\|#5aad\\|overflow' /opt/Gaia/static/senses.html | head -20")
print(f"SVG/green:\n{out}\n")

# Find the spot between ecosystem boxes and the manifesto text
out, _ = run("grep -n 'One human built\\|artisan.*mirror\\|BUTTON\\|entropy' /opt/Gaia/static/senses.html")
print(f"Manifesto:\n{out}\n")

# Read the ecosystem rendering JS
out, _ = run("grep -n 'ecosystem\\|Ecosystem\\|network\\|tentacle\\|node-card\\|card.*tuebor' /opt/Gaia/static/senses.html | head -20")
print(f"Ecosystem rendering:\n{out}\n")

c.close()
