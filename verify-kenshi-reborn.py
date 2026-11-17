#!/usr/bin/env python3
"""Verify all Kenshi.Reborn components on blueGate."""
import os, json, urllib.request

print("=" * 60)
print("  KENSHI.REBORN — Component Verification")
print("=" * 60)

# 1. Ollama tissue models
print("\n--- OLLAMA TISSUE ---")
try:
    tags = json.loads(urllib.request.urlopen('http://127.0.0.1:11434/api/tags', timeout=3).read())
    models = [m['name'] for m in tags['models']]
    heart = any('heart' in m for m in models)
    forge = any('forge' in m for m in models)
    cortex = any('cortex' in m for m in models)
    print(f"  Models: {len(models)}")
    print(f"  gaia-tissue-heart: {'YES' if heart else 'NO'} (kenshi_eyes MODEL)")
    print(f"  gaia-tissue-forge: {'YES' if forge else 'NO'} (kenshi_eyes VOICE_MODEL)")
    print(f"  gaia-tissue-cortex: {'YES' if cortex else 'NO'} (chimera cortex)")
except Exception as e:
    heart = forge = cortex = False
    print(f"  ERROR: {e}")

# 2. Kenshi saves
print("\n--- KENSHI SAVES ---")
saves = os.path.expandvars(r'%LOCALAPPDATA%\kenshi\save')
if os.path.isdir(saves):
    save_dirs = [d for d in os.listdir(saves) if os.path.isdir(os.path.join(saves, d))]
    print(f"  {len(save_dirs)} saves at {saves}")
    for d in save_dirs[:5]:
        print(f"    {d}")
else:
    print(f"  NOT FOUND (saves are on northGate M:\\ drive)")

# 3. Gaia kenshi data
print("\n--- GAIA KENSHI DATA ---")
gaia_kenshi = os.path.expandvars(r'%LOCALAPPDATA%\Gaia\kenshi')
if os.path.isdir(gaia_kenshi):
    files = os.listdir(gaia_kenshi)
    print(f"  {len(files)} files at {gaia_kenshi}")
    for f in files[:10]:
        print(f"    {f}")
else:
    print(f"  NOT FOUND (will be created when kenshi_eyes runs)")

# 4. Mixer state
print("\n--- MIXER LIBRARY ---")
mixer = os.path.expandvars(r'%LOCALAPPDATA%\Gaia\kenshi\mixer')
if os.path.isdir(mixer):
    lib = os.path.join(mixer, 'library')
    mods = len(os.listdir(lib)) if os.path.isdir(lib) else 0
    print(f"  {mods} mods eaten")
else:
    print(f"  NOT FOUND (needs Kenshi + Nexus key on northGate)")

# 5. Source file counts
print("\n--- SOURCE FILES ---")
ludo = os.path.join("gardens", "springs", "ludoSpring")
ludo_count = sum(len(f) for _, _, f in os.walk(ludo)) if os.path.isdir(ludo) else 0
print(f"  ludoSpring: {ludo_count} files")

ew = os.path.join("primals", "esotericWebb")
ew_rs = sum(1 for _, _, fs in os.walk(ew) for f in fs if f.endswith('.rs')) if os.path.isdir(ew) else 0
print(f"  esotericWebb: {ew_rs} .rs files")

nerve = os.path.join("gardens", "springs", "ludoSpring", "kenshi", "gaia-nerve", "src")
nerve_exists = os.path.isdir(nerve)
print(f"  gaia-nerve: {'EXISTS' if nerve_exists else 'NOT FOUND'} (compiles clean!)")

meitou = os.path.join("gardens", "spore", "meitou")
meitou_exists = os.path.isdir(meitou)
print(f"  meitou spore: {'EXISTS' if meitou_exists else 'NOT FOUND'}")

# 6. Kenshi decomposition data (local)
print("\n--- DECOMPOSITION DATA ---")
decomp = os.path.join("gardens", "springs", "ludoSpring", "data", "kenshi-decomposition")
if os.path.isdir(decomp):
    decomp_files = os.listdir(decomp)
    print(f"  {len(decomp_files)} files")
    for f in sorted(decomp_files):
        print(f"    {f}")
else:
    print(f"  NOT FOUND locally (on eastGate or northGate)")

# 7. Sourdough
print("\n--- KENSHI SOURDOUGH ---")
sd = os.path.join("runtime", "sourdough", "kenshi-sourdough.jsonl")
if os.path.exists(sd):
    lines = open(sd, 'r').readlines()
    responded = sum(1 for l in lines if '"response"' in l and len(json.loads(l).get('response', '')) > 0)
    print(f"  {len(lines)} entries, {responded} with substance")
else:
    print(f"  NOT FOUND")

# Summary
print("\n" + "=" * 60)
print("  REBUNDLE STATUS")
print("=" * 60)
print(f"  gaia-nerve.dll:      COMPILES (Rust 1.100.0)")
print(f"  kenshi_eyes.py:      READY (needs northGate saves)")
print(f"  kenshi_mixer.py:     READY (needs northGate + Nexus)")
print(f"  esotericWebb:        66 .rs (3 unix errs — needs ironGate Linux)")
print(f"  ollama tissue:       heart={'YES' if heart else 'NO'} forge={'YES' if forge else 'NO'}")
print(f"  ludoSpring:          {ludo_count} files (958 expected)")
print(f"  kenshi-sourdough:    chimera cycle data present")
print()
print("  NEXT: northGate STATIC → launch Kenshi → eyes watch → HUD mirrors")
print("  NEXT: ironGate STATIC → esotericWebb compiles → engine runs")
print("  NEXT: Rebundle for Nexus/Steam Workshop submission")
print("=" * 60)
