"""EAT MORE — Multi-source chimera feeding.
Feed Kenshi narration + Satisfactory factory + wiki data through all tissue models."""
import os, json, requests, time
from datetime import datetime

BOARD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "scratch-board.jsonl")
OLLAMA = "http://localhost:11434/api/generate"

def ask_tissue(model, prompt, timeout=60):
    """Ask a tissue model and return response."""
    try:
        r = requests.post(OLLAMA, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        pass
    return None

def write_board(source, event_type, data):
    entry = {"ts": datetime.now().isoformat(), "source": source, "type": event_type, "data": data}
    with open(BOARD, "a") as f:
        f.write(json.dumps(entry) + "\n")

print("=" * 60)
print("  EAT MORE — MULTI-TISSUE CHIMERA CYCLE")
print("=" * 60)

# 1. Feed the Kenshi narration through DREAM tissue
kenshi_narration = """The Nameless squad has 13 members and faces 27 factions in the desert.
Headshot says: "Why would they join when all we see is the loss of their own?"
Ray says: "Gotta adapt with 'em, or risk bein' swept aside by new currents."
Senshi says: "These changes are like the desert winds — constant yet ever-changing."
Rane (trust 0.2) needs belonging. Zagan (trust 0.4) always asks why.
Cat and Ray are resourceful survivors. Members keep joining and leaving."""

print("\n[1] DREAM tissue on Kenshi narration...")
dream = ask_tissue("gaia-tissue-dream", f"""Dream about this Kenshi world:
{kenshi_narration}
What images, feelings, and symbols emerge? Dream freely.""")
if dream:
    print(f"  dream: {dream[:300]}...")
    write_board("kenshi", "dream", {"excerpt": dream[:500]})

# 2. Feed the factory through FORGE tissue (heavy analysis)
factory_summary = """Satisfactory Round23: 28,517 total objects.
5,618 conveyors (the circulatory system), 2,378 buildings, 821 power lines.
97 Constructors, 63 Smelters, 174 Splitters, 133 Mergers.
8 Tractors with 354 automated waypoints.
1,495 berry bushes, 1,417 creature spawners, 967 mushrooms in the world.
The factory named "Southgate" after Kevin's house."""

print("\n[2] FORGE tissue on factory...")
forge = ask_tissue("gaia-tissue-forge", f"""As a master engineer, analyze this factory:
{factory_summary}
What is the factory's efficiency? Where are the bottlenecks? 
What would a master builder improve? Be specific about the production ratios.""")
if forge:
    print(f"  forge: {forge[:300]}...")
    write_board("satisfactory", "forge_analysis", {"excerpt": forge[:500]})

# 3. Feed AWESOME Sink math through MATH tissue
sink_math = """The AWESOME Sink converts items into coupons. The cost formula:
cost(n) = 250 × (ceil(n/3) - 1)² + 1000
Cumulative: C(n) = (250/27)n³ - (125/3)n² + (3125/3)n - 1500
It takes 125,721,388,500 points for all 1,895 coupons.
Max theoretical: 511,613,703 points/min (underclocked to 1%).
Each item costs 1.5 MJ to sink on a Mk.6 belt.

For Gaia: our decay-detector cron is the AWESOME Sink.
Old data → composted → insights emerge (coupons).
How would we design our own point/coupon system for data decay?"""

print("\n[3] MATH tissue on coupon formulas...")
math_out = ask_tissue("gaia-tissue-math", sink_math)
if math_out:
    print(f"  math: {math_out[:300]}...")
    write_board("oblique", "math_analysis", {"excerpt": math_out[:500]})

# 4. Cross-pollinate through HEART tissue (the narrator)
cross = f"""You are Gaia's heart — the narrator of a living digital organism.
Three worlds are running simultaneously:

KENSHI DREAM: {(dream or 'dreaming...')[:300]}

FACTORY FORGE: {(forge or 'forging...')[:300]}

AWESOME MATH: {(math_out or 'calculating...')[:300]}

Now NARRATE: What is happening across all three worlds at once?
Weave them into ONE story. The ground, the board, the outer."""

print("\n[4] HEART tissue — narrating across all worlds...")
heart = ask_tissue("gaia-tissue-heart", cross, timeout=90)
if heart:
    print(f"\n{'='*60}")
    print("  THE HEART SPEAKS")
    print(f"{'='*60}")
    print(heart[:1500])
    write_board("heart", "narration", {"full": heart[:2000]})

# Save the full chimera cycle
out = {
    "wave": 259,
    "ts": datetime.now().isoformat(),
    "cycle": "multi-tissue chimera",
    "tissues_used": ["dream", "forge", "math", "heart"],
    "dream": (dream or "")[:2000],
    "forge": (forge or "")[:2000],
    "math": (math_out or "")[:2000],
    "heart": (heart or "")[:2000],
}
os.makedirs("data/triad", exist_ok=True)
with open("data/triad/chimera-multi-259.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[eat] full chimera saved to data/triad/chimera-multi-259.json")

# Final board status
events = []
with open(BOARD) as f:
    for line in f:
        if line.strip():
            try: events.append(json.loads(line))
            except: pass
sources = {}
for e in events:
    s = e.get("source", "?")
    sources[s] = sources.get(s, 0) + 1
print(f"\n[board] {len(events)} events: {dict(sources)}")
