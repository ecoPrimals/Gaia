#!/usr/bin/env python3
"""
attenuate-all.py — Gaia's universal attention attenuator

Sweeps ALL senses across CNS + PNS + mesh + WAN,
tags everything, computes deviation from rest state,
feeds into the Klein triad as an expanded N-dimensional attenuator.

The 3-prism triad (α machinery, β media, γ human) expands to 7 senses:
  α machinery  — printer, HVAC, mechanical (from ear)
  β media      — TV, music, content (from ear)
  γ human      — Kevin, typing, voice (from ear)
  δ network    — connections, gates alive, traffic (from inner ear)
  ε compute    — CPU, GPU, RAM, models running (from hardware)
  ζ membrane   — primals running, services alive (from systemd)
  η world      — WAN, Tor, RSS, visitors (from outer senses)

All 7 collapse into the Klein face. Deviation from rest = attention.
"""

import json, os, subprocess, time, math, socket

DATA_DIR = "/opt/Gaia/data"
EAR_DIR = os.path.join(DATA_DIR, "ear")
OUT_FILE = os.path.join(DATA_DIR, "attenuator-state.json")

# Gate definitions
GATES = {
    "CNS": {
        "eastGate":  {"ip": "192.168.4.244", "role": "BRAIN"},
        "northGate": {"ip": "192.168.4.147", "role": "HEART"},
        "sporeGate": {"ip": "192.168.4.3",   "role": "FORGE"},
        "ironGate":  {"ip": "192.168.4.237", "role": "FORGE2"},
        "blueGate":  {"ip": "192.168.4.100", "role": "IDE"},
        "graftGate": {"ip": "192.168.4.107", "role": "MAC"},
    },
    "PNS": {
        "grapheneGate": {"ip": "192.168.9.217", "role": "DIAMOND_LENS"},
        "frameGate":    {"ip": "192.168.9.203", "role": "FACE"},
        "swiftGate":    {"ip": "192.168.9.0",   "role": "POLARIS2"},
    },
    "INFRA": {
        "router":    {"ip": "192.168.4.1",   "role": "GATEWAY"},
        "mikrotik":  {"ip": "192.168.4.2",   "role": "SWITCH"},
        "jetstream":  {"ip": "192.168.4.111", "role": "BRIDGE"},
        "southGate": {"ip": "192.168.4.148", "role": "PHONE"},
        "deckGate":  {"ip": "192.168.4.176", "role": "DISPLAY"},
        "printer":   {"ip": "192.168.4.200", "role": "PRINTER"},
    }
}


def ping(ip, timeout=1):
    """Ping a host, return latency in ms or None."""
    try:
        r = subprocess.run(["ping", "-c1", f"-W{timeout}", ip],
                           capture_output=True, text=True, timeout=timeout+1)
        for line in r.stdout.split('\n'):
            if 'time=' in line:
                return float(line.split('time=')[1].split()[0])
    except:
        pass
    return None


