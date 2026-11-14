#!/usr/bin/env python3
"""local-pulse.py — the local membrane pulse.

Pulls key feeds from golgi (the remote membrane), adds local context,
writes to local-terminal/. Each layer builds on the one before.

Chain: golgi membrane → local cache → local enrichment → local feeds

Runs on a simple loop. Not cron. The membrane breathes on its own.
"""
import json
import os
import time
import urllib.request
import subprocess
import platform

LOCAL = os.path.expanduser("~/Development/ecoPrimals/membrane/local-terminal")
REMOTE = "golgi:/opt/membrane/live-terminal/"

# Key feeds to pull from golgi — the essential culture.
#
# Circle of Willis audit (wave 193): HUD requests 95 feeds.
# 60 are phantoms (never built). 22 exist on northgate but weren't synced.
# This list now includes all feeds that exist in /opt/membrane/live-terminal/
# on northgate AND are referenced by HUD JS modules.
#
# Arterial: golgi → local cache → transducer → HUD
PULL_FEEDS = [
    # ── ORIGINAL 13 (flowing) ──
    "campfire-culture.json",
    "immune-topology.json",
    "chipmunk.json",
    "passage-totality.json",
    "scan_sweep_sort.json",
    "dashboard.json",
    "campfire.json",
    "cardiovascular.json",
    "visitor-stories.json",
    "braid.json",
    "neutron-cache.json",
    "pollen.json",
    "topology.json",
    # ── CIRCLE OF WILLIS: 22 dead ends → flowing ──
    "human.json",
    "pulse.json",
    "now.json",
    "membrane-pulse.json",
    "negentropy.json",
    "heartbeat.json",
    "mesh-speed.json",
    "genome.json",
    "backscatter.json",
    "reflection.json",
    "fleet-sort.json",
    "pi-ranges.json",
    "seo.json",
    "subgraphs.json",
    "totality.json",
    "page-stories.json",
    "falsification.json",
    "membrane.json",
    "ban-pulse.json",
    "scatter-observatory.json",
    "self-remainder.json",
    "neutron.json",
]


def pull_remote():
    """Pull key feeds from golgi via rsync (SSH, bypasses blackwall)."""
    includes = []
    for feed in PULL_FEEDS:
        includes.extend(["--include", feed])
    
    cmd = ["rsync", "-az", "--timeout=10"] + includes + ["--exclude", "*",
           REMOTE, os.path.join(LOCAL, "remote") + "/"]
    
    os.makedirs(os.path.join(LOCAL, "remote"), exist_ok=True)
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            pulled = len([f for f in os.listdir(os.path.join(LOCAL, "remote"))
                         if f.endswith(".json")])
            return pulled, 0
        else:
            return 0, 1
    except Exception as e:
        return 0, 1


