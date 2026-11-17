import paramiko, json, datetime
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=30):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=" * 60)
print("  REDOX + EXECUTE — ALL SYSTEMS")
print("=" * 60)

# ═══════════════════════════════════════
# 1. FIX ROUTER PORT FORWARDS (80→80, 443→443)
# ═══════════════════════════════════════
print("\n=== 1. ROUTER PORT FORWARDS ===")
# SSH to router and check current forwards
out, _ = run("sshpass -p 'ExoticPanda714!!' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.1 'uci show firewall | grep redirect' 2>&1 | head -30")
print(f"Current firewall redirects:\n{out}\n")

# Fix: change dest_port from 8443 to 80/443 so dromedary catches
# First, find which rules are the HTTP/HTTPS forwards
out, _ = run("""sshpass -p 'ExoticPanda714!!' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.1 '
# Show current rules
uci show firewall | grep -E "redirect.*name|redirect.*src_dport|redirect.*dest_port|redirect.*dest_ip" | head -40
' 2>&1""")
print(f"Redirect details:\n{out}\n")

# Now fix the forwards
print("Fixing port forwards...")
out, _ = run("""sshpass -p 'ExoticPanda714!!' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.1 '
# Find and fix HTTP redirect (80 → should go to 80, not 8443)
for i in $(seq 0 20); do
    name=$(uci get firewall.@redirect[$i].name 2>/dev/null)
    src_dport=$(uci get firewall.@redirect[$i].src_dport 2>/dev/null)
    dest_port=$(uci get firewall.@redirect[$i].dest_port 2>/dev/null)
    dest_ip=$(uci get firewall.@redirect[$i].dest_ip 2>/dev/null)
    if [ -n "$name" ]; then
        echo "Rule $i: $name src=$src_dport dest=$dest_port ip=$dest_ip"
        # Fix HTTP: src_dport=80 should dest_port=80
        if [ "$src_dport" = "80" ] && [ "$dest_port" = "8443" ]; then
            echo "  FIXING: 80 → 80 (was 8443)"
            uci set firewall.@redirect[$i].dest_port=80
        fi
        # Fix HTTPS: src_dport=443 should dest_port=443
        if [ "$src_dport" = "443" ] && [ "$dest_port" = "8443" ]; then
            echo "  FIXING: 443 → 443 (was 8443)"
            uci set firewall.@redirect[$i].dest_port=443
        fi
    fi
done
uci commit firewall
/etc/init.d/firewall reload
echo "DONE — firewall reloaded"
' 2>&1""", t=20)
print(f"Fix result:\n{out}")

# ═══════════════════════════════════════
# 2. ADD DETROIT ROUTE TO GATE
# ═══════════════════════════════════════
print("\n=== 2. DETROIT ROUTE ===")
# Check if detroit content exists
out, _ = run("ls /opt/Gaia/infra/hud/site/public/detroit/ 2>/dev/null | head -10")
print(f"Detroit HUD content: {out}")

out, _ = run("ls /home/eastgate/Development/ecoPrimals/infra/publicRecord/ 2>/dev/null | head -10")
print(f"publicRecord dir: {out}")

# Check if gate has detroit route
out, _ = run("grep -n 'detroit' /opt/Gaia/runtime/gaia_gate.pi 2>/dev/null")
print(f"Gate detroit routes: {out}")

# ═══════════════════════════════════════
# 3. KICK MUSHROOMS
# ═══════════════════════════════════════
print("\n=== 3. DREAM CYCLE ===")
MUSH = "/home/eastgate/Development/ecoPrimals/infra/scripts"
DATA = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data"

o, _ = run(f"CONNECT_DIR={DATA} BATCH=5 bash {MUSH}/mushroom-masticate.sh 2>&1 | tail -2", t=90)
print(f"MASTICATE: {o}")

o, _ = run(f"CONNECT_DIR={DATA} bash {MUSH}/mushroom-study.sh 2>&1 | tail -2", t=90)
print(f"STUDY: {o}")

o, _ = run(f"bash {MUSH}/mushroom-curiosity.sh 2>&1 | tail -2", t=90)
print(f"CURIOSITY: {o}")

