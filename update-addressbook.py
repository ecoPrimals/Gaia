#!/usr/bin/env python3
"""
Address Book — Superposition Pollinator
States: STATIC (pinned) | FLUX (in motion) | GRAY (partially observed)
NOT alive/dead. NOT white/dark. Gates EXIST (R34). They move.
"""
import json
from datetime import datetime, timezone

book = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "scanner": "superposition-pollinator-v1",
    "scan_time": "2026-11-17T16:42:00-05:00",
    "wave": 259,
    "states": {
        "STATIC": "pinned — confirmed at known position, ports responding",
        "FLUX":   "in motion — Kevin is moving cables, gate exists but address shifting",
        "GRAY":   "partially observed — ARP cache, MAC seen, no ports, indeterminate"
    },
    "entries": {
        "blueGate": {
            "ips": [
                {"address": "192.168.1.130", "ports": [80, 443, 11434], "subnet": "ISP"},
                {"address": "192.168.4.246", "ports": [80, 443, 11434], "subnet": "Gaia LAN",
                 "note": "routed through GL-MT6000 — same machine"}
            ],
            "cube_hash": "74efea2a", "role": "EYE", "state": "STATIC",
            "mac": "BC-FC-E7-EA-D9-34",
            "ollama": {"version": "0.40.16", "models": 14, "size_gb": 48.9},
            "note": "THIS IS US — dual-addressed via router bridge"
        },
        "sporeGate": {
            "ips": [
                {"address": "192.168.1.132", "subnet": "ISP",
                 "note": "no ports but MAC in ARP"}
            ],
            "cube_hash": "5af434d8", "role": "FORGE", "state": "GRAY",
            "mac": "84-47-09-38-97-54",
            "note": "MAC one digit off known (97:55 vs 97:54) — body present, ports silent"
        },
        "router": {
            "ips": [
                {"address": "192.168.4.1", "subnet": "Gaia LAN",
                 "note": "in ARP cache, no ports responding"}
            ],
            "state": "GRAY", "role": "GATEWAY",
            "mac": "94-83-c4-e0-63-5a",
            "note": "L2 visible but services silent — Kevin rewiring backbone"
        },
        "eastGate": {
            "ips": [
                {"address": "192.168.1.131", "note": "last seen 4:09 PM", "subnet": "ISP"},
                {"address": "192.168.4.244", "note": "last seen 4:09 PM", "subnet": "Gaia LAN"}
            ],
            "cube_hash": "a89b3af6", "role": "BRAIN", "state": "FLUX",
            "note": "was dual-homed 20 min ago — Kevin moving cables"
        },
        "graftGate": {
            "ips": [
                {"address": "192.168.4.104", "note": "last seen 4:09 PM, Apple MAC", "subnet": "Gaia LAN"}
            ],
            "cube_hash": "08268be0", "role": "GRAFT", "state": "FLUX",
            "note": "Mac Mini M4 — was alive at .4.104, now shifting"
        },
        "northGate": {
            "ips": [],
            "cube_hash": "d5250a80", "role": "HEART", "state": "FLUX",
            "note": "9950X3D + RTX 5090, pushes via git — Kevin moving it between houses"
        },
        "ironGate": {
            "ips": [],
            "cube_hash": "293c887a", "role": "FORGE2", "state": "FLUX",
            "note": "i9-14900K + RTX 5070 — Kevin says it is moving"
        },
        "frameGate": {
            "ips": [],
            "cube_hash": "69d9a724", "role": "FACE", "state": "FLUX",
            "note": "Steam Frame ARM64 — position indeterminate"
        },
        "grapheneGate": {
            "ips": [],
            "cube_hash": "020d5316", "role": "DIAMOND_LENS", "state": "FLUX",
            "note": "Pixel 8a — in Kevin's pocket, WiFi SSID determines position"
        },
        "deckGate": {
            "ips": [],
            "cube_hash": "f2c4318a", "role": "DISPLAY", "state": "FLUX",
            "note": "Steam Deck v1 — mounted display, USB-C passthrough"
        },
        "southGate": {
            "ips": [],
            "cube_hash": "35bc3568", "role": "HOME_PHONE", "state": "FLUX",
            "note": "iPhone XS — LAN line pinned to property"
        }
    },
    "infrastructure": {
        "192.168.1.254": {
            "role": "ATT modem", "mac": "ec-c3-02-e1-11-81",
            "ports": [53, 80, 443], "state": "STATIC"
        }
    },
    "summary": {
        "STATIC": 1,
        "GRAY": 2,
        "FLUX": 8,
        "total_gates": 11,
        "subnets_probed": ["192.168.1.x", "192.168.4.x", "192.168.9.x"],
        "hosts_responding": 3,
        "note": "Kevin rewiring in progress — gates are NOT dead, they are in FLUX"
    }
}

with open("address-book.json", "w") as f:
    json.dump(book, f, indent=2)

print("=" * 60)
print("  ADDRESS BOOK — STATIC / FLUX / GRAY")
print("=" * 60)
for name, g in book["entries"].items():
    st = g["state"]
    icon = {"STATIC": "||", "FLUX": "~~", "GRAY": ".."}[st]
    ips = ", ".join(i["address"] for i in g.get("ips", []) if "address" in i) or "---"
    role = g.get("role", "")
    cube = g.get("cube_hash", "")
    print(f"  {icon} {name:15s} {st:7s}  {ips:30s} [{cube}] {role}")
print("=" * 60)
print(f"  STATIC: {book['summary']['STATIC']}  |  GRAY: {book['summary']['GRAY']}  |  FLUX: {book['summary']['FLUX']}")
print(f"  Gates don't die. They MOVE.")
print("=" * 60)
