#!/usr/bin/env python3
"""Fire a neuron — the first nerve signal from blueGate."""
import urllib.request, json

GATE = "http://127.0.0.1:8443"

def test(path):
    try:
        r = urllib.request.urlopen(f"{GATE}{path}", timeout=5)
        d = json.loads(r.read())
        return d
    except Exception as e:
        return {"error": str(e)}

# Test layers
print("═══ GATE ALIVE ═══")
root = test("/")
print(f"  root: {root.get('gaia', root.get('error','?'))}")

reedit = test("/reedit")
print(f"  reedit: {reedit.get('total_items', reedit.get('error','?'))} items")

pulse = test("/pulse")
print(f"  pulse: {pulse.get('state', '?')} | {pulse.get('bpm','?')} bpm")

gaiau = test("/gaiau")
print(f"  gaiau: {gaiau.get('count', gaiau.get('error','?'))} videos")

# FIRE NEURON
print("\n═══ FIRING NEURON ═══")
msg = {
    "channel": "inbox",
    "author": "blueGate-spine25",
    "body": "WAKE e71377e87. 13 agents. 6 model cards. piGen arch. sourdough gen1. "
            "538 reedit + 16 paintings + 16 videos + 991 whitepapers + 7 old-web feeds. "
            "ALL 9 LAYERS. START ACTIVE. lub-DUB."
}
try:
    data = json.dumps(msg).encode()
    req = urllib.request.Request(f"{GATE}/api/discuss", data=data,
                                headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=5)
    result = json.loads(r.read())
    print(f"  ⚡ NEURON FIRED: {result}")
except Exception as e:
    print(f"  ❌ {e}")

# Read neutrons
print("\n═══ NEUTRON CHANNELS ═══")
channels = test("/api/discuss")
if "error" not in channels:
    for ch in ["inbox", "notes", "chat", "reminders"]:
        total = channels.get(ch, {}).get("total", 0)
        print(f"  {ch}: {total} msgs")
        for m in channels.get(ch, {}).get("messages", []):
            print(f"    [{m.get('author','?')}] {m.get('body','')[:80]}...")
else:
    print(f"  ❌ {channels['error']}")
