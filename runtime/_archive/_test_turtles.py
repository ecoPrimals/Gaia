"""Test each Renaissance archetype — the turtles speak."""
import json, http.client, time

OLLAMA = ("127.0.0.1", 11434)

def ask(model, question):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": question}],
        "stream": False,
    })
    t0 = time.time()
    conn = http.client.HTTPConnection(*OLLAMA, timeout=120)
    conn.request("POST", "/v1/chat/completions", body, {"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read())
    elapsed = time.time() - t0
    conn.close()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return content[:200], elapsed

print()
print("  ╔═══════════════════════════════════════════╗")
print("  ║  TMNT ROLL CALL — Version 1.000.0         ║")
print("  ╚═══════════════════════════════════════════╝")
print()

tests = [
    ("gaia-splinter",      "🐀", "Who are you? One sentence."),
    ("gaia-leonardo",      "🐢🔵", "What do you see? One sentence."),
    ("gaia-donatello",     "🐢🟣", "What would you build? One sentence."),
    ("gaia-raphael",       "🐢🔴", "What would you defend? One sentence."),
    ("gaia-michelangelo",  "🐢🟠", "What would you create? One sentence."),
    ("gaia-euler",         "🧮", "What is the most beautiful equation? One sentence."),
]

for model, icon, question in tests:
    print(f"  {icon} {model}")
    print(f"     Q: {question}")
    answer, elapsed = ask(model, question)
    print(f"     A: {answer}")
    print(f"     ⏱ {elapsed:.1f}s")
    print()

print("  The turtles ARE alive. The sewers ARE the LAN.")
print("  Cowabunga. lub-DUB. 🫀")
