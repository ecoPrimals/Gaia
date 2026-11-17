import paramiko, time
time.sleep(3)
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=20,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=25)
_, o, _ = c.exec_command('cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git pull forgejo main --no-rebase --no-edit', timeout=15)
print(o.read().decode())
c.close()
