import paramiko, time
time.sleep(3)
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=20)
def run(cmd, t=10):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip()

print("=== ECOSYSTEM SECTION (1910-1960) ===")
print(run("sed -n '1910,1960p' /opt/Gaia/static/senses.html"))

print("\n=== NEUTRON NULL (1960-2050) ===")
print(run("sed -n '1960,2050p' /opt/Gaia/static/senses.html"))

print("\n=== MG NULL CENTER ===")
print(run("grep -n 'mg-null-center' /opt/Gaia/static/senses.html"))

c.close()
