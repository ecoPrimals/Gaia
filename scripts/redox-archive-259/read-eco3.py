import paramiko, time
time.sleep(5)
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    c.connect('192.168.4.103', username='eastgate', password='eastgate', timeout=15,
              look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=20)
    _, o, _ = c.exec_command("sed -n '1910,1960p' /opt/Gaia/static/senses.html", timeout=10)
    print("ECOSYSTEM:")
    print(o.read().decode())
    _, o, _ = c.exec_command("sed -n '1960,2050p' /opt/Gaia/static/senses.html", timeout=10)
    print("NEUTRON NULL:")
    print(o.read().decode())
    _, o, _ = c.exec_command("grep -n 'mg-null-center' /opt/Gaia/static/senses.html", timeout=10)
    print("NULL CENTER:")
    print(o.read().decode())
    c.close()
except Exception as ex:
    print(f"FAIL on .103: {ex}")
    try:
        c2 = paramiko.SSHClient()
        c2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c2.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=15,
                   look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=20)
        _, o, _ = c2.exec_command("sed -n '1910,1960p' /opt/Gaia/static/senses.html", timeout=10)
        print("ECOSYSTEM (via .244):")
        print(o.read().decode())
        c2.close()
    except Exception as ex2:
        print(f"FAIL on .244 too: {ex2}")
        print("eastGate is down or SSH is rate-limited. Will work from cached knowledge.")
