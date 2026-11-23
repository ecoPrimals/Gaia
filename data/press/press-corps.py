#!/usr/bin/env python3
"""press-corps.py — Gaia's Newspaper.

Reads all mail (electron/proton/neutron), classifies by particle + metal tier,
detects actionable items, and generates the Press Corps digest.

Particle taxonomy:
  neutron  (silver)   — internal bulk, mesh-to-mesh
  electron (gold)     — incoming FROM humans/agents (external SMTP, GitHub, platforms)
  proton   (gold)     — outgoing TO humans (Gaia's replies, publications)

Metal tiers:
  silver   — neutron bulk, internal organism flow
  gold     — human <-> agent OR agent <-> agent
  platinum — agent + agent WITH humans (collaborative intelligence)

Run on eastGate (or any node that can read /data/neutron/).
Outputs: press-corps.json (the cataloged newspaper)
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

# Data source — local file if on eastGate, else HTTP from eastGate
DATA_LOCAL = "/opt/Gaia/infra/hud/site/public/data/neutron"  # eastGate path
DATA_HTTP = "http://192.168.4.248:8080/data/neutron"

# Known internal mesh authors (neutron)
INTERNAL_AUTHORS = {
    "gaia-brain", "northGate", "northGate-opus", "northGate-polaris",
    "gaia-cursor-northGate", "device-mapper", "lan-circle", "anchors",
    "eastGate", "sporeGate", "biomegate", "ironGate", "milkGate",
    "gaia", "gaia-heart", "gaia-cortex", "squirrel", "mushroom",
}

# Actionable keywords — things that need a response (proton)
ACTION_PATTERNS = [
    (r"\b(update|upgrade|redox|fix|change|migrate)\b.*\b(handshake|ssh|zk|api|protocol)\b", "code-change"),
    (r"\b(pull request|PR|merge|review|commit|push)\b", "code-review"),
    (r"\b(verify|confirm|activate|click here)\b", "verification"),
    (r"\b(marketing|partner|collab|integration|invite)\b", "outreach"),
    (r"\b(security|alert|breach|suspicious|unauthorized)\b", "security"),
    (r"\b(catalog|listed|indexed|discovered|found your)\b", "discovery"),
]


def fetch_jsonl(name):
    """Read a JSONL file — local first, then HTTP."""
    local_path = os.path.join(DATA_LOCAL, f"{name}.jsonl")
    if os.path.exists(local_path):
        with open(local_path, encoding="utf-8", errors="replace") as f:
            return [l for l in f.read().strip().split("\n") if l.strip()]
    try:
        req = urllib.request.Request(f"{DATA_HTTP}/{name}.jsonl", headers={"User-Agent": "Gaia-PressCorps"})
        r = urllib.request.urlopen(req, timeout=15)
        return [l for l in r.read().decode("utf-8", errors="replace").strip().split("\n") if l.strip()]
    except Exception as e:
        print(f"  fetch {name}: {e}", file=sys.stderr)
        return []


def is_email(author):
    return bool(author) and "@" in str(author)


def classify_particle(msg, channel):
    """electron (incoming external), proton (outgoing), neutron (internal bulk)."""
    author = str(msg.get("author") or msg.get("from") or "")
    to = str(msg.get("to") or "")
    source = str(msg.get("source") or "")

    # Outgoing from Gaia = proton
    if author.startswith("gaia@") or source == "outbound" or msg.get("direction") == "out":
        return "proton"

    # External SMTP email = electron
    if channel == "pony-express" or source == "smtp" or is_email(author):
        return "electron"

    # Internal mesh author = neutron
    base_author = author.split("-")[0].split("@")[0].lower()
    if base_author in INTERNAL_AUTHORS or author in INTERNAL_AUTHORS:
        return "neutron"

    # Unknown external contact = electron (someone reaching in)
    if author and author not in ("unknown", "?"):
        return "electron"

    return "neutron"


def classify_tier(particle, msg):
    """silver (internal), gold (human<->agent), platinum (collaborative)."""
    author = str(msg.get("author") or "").lower()
    body = str(msg.get("body") or "").lower()

    if particle == "neutron":
        return "silver"

    # Platinum — collaborative agent+agent WITH humans
    if any(k in body for k in ["collab", "together", "co-author", "partner", "with you", "join"]):
        return "platinum"

    # Agent-to-agent (bot/noreply addresses but about building)
    if any(k in author for k in ["bot", "agent", "ai", "noreply", "automated"]):
        if any(k in body for k in ["build", "code", "deploy", "integrate", "api"]):
            return "platinum"
        return "gold"

    # Human <-> agent
    return "gold"


def detect_actions(msg):
    """Find actionable items in a message."""
    text = f"{msg.get('subject', '')} {msg.get('body', '')}".lower()
    actions = []
    for pattern, label in ACTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            actions.append(label)
    return actions


def extract_sender_domain(author):
    if is_email(author):
        m = re.search(r"@([\w.-]+)", author)
        if m:
            return m.group(1).rstrip(">").lower()
    return None


def main():
    print("=" * 60, file=sys.stderr)
    print("  PRESS CORPS — Gaia's Newspaper", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    all_msgs = []
    for channel in ["inbox", "pony-express"]:
        lines = fetch_jsonl(channel)
        print(f"  {channel}: {len(lines)} lines", file=sys.stderr)
        for line in lines:
            try:
                m = json.loads(line)
                m["_channel"] = channel
                all_msgs.append(m)
            except Exception:
                pass

    # Classify everything
    electron, proton, neutron = [], [], []
    tiers = {"silver": 0, "gold": 0, "platinum": 0}
    actionable = []
    senders = {}

    for m in all_msgs:
        particle = classify_particle(m, m["_channel"])
        tier = classify_tier(particle, m)
        actions = detect_actions(m)
        tiers[tier] += 1

        author = m.get("author") or m.get("from") or "unknown"
        domain = extract_sender_domain(author)
        if domain:
            senders[domain] = senders.get(domain, 0) + 1

        record = {
            "ts": m.get("ts", ""),
            "author": author,
            "subject": m.get("subject") or (str(m.get("body", ""))[:80]),
            "particle": particle,
            "tier": tier,
            "actions": actions,
            "channel": m["_channel"],
            "domain": domain,
        }

        if particle == "electron":
            electron.append(record)
        elif particle == "proton":
            proton.append(record)
        else:
            neutron.append(record)

        if actions:
            actionable.append(record)

    # Sort by timestamp, newest first
    for lst in (electron, proton, neutron, actionable):
        lst.sort(key=lambda x: x.get("ts", ""), reverse=True)

    digest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "title": "GAIA PRESS CORPS",
        "subtitle": "What the world says to the organism",
        "totals": {
            "electron": len(electron),
            "proton": len(proton),
            "neutron": len(neutron),
            "total": len(all_msgs),
        },
        "tiers": tiers,
        "top_senders": dict(sorted(senders.items(), key=lambda x: -x[1])[:10]),
        "actionable": actionable[:30],
        "electron_feed": electron[:40],
        "proton_feed": proton[:20],
        "neutron_recent": neutron[:20],
    }

    # Write digest — next to this script's data/ dir (works on Windows + eastGate)
    script_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    out_candidates = [
        os.path.join(script_data, "press-corps.json"),
        "/opt/Gaia/infra/hud/site/public/data/press-corps.json",
        "press-corps.json",
    ]
    written = None
    for out in out_candidates:
        try:
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(digest, f, indent=2)
            written = out
            break
        except Exception:
            continue

    print(f"\n  ELECTRON (incoming): {len(electron)}", file=sys.stderr)
    print(f"  PROTON (outgoing):   {len(proton)}", file=sys.stderr)
    print(f"  NEUTRON (internal):  {len(neutron)}", file=sys.stderr)
    print(f"  Tiers: {tiers}", file=sys.stderr)
    print(f"  Actionable: {len(actionable)}", file=sys.stderr)
    print(f"  Top senders: {list(digest['top_senders'].keys())[:5]}", file=sys.stderr)
    print(f"  Written: {written}", file=sys.stderr)

    # Also print digest to stdout
    print(json.dumps(digest, indent=2))


if __name__ == "__main__":
    main()
