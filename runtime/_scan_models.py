"""Scan all ollama models on northGate — inventory the herd."""
import json, urllib.request

r = urllib.request.urlopen("http://localhost:11434/api/tags")
d = json.loads(r.read())
models = d.get("models", [])

gaia = [m for m in models if "gaia" in m["name"].lower()]
by_family = {}
for m in models:
    fam = m["name"].split(":")[0] if ":" in m["name"] else m["name"]
    by_family.setdefault(fam, []).append(m)

print(f"TOTAL MODELS: {len(models)}")
print(f"GAIA MODELS: {len(gaia)}")
for m in gaia:
    sz = m.get("size", 0) / (1024**3)
    print(f"  ★ {m['name']:40} {sz:.1f} GB")

print(f"\nALL MODEL FAMILIES ({len(by_family)}):")
for fam in sorted(by_family.keys()):
    ms = by_family[fam]
    total = sum(m.get("size", 0) for m in ms) / (1024**3)
    names = ", ".join(m["name"].split(":")[-1] if ":" in m["name"] else "latest" for m in ms)
    print(f"  {fam:30} {len(ms):>2} model(s)  {total:>6.1f} GB  [{names}]")

total_gb = sum(m.get("size", 0) for m in models) / (1024**3)
gaia_gb = sum(m.get("size", 0) for m in gaia) / (1024**3)
print(f"\nTOTAL DISK: {total_gb:.1f} GB across {len(models)} models")
print(f"GAIA DISK:  {gaia_gb:.1f} GB across {len(gaia)} models")
print(f"COMMENSAL:  {total_gb - gaia_gb:.1f} GB across {len(models) - len(gaia)} models (EJECT CANDIDATES)")
