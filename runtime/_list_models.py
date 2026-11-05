import json, urllib.request
r = urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10)
data = json.loads(r.read())
for m in sorted(data.get("models", []), key=lambda x: x["name"]):
    size_gb = m.get("size", 0) / 1024**3
    name = m["name"]
    is_gaia = "gaia" in name.lower()
    marker = "★" if is_gaia else " "
    print(f"  {marker} {name:45s} {size_gb:.1f}GB")
print(f"\n  TOTAL: {len(data.get('models', []))} models")
gaia_count = sum(1 for m in data.get("models", []) if "gaia" in m["name"].lower())
legacy_count = len(data.get("models", [])) - gaia_count
print(f"  GAIA: {gaia_count}  LEGACY: {legacy_count}")
