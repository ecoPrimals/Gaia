"""Probe the Satisfactory save object structure."""
import os, satisfactory_save as s

SAVE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "FactoryGame", "Saved", "SaveGames")

# Find newest save
import glob
saves = []
for root, dirs, files in os.walk(SAVE_DIR):
    for f in files:
        if f.endswith(".sav"):
            full = os.path.join(root, f)
            saves.append((os.path.getmtime(full), full, f))
saves.sort(reverse=True)
path = saves[0][1]
name = saves[0][2]
print(f"Reading: {name}")

save = s.SaveGame(path)

# Header
h = save.mSaveHeader
print(f"\n=== HEADER ===")
for attr in dir(h):
    if not attr.startswith("_"):
        try:
            val = getattr(h, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except:
            pass

# Objects
objs = save.mPersistentAndRuntimeData.SaveObjects
print(f"\n=== {len(objs)} OBJECTS ===")
if len(objs) > 0:
    obj0 = objs[0]
    print(f"\nFirst object type: {type(obj0)}")
    print(f"First object attrs:")
    for attr in dir(obj0):
        if not attr.startswith("_"):
            try:
                val = getattr(obj0, attr)
                if not callable(val):
                    print(f"  {attr}: {repr(val)[:200]}")
            except Exception as e:
                print(f"  {attr}: ERROR {e}")

    # Sample a few objects
    print(f"\n=== SAMPLE OBJECTS (first 10) ===")
    for i, obj in enumerate(objs[:10]):
        attrs = {}
        for attr in ["TypePath", "ClassName", "PathName", "InstanceName", "LevelName", "ObjectName"]:
            try:
                val = getattr(obj, attr, None)
                if val is not None:
                    attrs[attr] = str(val)
            except:
                pass
        print(f"  [{i}] {attrs}")

    # Also check if there's a different way to get class
    print(f"\n=== OBJECT TYPES in sample ===")
    types_seen = set()
    for obj in objs[:50]:
        t = type(obj).__name__
        if t not in types_seen:
            types_seen.add(t)
            print(f"  type: {t}")

# Levels
print(f"\n=== LEVELS ===")
print(f"Level count: {len(save.mPerLevelDataMap)}")
for i in range(min(5, len(save.mPerLevelDataMap))):
    key = save.mPerLevelDataMap.Keys[i]
    val = save.mPerLevelDataMap.Values[i]
    obj_count = len(val.SaveObjects)
    print(f"  {key}: {obj_count} objects")
    if obj_count > 0:
        obj0 = val.SaveObjects[0]
        for attr in dir(obj0):
            if not attr.startswith("_"):
                try:
                    v = getattr(obj0, attr)
                    if not callable(v):
                        print(f"    {attr}: {repr(v)[:150]}")
                except:
                    pass
        break

# Find the big save (Round23) for more interesting data
round23 = [s for s in saves if "Round23_autosave_0" in s[2]]
if round23:
    path2 = round23[0][1]
    print(f"\n\n=== READING BIGGER SAVE: Round23 ===")
    save2 = s.SaveGame(path2)
    objs2 = save2.mPersistentAndRuntimeData.SaveObjects
    print(f"Objects: {len(objs2)}")
    if len(objs2) > 0:
        for attr in dir(objs2[0]):
            if not attr.startswith("_"):
                try:
                    val = getattr(objs2[0], attr)
                    if not callable(val):
                        print(f"  {attr}: {repr(val)[:200]}")
                except:
                    pass
