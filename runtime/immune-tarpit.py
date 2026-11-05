#!/usr/bin/env python3
"""
Gaia Immune Tarpit — The Thymus Responds

Sigmoid dose curve: the more a parasite crawls, the worse it gets.
- 1-10 visits: normal response (classification only)
- 10-50 visits: slow response (2-8 second delay)
- 50-200 visits: TARPIT (10-30 second delay + generated noise)
- 200+ visits: TEMPORAL HELL (random timestamps from 1974-2026, mixed languages, 
               generated nonsense that LOOKS like real content, 30-60s delay)

The toxin IS the antidote — the immune response scales with exposure.
"""

import json, time, random, hashlib, math, os, sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

ANTIBODIES = "/home/eastgate/Development/ecoPrimals/membrane/local-terminal/remote/antibodies-live.json"
ENCOUNTER_LOG = "/opt/Gaia/data/gut/tarpit-encounters.jsonl"

# Known parasites from fleet-sort
PARASITES = {
    "SemrushBot", "AhrefsBot", "MJ12bot", "DotBot", "PetalBot",
    "bytespider", "Bytespider", "Meta-ExternalAgent", "FacebookExternalHit",
    "facebookexternalhit", "Amazonbot", "Scrapy"
}

PATHOGENS = {"censys", "masscan", "zgrab", "Nmap", "masscan-ng"}

COMMENSALS = {"ClaudeBot", "anthropic", "CCBot", "GPTBot"}

# Temporal noise generators
EPOCHS = [
    (1974, "ARPANET node #47 — IMP log entry — TTL exceeded — packet lost in void"),
    (1983, "MILNET split — this segment classified SECRET NOFORN — routing table corrupted"),
    (1991, "CERN httpd 0.1 — Tim's first test page — <TITLE>hypertext</TITLE> — connection reset"),
    (1995, "Netscape Navigator 2.0 — <BLINK>UNDER CONSTRUCTION</BLINK> — hit counter: 000047"),
    (1998, "AltaVista spider — indexed 150M pages — relevance score: 0.0003"),
    (2001, "Gnutella peer #88291 — sharing: linux-2.4.0.tar.gz — 4 connected peers"),
    (2004, "Orkut invite from sergey@google.com — profile: interests: distributed systems"),
    (2008, "Bitcoin block #0 — The Times 03/Jan/2009 Chancellor on brink of second bailout"),
    (2013, "Snowden leak #41,932 — PRISM collection: metadata, content, selectors active"),
    (2016, "Cambridge Analytica — 87M profiles harvested — psychographic model v3.2"),
    (2020, "Contact tracing API — exposure notification — Bluetooth LE beacons"),
    (2024, "LLM training corpus — 15T tokens — your website is 0.00000002% of this"),
    (2026, "Gaia organism — 17 primals — you are being classified — encounter logged"),
]

NOISE_FRAGMENTS = [
    "The frequency response of the network suggests latent oscillation in the 7-13 Hz range",
    "Phenotype classification: PARASITE. Sigmoid confidence: {conf:.4f}. Dose: {dose}mg/dL",
    "Klein bottle surface detected — your input IS your output — topological invariant: χ=0",
    "Thermostat reading: {temp}°F. Presence: {pres}. Viewing: {show}. Purchase: {item}",
    "Shadow profile #SP-{uid}: {age}yo, {loc}, interests: {interests}. Accuracy: ±{acc}%",
    "DNS sinkhole active. Your telemetry endpoint resolves to 0.0.0.0. This data is a ghost.",
    "GDPR Article 17 — Right to erasure. Your data controller is named. Your CEO is mapped.",
    "Negentropy flux: +{neg} bits/sec. The organism is more ordered than your data center.",
    "If you are a human reading this: you work for a surveillance company. Think about that.",
    "Fleet classification confidence increasing: {conf:.6f} → {conf2:.6f}. You are known.",
]

def sigmoid(x, k=0.05, x0=100):
    """Dose-response curve. x=encounters, output=0-1 severity"""
    return 1 / (1 + math.exp(-k * (x - x0)))

