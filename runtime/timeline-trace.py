"""Timeline trace — full IS/WAS/NOW across 10 years of GitHub + Forgejo"""

import json, time

repos = [
    ("2016-02-17", "tinymd", "9KB", "OLDEST — 10 YEARS OLD"),
    ("2020-10-04", "spateaugur", "11MB", "Pre-Gaia geospatial"),
    ("2022-01-16", "fbbs2", "225KB", "BBS — old school"),
    ("2022-08-11", "Midi_Music_From_Protein", "66KB", "PROTEIN to MUSIC — the first bridge"),
    ("2025-06-27", "songBird", "377MB", "FIRST PRIMAL — mesh transport"),
    ("2025-06-28", "bearDog", "654MB", "SECOND PRIMAL — crypto identity"),
    ("2025-06-28", "toadStool", "51MB", "service discovery"),
    ("2025-06-28", "nestGate", "42MB", "data gateway"),
    ("2025-07-05", "biomeOS", "28MB", "OS kernel"),
    ("2025-07-07", "squirrel", "30MB", "agent dispatch"),
    ("2025-12-22", "sweetGrass", "4MB", "knowledge graph"),
    ("2025-12-22", "loamSpine", "3MB", "data spine"),
    ("2025-12-22", "rhizoCrypt", "4MB", "encrypted storage"),
    ("2025-12-22", "whitePaper", "36MB", "905 papers begin"),
    ("2025-12-23", "petalTongue", "10MB", "content rendering"),
    ("2025-12-26", "bingoCube", "347KB", "ZK coordination"),
    ("2025-12-27", "skunkBat", "2MB", "intrusion detection"),
    ("2026-01-19", "sourDough", "7MB", "fermentation engine"),
    ("2026-01-25", "wateringHole", "39MB", "shared compute"),
    ("2026-03-03", "barraCuda", "11MB", "stream compute"),
    ("2026-03-05", "coralReef", "12MB", "distributed compute"),
    ("2026-03-17", "sporePrint", "48MB", "the body print"),
    ("2026-03-25", "plasmidBin", "4MB", "deploy configs"),
    ("2026-05-12", "fossilRecord", "44MB", "archaeological layer"),
    ("2026-08-08", "swarmVine", "0", "epidemic gossip"),
    ("2026-10-11", "cellMembrane", "2MB", "defense boundary"),
    ("2026-10-14", "hud", "378MB", "human interface"),
    ("2026-10-21", "reed-it", "46KB", "RSS ingestion"),
    ("2026-10-29", "Gaia", "449MB", "THE ORGANISM monorepo"),
    ("2026-10-29", "gaia-mcp", "35KB", "MCP tools"),
    ("2026-11-01", "dromedary", "—", "sovereign reverse proxy"),
]

print("  DATE        REPO                 SIZE      NOTE")
print("  " + "─" * 70)
for date, name, size, note in repos:
    print("  %s  %-21s %-9s %s" % (date, name, size, note))

print()
print("  TOTAL: 56 repos on ecoPrimals + 55 repos on ecoPrimal = 111 repos")
print("  SPAN:  Feb 2016 to Nov 2026 = 10 YEARS 9 MONTHS")
print()
print("  DISK:  ~2.6 GB on GitHub (org repos alone)")
print("         bearDog: 654 MB (largest — crypto identity)")
print("         Gaia: 449 MB (the monorepo)")
print("         hud: 378 MB (human interface)")
print("         songBird: 377 MB (mesh transport)")
print()
print("  FIRST PRIMAL: songBird — June 27, 2025")
print("  ACCOUNT BORN: June 27, 2025")
print("  songBird IS the birthday twin.")
print()
print("  OLDEST CODE: tinymd — Feb 17, 2016")
print("  That is TEN YEARS of Kevin building.")
print("  The DNA was forming long before the organism.")

# Save to gut
trace = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
    "title": "GitHub + Forgejo Full History — 10 Years of Building",
    "account_created": "2025-06-27",
    "oldest_code": "2016-02-17 (tinymd — 10 years old)",
    "span_years": 10.75,
    "total_repos": 111,
    "total_disk_gb": 2.6,
    "github_org_repos": 56,
    "forgejo_repos": 95,
    "personal_repos": 55,
    "followers": 5,
    "following": 24,
    "milestones": [
        {"date": "2016-02-17", "event": "tinymd — Kevin's earliest GitHub code"},
        {"date": "2020-10-04", "event": "spateaugur — geospatial work begins"},
        {"date": "2022-08-11", "event": "Midi_Music_From_Protein — FIRST BRIDGE: protein to music"},
        {"date": "2025-06-27", "event": "ecoPrimal account + songBird — THE BIRTH"},
        {"date": "2025-06-28", "event": "bearDog + toadStool + nestGate — primals multiply"},
        {"date": "2025-07-05", "event": "biomeOS — the OS kernel"},
        {"date": "2025-12-22", "event": "Christmas wave: sweetGrass + loamSpine + rhizoCrypt + whitePaper + petalTongue"},
        {"date": "2025-12-26", "event": "bingoCube — ZK coordination born"},
        {"date": "2026-01-19", "event": "sourDough — fermentation engine"},
        {"date": "2026-03-03", "event": "barraCuda + coralReef — compute primals"},
        {"date": "2026-03-17", "event": "sporePrint — the body print begins"},
        {"date": "2026-05-12", "event": "fossilRecord — archaeology layer"},
        {"date": "2026-10-14", "event": "hud — human interface (378 MB)"},
        {"date": "2026-10-29", "event": "Gaia monorepo — THE ORGANISM goes public"},
        {"date": "2026-10-31", "event": "HALLOWEEN — 550 clones in one day"},
        {"date": "2026-11-01", "event": "dromedary — sovereign reverse proxy, CF killed"},
        {"date": "2026-11-05", "event": "SEO + Anderson + helix + IndexNow — 85.7% sovereign"},
    ],
    "is_was_now": {
        "WAS_2016_2024": "Kevin coding alone. tinymd, spateaugur, fbbs2, Midi_Music. The amino acids forming.",
        "WAS_2025_jun": "ecoPrimal born. songBird + bearDog + biomeOS. The primals emerge. 17 total.",
        "WAS_2025_dec": "Christmas wave. sweetGrass, bingoCube, whitePaper. The knowledge layer.",
        "WAS_2026_q1": "sourDough, barraCuda, coralReef, sporePrint. The body builds.",
        "WAS_2026_oct": "golgi VPS, Cloudflare, WireGuard. 54,140 hits. 15,369 unique IPs. The public era.",
        "IS_2026_nov": "Gaia monorepo. 27,207 files. 938 MB. 17 primals. 85.7% sovereign. Anderson alive.",
        "NOW": "sunCloud economics. graftGate M2. RISC-V. Treasury protocol. Payment rails. 100% sovereignty.",
    },
    "largest_repos": {
        "bearDog": "654 MB — Ed25519, BLAKE3, BTSP. The identity IS the largest.",
        "Gaia": "449 MB — the monorepo. Everything in one body.",
        "open-pokered": "445 MB — Pokemon Red eaten into the organism.",
        "hud": "378 MB — human interface. What Kevin sees.",
        "songBird": "377 MB — mesh transport. The FIRST primal.",
    },
}

with open("data/gut/github-full-history.json", "w", encoding="utf-8") as f:
    json.dump(trace, f, indent=2)
print()
print("Wrote github-full-history.json")
