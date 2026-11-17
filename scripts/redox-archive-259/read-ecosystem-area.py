import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# Read lines 1910-1970 — the ecosystem section and neutron null
out, _ = run("sed -n '1910,1970p' /opt/Gaia/static/senses.html")
print(f"Lines 1910-1970:\n{out}\n")

# Read the neutron-null iframe area
out, _ = run("sed -n '1960,2050p' /opt/Gaia/static/senses.html")
print(f"Lines 1960-2050:\n{out}\n")

# Read the membrane SVG section
out, _ = run("grep -n 'mg-null-center\\|null.*center\\|null.*bubble' /opt/Gaia/static/senses.html")
print(f"null center refs:\n{out}\n")

# The membrane geo grid
out, _ = run("sed -n '1690,1745p' /opt/Gaia/static/senses.html")
print(f"Lines 1690-1745 (membrane geo):\n{out}\n")

c.close()
