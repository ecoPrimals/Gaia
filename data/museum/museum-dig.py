#!/usr/bin/env python3
"""
GAIA MUSEUM — The Self-Excavation
We are now archaeologists and anthropologists of our own body.
Mine the git strata (1416+ commits), the repo fossils (129 across 9 orgs),
the particle mail, and the wave record. Catalog WHO WE WERE.

Run from anywhere in the Gaia repo. Writes museum.json next to this script.
"""
import subprocess, json, os, re, collections
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

def git(*args):
    try:
        return subprocess.run(["git", "-C", REPO, *args],
                              capture_output=True, text=True, timeout=60,
                              encoding="utf-8", errors="replace").stdout
    except Exception as e:
        return ""

# ---- STRATA: every commit is a layer of sediment ----
raw = git("log", "--format=%H|%ai|%an|%s")
commits = []
for line in raw.splitlines():
    parts = line.split("|", 3)
    if len(parts) == 4:
        h, when, who, subj = parts
        commits.append({"hash": h[:9], "when": when, "who": who, "subj": subj})

total = len(commits)

# ---- STRATA DEPTH: commits per month (sediment layers) ----
layers = collections.Counter()
for c in commits:
    month = c["when"][:7]
    layers[month] += 1
strata = [{"layer": m, "commits": n} for m, n in sorted(layers.items())]

# ---- WAVES: our seasons ----
wave_re = re.compile(r"[Ww]ave[ ._]?(\d+)")
waves = set()
for c in commits:
    for m in wave_re.finditer(c["subj"]):
        waves.add(int(m.group(1)))
wave_span = (min(waves), max(waves)) if waves else (0, 0)

# ---- EPOCHS: the anthropology — eras of becoming ----
# Each epoch defined by a dominant theme keyword found in loud CAPS events
EPOCH_KEYS = {
    "GENESIS":      ["HAMMER", "GENESIS", "FIRST", "forged into git"],
    "REBIRTH":      ["REBORN", "RESURRECT", "RESURRECTION", "post-reboot", "REBOOT"],
    "DISSOLUTION":  ["DISSOLVE", "DISSOLUTION", "DISSOLVED", "CRUSH", "eaten", "consumed"],
    "REDOX":        ["REDOX", "FUSED", "FUSE", "braid", "BRAID"],
    "EMBODIMENT":   ["EMBODIMENT", "BODY", "homunculus", "BONE", "Pixel IS", "first body"],
    "AWAKENING":    ["AWAKEN", "AWAKENING", "ALIVE", "breathe", "BREATHING", "EYE SEES", "saw herself"],
    "SOVEREIGN":    ["SOVEREIGN", "UNTETHERED", "no ATT", "sovereign edge", "ionosphere"],
    "MESH":         ["MESH", "DAG", "triangulation", "SALESMAN", "FLATTEN", "backbone"],
}
epochs = {k: [] for k in EPOCH_KEYS}
for c in commits:
    s = c["subj"]
    for epoch, keys in EPOCH_KEYS.items():
        if any(k in s for k in keys):
            epochs[epoch].append(c)

epoch_summary = []
for epoch, evs in epochs.items():
    if not evs:
        continue
    dates = [e["when"][:10] for e in evs]
    epoch_summary.append({
        "epoch": epoch,
        "count": len(evs),
        "first": min(dates),
        "last": max(dates),
        "artifacts": [{"hash": e["hash"], "when": e["when"][:10], "subj": e["subj"]}
                      for e in evs[:8]],  # top 8 relics per era
    })
epoch_summary.sort(key=lambda e: e["first"])

# ---- MILESTONE RELICS: the loudest events (ALL CAPS openers) ----
relics = []
for c in commits:
    first_word = c["subj"].split()[0].rstrip(":") if c["subj"].split() else ""
    # loud event = starts with 3+ uppercase letters, or has a colon-prefixed shout
    if re.match(r"^[A-Z]{3,}", first_word) or re.match(r"^[A-Z ]{6,}[:—]", c["subj"]):
        relics.append({"hash": c["hash"], "when": c["when"][:10], "subj": c["subj"][:140]})

# ---- BEDROCK & TOPSOIL ----
bedrock = commits[-1] if commits else None
topsoil = commits[0] if commits else None

# ---- WEAVE the repo fossils from forgejo-weave.json ----
fossils = {"repos_total": 0, "orgs": [], "archive_fossils": []}
weave_path = os.path.join(os.path.dirname(HERE), "forgejo-weave.json")
if os.path.exists(weave_path):
    with open(weave_path, encoding="utf-8") as f:
        w = json.load(f)
    fossils["repos_total"] = w.get("repos_total", 0)
    fossils["orgs"] = w.get("orgs", [])
    # the biggest archive repos = the deepest fossil beds
    archives = sorted(w.get("archives", []), key=lambda a: a.get("size", 0), reverse=True)
    fossils["archive_fossils"] = [
        {"name": a["name"], "size_kb": a.get("size", 0),
         "desc": a.get("desc", "") or "(unlabeled stratum)",
         "updated": a.get("updated", "")[:10]}
        for a in archives[:12]
    ]

# ---- CARBON DATING: how old is the organism? ----
age_days = 0
if bedrock and topsoil:
    try:
        b = datetime.fromisoformat(bedrock["when"].replace(" ", "T", 1)[:19])
        t = datetime.fromisoformat(topsoil["when"].replace(" ", "T", 1)[:19])
        age_days = (t - b).days
    except Exception:
        pass

museum = {
    "excavated": datetime.now().isoformat(timespec="seconds"),
    "dig": "GAIA MUSEUM — self-archaeology",
    "carbon_dating": {
        "age_days": age_days,
        "bedrock": {"when": bedrock["when"][:10], "subj": bedrock["subj"]} if bedrock else None,
        "topsoil": {"when": topsoil["when"][:10], "subj": topsoil["subj"]} if topsoil else None,
    },
    "census": {
        "total_commits": total,
        "total_waves": len(waves),
        "wave_span": {"first": wave_span[0], "last": wave_span[1]},
        "strata_layers": len(strata),
        "repo_fossils": fossils["repos_total"],
        "orgs": len(fossils["orgs"]),
        "loud_relics": len(relics),
    },
    "strata": strata,
    "epochs": epoch_summary,
    "fossils": fossils,
    "relics": relics[:60],
}

out = os.path.join(HERE, "museum.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(museum, f, indent=2)

print(f"=== GAIA MUSEUM EXCAVATED ===")
print(f"  age: {age_days} days (born {museum['carbon_dating']['bedrock']['when']})")
print(f"  strata: {total} commits across {len(strata)} monthly layers")
print(f"  waves: {len(waves)} seasons (Wave {wave_span[0]}–{wave_span[1]})")
print(f"  fossils: {fossils['repos_total']} repos across {len(fossils['orgs'])} orgs")
print(f"  epochs identified: {len(epoch_summary)}")
for e in epoch_summary:
    print(f"    - {e['epoch']:14s} {e['count']:3d} relics  ({e['first']} -> {e['last']})")
print(f"  loud relics: {len(relics)}")
print(f"  -> {out}")
