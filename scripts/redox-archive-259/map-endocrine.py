import paramiko, json, datetime
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=== ENDOCRINE GLAND MAPPING ===\n")

# What RSS/gut data does eastGate produce?
print("--- eastGate GUT (pituitary source) ---")
out, _ = run("ls -la /opt/Gaia/data/gut/ 2>/dev/null | tail -15")
print(f"Gut contents:\n{out}\n")

out, _ = run("ls -la /opt/Gaia/data/rss/ 2>/dev/null | tail -10")
print(f"RSS contents:\n{out}\n")

out, _ = run("cat /opt/Gaia/data/gut/rss-drain.json 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(f\"RSS items: {len(d) if isinstance(d,list) else d.get(\\\"count\\\",\\\"?\\\")}\")'  2>/dev/null")
print(f"RSS drain: {out}")

# What does the Frame solar feed look like?
print("\n--- Frame solar feed (what the Frame currently eats) ---")
out, _ = run("tail -3 /opt/Gaia/data/body/frame-solar-feed.jsonl 2>/dev/null")
print(f"Last entries:\n{out}\n")

# What runs on the Frame already?
print("--- Frame processes (via ADB) ---")

# ironMountain contents (pancreas archive)
print("--- ironMountain (pancreas substrate) ---")
out, _ = run("ls /opt/Gaia/data/ironMountain/ 2>/dev/null | wc -l")
print(f"ironMountain bones: {out}")
out, _ = run("ls /opt/Gaia/data/ironMountain/ 2>/dev/null | tail -15")
print(f"Recent bones:\n{out}\n")

# Willis circulation — the blood flow
print("--- Willis circulation (blood carrying hormones) ---")
out, _ = run("cat /opt/Gaia/data/willis-circulation.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -30")
print(f"{out}\n")

# sourDough fermentation state
print("--- sourDough (fermentation engine) ---")
out, _ = run("cat /opt/Gaia/data/sourdough-form.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -20")
print(f"{out}\n")

# heart-pull.json — what Polaris absorbs
print("--- heart-pull (what gates absorb) ---")
out, _ = run("cat /opt/Gaia/data/heart-pull.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -20")
print(f"{out}\n")

# Check what crons drip data
print("--- Cron drip schedule (hormone pulses) ---")
out, _ = run("crontab -l 2>/dev/null | grep -E 'rss|drain|feed|solar|frame|publish|masticate|ferment|sourdough' | head -10")
print(f"{out}\n")

# Waterlock — intake valve
print("--- Waterlock (OSINT intake valve) ---")
out, _ = run("cat /opt/Gaia/data/waterlock-state.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -15")
print(f"{out}\n")

c.close()
print("=== DONE ===")
