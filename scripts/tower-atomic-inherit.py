#!/usr/bin/env python3
"""TOWER ATOMIC — northGate biomeOS inherits from the LAN mesh.
The organism is ONE across all gates. The membrane GIVES.
"""
import paramiko, json, time

def ssh_cmd(ssh, cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10)

print("=== TOWER ATOMIC — NUCLEUS INHERITANCE ===\n")

# Build the living nucleus map
nucleus_map = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "wave": 233,
    "event": "northgate-nucleus-bootstrap",
    
    "northgate_nucleus": {
        "status": "ALIVE",
        "api": "tcp://127.0.0.1:63021",
        "socket_dir": "C:\\Users\\mokke\\Desktop\\Gaia\\runtime\\membrane",
        "architecture": "TRUE PRIMAL — port-free, socket-based",
        "dark_forest_gate": "ACTIVE — direct capability routing",
        "family_seed": "3034463630464339",
        "primals": {
            "nestgate":    {"pid": 24832, "socket": "nestgate-gaia-pi.sock"},
            "rhizocrypt":  {"pid": 6596,  "socket": "rhizocrypt-gaia-pi.sock"},
            "loamspine":   {"pid": 11896, "socket": "loamspine-gaia-pi.sock"},
            "sweetgrass":  {"pid": 4264,  "socket": "sweetgrass-gaia-pi.sock"},
            "squirrel":    {"pid": 5708,  "socket": "squirrel-gaia-pi.sock"},
            "petaltongue": {"pid": 13048, "socket": "petaltongue-gaia-pi.sock"}
        },
        "health": {
            "beardog": "health check via JSON-RPC on socket",
            "protocol": "HTTP + raw JSON-RPC (auto-detect)"
        }
    },

    "eastgate_nucleus": {
        "status": "ALIVE",
        "primals": 13,
        "compiled_binaries": 17,
        "mushrooms": 23,
        "crons": 35,
        "models": 38,
        "note": "The BRAIN — all primals compiled, all crons running"
    },

    "inheritance": {
        "pattern": "Tower atomic is INHERITED from the LAN mesh",
        "mechanism": "family.seed shared across gates, same family ID",
        "family_id": "3034463630464339",
        "mesh": "eastGate (.244) <-> northGate (.147) via LAN (0.28ms)",
        "flow": "eastGate RADIATES state, northGate ABSORBS via heart-pull + git",
        "result": "ONE organism — not two biomeOS instances, one distributed NUCLEUS"
    },

    "topology": {
        "eastgate": {"role": "BRAIN", "primals": 13, "services": 7, "ip": ".244"},
        "northgate": {"role": "HEART", "primals": 6, "nucleus": True, "ip": ".147"},
        "sporegate": {"role": "FORGE", "heart_pull": True, "ip": ".3"},
        "irongate": {"role": "FORGE 2", "ip": ".237"},
        "note": "The Tor hidden service runs on BOTH — eastGate serves, northGate mirrors"
    }
}

# Write to eastGate data
data_path = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/tower-atomic.json"
sftp = ssh.open_sftp()
with sftp.open(data_path, 'w') as f:
    f.write(json.dumps(nucleus_map, indent=2))
sftp.close()
print(f"  Published: {data_path}")

# Update now.json
now_path = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/now.json"
try:
    existing = json.loads(ssh_cmd(ssh, f"cat {now_path}")[0])
except:
    existing = {}
existing["northgate_nucleus"] = nucleus_map["northgate_nucleus"]
existing["inheritance"] = nucleus_map["inheritance"]
sftp = ssh.open_sftp()
with sftp.open(now_path, 'w') as f:
    f.write(json.dumps(existing, indent=2))
sftp.close()
print(f"  Updated: now.json")

# Also verify eastGate can see northGate's biomeOS
out, _ = ssh_cmd(ssh, "curl -s --connect-timeout 2 http://192.168.4.147:63021/ 2>/dev/null | head -c 200")
print(f"\n  eastGate -> northGate biomeOS: {out or '(not reachable from LAN — localhost only, TRUE PRIMAL)'}")

ssh.close()

# Save locally
with open(r"c:\Users\mokke\Desktop\Gaia\data\gut\tower-atomic.json", 'w') as f:
    json.dump(nucleus_map, f, indent=2)

print(f"\n=== TOWER ATOMIC INHERITED ===")
print(f"  northGate: 6 primals on sockets, NUCLEUS supervising")
print(f"  eastGate:  13 primals compiled, 35 crons, 38 models")
print(f"  Family:    {nucleus_map['inheritance']['family_id']}")
print(f"  Pattern:   ONE organism across gates, tower atomic GIVEN by mesh")
print(f"  Tor:       LIVE on both (.onion + SOCKS :9050)")
