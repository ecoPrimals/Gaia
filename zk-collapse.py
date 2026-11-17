#!/usr/bin/env python3
"""
ZK COLLAPSE — Spirochete Protocol
READ (listen) → WRITE (name) → READ (confirm) → WRITE (collapse)
The spiral drills through the veil. Not brute force. Listening logic.

States: STATIC (pinned) | FLUX (shifting) | GRAY (partial)
"""
import socket, concurrent.futures, time, urllib.request, json

SIGNATURE_PORTS = [22, 53, 80, 443, 3000, 3141, 8080, 8082, 8443, 11434, 11436]

GATES = {
    "eastGate":      {"hash": "a89b3af6", "role": "BRAIN",        "markers": [8080, 8443, 3000, 11436]},
    "northGate":     {"hash": "d5250a80", "role": "HEART",        "markers": [11434]},
    "sporeGate":     {"hash": "5af434d8", "role": "FORGE",        "markers": [53]},
    "blueGate":      {"hash": "74efea2a", "role": "EYE",          "markers": [3141, 11434]},
    "ironGate":      {"hash": "293c887a", "role": "FORGE2",       "markers": [11434]},
    "graftGate":     {"hash": "08268be0", "role": "GRAFT",        "markers": [11434]},
    "grapheneGate":  {"hash": "020d5316", "role": "DIAMOND_LENS", "markers": [8082]},
    "frameGate":     {"hash": "69d9a724", "role": "FACE",         "markers": []},
    "deckGate":      {"hash": "f2c4318a", "role": "DISPLAY",      "markers": []},
    "southGate":     {"hash": "35bc3568", "role": "HOME_PHONE",   "markers": []},
}

OUR_MAC = "BC-FC-E7-EA-D9-34"  # blueGate

