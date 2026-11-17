import paramiko, json, datetime
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# Check if bone was already written
out, _ = run("ls /opt/Gaia/data/ironMountain/redox-259-wan-dns-last-plug.json 2>/dev/null")
if not out:
    # Write it fresh
    bone = {"WAVE":259,"BONE":"WAN DNS LAST PLUG","TS":datetime.datetime.now(datetime.UTC).isoformat()+"Z",
            "TLS":"primals.eco Nov17→Feb15 2027","DNS":"NXDOMAIN—Porkbun expired",
            "FIX":"4 A records at noon","FRAME":"alive 10h, ollama+VR+octopus on USB-C ponytail"}
    run("cat > /opt/Gaia/data/ironMountain/redox-259-wan-dns-last-plug.json << 'EOF'\n" + json.dumps(bone,indent=2) + "\nEOF")

out, _ = run('cd /opt/Gaia && git add -A && git status --short | head -5')
print(f"Status: {out}")

msg = "REDOX: WAN ready, TLS fresh, DNS is last plug, Frame alive with VR+ollama+octopus"
out, _ = run(f'cd /opt/Gaia && git commit -m "{msg}" 2>&1')
print(f"Commit: {out}")

o, e = run("cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git push forgejo main")
print(f"Forgejo: {o} {e}")
c.close()
