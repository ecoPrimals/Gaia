import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=20,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=30)

def run(cmd, t=30):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

msg = "REDOX: PUSH ALL - 80 repos pushed, 38 new, 6 orgs synced"
cmd = "cd /opt/Gaia && git add data/ironMountain/redox-259-push-all.json"
out, _ = run(cmd)
print(f"add: {out}")

cmd2 = f'cd /opt/Gaia && git commit -m "{msg}"'
out, _ = run(cmd2)
print(f"commit: {out}")

cmd3 = "cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git push forgejo main"
out, err = run(cmd3)
print(f"push: {out} {err}")

c.close()
