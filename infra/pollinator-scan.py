#!/usr/bin/env python3
"""
Superposition Pollinator — finds gates wherever they are.

R34: If a gate EXISTS, there IS a way to find it.
The pollinator carries identity (pollen) between gates (flowers).
When it LANDS (observes), superposition collapses to one IP.

Usage: python pollinator-scan.py [--subnet 192.168.4] [--json]
"""
import socket
import json
import sys
import time
import struct
import concurrent.futures
from datetime import datetime, timezone

GATES = {
    "eastGate":  {"seed": "eastgate_GAIA_PRIMAL_V1",  "ports": [8080, 8443, 3000, 11436], "role": "BRAIN", "markers": ["/pulse", "/data/now.json"]},
    "northGate": {"seed": "northgate_GAIA_PRIMAL_V1", "ports": [11434], "role": "HEART", "markers": ["/api/tags"]},
    "sporeGate": {"seed": "sporegate_GAIA_PRIMAL_V1", "ports": [53, 8080], "role": "FORGE", "markers": []},
    "blueGate":  {"seed": "bluegate_GAIA_PRIMAL_V1",  "ports": [3141], "role": "EYE", "markers": ["/gaia/status"]},
    "ironGate":  {"seed": "irongate_GAIA_PRIMAL_V1",  "ports": [11434], "role": "FORGE2", "markers": ["/api/tags"]},
    "graftGate": {"seed": "graftgate_GAIA_PRIMAL_V1", "ports": [11434], "role": "GRAFT", "markers": ["/api/tags"]},
    "grapheneGate": {"seed": "graphenegate_GAIA_PRIMAL_V1", "ports": [8082], "role": "DIAMOND_LENS", "markers": []},
    "frameGate": {"seed": "framegate_GAIA_PRIMAL_V1", "ports": [22], "role": "FACE", "markers": []},
    "deckGate":  {"seed": "deckgate_GAIA_PRIMAL_V1",  "ports": [22], "role": "DISPLAY", "markers": []},
    "southGate": {"seed": "southgate_GAIA_PRIMAL_V1", "ports": [22], "role": "HOME_PHONE", "markers": []},
}

# All signature ports — if we see these, a gate is likely there
SIGNATURE_PORTS = [22, 53, 3000, 3141, 8080, 8082, 8443, 11434, 11436]

# FNV-1a hash (matches bingocube.js browser-side)
def fnv64(s):
    h1 = 0x811c9dc5
    h2 = 0x811c9dc5
    for c in s.encode():
        h1 = ((h1 ^ c) * 0x01000193) & 0xFFFFFFFF
        h2 = ((h2 ^ (c + 0x9e)) * 0x01000193) & 0xFFFFFFFF
    return h1, h2

def bingocube_hash(entity_id):
    """Generate the same identity hash as bingocube.js"""
    h1, h2 = fnv64(entity_id + '_ZK_IDENTITY')
    return format((h1 ^ h2) & 0xFFFFFFFF, '08x')

def probe_port(ip, port, timeout=0.5):
    """Try to connect to ip:port. Returns True if open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except:
        return False

def probe_http(ip, port, path, timeout=1.0):
    """Try HTTP GET, return status code and first 200 bytes."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        req = f"GET {path} HTTP/1.0\r\nHost: {ip}\r\n\r\n"
        s.send(req.encode())
        resp = s.recv(1024).decode('utf-8', errors='replace')
        s.close()
        if resp.startswith('HTTP/'):
            code = int(resp.split(' ')[1])
            body_start = resp.find('\r\n\r\n')
            body = resp[body_start+4:body_start+204] if body_start > 0 else ''
            return code, body
        return None, resp[:200]
    except:
        return None, None

def identify_gate(ip, open_ports):
    """Given an IP and its open ports, try to identify which gate it is."""
    matches = []
    for name, gate in GATES.items():
        port_overlap = set(gate["ports"]) & set(open_ports)
        if port_overlap:
            score = len(port_overlap)
            # Try marker endpoints for positive ID
            for marker in gate.get("markers", []):
                for port in port_overlap:
                    code, body = probe_http(ip, port, marker)
                    if code == 200:
                        score += 10
                        break
            matches.append((name, score, list(port_overlap), gate["role"]))
    
    matches.sort(key=lambda x: -x[1])
    return matches

def scan_ip(ip, ports=None):
    """Scan a single IP for open ports."""
    if ports is None:
        ports = SIGNATURE_PORTS
    open_ports = []
    for port in ports:
        if probe_port(ip, port, timeout=0.3):
            open_ports.append(port)
    return ip, open_ports

