#!/usr/bin/env python3
"""
commons_holders.py - who holds the commons, and is every copy the same?

The sporePrint keeps the files its pages name under static/commons/, with a manifest of their hashes
(sporePrint/scripts/commons.py). A file that lives in one place is gone when that place sleeps. This asks
every place that should hold the commons to show each file, hashes what comes back against the manifest,
and writes the answer where the HUD can read it: static/commons.json, shown by static/commons.html.

  python tools/commons_holders.py <sporePrint checkout> [--gate northGate] [--forge <address of the forge mirror>]

Holders asked:
  this gate      the checkout given (files on this machine's disk)
  GitHub         the repository as GitHub holds it (raw files of the main branch)
  GitHub Pages   https://ecoprimals.github.io/sporePrint, the copy that stands when the house is dark
  the house      https://primals.eco/sporeprint, the built copy the house gate serves
  the site name  https://sporeprint.primals.eco, the same copy under the sporePrint name
  house forge    the forge's mirror, when --forge is given (its address is not written to the file)
  nestgates      read from data/commons/nest.json, which tools/commons_nest.py writes when it checks a
                 gate's content store; this tool does not ask them again

It is a check someone runs, not a service: the file says when it was made. Nothing is copied or repaired.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "static" / "commons.json"
NEST = REPO / "data" / "commons" / "nest.json"
HOUSE = "https://primals.eco/sporeprint"        # where a held file can be opened today


def ask(checkout, holder, raw=False):
    cmd = [sys.executable, "-X", "utf8", str(checkout / "scripts" / "commons.py"), "check", holder, "--json"]
    if raw:
        cmd.append("--raw")
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=900)
        return json.loads(r.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    except (subprocess.TimeoutExpired, ValueError, IndexError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("checkout")
    ap.add_argument("--forge", default="")
    ap.add_argument("--gate", default="this gate", help="the name of the gate this runs on, as the mesh knows it")
    a = ap.parse_args()
    checkout = Path(a.checkout).resolve()
    manifest = json.loads((checkout / "static" / "commons" / "manifest.json").read_text(encoding="utf-8"))

    asked = [
        (a.gate, "this gate's disk", str(checkout), False),
        ("GitHub", "the repository, main branch", "https://raw.githubusercontent.com/ecoPrimals/sporePrint/main", True),
        ("GitHub Pages", "ecoprimals.github.io/sporePrint, as served", "https://ecoprimals.github.io/sporePrint", False),
        ("the house", "primals.eco/sporeprint, as the house gate serves it", HOUSE, False),
        ("the site name", "sporeprint.primals.eco, as served", "https://sporeprint.primals.eco", False),
    ]
    if a.forge:
        asked.append(("house forge", "the forge's mirror of the repository", a.forge.rstrip("/"), True))

    holders = []
    for name, what, where, raw in asked:
        got = ask(checkout, where, raw)
        if got is None:
            holders.append({"name": name, "what": what, "answered": False})
            print("  %-13s did not answer" % name)
            continue
        holders.append({"name": name, "what": what, "answered": True, "of": got["of"], "same": got["same"],
                        "differs": got["differs"], "missing": got["missing"] + got.get("no_answer", 0), "checked": got["checked"]})
        print("  %-13s %d of %d the same; %d differ; %d missing; %d did not answer" % (
            name, got["same"], got["of"], got["differs"], got["missing"], got.get("no_answer", 0)))

    passing = []
    if NEST.exists():
        nest = json.loads(NEST.read_text(encoding="utf-8"))
        for gate, g in sorted(nest.get("gates", {}).items()):
            holders.append({"name": gate + " nestgate", "what": "nestgate's content store on %s (collection %s)" % (gate, nest["collection"]),
                            "answered": True, "of": g["of"], "same": g["same"], "differs": g["differs"], "missing": g["missing"],
                            "checked": g["checked"]})
            print("  %-13s %d of %d the same (read from %s)" % (gate + " nest", g["same"], g["of"], NEST.name))
        passing = [{k: m[k] for k in ("when", "how", "from", "to", "ids", "passed", "already_there", "failed", "why")}
                   for m in nest.get("moves", [])]

    blobs = []
    for b in manifest["blobs"]:
        e = {"name": b["name"], "kind": b["kind"], "state": b["state"], "pages": b["pages"]}
        if b["state"] == "held":
            e.update(bytes=b["bytes"], sha256=b["sha256"], repo=b["from"].get("repo", ""),
                     address=(HOUSE + b["address"]) if b.get("address") else
                     "https://github.com/ecoPrimals/sporePrint/blob/main/" + b["path"])
        elif b.get("why"):
            e["why"] = b["why"]
        blobs.append(e)

    out = {"what": "Who holds the commons of the sporePrint, and whether each copy matches the manifest. "
                   "Made by tools/commons_holders.py when someone runs it.",
           "made": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "manifest_made": manifest["made"],
           "counts": manifest["counts"], "holders": holders, "passing": passing, "blobs": blobs}
    text = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if a.forge and a.forge.split("//")[-1].split("/")[0].split(":")[0] in text:
        sys.exit("STOP: the forge's address would be written into a served file; nothing written")
    OUT.write_text(text, encoding="utf-8", newline="\n")
    full = sum(1 for h in holders if h.get("answered") and h["same"] == h["of"])
    print("holders with every file the same: %d of %d -> %s" % (full, len(holders), OUT.relative_to(REPO)))


if __name__ == "__main__":
    main()
