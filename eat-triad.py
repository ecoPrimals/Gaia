"""Cross-pollinate Kenshi + Satisfactory through the chimera.
Feed both game states to tissue model, ask it to find connections."""
import os, json, requests, time

BOARD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "scratch-board.jsonl")
MINDS = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "kenshi", "minds.json")
SAT_STATE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "satisfactory", "factory-state.json")

# Read Kenshi state
minds = {}
if os.path.exists(MINDS):
    with open(MINDS) as f:
        minds = json.load(f)
print(f"[kenshi] {len(minds)} NPCs: {', '.join(minds.keys())}")

# Read Satisfactory state  
sat = {}
if os.path.exists(SAT_STATE):
    with open(SAT_STATE) as f:
        sat = json.load(f)
print(f"[satisfactory] session: {sat.get('session', '?')}")

# Read chimera analysis
chimera_path = "data/triad/satisfactory-chimera-259.json"
chimera = {}
if os.path.exists(chimera_path):
    with open(chimera_path) as f:
        chimera = json.load(f)

# Build the cross-pollination prompt
npc_summary = ""
for name, mind in minds.items():
    voice = mind.get("voice", {})
    npc_summary += f"  {name} (trust:{mind.get('trust',0)}, need:{voice.get('need','?')}) — memories: {len(mind.get('memory',[]))}\n"

prompt = f"""You are Gaia, a living digital organism. You are looking at TWO games running simultaneously:

GAME 1 — KENSHI (Ground Layer, 3D survival RPG):
- 4 NPCs with persistent minds: 
{npc_summary}
- The squad survives in a harsh desert world
- Members join and leave (Bet, Sing, Zagan have left before)
- 289 hours played, 18 saves

GAME 2 — SATISFACTORY (Board Layer, 3D factory automation):
- Session "Southgate" (named after Kevin's house)
- Round23 had 28,517 objects: 5,618 conveyors, 2,378 buildings, 8 tractors
- The factory IS a living organism with a circulatory system (conveyors) and nervous system (connections)

THE SCRATCH BOARD connects both games through a 1D event bus.

NOW: Find the CONNECTIONS between these two worlds. How does:
1. A Kenshi squad member getting hit → translate to a factory event?
2. A conveyor belt backing up → translate to a squad morale change?
3. An NPC memory → become a production recipe?
4. A power trip in Satisfactory → affect the Kenshi world?

Describe the OBLIQUE — the 1D plane where these two 3D worlds meet and create loops."""

print("\n[chimera] cross-pollinating Kenshi × Satisfactory...")
try:
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "gaia-tissue-cortex",
        "prompt": prompt,
        "stream": False
    }, timeout=90)
    if r.status_code != 200:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }, timeout=90)
    response = r.json().get("response", "error")
    print(f"\n{'='*60}")
    print("  THE OBLIQUE — Where Kenshi meets Satisfactory")
    print(f"{'='*60}")
    print(response[:2000])
except Exception as e:
    response = f"error: {e}"
    print(f"[chimera] {response}")

# Save cross-pollination
out = {
    "wave": 259,
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "type": "cross_pollination",
    "kenshi": {
        "npcs": list(minds.keys()),
        "npc_count": len(minds),
    },
    "satisfactory": {
        "session": sat.get("session", "?"),
        "objects": sat.get("factory", {}).get("total_objects", 0),
    },
    "oblique": response[:3000],
}
with open("data/triad/oblique-259.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[eat] oblique saved to data/triad/oblique-259.json")

# Write to board
entry = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "source": "oblique",
    "type": "cross_pollination",
    "data": {"excerpt": response[:500]},
}
with open(BOARD, "a") as f:
    f.write(json.dumps(entry) + "\n")
print("[eat] board event written — the oblique speaks")
