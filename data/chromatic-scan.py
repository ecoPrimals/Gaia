#!/usr/bin/env python3
"""Chromatic GIS scanner — pings all gates, checks ollama, writes chromatic-state.json.
Run from cron every 2 min or on-demand. Colors devices by particle state."""
import json, subprocess, time, os
from datetime import datetime, timezone

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DATA_DIR, "chromatic-state.json")

GATES = [
    {"id":"router",      "ip":"192.168.4.1",   "role":"backbone"},
    {"id":"mikrotik",    "ip":"192.168.4.2",   "role":"backbone"},
    {"id":"sporegate",   "ip":"192.168.4.3",   "role":"forge"},
    {"id":"bluegate",    "ip":"192.168.4.100", "role":"eye"},
    {"id":"graftgate",   "ip":"192.168.4.107", "role":"forge"},
    {"id":"jetstream",   "ip":"192.168.4.111", "role":"backbone"},
    {"id":"northgate",   "ip":"192.168.4.147", "role":"heart"},
    {"id":"southgate",   "ip":"192.168.4.148", "role":"phone"},
    {"id":"milkgate",    "ip":"192.168.4.160", "role":"transponder"},
    {"id":"deckgate",    "ip":"192.168.4.176", "role":"display"},
    {"id":"framegate",   "ip":"192.168.4.181", "role":"face"},
    {"id":"epson",       "ip":"192.168.4.200", "role":"output"},
    {"id":"graphenegate","ip":"192.168.4.202", "role":"eye"},
    {"id":"irongate",    "ip":"192.168.4.237", "role":"forge"},
    {"id":"eastgate",    "ip":"192.168.4.244", "role":"brain"},
]

OLLAMA_PORTS = {
    "eastgate": 11436,
    "northgate": 11434,
    "irongate": 11434,
    "graftgate": 11434,
}

def ping(ip, timeout=0.4):
    try:
        r = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            capture_output=True, text=True, timeout=2
        )
        if r.returncode == 0:
            for line in r.stdout.split("\n"):
                if "time=" in line:
                    ms = float(line.split("time=")[1].split()[0])
                    return True, ms
            return True, None
        return False, None
    except:
        return False, None

def check_ollama(ip, port):
    import urllib.request
    try:
        url = f"http://{ip}:{port}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            d = json.loads(resp.read())
            return len(d.get("models", []))
    except:
        return 0

def color_for(g):
    if not g["alive"]:
        return "void" if not g.get("last_seen") else "fossil"
    if g["role"] == "backbone":
        return "backbone"
    if g["role"] in ("eye", "display", "face"):
        return "see"
    if g.get("ollama", 0) > 0:
        return "dream"
    return {
        "heart": "pulse", "brain": "breath", "forge": "create",
        "phone": "sense", "output": "digest", "transponder": "immune",
    }.get(g["role"], "sense")

def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []

    for g in GATES:
        alive, rtt = ping(g["ip"])
        ollama = 0
        if alive and g["id"] in OLLAMA_PORTS:
            ollama = check_ollama(g["ip"], OLLAMA_PORTS[g["id"]])

        entry = {
            "id": g["id"],
            "ip": g["ip"],
            "role": g["role"],
            "alive": alive,
            "rtt": round(rtt, 2) if rtt else None,
            "ollama": ollama,
            "last_seen": ts if alive else None,
        }
        entry["color"] = color_for(entry)
        results.append(entry)

    alive_n = sum(1 for r in results if r["alive"])
    down_n = sum(1 for r in results if not r["alive"])
    ollama_n = sum(r["ollama"] for r in results)

    state = {
        "type": "chromatic-gis-state",
        "wave": "239l",
        "ts": ts,
        "alive": alive_n,
        "down": down_n,
        "ollama_total": ollama_n,
        "gates": results,
        "triads": {
            "rhythm": sum(1 for r in results if r["color"] in ("pulse","breath","sense")),
            "meaning": sum(1 for r in results if r["color"] in ("immune","dream","create")),
            "digestion": sum(1 for r in results if r["color"] in ("digest","fossil","void")),
            "perception": sum(1 for r in results if r["color"] in ("backbone","see","speak")),
        },
    }

    with open(OUT, "w") as f:
        json.dump(state, f, indent=2)

    print(f"[chromatic-gis] {ts} alive={alive_n} down={down_n} ollama={ollama_n}")
    for r in results:
        sym = "✓" if r["alive"] else "✗"
        rtt_s = f"{r['rtt']}ms" if r["rtt"] else "—"
        oll_s = f" ollama={r['ollama']}" if r["ollama"] else ""
        print(f"  {sym} {r['id']:15s} {r['ip']:16s} {r['color']:10s} {rtt_s}{oll_s}")

if __name__ == "__main__":
    main()