def scan_subnet(subnet_prefix, start=1, end=254, max_workers=50):
    """Scan a /24 subnet for gates."""
    results = {}
    ips = [f"{subnet_prefix}.{i}" for i in range(start, end + 1)]
    
    print(f"\n  🐝 Pollinator scanning {subnet_prefix}.0/24 ...")
    print(f"     Probing {len(ips)} IPs × {len(SIGNATURE_PORTS)} ports\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_ip, ip): ip for ip in ips}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            ip, open_ports = future.result()
            if open_ports:
                results[ip] = open_ports
                gate_matches = identify_gate(ip, open_ports)
                if gate_matches:
                    best = gate_matches[0]
                    name, score, ports_found, role = best
                    cube_hash = bingocube_hash(GATES[name]["seed"])
                    print(f"  ★ {ip:16s} → {name} ({role}) [{cube_hash}]")
                    print(f"    ports: {ports_found}  score: {score}")
                else:
                    print(f"  ? {ip:16s} → UNKNOWN  ports: {open_ports}")
            if done % 50 == 0:
                print(f"    ... {done}/{len(ips)} scanned")
    
    return results

def build_address_book(scan_results):
    """Build the address book from scan results."""
    book = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "scanner": "superposition-pollinator-v1",
        "entries": {}
    }
    
    for ip, open_ports in scan_results.items():
        gate_matches = identify_gate(ip, open_ports)
        if gate_matches:
            best_name, score, ports_found, role = gate_matches[0]
            cube_hash = bingocube_hash(GATES[best_name]["seed"])
            
            if best_name not in book["entries"]:
                book["entries"][best_name] = {
                    "ips": [],
                    "cube_hash": cube_hash,
                    "role": role,
                    "seed": GATES[best_name]["seed"],
                    "state": "ALIVE"
                }
            
            book["entries"][best_name]["ips"].append({
                "address": ip,
                "ports": ports_found,
                "score": score,
                "seen": datetime.now(timezone.utc).isoformat()
            })
    
    # Mark unseen gates as SUPERPOSITION
    for name, gate in GATES.items():
        if name not in book["entries"]:
            book["entries"][name] = {
                "ips": [],
                "cube_hash": bingocube_hash(gate["seed"]),
                "role": gate["role"],
                "seed": gate["seed"],
                "state": "SUPERPOSITION"
            }
    
    return book

def main():
    subnets = ["192.168.4", "192.168.9", "192.168.1"]
    output_json = "--json" in sys.argv
    
    for arg in sys.argv[1:]:
        if arg.startswith("--subnet"):
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                subnets = [sys.argv[idx + 1]]
    
    print("=" * 60)
    print("  🐝 SUPERPOSITION POLLINATOR — R34 Scanner")
    print("  If a gate EXISTS, there IS a way to find it.")
    print("=" * 60)
    print(f"\n  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Subnets: {', '.join(s + '.0/24' for s in subnets)}")
    
    # Generate all gate identity hashes
    print(f"\n  Gate Identity Hashes (BingoCube FNV-1a):")
    for name, gate in GATES.items():
        h = bingocube_hash(gate["seed"])
        print(f"    {name:16s} [{h}]  {gate['role']}")
    
    all_results = {}
    for subnet in subnets:
        results = scan_subnet(subnet)
        all_results.update(results)
    
    book = build_address_book(all_results)
    
    # Summary
    alive = sum(1 for e in book["entries"].values() if e["state"] == "ALIVE")
    superpos = sum(1 for e in book["entries"].values() if e["state"] == "SUPERPOSITION")
    
    print(f"\n{'=' * 60}")
    print(f"  ADDRESS BOOK — {alive} COLLAPSED / {superpos} IN SUPERPOSITION")
    print(f"{'=' * 60}")
    
    for name, entry in sorted(book["entries"].items()):
        state = entry["state"]
        if state == "ALIVE":
            ips = ", ".join(e["address"] for e in entry["ips"])
            print(f"  ★ {name:16s} → {ips:20s} [{entry['cube_hash']}] {entry['role']}")
        else:
            print(f"  ◌ {name:16s} → ???                  [{entry['cube_hash']}] {entry['role']} (unseen)")
    
    if output_json:
        out_path = "address-book.json"
        with open(out_path, 'w') as f:
            json.dump(book, f, indent=2)
        print(f"\n  Wrote: {out_path}")
    
    print(f"\n  🌅 R34: 34°F at 03:00, sunrise unseen at 07:14,")
    print(f"     collapsed at 07:25:28 — Detroit, 17 Nov 2026")

if __name__ == "__main__":
    main()
