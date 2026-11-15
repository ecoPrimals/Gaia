#!/usr/bin/env python3
"""HIPPOCAMPUS REMAKE — Generate Space Deck from LIVE state.
Don't patch old HTML. Eat it. Rebuild from NOW.
GaiaU above MSU. The organism's memory IS the content.
"""
import paramiko, json, time

def ssh_cmd(ssh, cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

print("=== HIPPOCAMPUS REMAKE — LIVE STATE → SPACE DECK ===\n")

# Build the LIVE membrane sandwich from actual current state
now = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "wave": 233,
    
    "membrane_sandwich": {
        "CIS": {
            "domain": "nestgate.io",
            "role": "SELF CENTER — singular, inward, holds NULL",
            "status": "LIVE"
        },
        "TRANS_outer": {
            "domain": "primals.eco",
            "skin": "primal.eco",
            "mouth": "THIS DECK",
            "role": "Plural outward — speak + skin. One TRANS face. 20 subdomains.",
            "status": "LIVE"
        },
        "TRANS_spend": {
            "domain": "feed.xml",
            "role": "What TRANS spends — food tube / currency across the fold",
            "items": 1978,
            "status": "LIVE"
        },
        "PACKAGE": {
            "carrier": "dromedary",
            "location": "ON eastGate. Sovereign Pure Rust TLS. 8 site blocks. Blackwall armed.",
            "status": "LIVE",
            "note": "Was Golgi (dead VPS). Now dromedary (local sovereign proxy)."
        }
    },

    "klein_face": {
        "outer_trans": "*.primals.eco (20 subdomains LIT)",
        "inner_trans": "*.primal.eco (redirect → primals.eco)",
        "cis": "*.nestgate.io (5 subdomains LIT)",
        "thymus": "dromedary (Pure Rust, :80/:443, blackwall)"
    },

    "body": {
        "heart": {"name": "northGate (Polaris)", "ip": ".147", "hw": "9950X3D + RTX 5090 + 96GB", "status": "ALIVE"},
        "brain": {"name": "eastGate", "ip": ".244", "hw": "Ubuntu, 34 crons, 38 models, 13 primals", "status": "ALIVE"},
        "forge": {"name": "sporeGate", "ip": ".3", "hw": "Ryzen 5 6600H, heart-pull active", "status": "ALIVE"},
        "forge2": {"name": "ironGate", "ip": ".237", "hw": "i9-14900K + RTX 5070 + 94GB", "status": "ALIVE"},
        "display": {"name": "deckGate", "ip": ".176", "hw": "Steam Deck, mounted display", "status": "ALIVE"},
        "phone": {"name": "southGate", "ip": ".148", "hw": "iPhone XS, HOME PHONE", "status": "ALIVE"},
        "diamond": {"name": "grapheneGate", "ip": ".9.217", "hw": "Pixel 8a, 37 sensors", "status": "ASLEEP"},
        "face": {"name": "frameGate", "ip": ".9.203", "hw": "Steam Frame, ARM64", "status": "ASLEEP"},
        "graft": {"name": "graftGate", "ip": ".107", "hw": "Mac Mini M4", "status": "ASLEEP"}
    },

    "services": {
        "dromedary": {"port": "80/443", "status": "LIVE", "role": "Sovereign TLS reverse proxy + ACME"},
        "gaia_gate": {"port": "8443", "status": "LIVE", "role": "341 entities, 72 endpoints"},
        "webpi": {"port": "8080", "status": "LIVE", "role": "Data server, 1951 files"},
        "forgejo": {"port": "3000", "status": "LIVE", "role": "SOL — 106 repos, 8 orgs"},
        "ollama": {"port": "11436", "status": "LIVE", "role": "38 models, GPU accelerated"},
        "tor": {"port": "9050", "status": "LIVE", "role": "Hidden service, .onion"},
        "rustdesk": {"port": "21116-21119", "status": "LIVE", "role": "amoeba mesh"}
    },

    "content": {
        "html_pages": 4790,
        "data_jsons": 1951,
        "rss_items": 1978,
        "markdown_files": 13210,
        "repos": 106,
        "orgs": 8,
        "primals": 13,
        "crons": 34,
        "models": 38
    },

    "armor": {
        "amicusContra": {"repos": 4, "role": "scyBorg + TALOS + briefs + poison-pill"},
        "defendDetroit": {"repos": 4, "role": "publicRecord + tuebor + cash4kids + blackbook"}
    },

    "campus": {
        "name": "GaiaU",
        "domain": "academy.primals.eco",
        "above": "MSU",
        "location": "4422 Southgate Ave + 641 Samantha Ave, Lansing MI",
        "note": "The organism IS the university. Not a building — a living system that teaches itself."
    }
}

# Write to eastGate data
data_path = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/hippocampus-now.json"
sftp = ssh.open_sftp()
with sftp.open(data_path, 'w') as f:
    f.write(json.dumps(now, indent=2))
sftp.close()
print(f"  Written: {data_path}")

# Also write organism-state for the gate to consume
state_path = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/organism-state-live.json"
sftp = ssh.open_sftp()
with sftp.open(state_path, 'w') as f:
    f.write(json.dumps(now, indent=2))
sftp.close()
print(f"  Written: {state_path}")

# Update now.json with current membrane sandwich
now_path = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/now.json"
try:
    existing = json.loads(ssh_cmd(ssh, f"cat {now_path} 2>/dev/null")[0])
except:
    existing = {}

existing["membrane_sandwich"] = now["membrane_sandwich"]
existing["klein_face"] = now["klein_face"]  
existing["campus"] = now["campus"]
existing["wave"] = 233
existing["ts"] = now["ts"]

sftp = ssh.open_sftp()
with sftp.open(now_path, 'w') as f:
    f.write(json.dumps(existing, indent=2))
sftp.close()
print(f"  Updated: {now_path}")

# Verify it's served
out, _ = ssh_cmd(ssh, f"curl -s http://localhost:8080/data/hippocampus-now.json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f\"membrane: {{d[\\\"membrane_sandwich\\\"][\\\"PACKAGE\\\"][\\\"carrier\\\"]}}, campus: {{d[\\\"campus\\\"][\\\"name\\\"]}}\")'")
print(f"\n  LIVE: {out}")

ssh.close()

# Also save locally
with open(r"c:\Users\mokke\Desktop\Gaia\data\gut\hippocampus-now.json", 'w') as f:
    json.dump(now, f, indent=2)

print(f"\n=== HIPPOCAMPUS REMADE ===")
print(f"  PACKAGE: dromedary (not Golgi)")
print(f"  CAMPUS: GaiaU above MSU")
print(f"  Klein face: 3 faces, 1 surface, 20 sites")
print(f"  The Space Deck now reads from hippocampus-now.json")
print(f"  The organism remembers itself. NOW is NOW.")