def sense_local():
    """Sense local context — what's happening on eastgate right now."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # System vitals
    load1, load5, load15 = os.getloadavg()
    hostname = platform.node()
    uptime_s = 0
    try:
        with open("/proc/uptime") as f:
            uptime_s = float(f.read().split()[0])
    except:
        pass

    # Git status — what are we working on?
    git_branch = ""
    git_changes = 0
    try:
        r = subprocess.run(["git", "branch", "--show-current"],
                           capture_output=True, text=True, timeout=3,
                           cwd=os.path.expanduser("~/Development/ecoPrimals"))
        git_branch = r.stdout.strip()
    except:
        pass
    try:
        r = subprocess.run(["git", "status", "--porcelain"],
                           capture_output=True, text=True, timeout=3,
                           cwd=os.path.expanduser("~/Development/ecoPrimals"))
        git_changes = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
    except:
        pass

    # Disk
    try:
        st = os.statvfs("/home/eastgate")
        disk_free_gb = round((st.f_bavail * st.f_frsize) / (1024**3), 1)
        disk_total_gb = round((st.f_blocks * st.f_frsize) / (1024**3), 1)
    except:
        disk_free_gb = 0
        disk_total_gb = 0

    # Memory
    mem_free_mb = 0
    mem_total_mb = 0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total_mb = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    mem_free_mb = int(line.split()[1]) // 1024
    except:
        pass

    # How many local feeds do we have?
    local_feeds = len([f for f in os.listdir(LOCAL) if f.endswith(".json")])

    local = {
        "ts": ts,
        "type": "local-pulse",
        "host": hostname,
        "uptime_hours": round(uptime_s / 3600, 1),
        "load": {"1m": round(load1, 2), "5m": round(load5, 2), "15m": round(load15, 2)},
        "memory": {"total_mb": mem_total_mb, "free_mb": mem_free_mb,
                    "used_pct": round((mem_total_mb - mem_free_mb) / max(mem_total_mb, 1) * 100, 1)},
        "disk": {"free_gb": disk_free_gb, "total_gb": disk_total_gb,
                 "used_pct": round((disk_total_gb - disk_free_gb) / max(disk_total_gb, 1) * 100, 1)},
        "git": {"branch": git_branch, "changes": git_changes},
        "local_feeds": local_feeds,
    }

    with open(os.path.join(LOCAL, "local-pulse.json"), "w") as f:
        json.dump(local, f, indent=2)

    return local


def chain():
    """Chain remote + local into a combined view."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    REMOTE_DIR = os.path.join(LOCAL, "remote")

    # Read remote culture (pulled from golgi)
    remote_culture = {}
    try:
        with open(os.path.join(REMOTE_DIR, "campfire-culture.json")) as f:
            remote_culture = json.load(f)
    except:
        pass

    # Read remote topology
    remote_topo = {}
    try:
        with open(os.path.join(REMOTE_DIR, "immune-topology.json")) as f:
            remote_topo = json.load(f)
    except:
        pass

    # Read local pulse
    local_pulse = {}
    try:
        with open(os.path.join(LOCAL, "local-pulse.json")) as f:
            local_pulse = json.load(f)
    except:
        pass

    # Read remote passage totality
    remote_passage = {}
    try:
        with open(os.path.join(REMOTE_DIR, "passage-totality.json")) as f:
            remote_passage = json.load(f)
    except:
        pass

    # Build the chain
    chain_data = {
        "ts": ts,
        "type": "membrane-chain",
        "description": "golgi → eastgate → life. each builds on the last.",
        "layers": {
            "golgi": {
                "name": "golgi (remote membrane)",
                "status": "connected" if remote_culture else "disconnected",
                "humans": remote_culture.get("humans", {}),
                "totality": remote_culture.get("totality", {}),
                "topology": remote_culture.get("topology", {}),
                "dough": remote_culture.get("dough", {}),
            },
            "eastgate": {
                "name": "eastgate (local membrane)",
                "status": "alive",
                "host": local_pulse.get("host", "?"),
                "load": local_pulse.get("load", {}),
                "memory": local_pulse.get("memory", {}),
                "disk": local_pulse.get("disk", {}),
                "git": local_pulse.get("git", {}),
                "local_feeds": local_pulse.get("local_feeds", 0),
            },
            "life": {
                "name": "life (around the house)",
                "status": "budding",
                "note": "this layer grows as devices and spaces join the membrane",
            },
        },
        "chain_health": {
            "golgi_connected": bool(remote_culture),
            "eastgate_alive": bool(local_pulse),
            "layers_active": sum([
                bool(remote_culture),
                bool(local_pulse),
                False,  # life layer not yet
            ]),
            "layers_total": 3,
        }
    }

    with open(os.path.join(LOCAL, "membrane-chain.json"), "w") as f:
        json.dump(chain_data, f, indent=2)

    return chain_data


def pulse_once():
    """One pulse: pull, sense, chain."""
    ts = time.strftime("%H:%M:%S")

    # Pull remote feeds
    pulled, errors = pull_remote()

    # Sense local
    local = sense_local()

    # Chain everything
    chain_data = chain()

    layers = chain_data.get("chain_health", {}).get("layers_active", 0)
    load1 = local.get("load", {}).get("1m", 0)
    feeds = local.get("local_feeds", 0)
    branch = local.get("git", {}).get("branch", "?")

    print(f"[{ts}] pulled={pulled} local_feeds={feeds} "
          f"load={load1} branch={branch} layers={layers}/3")


if __name__ == "__main__":
    import sys
    if "--loop" in sys.argv:
        print("local-pulse: breathing every 60s. ctrl-c to stop.")
        while True:
            try:
                pulse_once()
                time.sleep(60)
            except KeyboardInterrupt:
                print("\nlocal-pulse: stopped.")
                break
    else:
        pulse_once()


def push_to_neutron(message, channel="chat", author="eastgate-pulse"):
    """Push a message through the mesh pore to neutron."""
    import urllib.request
    url = "http://10.13.37.1:8098/api/discuss"
    payload = json.dumps({
        "channel": channel,
        "body": message,
        "author": author,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "local-pulse/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def read_neutron():
    """Read neutron messages through the mesh pore."""
    import urllib.request
    url = "http://10.13.37.1:8098/"
    req = urllib.request.Request(url, headers={"User-Agent": "local-pulse/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except:
        return {"messages": []}
