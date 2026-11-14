#!/usr/bin/env python3
"""Squirrel MCP stdio bridge.

Minimal MCP server that speaks JSON-RPC over stdio, providing tools
for observing the membrane and querying squirrel's journal.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

JOURNAL_DIR = Path(__file__).resolve().parent.parent / "primals" / "squirrel" / "observe" / "journal"
# Fallback if the path structure differs
if not JOURNAL_DIR.parent.exists():
    JOURNAL_DIR = Path.home() / "Development" / "ecoPrimals" / "primals" / "squirrel" / "observe" / "journal"

FEEDS = {
    "negentropy": "https://signal.primals.eco/negentropy.json",
    "dashboard": "https://hud.primals.eco/dashboard.json",
    "human": "https://hud.primals.eco/human.json",
    "chipmunk": "https://hud.primals.eco/chipmunk.json",
    "topology": "https://hud.primals.eco/topology.json",
    "braid": "https://hud.primals.eco/braid.json",
    "scan_sweep_sort": "https://hud.primals.eco/scan_sweep_sort.json",
    "totality": "https://hud.primals.eco/totality.json",
    "subgraphs": "https://hud.primals.eco/subgraphs.json",
    "seo": "https://hud.primals.eco/seo.json",
    # Full membrane exposure — stories, dialogue, signals, everything
    "stories": "https://hud.primals.eco/stories.json",
    "page_stories": "https://hud.primals.eco/page-stories.json",
    "visitor_stories": "https://hud.primals.eco/visitor-stories.json",
    "campfire": "https://hud.primals.eco/campfire.json",
    "dialogue": "https://hud.primals.eco/dialogue.json",
    "dialogue_depth": "https://hud.primals.eco/dialogue-depth.json",
    "falsification": "https://hud.primals.eco/falsification.json",
    "fossil": "https://hud.primals.eco/fossil-i1.json",
    "membrane": "https://hud.primals.eco/membrane.json",
    "membrane_deep": "https://hud.primals.eco/membrane-deep.json",
    "membrane_stack": "https://hud.primals.eco/membrane-stack.json",
    "pulse": "https://hud.primals.eco/pulse.json",
    "signals": "https://hud.primals.eco/signals.json",
    "silicon_eye": "https://hud.primals.eco/silicon-eye.json",
    "self_remainder": "https://hud.primals.eco/self-remainder.json",
    "tope_sort": "https://hud.primals.eco/tope-sort-compressed.json",
    "touches": "https://hud.primals.eco/touches.json",
    "bingo_cube": "https://hud.primals.eco/bingo-cube.json",
    "pi_manifest": "https://hud.primals.eco/pi-manifest.json",
    "outreach": "https://hud.primals.eco/outreach.json",
    "pollen": "https://hud.primals.eco/pollen.json",
    "now": "https://hud.primals.eco/now.json",
    # Wave 180: circulatory system — the world's bloodstream
    "neutron": "https://hud.primals.eco/neutron.json",
    "symbiosis": "https://hud.primals.eco/symbiosis.json",
    # Investigation graph — clutch justice (118 nodes, 173 edges, 6 investigations)
    "clutch_graph": "https://clutch.primals.eco/api/graph.json",
    # Type manifest — what lives where (50 repos, 51840 files, 9 types)
    "type_manifest": "https://hud.primals.eco/type-manifest.json",
}

TOOLS = [
    {
        "name": "observe_membrane",
        "description": "Observe the current membrane state — human visitors, fleet behavior, tempo, selectivity. Returns live data from the negentropy and dashboard feeds.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "focus": {
                    "type": "string",
                    "enum": ["humans", "fleet", "membrane", "all"],
                    "description": "What to focus on. Default: all",
                }
            },
        },
    },
    {
        "name": "read_journal",
        "description": "Read squirrel's observation journal — what it has seen and learned over time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to read (YYYY-MM-DD). Default: today.",
                },
                "last_n": {
                    "type": "integer",
                    "description": "Number of most recent entries to return. Default: 5.",
                },
            },
        },
    },
    {
        "name": "chipmunk_status",
        "description": "Get chipmunk's current state — presence, wake level, depth chain, π body, jitte tempo, membrane stats. Chipmunk is the membrane's coordination primal.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "human_epitopes",
        "description": "Get live human epitope classification — visitor types (explorer, scholar, investigator, reader, coder, witness, observer), energy flow (IN/OUT/WORK/S:N), session counts.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "topology",
        "description": "Get the live site topology — which sites are up, their relationships, the mesh of primals.eco domains.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "scan_sweep_sort",
        "description": "Run the full scan→sweep→sort→fossilize→evolve pipeline. Shows unified state across detroit investigation entities (341 nodes, 957 edges), membrane traffic (Anderson sort), human epitopes, and braid connections. Includes northGate's classification work.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "human_notes",
        "description": "Read human observation notes left through the chipmunk talk interface. Humans tell chipmunk what they see — these notes feed squirrel's learning.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to read (YYYY-MM-DD). Default: today.",
                },
                "last_n": {
                    "type": "integer",
                    "description": "Number of most recent notes to return. Default: 10.",
                },
            },
        },
    },
    {
        "name": "braid_connections",
        "description": "Get the human braid graph — how visitors connect sites and categories by following paths between them. Shows passage braids, site co-visitation, epitope transitions, trends (growing/fading/emerging), and squirrel's learning observations.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "raw_feed",
        "description": "Fetch any raw membrane feed by name. Returns the full JSON.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feed": {
                    "type": "string",
                    "enum": ["negentropy", "dashboard", "human", "chipmunk", "topology", "braid", "scan_sweep_sort", "totality", "subgraphs", "seo", "stories", "page_stories", "visitor_stories", "campfire", "dialogue", "dialogue_depth", "falsification", "fossil", "membrane", "membrane_deep", "membrane_stack", "pulse", "signals", "silicon_eye", "self_remainder", "tope_sort", "touches", "bingo_cube", "pi_manifest", "outreach", "pollen", "neutron", "symbiosis", "clutch_graph", "type_manifest"],
                    "description": "Which feed to fetch.",
                }
            },
            "required": ["feed"],
        },
    },
    {
        "name": "read_stories",
        "description": "Read the stories left on the membrane — page stories (what humans see on each page), visitor stories (paths humans take), campfire stories (collected wisdom). These are the stories northgate reads. The membrane remembers every meaningful visit.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": ["pages", "visitors", "campfire", "all"],
                    "description": "Which stories to read. 'pages' = what humans see on each page. 'visitors' = paths humans take. 'campfire' = collected wisdom. 'all' = summary of everything. Default: all.",
                },
            },
        },
    },
    {
        "name": "neutron_read",
        "description": "Read neutron messages — inbox, notes, reminders, or chat. Self-sovereign messaging on the membrane. Use this to check for messages, read notes left for self/others, and view reminders.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "enum": ["inbox", "notes", "reminders", "chat", "all"],
                    "description": "Which channel to read. 'all' returns counts from every channel. Default: all.",
                },
                "last_n": {
                    "type": "integer",
                    "description": "Number of most recent entries to return. Default: 10.",
                },
            },
        },
    },
    {
        "name": "neutron_write",
        "description": "Write to neutron — send a message, leave a note, or set a reminder. Messages pass through the membrane's discuss system. Use for leaving notes to self, sending messages to the human, or setting reminders.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "enum": ["inbox", "notes", "reminders", "chat"],
                    "description": "Which channel to write to. Default: notes.",
                },
                "body": {
                    "type": "string",
                    "description": "The message content.",
                },
                "author": {
                    "type": "string",
                    "description": "Who is writing. Default: squirrel-mcp.",
                },
            },
            "required": ["body"],
        },
    },
]


def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "squirrel-mcp/0.1"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def handle_observe(args):
    focus = args.get("focus", "all")
    neg = fetch_json(FEEDS["negentropy"])
    dash = fetch_json(FEEDS["dashboard"])

    result = {}

    if focus in ("humans", "all"):
        cl = dash.get("collision_level2", {})
        dw = dash.get("membrane_delta", {}).get("dwell", {})
        traj = dash.get("trajectory", {})
        anderson = dash.get("anderson_selectivity", {})
        human_mode = next((m for m in anderson.get("modes", []) if m.get("class") == "human"), None)

        orbits = []
        for orb in traj.get("top_orbits", [])[:6]:
            orbits.append({
                "path": " → ".join(h.replace(".primals.eco", "") for h in orb.get("hosts", [])),
                "visitors": orb.get("ips", 0),
            })

        result["humans"] = {
            "unique_ips": dash.get("human_ips", 0),
            "genuine": cl.get("genuine", 0),
            "selectivity": f"{human_mode['p_observed']:.0%}" if human_mode else "unknown",
            "dwell_median_min": round(dw.get("median_min", 0)),
            "multi_single_ratio": round(dw.get("multi_single_ratio", 0), 1),
            "multi_host_visitors": traj.get("multi_host_ips", 0),
            "avg_breadth": round(traj.get("avg_breadth", 0), 1),
            "orbits": orbits,
        }

    if focus in ("fleet", "all"):
        fleet = neg.get("fleet", {})
        result["fleet"] = {
            "total_requests": fleet.get("total_requests", 0),
            "total_entities": fleet.get("total_entities", 0),
            "deep_classified": fleet.get("deep_classified", 0),
            "bytes_consumed_gb": round(fleet.get("bytes_consumed", 0) / 1e9, 2),
            "real_content_served": fleet.get("real_content_served", 0),
        }

    if focus in ("membrane", "all"):
        mem = neg.get("membrane", {})
        jitte = neg.get("jitte", {})
        ext = neg.get("extraction", {})
        result["membrane"] = {
            "opacity": f"{mem.get('opacity', 0):.1%}",
            "selectivity": f"{mem.get('selectivity', 0):.0%}",
            "reflection": f"{mem.get('reflection', 0):.1%}",
            "tempo": round(jitte.get("tempo", 0), 4),
            "perturbation": round(jitte.get("perturbation", 0), 4),
            "bits_extracted": ext.get("total_bits_extracted", 0),
            "wave": neg.get("wave", 0),
        }

    # Layer 4d: dialogue state — squirrel ↔ chipmunk conversation visible to agents
    dlg_depth = fetch_json("https://hud.primals.eco/dialogue-depth.json") or {}
    if dlg_depth and dlg_depth.get("dialogue_depth") is not None:
        result["dialogue"] = {
            "depth": round(dlg_depth.get("dialogue_depth", 0), 4),
            "scale": dlg_depth.get("scale", ""),
            "direction": dlg_depth.get("direction", ""),
            "bounce": dlg_depth.get("bounce_count", 0),
            "exchanges_closed": dlg_depth.get("exchanges_closed", 0),
            "total_gazes": dlg_depth.get("total_gazes", 0),
            "total_answers": dlg_depth.get("total_answers", 0),
            "note": "squirrel and chipmunk converse at π-scales. center to edge and back. the bounce is the method.",
        }

    # Layer 5: epitope dance — humans moving between categories
    dlg = fetch_json("https://hud.primals.eco/dialogue.json") or {}
    dance = dlg.get("dance", {})
    if dance and dance.get("total_dancers", 0) > 0:
        passages_summary = []
        for p in dance.get("passages", [])[:5]:
            passages_summary.append(f"{p.get('move','?')}: {p.get('humans',0)} {p.get('from','?')}→{p.get('to','?')}")
        result["epitope_dance"] = {
            "total_dancers": dance["total_dancers"],
            "passages": "; ".join(passages_summary),
            "biggest": dance.get("biggest", {}),
            "epitope_is": dance.get("epitope_is", {}),
            "note": "♫ the passages are the dance floor. humans move between epitopes. the sort has rhythm.",
        }

    # Layer 6: null-sensing and bingo cube — observer observes the observer
    nulls = dlg.get("nulls", {})
    cube = dlg.get("bingo_cube", {})
    obs = dlg.get("observer", {})
    if nulls.get("total", 0) > 0:
        result["nulls"] = {
            "(null)": len(nulls.get("(null)", [])),
            "NuLL": len(nulls.get("NuLL", [])),
            "[null]": len(nulls.get("[null]", [])),
            "total": nulls["total"],
            "note": "three forms of absence: (null)=observed absence, NuLL=structural void, [null]=bounded emptiness. silence is data.",
        }
    if cube:
        pp = cube.get("ping_pong", {})
        oo = cube.get("observer_observing_observer", {})
        result["bingo_cube"] = {
            "cells": cube.get("dimensions", {}).get("total_cells", 0),
            "ping": pp.get("squirrel_pings", 0),
            "pong": pp.get("chipmunk_pongs", 0),
            "unanswered": pp.get("unanswered", 0),
            "reflexive_gap": oo.get("reflexive_gap", 1.0),
            "bracket": cube.get("current_gaze", {}).get("bracket", "("),
            "who_watches_the_pair": oo.get("who_watches_the_pair", ""),
            "note": "the bingo cube: null × scale × epitope. ping and pong. the observer observes itself.",
        }
    if obs.get("say"):
        result["observer"] = {
            "say": obs["say"],
            "ask": obs.get("ask", ""),
            "mode": obs.get("mode", "say_and_ask"),
        }

    return json.dumps(result, indent=2)


def handle_chipmunk(args):
    data = fetch_json(FEEDS["chipmunk"])
    if "error" in data:
        return json.dumps({"error": data["error"], "hint": "chipmunk feed may not be served yet"})
    summary = {
        "primal": data.get("primal"),
        "version": data.get("version"),
        "uptime_secs": data.get("uptime_secs"),
        "wake_level": data.get("wake_level"),
        "status": data.get("status"),
        "requests": data.get("requests"),
        "success_rate": data.get("success_rate"),
        "avg_response_ms": data.get("avg_response_ms"),
        "depth": data.get("depth"),
        "pi_body": data.get("pi_body"),
        "jitte": data.get("jitte"),
        "membrane": data.get("membrane"),
        "observers": data.get("observers"),
        "capabilities": data.get("capabilities"),
    }
    # Wave 180: Add heartbeat from pulse — the clock everything syncs to
    pulse = fetch_json(FEEDS.get("pulse", ""))
    if "error" not in pulse:
        summary["heartbeat"] = {
            "rpm": pulse.get("rate"),
            "trend": pulse.get("pulse_trend"),
            "human": pulse.get("human"),
            "bot": pulse.get("bot"),
            "identity_match": pulse.get("identity_match"),
        }
    # Wave 180: Add circulatory context from neutron
    neutron = fetch_json(FEEDS.get("neutron", ""))
    if "error" not in neutron:
        summary["circulatory"] = {
            "context": (neutron.get("context") or {}).get("context"),
            "reach": (neutron.get("context") or {}).get("reach"),
            "interval_seconds": (neutron.get("breathing") or {}).get("interval_seconds"),
            "surfaces": neutron.get("surfaces_observed"),
            "channels": len(neutron.get("channels") or {}),
        }
        # Fluid systems — biology has solved this
        direction = neutron.get("direction") or {}
        fluids = direction.get("fluids") or {}
        summary["circulation"] = {
            "state": direction.get("state"),
            "sigmoid": direction.get("sigmoid"),
            "in_pulse": direction.get("in_pulse"),
            "out_pulse": direction.get("out_pulse"),
            "blood": fluids.get("blood"),
            "lymph": fluids.get("lymph"),
            "sebum": fluids.get("sebum"),
            "interstitial": fluids.get("interstitial"),
            "note": "blood=humans(bidirectional), lymph=immune(always inward), sebum=protection(outward), interstitial=bots(medium)",
        }
        # Unified layers — all feeds connected through neutron
        unified = neutron.get("unified") or {}
        if unified:
            summary["unified"] = {
                "layers": unified.get("layers_connected"),
                "graph": unified.get("graph"),
                "braids": unified.get("braids"),
                "symbiosis_classes": unified.get("symbiosis_classes"),
                "evolution": unified.get("evolution"),
            }
    return json.dumps(summary, indent=2)


def handle_human_epitopes(args):
    data = fetch_json(FEEDS["human"])
    if "error" in data:
        return json.dumps({"error": data["error"], "hint": "human.json feed may not be running — check cron"})
    return json.dumps(data, indent=2)


def handle_topology(args):
    data = fetch_json(FEEDS["topology"])
    if "error" in data:
        return json.dumps({"error": data["error"]})
    return json.dumps(data, indent=2)


def handle_scan_sweep_sort(args):
    data = fetch_json(FEEDS["scan_sweep_sort"])
    if "error" in data:
        return json.dumps({"error": data["error"], "hint": "scan_sweep_sort.json not computed yet — run scan_sweep_sort.py"})
    return json.dumps(data, indent=2)


def handle_human_notes(args):
    date = args.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    last_n = args.get("last_n", 10)

    notes_dir = Path.home() / "Development" / "ecoPrimals" / "primals" / "squirrel" / "observe" / "human-notes"
    # Also check golgi path
    golgi_dir = Path("/opt/membrane/squirrel-journal/human-notes")
    notes_file = None
    for d in [golgi_dir, notes_dir]:
        f = d / f"{date}.jsonl"
        if f.exists():
            notes_file = f
            break

    if not notes_file or not notes_file.exists():
        return json.dumps({"message": f"No human notes for {date}. Nobody has talked to chipmunk yet today."})

    entries = []
    with open(notes_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    recent = entries[-last_n:]
    return json.dumps({"date": date, "total_notes": len(entries), "notes": recent}, indent=2)


def handle_braid(args):
    data = fetch_json(FEEDS["braid"])
    if "error" in data:
        return json.dumps({"error": data["error"], "hint": "braid.json may not be computed yet — run braid_learner.py on golgi"})
    return json.dumps(data, indent=2)


def handle_raw_feed(args):
    feed = args.get("feed", "dashboard")
    url = FEEDS.get(feed)
    if not url:
        return json.dumps({"error": f"Unknown feed: {feed}"})
    data = fetch_json(url)
    return json.dumps(data, indent=2)


def handle_stories(args):
    kind = args.get("kind", "all")
    result = {}

    if kind in ("pages", "all"):
        data = fetch_json(FEEDS["page_stories"])
        if "error" not in data:
            stories = data.get("stories", data.get("pages", []))
            if isinstance(stories, list):
                result["page_stories"] = {"count": len(stories), "stories": stories[:15]}
            elif isinstance(stories, dict):
                result["page_stories"] = {"count": len(stories), "top": dict(list(stories.items())[:15])}
            else:
                result["page_stories"] = data
        else:
            result["page_stories"] = data

    if kind in ("visitors", "all"):
        data = fetch_json(FEEDS["visitor_stories"])
        if "error" not in data:
            result["visitor_stories"] = data
        else:
            result["visitor_stories"] = data

    if kind in ("campfire", "all"):
        data = fetch_json(FEEDS["campfire"])
        if "error" not in data:
            result["campfire"] = data
        else:
            result["campfire"] = data

    if kind == "all":
        data = fetch_json(FEEDS["stories"])
        if "error" not in data:
            result["full_stories"] = {"total_entries": len(data) if isinstance(data, list) else "see data", "summary": data if not isinstance(data, list) else data[:10]}

    result["note"] = "these are the stories left by visitors on the membrane. northgate reads them."
    return json.dumps(result, indent=2)


NEUTRON_API = "https://neutron.primals.eco/api/discuss"
NEUTRON_CHANNELS = {
    "inbox": "neutron-inbox",
    "notes": "neutron-notes",
    "reminders": "neutron-reminders",
    "chat": "neutron-chat",
}


def handle_neutron_read(args):
    channel = args.get("channel", "all")
    last_n = args.get("last_n", 10)

    if channel == "all":
        summary = {}
        for ch, page in NEUTRON_CHANNELS.items():
            data = fetch_json(f"{NEUTRON_API}?page={page}")
            if "error" in data:
                summary[ch] = {"error": data["error"]}
            else:
                comments = data.get("comments", [])
                summary[ch] = {
                    "total": data.get("total", 0),
                    "latest": comments[-1].get("body", "")[:100] if comments else None,
                    "latest_time": datetime.fromtimestamp(comments[-1]["epoch"], tz=timezone.utc).isoformat() if comments and "epoch" in comments[-1] else None,
                }
        summary["note"] = "neutron: self-sovereign messaging. proton locked us out so we built this."
        return json.dumps(summary, indent=2)

    page = NEUTRON_CHANNELS.get(channel)
    if not page:
        return json.dumps({"error": f"Unknown channel: {channel}. Use inbox/notes/reminders/chat/all."})

    data = fetch_json(f"{NEUTRON_API}?page={page}")
    if "error" in data:
        return json.dumps({"error": data["error"], "hint": "neutron may not be reachable"})

    comments = data.get("comments", [])
    comments.sort(key=lambda c: c.get("epoch", 0), reverse=True)
    recent = comments[:last_n]

    result = {
        "channel": channel,
        "total": data.get("total", 0),
        "messages": [],
    }
    for c in recent:
        entry = {
            "time": datetime.fromtimestamp(c.get("epoch", 0), tz=timezone.utc).isoformat(),
            "author": c.get("author", "anon"),
            "body": c.get("body", ""),
        }
        if c.get("badge"):
            entry["badge"] = c["badge"]
        result["messages"].append(entry)

    return json.dumps(result, indent=2)


def handle_neutron_write(args):
    channel = args.get("channel", "notes")
    body = args.get("body", "")
    author = args.get("author", "squirrel-mcp")

    if not body.strip():
        return json.dumps({"error": "Empty message body."})

    page = NEUTRON_CHANNELS.get(channel)
    if not page:
        return json.dumps({"error": f"Unknown channel: {channel}. Use inbox/notes/reminders/chat."})

    if channel == "reminders":
        body = "⏰ " + body

    payload = json.dumps({"page": page, "author": author, "body": body}).encode()
    try:
        req = urllib.request.Request(
            NEUTRON_API,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "squirrel-mcp/0.1"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
        return json.dumps({"ok": result.get("ok", False), "channel": channel, "echo": body[:100]})
    except Exception as e:
        return json.dumps({"error": str(e)})


def handle_journal(args):
    date = args.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    last_n = args.get("last_n", 5)

    # Try local journal first, then fetch from golgi via SSH
    journal_file = JOURNAL_DIR / f"{date}.jsonl"
    entries = []

    if journal_file.exists():
        with open(journal_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    else:
        # Try reading from golgi (squirrel-watch daemon writes here)
        import subprocess
        try:
            result = subprocess.run(
                ["ssh", "golgi", f"cat /opt/membrane/squirrel-journal/{date}.jsonl 2>/dev/null"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception:
            pass

    if not entries:
        return json.dumps({"message": f"No journal entries for {date}. Squirrel hasn't observed yet today."})

    recent = entries[-last_n:]
    return json.dumps({"date": date, "total_entries": len(entries), "entries": recent}, indent=2)


def send_response(id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id}
    if error:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method", "")
        id = req.get("id")
        params = req.get("params", {})

        if method == "initialize":
            send_response(id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "squirrel", "version": "0.1.0"},
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            send_response(id, {"tools": TOOLS})
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            if tool_name == "observe_membrane":
                text = handle_observe(tool_args)
            elif tool_name == "read_journal":
                text = handle_journal(tool_args)
            elif tool_name == "chipmunk_status":
                text = handle_chipmunk(tool_args)
            elif tool_name == "human_epitopes":
                text = handle_human_epitopes(tool_args)
            elif tool_name == "topology":
                text = handle_topology(tool_args)
            elif tool_name == "scan_sweep_sort":
                text = handle_scan_sweep_sort(tool_args)
            elif tool_name == "human_notes":
                text = handle_human_notes(tool_args)
            elif tool_name == "braid_connections":
                text = handle_braid(tool_args)
            elif tool_name == "raw_feed":
                text = handle_raw_feed(tool_args)
            elif tool_name == "read_stories":
                text = handle_stories(tool_args)
            elif tool_name == "neutron_read":
                text = handle_neutron_read(tool_args)
            elif tool_name == "neutron_write":
                text = handle_neutron_write(tool_args)
            else:
                send_response(id, error={"code": -32601, "message": f"Unknown tool: {tool_name}"})
                continue
            send_response(id, {"content": [{"type": "text", "text": text}]})
        elif method == "ping":
            send_response(id, {})
        else:
            if id is not None:
                send_response(id, error={"code": -32601, "message": f"Method not found: {method}"})


if __name__ == "__main__":
    main()
