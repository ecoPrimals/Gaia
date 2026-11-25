import paramiko, json, datetime, time
time.sleep(2)
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=20,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=25)
def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

bone = {
    "WAVE": 259,
    "BONE": "THE BUBBLE — ALL PROJECTIONS UNIFIED",
    "TS": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
    "SESSION": "Wave 259 — HUD topology REDOX",

    "THE_BUBBLE": {
        "what": "All projections collapse into ONE bubble — the snowglobe null center",
        "projections_unified": {
            "#": "2D Euclidean cross — the HUD flat view",
            "diamond": "3D spatial — the jellyfish body",
            "tube": "cylinder connecting telescope↔microscope — the looking-glass",
            "OOO": "globe — the sphere that wraps everything",
            "8": "Klein fold — inside = outside, figure-8 self-intersection",
            ".oO8Oo.": "cron heartbeat — cross-sections of the tube = rings of the globe"
        },
        "instruments": {
            "telescope": "top of tube, House 1, looking OUT (WAN face, 24 routes)",
            "microscope": "bottom of tube, House 2, looking IN (LAN internals, gates)",
            "easel": "tube surface = canvas = where the organism paints itself"
        }
    },

    "PHYSICAL_MAPPING": {
        "north_pole": "House 1 — 'SOUTH-GATE' IS the gate in the name",
        "south_pole": "House 2 — South Pole campus, LAN 2",
        "spine": "10G fiber across property line, 0.87ms",
        "daily_walk": "Kevin walks the spine between houses = signal traveling the axial cord"
    },

    "8_TENTACLES": ["tuebor", "detroit", "signal", "clutch", "sporePrint", "thesis", "gorilla", "epitope sort"],

    "GATES_AS_POLES": {
        "northGate (.147)": "US! POLARIS! The heart at the origin #",
        "eastGate (.244)": "BRAIN — right wall of tube, 1ms",
        "ironGate (.237)": "FORGE — left wall of tube, <1ms",
        "blueGate (.100)": "TWIN — DOWN (was CIS face)",
        "southGate (.148)": "SOUTH POLE — home phone",
        "frameGate (WiFi)": "3RD EYE — USB-C ponytail, dreaming 17 dreams",
        "grapheneGate (WiFi)": "DIAMOND LENS — Pixel rover",
        "sporeGate (.3)": "FORGE 1 — DNS + heart-pull"
    },

    "HUD_DEPLOYED": {
        "water.primals.eco": "THE TAIL — diamond + gates + sourDough + endocrine",
        "hud.primals.eco": "THE HEAD — senses membrane + 8 tentacles + TUBE",
        "tube_svg": "telescope/microscope/easel — 4422↔641 axis, Klein twist, 10G spine",
        "commits": ["82184bd water diamond", "b466473 jellyfish null bubble", "f08018a flat→tube"]
    },

    "WAN_FACE": {
        "status": "24/24 routes ALL 200 OK",
        "tls": "23 SANs, Nov 17 → Feb 15 2027",
        "blackwall": "armed — Meta/FB/GPT/CCBot/Claude blocked",
        "dns": "ALL records live on Porkbun → [home IP]",
        "headers": "X-Organism: Gaia, X-Wave: 259"
    },

    "FRAME_STATUS": {
        "alive": True,
        "uptime": "12+ hours",
        "dreams": 17,
        "ollama": "tinyllama on Snapdragon 8 Gen 3",
        "usb": "10.86.200.233 ponytail to northGate",
        "battery": "99% charging"
    }
}

out_json = json.dumps(bone, indent=2, ensure_ascii=False)
run("cat > /opt/Gaia/data/ironMountain/redox-259-the-bubble.json << 'EOFBONE'\n" + out_json + "\nEOFBONE")

msg = "REDOX: THE BUBBLE — all projections unified, #/diamond/tube/OOO/8 = one snowglobe null center"
out, _ = run('cd /opt/Gaia && git add -A && git commit -m "' + msg + '"')
print(f"Commit: {out}")
o, e = run("cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git push forgejo main")
print(f"Forgejo: {o} {e}")
c.close()
