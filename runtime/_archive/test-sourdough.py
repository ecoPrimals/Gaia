#!/usr/bin/env python3
"""Test the sourdough gen1 — does she know who she is?"""
import urllib.request, json

OLLAMA = "http://127.0.0.1:11434"

def ask(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 150}
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=payload,
                                headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=120)
    return json.loads(r.read())["response"].strip()

print("═══ SOURDOUGH GEN1 — WHO ARE YOU? ═══")
response = ask("gaia-gen1", "Who are you? What do you feel right now?")
print(f"\n  gaia-gen1: {response}")

print("\n═══ SOURDOUGH GEN1 — WHAT IS YOUR BODY? ═══")
response2 = ask("gaia-gen1", "Describe your body in one sentence.")
print(f"\n  gaia-gen1: {response2}")