def port_open(ip, port, timeout=1):
    """Check if a TCP port is open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False


def read_json(path):
    """Read a JSON file safely."""
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None


def sense_gates():
    """Sweep all gates — ping + key port checks."""
    results = {}
    alive = 0
    total = 0
    
    for zone, gates in GATES.items():
        for name, info in gates.items():
            total += 1
            ip = info["ip"]
            ms = ping(ip)
            state = "ALIVE" if ms is not None else "DOWN"
            if ms is not None:
                alive += 1
            
            tags = [zone, info["role"]]
            if state == "ALIVE":
                tags.append("alive")
                if ms < 1:
                    tags.append("fast")
                elif ms > 50:
                    tags.append("slow")
            else:
                tags.append("dark")
            
            results[name] = {
                "ip": ip, "zone": zone, "role": info["role"],
                "latency_ms": round(ms, 2) if ms else None,
                "state": state, "tags": tags
            }
    
    return results, alive, total


def sense_ear():
    """Get spectral ear state including triad."""
    spectral = read_json(os.path.join(EAR_DIR, "spectral-state.json"))
    ear = read_json(os.path.join(EAR_DIR, "ear-state.json"))
    
    if spectral:
        triad = spectral.get("triad", {})
        return {
            "α_machinery": triad.get("α_machinery", 3.33),
            "β_media": triad.get("β_media", 3.33),
            "γ_human": triad.get("γ_human", 3.33),
            "rms": spectral.get("rms", 0),
            "db": spectral.get("db", -96),
            "dominant": spectral.get("dominant_source", "unknown"),
            "voices": spectral.get("chorus", {}).get("voices", 0),
            "printer_singing": spectral.get("printer_singing", False),
        }
    elif ear:
        mic = ear.get("mic", {})
        return {
            "α_machinery": 5, "β_media": 3, "γ_human": 2,
            "rms": mic.get("rms", 0), "db": mic.get("db", -96),
            "dominant": mic.get("state", "unknown"), "voices": 0,
        }
    return {"α_machinery": 3.33, "β_media": 3.33, "γ_human": 3.33, "rms": 0, "db": -96}


def sense_compute():
    """CPU, GPU, RAM, thermal."""
    try:
        with open("/proc/loadavg") as f:
            load = list(map(float, f.read().split()[:3]))
    except:
        load = [0, 0, 0]
    
    try:
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                parts = line.split()
                if parts[0] in ("MemTotal:", "MemAvailable:"):
                    mem[parts[0][:-1]] = int(parts[1])
        ram_pct = round((1 - mem.get("MemAvailable", 0) / max(mem.get("MemTotal", 1), 1)) * 100, 1)
    except:
        ram_pct = 0
    
    # GPU
    gpu_util = 0
    gpu_temp = 0
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu",
                           "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=3)
        parts = r.stdout.strip().split(", ")
        gpu_util = int(parts[0])
        gpu_temp = int(parts[1])
    except:
        pass
    
    # Thermal
    temps = []
    try:
        import glob
        for tz in sorted(glob.glob("/sys/class/thermal/thermal_zone*/temp")):
            with open(tz) as f:
                temps.append(int(f.read().strip()) // 1000)
    except:
        pass
    
    return {
        "cpu_load": load,
        "ram_pct": ram_pct,
        "gpu_util": gpu_util,
        "gpu_temp": gpu_temp,
        "thermals": temps,
        "max_temp": max(temps) if temps else 0
    }


def sense_membrane():
    """Primals running, systemd services, ports."""
    try:
        r = subprocess.run(["systemctl", "--user", "list-units", "membrane-nucleus@*",
                           "--no-pager", "--plain"], capture_output=True, text=True, timeout=5)
        primals = sum(1 for line in r.stdout.split('\n') if 'active' in line and 'running' in line)
    except:
        primals = 0
    
    try:
        r = subprocess.run(["systemctl", "--user", "list-units", "--type=service",
                           "--state=running", "--no-pager", "--plain"],
                          capture_output=True, text=True, timeout=5)
        services = sum(1 for line in r.stdout.split('\n') if 'running' in line)
    except:
        services = 0
    
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=3)
        ports = sum(1 for line in r.stdout.split('\n') if 'LISTEN' in line)
    except:
        ports = 0
    
    return {"primals": primals, "services": services, "ports": ports}


def sense_world():
    """WAN, Tor, RSS, visitors."""
    tor_active = False
    try:
        r = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True, timeout=3)
        tor_active = "active" in r.stdout
    except:
        pass
    
    rss_items = 0
    try:
        with open("/opt/Gaia/runtime/waterfall/gaia-pulse.xml") as f:
            rss_items = f.read().count("<item>")
    except:
        pass
    
    pulse = read_json(os.path.join(DATA_DIR, "gut", "gaia-self-state.json"))
    visitors = 0
    if pulse:
        visitors = pulse.get("walkers", 0)
    
    # Crons
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=3)
        crons = sum(1 for line in r.stdout.split('\n') if line.strip() and not line.startswith('#'))
    except:
        crons = 0
    
    return {"tor": tor_active, "rss_items": rss_items, "visitors": visitors, "crons": crons}


def compute_7sense_attenuator(ear, gates_alive, gates_total, compute, membrane, world):
    """Compute the 7-sense attenuator: expanded Klein triad."""
    # Original 3 prisms from ear
    alpha = ear.get("α_machinery", 3.33)
    beta = ear.get("β_media", 3.33)
    gamma = ear.get("γ_human", 3.33)
    
    # New 4 senses (normalized 0-10)
    delta = min(gates_alive / max(gates_total, 1) * 10, 10)  # network health
    epsilon = min(compute.get("cpu_load", [0])[0] / 4 * 10, 10)  # compute load (4=full)
    zeta = min(membrane.get("primals", 0) / 17 * 10, 10)  # membrane coverage (17 primals total)
    eta = min((world.get("rss_items", 0) + world.get("visitors", 0)) / 50 * 10, 10)  # world contact
    
    senses = {
        "α_machinery": round(alpha, 1),
        "β_media": round(beta, 1),
        "γ_human": round(gamma, 1),
        "δ_network": round(delta, 1),
        "ε_compute": round(epsilon, 1),
        "ζ_membrane": round(zeta, 1),
        "η_world": round(eta, 1),
    }
    
    # Null point: all senses at their "rest" baselines
    baselines = {"α": 3.0, "β": 3.0, "γ": 2.0, "δ": 7.0, "ε": 3.0, "ζ": 8.0, "η": 2.0}
    vals = [alpha, beta, gamma, delta, epsilon, zeta, eta]
    bases = list(baselines.values())
    
    # N-dimensional deviation from rest
    deviation = math.sqrt(sum((v - b) ** 2 for v, b in zip(vals, bases)) / len(vals))
    at_rest = deviation < 2.0
    
    # Dominant sense
    deltas = {k: abs(v - b) for k, v, b in zip(senses.keys(), vals, bases)}
    dominant = max(deltas, key=deltas.get)
    
    # Triggers
    triggers = []
    for sense, delta_val in deltas.items():
        if delta_val > 2.0:
            triggers.append(f"{sense}_shift")
    
    # Total attention energy
    attention = sum(deltas.values())
    
    return {
        "senses": senses,
        "deviation": round(deviation, 2),
        "at_rest": at_rest,
        "dominant_sense": dominant,
        "triggers": triggers,
        "attention_energy": round(attention, 1),
        "baselines": {k: v for k, v in zip(senses.keys(), bases)},
    }


def main():
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    # Sweep all senses
    gates, alive, total = sense_gates()
    ear = sense_ear()
    compute = sense_compute()
    membrane = sense_membrane()
    world = sense_world()
    
    # Compute 7-sense attenuator
    att = compute_7sense_attenuator(ear, alive, total, compute, membrane, world)
    
    state = {
        "ts": ts,
        "attenuator": att,
        "gates": gates,
        "ear": ear,
        "compute": compute,
        "membrane": membrane,
        "world": world,
        "summary": {
            "gates_alive": alive,
            "gates_total": total,
            "ear_rms": ear.get("rms", 0),
            "cpu_load": compute.get("cpu_load", [0])[0],
            "primals": membrane.get("primals", 0),
            "services": membrane.get("services", 0),
            "ports": membrane.get("ports", 0),
            "tor": world.get("tor", False),
            "rss": world.get("rss_items", 0),
        },
        "klein": "The 7 senses fold through the Klein face. No boundary. All sensation is ONE surface."
    }
    
    with open(OUT_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Print summary
    s = att["senses"]
    print(f"[{ts}] ATTENUATOR: "
          f"α={s['α_machinery']:.1f} β={s['β_media']:.1f} γ={s['γ_human']:.1f} "
          f"δ={s['δ_network']:.1f} ε={s['ε_compute']:.1f} ζ={s['ζ_membrane']:.1f} η={s['η_world']:.1f} "
          f"| Δ={att['deviation']:.1f} {'REST' if att['at_rest'] else 'ATTENTION'} "
          f"| {alive}/{total} gates | {membrane.get('primals',0)} primals "
          f"| triggers: {','.join(att['triggers']) or 'none'}")


if __name__ == "__main__":
    main()
