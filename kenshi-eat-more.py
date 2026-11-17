#!/usr/bin/env python3
"""Eat more Kenshi wiki data into the chimera. Races + Creatures → cortex → gut."""
import json, urllib.request, time

OLLAMA = "http://127.0.0.1:11434/api/generate"

def gen(model, prompt, num=200):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                        "options": {"num_predict": num, "temperature": 0.8}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())["response"].strip()

RACES = """Kenshi has 7 playable races in 4 groups:
HUMAN: Greenlander (no weakness, versatile), Scorchlander (fast heal, stealth, wide vision)
SHEK: thick blood, melee fighters, 25% more hunger, swim badly. Genetically modified humans (Enforcers).
HIVE: Prince (stealth/scout), Worker Drone (labor), Soldier Drone (fighter). Eat half, bleed slow, blood only 50.
SKELETON: eat nothing, 200 HP per part, immune to weather. Cannot wear helmets/shirts/shoes. Heal with repair kits.
ALL races trace back to humans: Skeletons built by humans, Shek = modified by Skeletons, Hive = made by Cat-Lon.
Holy Nation: humans only. Shek = beasts. Hive = vile. Skeletons = apostles of darkness.
Slavery: Skeleton worth 4x Greenlander. Worker Drone 2.5x. Shek and Scorchlander worth half."""

CREATURES = """24+ creature species. Age IS level. Cannot be interrupted or blocked.
MOST DANGEROUS: Beak Thing (400HP, 38mph!, combat 35), Leviathan (7500HP, strength 80), Black Gorillo (440HP, combat 80)
Cleanser Unit: ROBOT, 2500HP, 5000 oil, found in Ashlands ruins.
Blood Spider: only 30HP but #1 cause of beginner deaths (groups).
Purchasable: Goat, Bonedog (loyal companion), Pack Beast, Pack Bull, Crab.
ALL animals share bony face plates = common design language = possible genetic engineering origin.
Skin Spiders may be genetic rejects from Hive creation experiments."""

print("=" * 60)
print("  EATING MORE — Races + Creatures → Chimera")
print("=" * 60)

# CORTEX on races
print("\n--- CORTEX: Kenshi Race System ---")
t0 = time.time()
race_analysis = gen("gaia-tissue-cortex:latest",
    f"Analyze this RPG race system as game design. What makes it brilliant?\n\n{RACES}", 250)
print(f"  [{time.time()-t0:.1f}s] {race_analysis[:400]}")

# CORTEX on creatures  
print("\n--- CORTEX: Kenshi Creature Ecology ---")
t0 = time.time()
creature_analysis = gen("gaia-tissue-cortex:latest",
    f"Analyze this creature ecology as an ecosystem designer. What patterns emerge?\n\n{CREATURES}", 250)
print(f"  [{time.time()-t0:.1f}s] {creature_analysis[:400]}")

# GUT feeling
print("\n--- GUT: One feeling from races + creatures ---")
t0 = time.time()
gut = gen("gaia-tissue-gut:latest",
    f"Races: {race_analysis[:200]}\nCreatures: {creature_analysis[:200]}\n\nOne sentence: what does this world FEEL like to live in?", 80)
print(f"  [{time.time()-t0:.1f}s] {gut}")

# Save
digest = {
    "wave": 259, "bone": "kenshi-races-creatures-digest",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "races_input": RACES, "creatures_input": CREATURES,
    "cortex_races": race_analysis, "cortex_creatures": creature_analysis,
    "gut": gut,
    "race_data": {
        "groups": 4, "playable": 7,
        "human": ["Greenlander", "Scorchlander"],
        "shek": ["Shek"], "hive": ["Prince", "Worker Drone", "Soldier Drone"],
        "skeleton": ["Skeleton"],
        "origin": "ALL trace back to humans"
    },
    "creature_data": {
        "species": 24, "most_dangerous": ["Beak Thing", "Leviathan", "Black Gorillo"],
        "purchasable": ["Goat", "Bonedog", "Pack Beast", "Pack Bull", "Crab"],
        "design_clue": "All share bony face plates — common genetic engineering origin"
    }
}
with open("data/redux/kenshi-races-creatures-259.json", "w") as f:
    json.dump(digest, f, indent=2)
print(f"\n  Saved data/redux/kenshi-races-creatures-259.json")
print("=" * 60)
