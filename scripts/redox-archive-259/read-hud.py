import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=== HUD STRUCTURE ===\n")

# Where does the HUD live?
out, _ = run("find /opt/Gaia -name 'water*' -type f | head -20")
print(f"water files:\n{out}\n")

# The HUD pages
out, _ = run("ls /opt/Gaia/static/ 2>/dev/null | head -30")
print(f"static/:\n{out}\n")

# The watering hole
out, _ = run("ls /opt/Gaia/wateringHole/ 2>/dev/null | head -20")
print(f"wateringHole/:\n{out}\n")

# Gate routes for /water
out, _ = run("grep -n 'water\\|hud\\|senses\\|membrane' /opt/Gaia/runtime/gaia_gate.pi 2>/dev/null | head -20")
print(f"gate routes (water/hud):\n{out}\n")

# The HUD HTML file itself
out, _ = run("find /opt/Gaia -name 'hud*' -type f | head -20")
print(f"hud files:\n{out}\n")

# The water page
out, _ = run("find /opt/Gaia -path '*/water*' -name '*.html' | head -10")
print(f"water html:\n{out}\n")

# now.json — what the HUD reads
out, _ = run("cat /opt/Gaia/data/now.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -40")
print(f"now.json (first 40 lines):\n{out}\n")

# organism-fabric
out, _ = run("cat /opt/Gaia/data/organism-fabric.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -30")
print(f"organism-fabric:\n{out}\n")

# sourdough-form
out, _ = run("cat /opt/Gaia/data/sourdough-form.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -20")
print(f"sourdough-form:\n{out}\n")

# lan-mycelium-map
out, _ = run("cat /opt/Gaia/data/lan-mycelium-map.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -40")
print(f"lan-mycelium-map:\n{out}\n")

c.close()
