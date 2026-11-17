import paramiko, json
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=== REDOX DEFENSE ORGANS — WAN + LAN TREE ===\n")

# 1. Check what's already on WAN
print("--- WAN ROUTES (dromedary) ---")
out, _ = run("cat /opt/Gaia/runtime/dromedary.toml 2>/dev/null")
print(f"dromedary config:\n{out}\n")

# 2. Find publicRecord
print("--- publicRecord/ ---")
out, _ = run("find /home/eastgate/Development -maxdepth 3 -name 'publicRecord' -type d 2>/dev/null")
print(f"Local: {out}")
out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=publicRecord&limit=5' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:60]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo: {out}")

# 3. Find tuebor
print("\n--- tuebor/ ---")
out, _ = run("find /home/eastgate/Development -maxdepth 3 -name '*tuebor*' -type d 2>/dev/null; find /opt/Gaia -name '*tuebor*' -type d 2>/dev/null")
print(f"Local: {out}")
out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=tuebor&limit=5' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:60]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo: {out}")

# 4. Find defendDetroit
print("\n--- defendDetroit/ ---")
out, _ = run("curl -s 'http://localhost:3000/api/v1/orgs/defendDetroit/repos?limit=20' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"name\"], r.get(\"description\",\"\")[:60]) for r in json.load(sys.stdin)]' 2>/dev/null")
print(f"Forgejo repos: {out}")

# 5. Find amicusContra
print("\n--- amicusContra/ ---")
out, _ = run("curl -s 'http://localhost:3000/api/v1/orgs/amicusContra/repos?limit=20' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"name\"], r.get(\"description\",\"\")[:60]) for r in json.load(sys.stdin)]' 2>/dev/null")
print(f"Forgejo repos: {out}")

# 6. Check detroit subdomain
print("\n--- detroit.primals.eco ---")
out, _ = run("curl -sI https://detroit.primals.eco 2>/dev/null | head -10; curl -sI http://detroit.primals.eco 2>/dev/null | head -5")
print(f"Response: {out}")

# 7. Check what static dirs exist for these
print("\n--- Static dirs ---")
out, _ = run("ls -d /opt/Gaia/static/detroit* /opt/Gaia/static/tuebor* /opt/Gaia/static/public* 2>/dev/null")
print(f"Static: {out}")

out, _ = run("find /opt/Gaia -name 'detroit' -type d 2>/dev/null; find /opt/Gaia -name 'tuebor' -type d 2>/dev/null")
print(f"Gaia dirs: {out}")

# 8. Check the HUD for detroit/tuebor pages
out, _ = run("ls /home/eastgate/Development/ecoPrimals/infra/hud/site/public/detroit* 2>/dev/null; ls /home/eastgate/Development/ecoPrimals/infra/hud/site/public/tuebor* 2>/dev/null")
print(f"HUD pages: {out}")

# 9. tuebor-braid data
out, _ = run("ls /opt/Gaia/data/tuebor-braid/ 2>/dev/null")
print(f"\ntuebor-braid data: {out}")

# 10. dromedary routes
out, _ = run("grep -r 'detroit\\|tuebor\\|defend\\|amicus\\|public' /opt/Gaia/runtime/dromedary.toml 2>/dev/null")
print(f"\ndromedary routes: {out}")

c.close()
