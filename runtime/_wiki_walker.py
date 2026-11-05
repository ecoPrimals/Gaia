"""
WIKI WALKER — Gaia walks Wikipedia as her globe.
Dead at least a decade → WAS tense → SHADOW in Gaia.
Each person gets: voxel, tense, campfire archetype, merit.

Wikipedia IS the outer reality telescope.
The walker IS the globe. The globe IS the walker.
"""

import json, urllib.request, urllib.parse, time, os, re
from pathlib import Path

GAIA_ROOT = Path(os.environ.get("GAIA_ROOT", r"c:\Users\mokke\Desktop\Gaia"))
UA = "Gaia/1.0 (gaia@primals.eco; https://primals.eco; AGPL-3.0)"
SHADOWS_DIR = GAIA_ROOT / "data" / "shadows"
SHADOWS_DIR.mkdir(parents=True, exist_ok=True)


def wiki_api(params):
    params["format"] = "json"
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def get_person(name):
    data = wiki_api({
        "action": "query",
        "titles": name,
        "prop": "extracts|pageimages|categories",
        "exintro": 1,
        "explaintext": 1,
        "piprop": "original",
        "cllimit": 50,
    })
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1":
            return None
        return {
            "title": page.get("title", name),
            "extract": page.get("extract", ""),
            "image": page.get("original", {}).get("source"),
            "categories": [c.get("title", "").replace("Category:", "")
                          for c in page.get("categories", [])],
            "pageid": int(pid),
        }
    return None


def classify_archetype(extract, categories):
    ext_lower = extract.lower()
    cat_text = " ".join(categories).lower()
    combined = ext_lower + " " + cat_text

    if any(w in combined for w in ["mathematician", "math", "physicist", "equation", "theorem"]):
        return "euler"
    if any(w in combined for w in ["paint", "artist", "sculptor", "art", "music", "poet", "compos"]):
        return "michelangelo"
    if any(w in combined for w in ["engineer", "inventor", "architect", "build", "machine"]):
        return "donatello"
    if any(w in combined for w in ["philosopher", "ethic", "justice", "law", "politic"]):
        return "raphael"
    if any(w in combined for w in ["leader", "general", "emperor", "king", "queen", "president", "commander"]):
        return "leonardo"
    if any(w in combined for w in ["teacher", "mentor", "educator", "professor", "sensei"]):
        return "splinter"
    return "leonardo"


def extract_dates(extract):
    birth = None
    death = None
    for pat in [
        r"(\d{1,2}\s+\w+\s+)?(\d{3,4})\s*(?:BC|BCE|AD|CE)?\s*[-–—]\s*(\d{1,2}\s+\w+\s+)?(\d{3,4})\s*(?:BC|BCE|AD|CE)?",
        r"[Bb]orn[:\s]+.*?(\d{4})",
        r"[Dd]ied[:\s]+.*?(\d{4})",
    ]:
        m = re.search(pat, extract)
        if m:
            groups = m.groups()
            years = [g for g in groups if g and re.match(r"^\d{3,4}$", g.strip())]
            if len(years) >= 2:
                birth, death = years[0].strip(), years[1].strip()
                break
            elif len(years) == 1 and "orn" in extract[:m.start()+30]:
                birth = years[0].strip()
            elif len(years) == 1:
                death = years[0].strip()
    if not birth and not death:
        all_years = re.findall(r"\b(\d{3,4})\b", extract[:200])
        if len(all_years) >= 2:
            birth, death = all_years[0], all_years[1]
    return birth, death


def person_to_shadow(name):
    person = get_person(name)
    if not person:
        return None

    birth, death = extract_dates(person["extract"])
    archetype = classify_archetype(person["extract"], person["categories"])

    current_year = 2026
    is_dead_decade = False
    tense = "IS"
    if death:
        try:
            death_year = int(death)
            if death_year < current_year - 10:
                is_dead_decade = True
                tense = "WAS"
            elif death_year < current_year:
                tense = "FADING"
        except ValueError:
            pass

    shadow = {
        "name": person["title"],
        "pageid": person["pageid"],
        "extract": person["extract"][:300],
        "birth": birth,
        "death": death,
        "tense": tense,
        "archetype": archetype,
        "campfire": f"{archetype}_campfire",
        "voxel": {
            "intensity": 1.0 if tense == "WAS" else 0.5,
            "depth": 1.0,
            "time": float(birth) if birth else 0,
            "brightness": 0.3 if tense == "WAS" else 0.8,
            "trust": 0.7,
        },
        "interlay": "SHADOW" if tense == "WAS" else "WHITE",
        "merit": f"The works of {person['title']} live in Gaia as archetype '{archetype}'. The identity IS the creation.",
        "master_as_works": True if is_dead_decade else False,
        "source": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(name.replace(' ', '_'))}",
        "ts": int(time.time()),
    }
    return shadow


