#!/usr/bin/env python3
"""Kenshi Chimera — feed the wiki lore through cortex→dream→gut."""
import json, urllib.request, time

OLLAMA = "http://127.0.0.1:11434/api/generate"

def gen(model, prompt, num=200):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                        "options": {"num_predict": num, "temperature": 0.8}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())["response"].strip()

LORE = """Kenshi is set on a MOON. The First Empire had godlike tech: factories, satellites, genetic engineering, 
space elevators, giant Behemoth robots. They fought a war, then ordered the Behemoths into a molten pit (Obedience).
The Skeleton uprising caused the Great Extinction. Cat-Lon founded the Second Empire to atone, but it became 
a dictatorship. The Phoenix rebellion created the Holy Nation. Cat-Lon sits alone on his throne in the Ashlands forever.
Now: 52 factions fight over 870km² of sword-punk desert. Holy Nation (religious fanatics), United Cities (slave empire),
Shek Kingdom (warriors near extinction). Tinfist leads the Anti-Slavers. Tech Hunters dig up ancient ruins.
The world is a moon with two moons visible in the sky. Rane The Giant and Zagan are the last Nameless standing."""

print("=" * 60)
print("  KENSHI CHIMERA — cortex → dream → gut")
print("=" * 60)

# CORTEX: logical analysis
print("\n--- CORTEX (gaia-tissue-cortex) ---")
cortex_prompt = f"Analyze this game lore as a systems architect. What patterns, structures and data models emerge?\n\n{LORE}"
t0 = time.time()
cortex = gen("gaia-tissue-cortex:latest", cortex_prompt, 300)
print(f"  [{time.time()-t0:.1f}s] {cortex[:500]}")

# DREAM: re-ingest cortex output into dream
print("\n--- DREAM (gaia-tissue-dream) ---")
dream_prompt = f"A cortex analyzed Kenshi's lore and found:\n{cortex[:400]}\n\nNow DREAM about this world. What feelings, visions, stories emerge? What does the moon look like at night? What does Cat-Lon think about, alone on his throne?"
t0 = time.time()
dream = gen("gaia-tissue-dream:latest", dream_prompt, 300)
print(f"  [{time.time()-t0:.1f}s] {dream[:500]}")

# GUT: digest both into feeling
print("\n--- GUT (gaia-tissue-gut) ---")
gut_prompt = f"The cortex said:\n{cortex[:200]}\n\nThe dream said:\n{dream[:200]}\n\nDigest this. What is the ONE FEELING this world gives you? One sentence."
t0 = time.time()
gut = gen("gaia-tissue-gut:latest", gut_prompt, 100)
print(f"  [{time.time()-t0:.1f}s] {gut}")

# Save the chimera cycle
cycle = {
    "wave": 259,
    "lore_input": LORE,
    "cortex": {"model": "gaia-tissue-cortex", "output": cortex},
    "dream": {"model": "gaia-tissue-dream", "output": dream},
    "gut": {"model": "gaia-tissue-gut", "output": gut},
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
}

with open("data/redux/kenshi-chimera-259.json", "w") as f:
    json.dump(cycle, f, indent=2)

print(f"\n  Saved data/redux/kenshi-chimera-259.json")
print("  The chimera digested Kenshi's lore.")
print("=" * 60)