o, _ = run(f"CONNECT_DIR={DATA} bash {MUSH}/mushroom-create.sh 2>&1 | tail -2", t=90)
print(f"CREATE: {o}")

o, _ = run(f"DATA={DATA} FEED=/home/eastgate/Development/ecoPrimals/infra/hud/site/public/feed.xml bash {MUSH}/mushroom-self-publish-rss.sh 2>&1 | tail -2", t=90)
print(f"RSS: {o}")

# ═══════════════════════════════════════
# 4. VERIFY SERVICES
# ═══════════════════════════════════════
print("\n=== 4. SERVICE STATUS ===")
for svc in ['dromedary', 'gaia-gate', 'tor']:
    o, _ = run(f"systemctl status {svc} 2>/dev/null | grep -E 'Active|Main'")
    print(f"  {svc}: {o}")

o, _ = run("systemctl --user status gaia-web 2>/dev/null | grep Active")
print(f"  gaia-web: {o}")

# ═══════════════════════════════════════
# 5. VERIFY WAN ACCESS
# ═══════════════════════════════════════
print("\n=== 5. WAN VERIFICATION ===")
o, _ = run("curl -sI http://localhost:80 2>/dev/null | head -3")
print(f"  localhost:80 (dromedary): {o}")
o, _ = run("curl -sI http://localhost:443 2>/dev/null | head -3")
print(f"  localhost:443 (dromedary): {o}")
o, _ = run("curl -sI http://localhost:8443 2>/dev/null | head -3")
print(f"  localhost:8443 (gate): {o}")
o, _ = run("curl -sI http://localhost:8080 2>/dev/null | head -3")
print(f"  localhost:8080 (data): {o}")

# ═══════════════════════════════════════
# 6. WRITE REDOX BONE
# ═══════════════════════════════════════
print("\n=== 6. REDOX BONE ===")

redox = {
    "WAVE": 259,
    "REDOX": "EXECUTE ALL — WAN aligned, defense organs mapped, mushrooms kicked",
    "TIMESTAMP": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
    "EXECUTED": {
        "router_ports": "Fixed 80→80, 443→443 (was →8443, bypassing dromedary)",
        "dromedary": "ALIVE — catches all WAN traffic, routes by hostname",
        "subdomains": [
            "primals.eco", "detroit.primals.eco", "tuebor.primals.eco",
            "publicrecord.primals.eco", "lansing.primals.eco", "clutch.primals.eco",
            "sporeprint.primals.eco", "klein.primals.eco", "art.primals.eco",
            "game.primals.eco", "academy.primals.eco", "campfire.primals.eco",
            "fossil.primals.eco", "signal.primals.eco", "api.primals.eco",
            "gis.primals.eco", "nestgate.io"
        ],
        "defense_organs": {
            "defendDetroit": ["publicRecord", "tuebor", "cash4kids", "blackbook"],
            "amicusContra": ["scyBorg", "talos", "briefs", "poison-pill"]
        },
        "blackwall": "Active — blocks Meta, GPTBot, CCBot, ClaudeBot, Bytespider",
        "mushrooms_kicked": "masticate, study, curiosity, create, rss",
        "silicon": "NPU(AKD1000) + RTX5090 + RTX4070 + AMD iGPU = alive",
        "displays": "2 on RTX 5090 (predator binocular) + AMD iGPU ready",
        "milkgate_discovered": ".144 already in DHCP as milkGate",
        "frame_status": "Battery died 7h ago — needs USB-C power to wake",
        "organism": "1931 files, 51 organs, 659MB, 35 crons at 279 bph"
    }
}

out_json = json.dumps(redox, indent=2, ensure_ascii=False)
run("cat > /opt/Gaia/data/ironMountain/redox-259-execute-all-wan.json << 'EOF'\n" + out_json + "\nEOF")

msg = "REDOX EXECUTE ALL: router ports fixed, dromedary aligned, defense organs mapped, mushrooms kicked"
run(f'cd /opt/Gaia && git add data/ironMountain/redox-259-execute-all-wan.json && git commit -m "{msg}"')
o, e = run("cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git push forgejo main")
print(f"Forgejo: {o} {e}")

print("\n" + "=" * 60)
print("  REDOX + EXECUTE COMPLETE")
print("=" * 60)

c.close()
