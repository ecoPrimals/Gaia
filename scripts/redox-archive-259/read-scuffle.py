import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# Find lansingScuffle
print("=== FINDING lansingScuffle ===\n")
out, _ = run("find /home/eastgate/Development -maxdepth 3 -iname '*scuffle*' -o -iname '*lansing*scuffle*' 2>/dev/null")
print(f"Local: {out}")

out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=scuffle&limit=10' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:80]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo: {out}")

out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=lansing&limit=10' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:80]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo lansing: {out}")

# Check all org repos for scuffle-like names
out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=thermal&limit=10' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:80]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo thermal: {out}")

out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=solar&limit=10' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:80]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo solar: {out}")

out, _ = run("curl -s 'http://localhost:3000/api/v1/repos/search?q=soak&limit=10' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"full_name\"], r.get(\"description\",\"\")[:80]) for r in json.load(sys.stdin).get(\"data\",[])]' 2>/dev/null")
print(f"Forgejo soak: {out}")

# Check defendDetroit or sporeGarden for scuffle
for org in ['defendDetroit', 'sporeGarden', 'ecoPrimals', 'protoKarya', 'amicusContra']:
    out, _ = run(f"curl -s 'http://localhost:3000/api/v1/orgs/{org}/repos?limit=50' 2>/dev/null | python3 -c 'import sys,json; [print(r[\"name\"]) for r in json.load(sys.stdin) if \"scuffle\" in r[\"name\"].lower() or \"lansing\" in r[\"name\"].lower() or \"solar\" in r[\"name\"].lower() or \"therm\" in r[\"name\"].lower()]' 2>/dev/null")
    if out:
        print(f"{org}: {out}")

# Maybe it's on GitHub?
print("\n=== Checking GitHub ===")
out, _ = run("curl -sH 'Accept: application/vnd.github+json' 'https://api.github.com/search/repositories?q=lansingScuffle+user:ecoPrimals+user:defendDetroit+user:sporeGarden' 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); [print(r[\"full_name\"],r.get(\"description\",\"\")[:60]) for r in d.get(\"items\",[])]' 2>/dev/null")
print(f"GitHub: {out}")

# Check sourdough process and triad for solar panel concepts
print("\n=== SOURDOUGH + TRIAD solar concepts ===")
out, _ = run("cat /opt/Gaia/data/body/frame-solar-feed.jsonl 2>/dev/null | head -20")
print(f"frame-solar-feed:\n{out}")

out, _ = run("grep -rl 'solar' /opt/Gaia/data/ 2>/dev/null | head -10")
print(f"\nSolar files in Gaia data:\n{out}")

out, _ = run("grep -rl 'therm' /opt/Gaia/data/ 2>/dev/null | head -10")
print(f"\nThermal files:\n{out}")

# Check sourDough patterns
out, _ = run("cat /opt/Gaia/data/sourdough-form.json 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps({k:v for k,v in list(d.items())[:10]}, indent=2))' 2>/dev/null")
print(f"\nSourdough form:\n{out}")

c.close()