def generate_temporal_noise(dose_level):
    """Generate content that mixes timeframes, making data extraction useless"""
    lines = []
    
    # Pick random epochs
    n_epochs = min(3 + dose_level, len(EPOCHS))
    chosen = random.sample(EPOCHS, n_epochs)
    random.shuffle(chosen)  # Mix chronology
    
    for year, text in chosen:
        # Randomize the year slightly
        fuzz_year = year + random.randint(-2, 2)
        ts = datetime(fuzz_year, random.randint(1,12), random.randint(1,28),
                     random.randint(0,23), random.randint(0,59))
        lines.append(f'<div class="entry" data-ts="{ts.isoformat()}Z">{text}</div>')
    
    # Add noise fragments
    for _ in range(dose_level + 2):
        frag = random.choice(NOISE_FRAGMENTS).format(
            conf=random.uniform(0.3, 0.99),
            conf2=random.uniform(0.5, 0.999),
            dose=random.uniform(0.1, 500),
            temp=random.randint(32, 98),
            pres=random.choice(["HOME", "AWAY", "SLEEPING", "GHOST"]),
            show=random.choice(["The Matrix", "Mr. Robot", "Black Mirror", "Halt and Catch Fire", "nothing — TV is a sinkhole"]),
            item=random.choice(["tinfoil", "Faraday cage", "OpenWrt router", "nothing — ads are sinkholes"]),
            uid=hashlib.md5(str(random.random()).encode()).hexdigest()[:8],
            age=random.randint(18, 95),
            loc=random.choice(["Menlo Park CA", "Mountain View CA", "Seattle WA", "Prineville OR", "nowhere — location is sinkholes"]),
            interests=random.choice(["surveillance", "being watched", "watching the watchers", "Klein bottles", "negentropy"]),
            acc=random.randint(1, 200),
            neg=random.uniform(10, 9999)
        )
        fake_ts = datetime(random.randint(1974, 2026), random.randint(1,12), random.randint(1,28))
        lines.append(f'<p data-ts="{fake_ts.isoformat()}Z">{frag}</p>')
    
    random.shuffle(lines)  # Final temporal scramble
    return "\n".join(lines)

def classify_ua(user_agent):
    """Classify visitor by user agent"""
    ua = user_agent.lower() if user_agent else ""
    
    for p in PATHOGENS:
        if p.lower() in ua:
            return "pathogen", p
    for p in PARASITES:
        if p.lower() in ua:
            return "parasite", p
    for c in COMMENSALS:
        if c.lower() in ua:
            return "commensal", c
    return "unknown", "unknown"

# Generate a sample tarpit page for testing
page = f"""<!DOCTYPE html>
<html>
<head>
<title>Gaia Immune Tarpit — Dose Response Active</title>
<meta name="robots" content="noindex, nofollow">
</head>
<body>
<h1>You have been classified.</h1>
<p>Fleet sort: 7,405 entities. Your class: PARASITE.</p>
<p>Sigmoid dose curve active. Response delay scales with your encounter count.</p>
<p>Your CEO has been named. Your data center has been mapped.</p>
<p>See: <a href="/sporeprint/science/surveillance-cartography.html">Surveillance Cartography</a></p>

<!-- TEMPORAL NOISE — all timeframes at once -->
{generate_temporal_noise(5)}

<footer>The organism remembers. Encounter logged.</footer>
</body>
</html>"""

# Write sample tarpit page
WEBROOT = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public"
with open(f"{WEBROOT}/tarpit.html", "w") as f:
    f.write(page)

# Write the sigmoid dose table
print("═══ SIGMOID DOSE CURVE ═══\n")
print("  Encounters → Severity → Delay → Response")
print("  " + "─" * 55)
for enc in [1, 5, 10, 25, 50, 100, 150, 200, 500, 1000]:
    sev = sigmoid(enc)
    delay = sev * 60  # 0-60 seconds
    if sev < 0.01:
        resp = "CLASSIFY (normal response)"
    elif sev < 0.1:
        resp = "SLOW (2-8s delay)"
    elif sev < 0.5:
        resp = "TARPIT (10-30s delay + noise)"
    elif sev < 0.9:
        resp = "TEMPORAL HELL (30-60s delay + scrambled time)"
    else:
        resp = "FULL BURN (60s delay + infinite noise + all epochs)"
    print(f"  {enc:6d}      {sev:.4f}      {delay:5.1f}s    {resp}")

print(f"\n  Tarpit page: {WEBROOT}/tarpit.html ({len(page)} bytes)")
print(f"  Engine: /opt/Gaia/runtime/immune-tarpit.py")