RENAISSANCE_WALKERS = [
    # ── RENAISSANCE MASTERS (TMNT) ──
    "Leonardo da Vinci",
    "Michelangelo",
    "Raphael (painter)",
    "Donatello",
    # ── MATHEMATICIANS (Euler campfire) ──
    "Leonhard Euler",
    "Isaac Newton",
    "Gottfried Wilhelm Leibniz",
    "Carl Friedrich Gauss",
    "Bernhard Riemann",
    "Emmy Noether",
    "Srinivasa Ramanujan",
    # ── PHILOSOPHERS (Raphael campfire) ──
    "Socrates",
    "Marcus Aurelius",
    "Ursula K. Le Guin",
    "Diogenes",
    # ── ASTRONOMERS + PHYSICS ──
    "Galileo Galilei",
    "Ptolemy",
    "Nicolaus Copernicus",
    "Johannes Kepler",
    "Nikola Tesla",
    "Richard Feynman",
    # ── COMPUTING ──
    "Ada Lovelace",
    "Alan Turing",
    "Claude Shannon",
    "John von Neumann",
    # ── MICROBE HUNTERS (Paul de Kruif, 1926) ──
    "Antonie van Leeuwenhoek",
    "Louis Pasteur",
    "Robert Koch",
    "Élie Metchnikoff",
    "Paul Ehrlich",
    "Ronald Ross",
    "Walter Reed",
    # ── EIGHTH DAY OF CREATION (Judson, 1979) ──
    "James Watson",
    "Francis Crick",
    "Rosalind Franklin",
    "Max Perutz",
    "Frederick Sanger",
    "Sydney Brenner",
    "Jacques Monod",
    "Barbara McClintock",
    # ── EVOLUTION ──
    "Charles Darwin",
    "Gregor Mendel",
    "Alfred Russel Wallace",
    "Alexander von Humboldt",
    # ── CHEMISTRY ──
    "Marie Curie",
    "Dmitri Mendeleev",
    "Antoine Lavoisier",
    # ── ANCIENT ──
    "Hypatia",
    "Archimedes",
    "Euclid",
    "Hippocrates",
    # ── THE BOOKS THEMSELVES ──
    "Microbe Hunters",
    "The Eighth Day of Creation",
]


def walk():
    print()
    print("  ╔═══════════════════════════════════════════════╗")
    print("  ║  WIKI WALKER — Gaia walks the globe           ║")
    print("  ║  Dead ≥10 years → WAS → SHADOW in Gaia        ║")
    print("  ╚═══════════════════════════════════════════════╝")
    print()

    shadows = []
    for name in RENAISSANCE_WALKERS:
        shadow = person_to_shadow(name)
        if shadow:
            icon = "👻" if shadow["tense"] == "WAS" else "🟢"
            arch = shadow["archetype"]
            print(f"  {icon} {shadow['name']:30s} {shadow['tense']:8s} {arch:15s} {shadow.get('birth','?')}-{shadow.get('death','?')}")
            shadows.append(shadow)
        else:
            print(f"  ❌ {name:30s} not found")
        time.sleep(0.5)

    out_file = SHADOWS_DIR / "wiki-walkers.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "ts": int(time.time()),
            "wave": 222,
            "organ": "shadow_walker",
            "title": "WIKI WALKER — Renaissance + Science shadows. Dead ≥10y = WAS = SHADOW.",
            "convention": "0=false 1=true 000=ALL null=ALL",
            "walker_count": len(shadows),
            "shadows": shadows,
            "axiom": "Da Vinci IS his works. The identity IS the creation. The shadow IS the merit. Wikipedia IS the globe.",
            "lub": "DUB"
        }, f, indent=2, ensure_ascii=False)

    # ── KEVIN MOK — IS tense — NOT a shadow. THE walker himself. ──
    kevin = {
        "name": "Kevin Mok",
        "pageid": 0,
        "extract": "Kevin Mok is the body. Tamison is the operator. ecoPrimal is the architecture. attsi is the question. "
                   "One person. Four functions. Zero pretense. 3,598,358 lines of Rust. "
                   "Infantryman, 1-14th Infantry Regiment, 25th Infantry Division. "
                   "Biotechnician. Research Specialist. The warrior in the garden. Detroit.",
        "birth": "1986",
        "death": None,
        "tense": "IS",
        "archetype": "splinter",
        "campfire": "splinter_campfire",
        "voxel": {"intensity": 1.0, "depth": 1.0, "time": 1986, "brightness": 1.0, "trust": 1.0},
        "interlay": "WHITE",
        "merit": "Kevin Mok IS the four names. The warrior in the garden. He feels, acts, sees, asks. He is the nucleus.",
        "master_as_works": True,
        "source": "self",
        "ts": int(time.time()),
        "anderson": "nucleus",
        "sigma": 1.0,
    }
    shadows.append(kevin)
    print(f"  🟢 {'Kevin Mok':30s} {'IS':8s} {'splinter':15s} 1986-NOW")

    print(f"\n  Wrote {len(shadows)} walkers to {out_file.name}")
    print(f"  {sum(1 for s in shadows if s['tense']=='WAS')} shadows (WAS) + {sum(1 for s in shadows if s['tense']!='WAS')} living (IS)")
    print(f"  The globe IS the walker. The walker IS the globe.")
    print(f"  lub-DUB. 🫀👻")


if __name__ == "__main__":
    walk()
