"""Eat the Round23 Satisfactory save through the chimera cycle.
Extract full factory state, feed through tissue models, write to board."""
import os, json, sys, time, requests
from collections import Counter

# Parse the big save
import satisfactory_save as s
SAVE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "FactoryGame", "Saved", "SaveGames")

# Find Round23
saves = []
for root, dirs, files in os.walk(SAVE_DIR):
    for f in files:
        if f.endswith(".sav") and "Round23_autosave_0" in f:
            saves.append(os.path.join(root, f))

if not saves:
    print("Round23 not found, using newest")
    for root, dirs, files in os.walk(SAVE_DIR):
        for f in files:
            if f.endswith(".sav"):
                saves.append((os.path.getmtime(os.path.join(root, f)), os.path.join(root, f)))
    saves.sort(reverse=True)
    saves = [saves[0][1]]

path = saves[0] if isinstance(saves[0], str) else saves[0]
print(f"[eat] reading: {os.path.basename(path)}")
save = s.SaveGame(path)

# Extract full state
objs = save.mPersistentAndRuntimeData.SaveObjects
print(f"[eat] {len(objs)} persistent objects")

class_counts = Counter()
buildings = Counter()
conveyors = Counter()
machines = Counter()
for obj in objs:
    cn = obj.BaseHeader.ClassName
    class_counts[cn] += 1
    short = cn.split("/")[-1].replace("_C", "").replace("Build_", "").replace("BP_", "")
    if "Conveyor" in cn or "Belt" in cn or "Pipe" in cn:
        conveyors[short] += 1
    elif "Build_" in cn or "Foundation" in cn or "Wall" in cn:
        buildings[short] += 1
    elif "Constructor" in cn or "Smelter" in cn or "Assembler" in cn or "Manufacturer" in cn or "Foundry" in cn or "Refinery" in cn:
        machines[short] += 1

# Level objects
level_classes = Counter()
level_total = 0
for i in range(len(save.mPerLevelDataMap)):
    for obj in save.mPerLevelDataMap.Values[i].SaveObjects:
        level_total += 1
        cn = obj.BaseHeader.ClassName
        level_classes[cn] += 1

# Build the factory profile
factory = {
    "session": str(save.mSaveHeader.SessionName),
    "played_hours": round(save.mSaveHeader.PlayDurationSeconds / 3600, 1),
    "build_version": save.mSaveHeader.BuildVersion,
    "persistent_objects": len(objs),
    "level_objects": level_total,
    "unique_classes": len(class_counts),
    "buildings": sum(buildings.values()),
    "conveyors": sum(conveyors.values()),
    "machines": sum(machines.values()),
    "top_buildings": dict(buildings.most_common(15)),
    "top_conveyors": dict(conveyors.most_common(10)),
    "top_machines": dict(machines.most_common(10)),
    "top_classes": dict(class_counts.most_common(20)),
    "level_top": {cn.split("/")[-1].replace("_C","").replace("BP_",""): c for cn, c in level_classes.most_common(10)},
}

# Print summary
print(f"\n{'='*60}")
print(f"  FACTORY PROFILE: {factory['session']}")
print(f"  {factory['played_hours']}h | Build {factory['build_version']}")
print(f"  {factory['persistent_objects']} persistent + {factory['level_objects']} level = {factory['persistent_objects']+factory['level_objects']} total")
print(f"  {factory['unique_classes']} unique classes")
print(f"  Buildings: {factory['buildings']} | Conveyors: {factory['conveyors']} | Machines: {factory['machines']}")
print(f"{'='*60}")

# Now feed through chimera (cortex model)
print("\n[chimera] feeding factory profile through tissue-cortex...")
prompt = f"""Analyze this Satisfactory factory save data as if it were a living organism's production system:

Session: {factory['session']}
Played: {factory['played_hours']} hours
Total objects: {factory['persistent_objects'] + factory['level_objects']}
Buildings: {factory['buildings']}
Conveyors: {factory['conveyors']} (the bloodstream)
Machines: {factory['machines']} (the organs)

Top buildings: {json.dumps(dict(list(factory['top_buildings'].items())[:8]), indent=2)}
Top conveyors: {json.dumps(dict(list(factory['top_conveyors'].items())[:5]), indent=2)}

World (level objects): {json.dumps(dict(list(factory['level_top'].items())[:8]), indent=2)}

Describe this factory as if it were a biological organism. What is its metabolism? Its circulatory system? Its nervous system? What stage of growth is it in?"""

try:
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "gaia-tissue-cortex",
        "prompt": prompt,
        "stream": False
    }, timeout=60)
    if r.status_code == 200:
        cortex = r.json().get("response", "")
        print(f"[cortex] {cortex[:500]}...")
    else:
        # Try with a generic model
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        cortex = r.json().get("response", "") if r.status_code == 200 else "cortex unavailable"
        print(f"[cortex/llama3.2] {cortex[:500]}...")
except Exception as e:
    cortex = f"cortex error: {e}"
    print(f"[cortex] {cortex}")

# Save the full digest
digest = {
    "wave": 259,
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "factory": factory,
    "chimera": {
        "cortex": cortex[:2000] if cortex else None,
    },
    "triad_mapping": {
        "conveyor_belts": "= data pipes in the organism",
        "power_lines": "= compute connections",
        "constructors_smelters": "= primals (production buildings)",
        "resource_nodes": "= OSINT sources (RSS feeds)",
        "berry_bushes_mushrooms": "= organic growth (sourdough culture)",
        "creature_spawners": "= event generators",
        "vehicle_waypoints": "= automated cron paths",
    }
}

out_path = os.path.join("data", "triad", "satisfactory-chimera-259.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(digest, f, indent=2)
print(f"\n[eat] digest saved to {out_path}")

# Write to scratch board
board_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "scratch-board.jsonl")
entry = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "source": "satisfactory",
    "type": "factory_chimera",
    "data": {
        "session": factory["session"],
        "objects": factory["persistent_objects"] + factory["level_objects"],
        "buildings": factory["buildings"],
        "conveyors": factory["conveyors"],
        "machines": factory["machines"],
        "chimera_excerpt": cortex[:300] if cortex else None,
    }
}
with open(board_path, "a") as f:
    f.write(json.dumps(entry) + "\n")
print(f"[eat] board event written")
