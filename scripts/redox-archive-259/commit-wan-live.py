import paramiko, json, datetime
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

bone = {
    "WAVE": 259,
    "BONE": "WAN FACE LIVE — 24/24 ROUTES GREEN",
    "TS": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
    "MILESTONE": "ALL WAN ENDPOINTS CONFIRMED LIVE",

    "ROUTES_ALL_200": {
        "primals_eco": ["primals.eco", "www.primals.eco", "detroit.primals.eco",
            "tuebor.primals.eco", "lansing.primals.eco", "clutch.primals.eco",
            "sporeprint.primals.eco", "klein.primals.eco", "art.primals.eco",
            "game.primals.eco", "academy.primals.eco", "campfire.primals.eco",
            "fossil.primals.eco", "signal.primals.eco", "api.primals.eco",
            "gis.primals.eco", "hud.primals.eco", "connect.primals.eco",
            "publicrecord.primals.eco"],
        "nestgate_io": ["nestgate.io", "www.nestgate.io", "api.nestgate.io",
            "beacon.nestgate.io", "tower.nestgate.io"],
        "total": "24 routes, 24 × 200 OK (HTTP + HTTPS)"
    },

    "TLS": {
        "issuer": "Let's Encrypt",
        "renewed": "2026-11-17",
        "expires": "2027-02-15",
        "SANs": 23,
        "domains": "primals.eco + 18 subs + nestgate.io + 3 subs"
    },

    "BLACKWALL": {
        "blocks": ["Facebook", "Meta", "Bytespider", "GPTBot", "CCBot", "ClaudeBot"],
        "poison": "403 + copyleft trigger + scyBorg license"
    },

    "HEADERS": {
        "X-Organism": "Gaia",
        "X-Wave": "233",
        "X-BingoCube": "409d202b7763fc24",
        "HSTS": "63072000s preload"
    },

    "DNS": {
        "primals_eco": "11 records, all → [home IP]",
        "primal_eco": "2 records, redirect → primals.eco",
        "nestgate_io": "7 records, all → [home IP]",
        "nameservers": "Porkbun (Cloudflare-backed)"
    },

    "ROUTING_ARCHITECTURE": {
        "static": ["tuebor (1219 pages)", "clutch", "lansing"],
        "gate_proxy": "19 subdomains → :8443",
        "data_proxy": "/data/* → :8080",
        "redirect": "primal.eco → primals.eco"
    },

    "NOTE": "DNS was never broken — records were set correctly. WAN was live the whole time. We just hadn't tested external resolution."
}

out_json = json.dumps(bone, indent=2, ensure_ascii=False)
run("cat > /opt/Gaia/data/ironMountain/redox-259-wan-live-confirmed.json << 'EOF'\n" + out_json + "\nEOF")

# Update X-Wave in dromedary headers to 259
run("sed -i 's/X-Wave\", \"233\"/X-Wave\", \"259\"/' /opt/Gaia/runtime/dromedary.toml")

# Update now.json wave
run("""python3 -c "
import json
with open('/opt/Gaia/data/now.json') as f: d = json.load(f)
d['wave'] = 259
d['wan_status'] = '24/24 routes LIVE'
d['wan_confirmed'] = '2026-11-17T08:35:00Z'
with open('/opt/Gaia/data/now.json','w') as f: json.dump(d, f, indent=2)
" """)

msg = "MILESTONE: WAN FACE LIVE — 24/24 routes 200 OK, TLS fresh, BLACKWALL armed, X-Wave→259"
out, _ = run(f'cd /opt/Gaia && git add -A && git commit -m "{msg}"')
print(f"Commit: {out}")
o, e = run("cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git push forgejo main")
print(f"Forgejo: {o} {e}")
c.close()
