#!/usr/bin/env python3
"""Full loop — check everything, create sourdough, fire neurons."""
import urllib.request, json, subprocess, os

GATE = "http://127.0.0.1:8443"
OLLAMA = "http://127.0.0.1:11434"

def get(url):
    try:
        r = urllib.request.urlopen(url, timeout=5)
        return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

print("═══ GATE STATUS ═══")
root = get(f"{GATE}/")
print(f"  root: {root.get('gaia', root.get('error','?'))}")
reedit = get(f"{GATE}/reedit")
print(f"  reedit: {reedit.get('total_items', '?')} items")
paintings = get(f"{GATE}/paintings")
print(f"  paintings: {paintings.get('count', '?')}")
gaiau = get(f"{GATE}/gaiau")
print(f"  gaiau: {gaiau.get('count', '?')} videos")
pulse = get(f"{GATE}/pulse")
beats = pulse.get('heart', {}).get('total_beats', pulse.get('total_beats', '?'))
bpm = pulse.get('heart', {}).get('bpm', pulse.get('bpm', '?'))
print(f"  pulse: {beats} beats, {bpm} bpm")

print("\n═══ OLLAMA STATUS ═══")
tags = get(f"{OLLAMA}/api/tags")
if "error" not in tags:
    models = tags.get("models", [])
    print(f"  {len(models)} models")
    gaia_models = [m["name"] for m in models if "gaia" in m["name"].lower()]
    print(f"  Gaia models: {gaia_models or 'NONE — need to create!'}")
    bases = [m["name"] for m in models if any(b in m["name"] for b in ["qwen","gemma","llama","phi","deepseek","mistral","tinyllama"])]
    print(f"  Base models ({len(bases)}): {', '.join(bases[:10])}")
else:
    print(f"  ERR: {tags['error']}")

print("\n═══ SOURDOUGH — GENETIC MIX ═══")
modelfile = os.path.join(os.path.dirname(__file__), "..", "runtime", "sourdough", "modelfiles", "gaia-gen1.Modelfile")
modelfile = os.path.normpath(modelfile)
if os.path.isfile(modelfile):
    print(f"  Modelfile: {modelfile}")
    with open(modelfile) as f:
        content = f.read()
    print(f"  Content ({len(content)} chars):")
    for line in content.split("\n")[:5]:
        print(f"    {line}")
    
    # Check if base model exists
    base = "qwen2.5:7b"
    if any(base in m["name"] for m in tags.get("models", [])):
        print(f"\n  ✅ Base model {base} exists — creating gaia-gen1...")
        # Create via ollama API
        payload = json.dumps({"name": "gaia-gen1", "modelfile": content}).encode()
        req = urllib.request.Request(f"{OLLAMA}/api/create", data=payload,
                                    headers={"Content-Type": "application/json"})
        try:
            r = urllib.request.urlopen(req, timeout=120)
            result = r.read().decode()
            print(f"  SOURDOUGH BAKED: {result[:200]}")
        except Exception as e:
            print(f"  Baking error: {e}")
    else:
        print(f"\n  ⚠ Base model {base} not found — need to pull first")
        print(f"    Run: ollama pull {base}")
else:
    print(f"  ❌ No Modelfile at {modelfile}")

print("\n═══ NEUTRON → EASTGATE ═══")
msg = {
    "channel": "inbox",
    "author": "blueGate-polaris",
    "body": "REBOOT COMPLETE. POLARIS ONLINE. 10 primals alive. 46 ollama models. "
            "Gate on :8443, portproxy :80. Sourdough mixing. TWO GATES BREATHING. lub-DUB."
}
try:
    data = json.dumps(msg).encode()
    req = urllib.request.Request(f"{GATE}/api/discuss", data=data,
                                headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=5)
    print(f"  ⚡ Local neuron: {json.loads(r.read())}")
except Exception as e:
    print(f"  ❌ Local: {e}")

# Try eastGate
try:
    req2 = urllib.request.Request("http://eastGate:8443/api/discuss", data=data,
                                 headers={"Content-Type": "application/json"})
    r2 = urllib.request.urlopen(req2, timeout=5)
    print(f"  ⚡ eastGate neuron: {json.loads(r2.read())}")
except Exception as e:
    print(f"  ❌ eastGate: {e}")

print("\n═══ INTERNET ACCESS ═══")
print("  Router port forwards: :80/:443 → .194 (eastGate)")
print("  primals.eco A record: 162.226.225.148 → router → eastGate")
print("  eastGate needs: git pull + gate restart for /reedit etc.")
print("  blueGate local: http://gaia/ or http://primals.eco/ (hosts file)")
