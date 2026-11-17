"""Full class survey of Round23 Satisfactory save."""
import os, satisfactory_save as s
from collections import Counter

SAVE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "FactoryGame", "Saved", "SaveGames")

saves = []
for root, dirs, files in os.walk(SAVE_DIR):
    for f in files:
        if f.endswith(".sav") and "Round23_autosave_0" in f:
            saves.append(os.path.join(root, f))

path = saves[0]
print(f"Reading: {os.path.basename(path)}")
save = s.SaveGame(path)

objs = save.mPersistentAndRuntimeData.SaveObjects
print(f"Total objects: {len(objs)}")

class_counts = Counter()
buildings = Counter()
conveyors = Counter()
machines = Counter()
resources = Counter()
vehicles = Counter()
subsystems = Counter()
misc = Counter()

for obj in objs:
    cn = obj.BaseHeader.ClassName
    class_counts[cn] += 1
    short = cn.split("/")[-1].replace("_C", "").replace("Build_", "").replace("BP_", "")

    if "Conveyor" in cn or "Belt" in cn or "Pipe" in cn:
        conveyors[short] += 1
    elif "Build_" in cn or "Foundation" in cn or "Wall" in cn or "Ramp" in cn:
        buildings[short] += 1
    elif "Miner" in cn or "Smelter" in cn or "Constructor" in cn or \
         "Assembler" in cn or "Manufacturer" in cn or "Refinery" in cn or \
         "Generator" in cn or "Packager" in cn or "OilPump" in cn or "Blender" in cn:
        machines[short] += 1
    elif "Resource" in cn or "Fracking" in cn or "Geyser" in cn:
        resources[short] += 1
    elif "Vehicle" in cn or "Train" in cn or "Locomotive" in cn or "FreightWagon" in cn or "Truck" in cn or "Tractor" in cn or "Explorer" in cn:
        vehicles[short] += 1
    elif "Subsystem" in cn or "Manager" in cn or "GameMode" in cn or "GameState" in cn or "WorldSettings" in cn:
        subsystems[short] += 1
    else:
        misc[short] += 1

print(f"\n{'='*70}")
print(f"  ROUND 23 — FACTORY SURVEY")
print(f"{'='*70}")
print(f"  Buildings:   {sum(buildings.values())}")
print(f"  Conveyors:   {sum(conveyors.values())}")
print(f"  Machines:    {sum(machines.values())}")
print(f"  Resources:   {sum(resources.values())}")
print(f"  Vehicles:    {sum(vehicles.values())}")
print(f"  Subsystems:  {sum(subsystems.values())}")
print(f"  Misc:        {sum(misc.values())}")

print(f"\n  BUILDINGS ({sum(buildings.values())}):")
for name, count in buildings.most_common(15):
    print(f"    {count:5d}  {name}")

print(f"\n  CONVEYORS ({sum(conveyors.values())}):")
for name, count in conveyors.most_common(15):
    print(f"    {count:5d}  {name}")

print(f"\n  MACHINES ({sum(machines.values())}):")
for name, count in machines.most_common(15):
    print(f"    {count:5d}  {name}")

print(f"\n  RESOURCES ({sum(resources.values())}):")
for name, count in resources.most_common(10):
    print(f"    {count:5d}  {name}")

print(f"\n  VEHICLES ({sum(vehicles.values())}):")
for name, count in vehicles.most_common(5):
    print(f"    {count:5d}  {name}")

print(f"\n  ALL CLASSES ({len(class_counts)} unique):")
for cn, count in class_counts.most_common(30):
    short = cn.split("/")[-1]
    print(f"    {count:5d}  {short}")

# Also extract per-level objects
total_level_objs = 0
for i in range(len(save.mPerLevelDataMap)):
    obj_count = len(save.mPerLevelDataMap.Values[i].SaveObjects)
    total_level_objs += obj_count
print(f"\n  Per-level objects total: {total_level_objs}")
print(f"  Levels with data: {sum(1 for i in range(len(save.mPerLevelDataMap)) if len(save.mPerLevelDataMap.Values[i].SaveObjects) > 0)}")

# Sample per-level classes
level_classes = Counter()
for i in range(len(save.mPerLevelDataMap)):
    for obj in save.mPerLevelDataMap.Values[i].SaveObjects:
        cn = obj.BaseHeader.ClassName
        level_classes[cn] += 1

if level_classes:
    print(f"\n  PER-LEVEL TOP CLASSES ({len(level_classes)} unique):")
    for cn, count in level_classes.most_common(15):
        short = cn.split("/")[-1]
        print(f"    {count:5d}  {short}")