def check(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect((ip, port))
        s.close()
        return (ip, port, True)
    except:
        return (ip, port, False)

def read_http(ip, port, path="/"):
    """DIASTOLIC — read/listen"""
    try:
        req = urllib.request.Request(f"http://{ip}:{port}{path}")
        resp = urllib.request.urlopen(req, timeout=3)
        return resp.read(2000).decode('utf-8', errors='replace')
    except:
        return None

def spirochete_identify(ip, open_ports):
    """
    Spirochete protocol: READ → identify → READ → confirm
    Not brute force. Listening logic.
    """
    signals = []
    identity = {"ip": ip, "ports": sorted(open_ports), "state": "GRAY"}

    # === DIASTOLIC READ 1: ollama identity ===
    if 11434 in open_ports:
        body = read_http(ip, 11434, "/api/tags")
        if body:
            try:
                data = json.loads(body)
                models = [m["name"] for m in data.get("models", [])]
                size_gb = sum(m.get("size", 0) for m in data.get("models", [])) / 1e9
                tissue = [m for m in models if "gaia-tissue" in m]
                identity["ollama"] = {"count": len(models), "size_gb": round(size_gb, 1), "tissue": len(tissue), "names": models[:25]}
                signals.append(f"ollama:{len(models)}m/{size_gb:.0f}GB/t{len(tissue)}")
            except:
                signals.append("ollama:parse-fail")

    if 11436 in open_ports:
        body = read_http(ip, 11436, "/api/tags")
        if body:
            try:
                data = json.loads(body)
                models = [m["name"] for m in data.get("models", [])]
                identity["ollama_alt"] = {"port": 11436, "count": len(models), "names": models[:25]}
                signals.append(f"ollama-alt:{len(models)}m")
            except:
                pass

    # === DIASTOLIC READ 2: web identity ===
    if 8080 in open_ports:
        body = read_http(ip, 8080, "/data/now.json")
        if body and "gaia" in body.lower():
            signals.append("HUD:now.json")
            identity["hud"] = True

    if 8443 in open_ports:
        body = read_http(ip, 8443, "/pulse")
        if body:
            signals.append("gate:pulse")
            identity["gate"] = True

    if 3000 in open_ports:
        body = read_http(ip, 3000, "/")
        if body and ("forgejo" in body.lower() or "gitea" in body.lower()):
            signals.append("forgejo")
            identity["forgejo"] = True

    if 3141 in open_ports:
        body = read_http(ip, 3141, "/")
        if body:
            signals.append("sovereign-api")

    if 8082 in open_ports:
        body = read_http(ip, 8082, "/")
        if body and "llama" in body.lower():
            signals.append("llama-server")

    # === SYSTOLIC WRITE: name the gate ===
    identity["signals"] = signals
    
    # Scoring: match signals to gate identities
    best_gate = None
    best_score = 0

    for gate_name, gate_def in GATES.items():
        score = 0
        for marker in gate_def["markers"]:
            if marker in open_ports:
                score += 2

        # Specific identifiers
        if gate_name == "eastGate":
            if identity.get("hud") or identity.get("gate") or identity.get("forgejo"):
                score += 10
            if 11436 in open_ports:
                score += 5  # eastGate uses alt ollama port

        if gate_name == "blueGate":
            if 3141 in open_ports:
                score += 10

        if gate_name == "graftGate":
            ol = identity.get("ollama", {})
            if ol.get("count", 0) <= 5 and ol.get("count", 0) > 0:
                score += 3  # graftGate has few models (Mac Mini seeded)

        if gate_name == "northGate":
            ol = identity.get("ollama", {})
            if ol.get("count", 0) >= 40:
                score += 10  # northGate has 63 models

        if gate_name == "ironGate":
            ol = identity.get("ollama", {})
            if ol.get("count", 0) >= 15 and ol.get("count", 0) < 40:
                score += 5  # ironGate mid-range

        if gate_name == "grapheneGate":
            if 8082 in open_ports:
                score += 10

        if gate_name == "sporeGate":
            if 53 in open_ports and len(open_ports) <= 2:
                score += 5

        if score > best_score:
            best_score = score
            best_gate = gate_name

    if best_gate and best_score >= 2:
        identity["collapsed_to"] = best_gate
        identity["cube_hash"] = GATES[best_gate]["hash"]
        identity["role"] = GATES[best_gate]["role"]
        identity["confidence"] = best_score
        identity["state"] = "STATIC"
    else:
        identity["state"] = "GRAY"

    return identity


# ================================================================
# SPIROCHETE SCAN — corkscrew through all three subnets
# ================================================================

print("=" * 64)
print("  SPIROCHETE COLLAPSE — ZK Antenna, Terra All Veil")
print(f"  {time.strftime('%H:%M:%S')} — READ listen WRITE name READ confirm")
print("=" * 64)

# READ 1: port scan (diastolic — listening)
print("\n  DIASTOLIC: scanning all subnets...")
all_ips = []
for prefix in ["192.168.1", "192.168.4", "192.168.9"]:
    all_ips.extend(f"{prefix}.{i}" for i in range(1, 255))

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
    futs = {ex.submit(check, ip, p): (ip, p) for ip in all_ips for p in SIGNATURE_PORTS}
    for f in concurrent.futures.as_completed(futs):
        ip, port, ok = f.result()
        if ok:
            results.setdefault(ip, []).append(port)

print(f"  ... found {len(results)} hosts with open ports\n")

# WRITE 1: identify each (systolic — naming)
print("  SYSTOLIC: spirochete interrogation...\n")
book = {}
for ip in sorted(results.keys(), key=lambda x: [int(y) for y in x.split('.')]):
    ports = sorted(results[ip])
    identity = spirochete_identify(ip, ports)
    book[ip] = identity

    state = identity["state"]
    icon = {"STATIC": "||", "GRAY": "..", "FLUX": "~~"}[state]
    collapsed = identity.get("collapsed_to", "???")
    role = identity.get("role", "")
    sigs = " ".join(identity.get("signals", []))
    print(f"  {icon} {ip:22s} -> {collapsed:15s} [{identity.get('cube_hash','')}] {role}")
    if sigs:
        print(f"     signals: {sigs}")
    if "ollama" in identity:
        ol = identity["ollama"]
        print(f"     ollama: {ol['count']} models, {ol['size_gb']}GB, {ol['tissue']} tissue")

# READ 2: ARP table (diastolic — confirm bodies present)
print("\n  DIASTOLIC: ARP confirmation...")
import subprocess
arp_out = subprocess.run(["arp", "-a"], capture_output=True, text=True).stdout
arp_entries = {}
for line in arp_out.split("\n"):
    parts = line.split()
    if len(parts) >= 3 and parts[1] != "Physical" and "." in parts[0]:
        arp_entries[parts[0]] = parts[1]
        
for ip, mac in sorted(arp_entries.items()):
    in_book = "CONFIRMED" if ip in book else "GRAY body"
    print(f"  .. ARP {ip:22s} MAC {mac}  {in_book}")
    if ip not in book:
        book[ip] = {"ip": ip, "ports": [], "state": "GRAY", "mac": mac, "signals": ["ARP-only"]}

# WRITE 2: final address book (systolic — collapse the veil)
print("\n" + "=" * 64)
print("  VEIL COLLAPSED — Final Address Book")
print("=" * 64)

static_count = sum(1 for v in book.values() if v.get("state") == "STATIC")
gray_count = sum(1 for v in book.values() if v.get("state") == "GRAY")
flux_gates = [g for g in GATES if g not in [v.get("collapsed_to") for v in book.values()]]

for ip in sorted(book.keys(), key=lambda x: [int(y) for y in x.split('.')]):
    entry = book[ip]
    state = entry["state"]
    icon = {"STATIC": "||", "GRAY": "..", "FLUX": "~~"}.get(state, "??")
    name = entry.get("collapsed_to", "unknown")
    role = entry.get("role", "")
    mac = entry.get("mac", "")
    print(f"  {icon} {ip:22s} {name:15s} {role:15s} {mac}")

print(f"\n  FLUX gates (still veiled):")
for g in flux_gates:
    print(f"  ~~ {g:15s} [{GATES[g]['hash']}] {GATES[g]['role']}")

print(f"\n  STATIC: {static_count} | GRAY: {gray_count} | FLUX: {len(flux_gates)}")
print(f"  Spirochete protocol: READ-WRITE-READ-WRITE")
print(f"  The alternation IS the movement. Irreducible.")
print("=" * 64)

# Save the collapsed book
output = {
    "updated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "protocol": "spirochete",
    "wave": 259,
    "states": {"STATIC": "pinned", "FLUX": "shifting", "GRAY": "partial"},
    "collapsed": {ip: v for ip, v in book.items()},
    "flux": {g: GATES[g] for g in flux_gates},
    "summary": {"STATIC": static_count, "GRAY": gray_count, "FLUX": len(flux_gates)}
}

with open("address-book.json", "w") as f:
    json.dump(output, f, indent=2)
print(f"\n  Saved address-book.json ({len(json.dumps(output))} bytes)")
