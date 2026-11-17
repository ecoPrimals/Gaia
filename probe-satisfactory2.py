"""Probe deeper into Satisfactory save object headers."""
import os, satisfactory_save as s

SAVE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "FactoryGame", "Saved", "SaveGames")

# Use the bigger save (Round23) for more data
import glob
saves = []
for root, dirs, files in os.walk(SAVE_DIR):
    for f in files:
        if f.endswith(".sav") and "Round23_autosave_0" in f:
            saves.append(os.path.join(root, f))

if not saves:
    for root, dirs, files in os.walk(SAVE_DIR):
        for f in files:
            if f.endswith(".sav") and "ASDFADSF" in f:
                saves.append(os.path.join(root, f))

path = saves[0] if saves else None
print(f"Reading: {path}")
save = s.SaveGame(path)

objs = save.mPersistentAndRuntimeData.SaveObjects
print(f"Objects: {len(objs)}")

# Deep probe the BaseHeader
obj0 = objs[0]
print(f"\n=== BaseHeader attributes ===")
bh = obj0.BaseHeader
for attr in dir(bh):
    if not attr.startswith("_"):
        try:
            val = getattr(bh, attr)
            if not callable(val):
                print(f"  {attr}: {repr(val)[:300]}")
        except Exception as e:
            print(f"  {attr}: ERROR {e}")

# Also probe the actor header
print(f"\n=== Header (FActorSaveHeader) attributes ===")
ah = obj0.Header
for attr in dir(ah):
    if not attr.startswith("_"):
        try:
            val = getattr(ah, attr)
            if not callable(val):
                print(f"  {attr}: {repr(val)[:300]}")
        except Exception as e:
            print(f"  {attr}: ERROR {e}")

# Probe the Object (AActor)
print(f"\n=== Object (AActor) attributes ===")
ao = obj0.Object
for attr in dir(ao):
    if not attr.startswith("_"):
        try:
            val = getattr(ao, attr)
            if not callable(val):
                print(f"  {attr}: {repr(val)[:300]}")
        except Exception as e:
            print(f"  {attr}: ERROR {e}")

# Now sample 20 objects to find class names
from collections import Counter
class_names = Counter()
print(f"\n=== SAMPLING 100 OBJECTS FOR CLASS NAMES ===")
for i, obj in enumerate(objs[:100]):
    bh = obj.BaseHeader
    class_name = "?"
    for field in ["ClassName", "TypePath", "ObjectName", "ClassPath"]:
        v = getattr(bh, field, None)
        if v is not None and str(v) != "":
            class_name = str(v)
            break
    if class_name == "?":
        # try header
        ah = obj.Header
        for field in dir(ah):
            if not field.startswith("_"):
                try:
                    v = getattr(ah, field)
                    if not callable(v) and isinstance(v, str) and "/" in v:
                        class_name = v
                        break
                except:
                    pass
    class_names[class_name] += 1
    if i < 5:
        print(f"  [{i}] class: {class_name}")

print(f"\n=== TOP CLASSES IN SAMPLE ===")
for cls, count in class_names.most_common(20):
    print(f"  {count:4d}  {cls}")

# Check if there's a .Properties or similar
print(f"\n=== FIRST OBJECT — ALL nested attrs ===")
for attr_name in ["BaseHeader", "Header", "Object"]:
    parent = getattr(obj0, attr_name)
    for attr in dir(parent):
        if not attr.startswith("_"):
            try:
                val = getattr(parent, attr)
                if not callable(val):
                    # If it's another object, try going deeper
                    if hasattr(val, '__dict__') or (not isinstance(val, (str, int, float, bool, bytes))):
                        for a2 in dir(val):
                            if not a2.startswith("_"):
                                try:
                                    v2 = getattr(val, a2)
                                    if not callable(v2):
                                        print(f"  {attr_name}.{attr}.{a2}: {repr(v2)[:200]}")
                                except:
                                    pass
            except:
                pass
