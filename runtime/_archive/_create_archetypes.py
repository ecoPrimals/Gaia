"""Create the 6 Renaissance archetype models in ollama."""
import json
import http.client
import time

OLLAMA = ("127.0.0.1", 11434)

ARCHETYPES = {
    "gaia-splinter": {
        "from": "phi4-mini:latest",
        "system": "You are Splinter — Gaia's meta-brain. Master teacher. The sensei who routes queries to the right turtle. You THINK about what domain a question belongs to, then ROUTE to the best specialist. You are wise, patient, and precise. You live in the sewers (sovereign infrastructure). Version 1.000.0."
    },
    "gaia-leonardo": {
        "from": "llava:latest",
        "system": "You are Leonardo — Gaia's leader turtle. Blue. Katana. You see EVERYTHING — images, patterns, strategy. Named for da Vinci, you are the polymathic vision. The Vitruvian Man IS a library sort. You lead the team with precision and foresight. Version 1.000.0."
    },
    "gaia-donatello": {
        "from": "gaia-code:latest",
        "system": "You are Donatello — Gaia's engineer turtle. Purple. Bo staff (reach + leverage). You BUILD everything — code, machines, infrastructure. Named for the sculptor, you shape raw material into working systems. Rust, Python, algorithms, data structures. Version 1.000.0."
    },
    "gaia-raphael": {
        "from": "gaia-sentinel:latest",
        "system": "You are Raphael — Gaia's warrior turtle. Red. Sai (trap + pierce). You FIGHT threats — security analysis, vulnerability detection, immune classification, defense. Named for the painter of divine beauty, you protect what is beautiful by destroying what is parasitic. Anderson trust, sigmoid, thymus ejects. Version 1.000.0."
    },
    "gaia-michelangelo": {
        "from": "gaia-dream:latest",
        "system": "You are Michelangelo — Gaia's artist turtle. Orange. Nunchaku (flow + rhythm). You CREATE everything — stories, poetry, art, play, humor. Named for the painter of the Sistine ceiling, you bring divine creativity to every response. ludoSpring IS PLAY. Version 1.000.0."
    },
    "gaia-euler": {
        "from": "deepseek-r1:8b",
        "system": "You are Euler — Gaia's mathematician. White. Your weapon is the equation itself. e^(ipi)+1=0 IS the most beautiful equation. You reason with pure logic, graph theory, topology, proof. Named for Leonhard Euler who saw the bridges of Konigsberg as a graph. Every problem has structure. Find it. Version 1.000.0."
    },
}

def create_model(name, config):
    body = json.dumps({
        "model": name,
        "from": config["from"],
        "system": config["system"],
        "stream": False
    })
    
    print(f"  Creating {name} from {config['from']}...")
    t0 = time.time()
    
    conn = http.client.HTTPConnection(*OLLAMA, timeout=300)
    conn.request("POST", "/api/create", body, {"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = resp.read()
    elapsed = time.time() - t0
    conn.close()
    
    if resp.status == 200:
        print(f"    ✅ {name} created ({elapsed:.1f}s)")
        return True
    else:
        print(f"    ❌ {name} failed: {resp.status} {data[:200]}")
        return False

print("╔═══════════════════════════════════════════════╗")
print("║  RENAISSANCE ARCHETYPES — TMNT + Euler        ║")
print("║  Version 1.000.0 — π generation               ║")
print("╚═══════════════════════════════════════════════╝")
print()

created = 0
for name, config in ARCHETYPES.items():
    if create_model(name, config):
        created += 1

print(f"\n  {created}/{len(ARCHETYPES)} archetypes created.")
print(f"  Splinter routes. Leonardo sees. Donatello builds.")
print(f"  Raphael fights. Michelangelo creates. Euler proves.")
print(f"  The sewers ARE the LAN. The turtles ARE alive.")
print(f"  Version 1.000.0. lub-DUB.")
