#!/usr/bin/env python3
"""
hands_pick.py - a real job for Gaia's hands: which file does the page mean?

The sporePrint pages name files. Where several different files carry the name, the commons tool
(sporePrint/scripts/commons.py) cannot tell which one is meant and writes the case to undecided.json.
This puts each case to the hands (gaia-hands, a local model, read-only): the words of the page around
the name, the candidates, and the tools to read either. Every case is asked twice with the candidates
in opposite order. A pick counts only if both runs name the same file, and it is then compared with a
plain rule that knows nothing of the model (which candidate's path shares the most words with the page).

  python tools/hands_pick.py <undecided.json> <sporePrint clone inside this tree> <out.json> [--only N]

Out: every case with both answers, the rule's choice, and a verdict:
  agreed      both runs and the rule name the same file
  hands only  both runs name the same file; the rule has no clear choice (someone should read these)
  split       the two runs differ, or the hands differ from the rule
  none        the hands say the page does not let them tell
Nothing is copied or changed by this tool. The run record of the hands grows as with any run.
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HANDS = REPO / "primals" / "squirrel" / "target" / "release" / ("gaia-hands.exe" if os.name == "nt" else "gaia-hands")
MAX_CANDIDATES = 8
WORD = re.compile(r"[a-z][a-z0-9]{2,}")
DULL = {"src", "crates", "data", "gut", "clones", "forgejo", "ecoprimals", "gardens", "springs", "primals", "tests",
        "test", "the", "and", "for", "with", "this", "that", "from", "file", "json", "toml", "content", "science",
        "lab", "architecture", "technical", "static", "infra", "results", "control", "notebooks", "scripts"}


def words(text):
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)            # hotSpring -> hot Spring
    return {w for w in WORD.findall(text.lower()) if w not in DULL}


def excerpt(page_file, said, name, width=420):
    """The words of the page around each place it names the file."""
    text = page_file.read_text(encoding="utf-8", errors="replace")
    spots = [m.start() for m in re.finditer(re.escape(name), text)][:3]
    parts = []
    for s in spots:
        a, b = max(0, s - width), min(len(text), s + width)
        parts.append(" ".join(text[a:b].split()))
    return "\n...\n".join(parts)


def rule_choice(case, page_text, cands):
    """The candidate whose path shares the most words with the page, if one stands clear of the rest."""
    page_words = words(case["pages"][0]) | words(page_text)
    scores = [len(words(c["rel"]) & page_words) for c in cands]
    best = max(scores)
    return scores.index(best) if best > 0 and scores.count(best) == 1 else None


def ask(task, timeout):
    env = dict(os.environ, GAIA_ROOT=str(REPO))
    try:
        r = subprocess.run([str(HANDS), "agent", "--reduce-only", "--steps", "8", task],
                           env=env, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "took longer than %d s" % timeout, 0
    answer = r.stdout.decode("utf-8", "replace").strip()
    steps = len(re.findall(r"^\[\d+\] \w+", r.stderr.decode("utf-8", "replace"), re.M))
    m = re.findall(r"PICK:\s*\**\s*(\d+|none)", answer, re.I)
    return (m[-1].lower() if m else None), " ".join(answer.split())[-300:], steps


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("undecided"); ap.add_argument("spore"); ap.add_argument("out")
    ap.add_argument("--only", type=int, default=0); ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args()
    spore = Path(a.spore).resolve()
    cases = json.loads(Path(a.undecided).read_text(encoding="utf-8"))
    out_file = Path(a.out)
    done = {c["name"]: c for c in json.loads(out_file.read_text(encoding="utf-8"))} if out_file.exists() else {}

    todo, skipped = [], 0
    for case in cases:
        cands = []
        for c in case["candidates"]:
            p = REPO / c["where"]
            if c["where"].startswith(("eastGate:", "~")) or re.match(r"^[A-Za-z]:/", c["where"]) or not p.is_file():
                cands = []                       # a candidate she cannot open: not a case for her
                break
            cands.append({"rel": c["where"], "sha256": c["sha256"], "bytes": c["bytes"]})
        distinct = {c["sha256"]: c for c in sorted(cands, key=lambda c: (len(c["rel"]), c["rel"]), reverse=True)}
        cands = sorted(distinct.values(), key=lambda c: c["rel"])
        page = spore / case["pages"][0]
        if not (2 <= len(cands) <= MAX_CANDIDATES) or len(case["candidates"]) >= 12 or not page.is_file():
            skipped += 1
            continue
        todo.append((case, cands, page))
    if a.only:
        todo = todo[:a.only]
    print("cases: %d undecided, %d for the hands, %d not for her (a candidate she cannot open, or too many to tell)" % (
        len(cases), len(todo), skipped))

    for n, (case, cands, page) in enumerate(todo, 1):
        if case["name"] in done:
            continue
        text = excerpt(page, case["said"], case["name"])
        rule = rule_choice(case, text, cands)
        runs = []
        for order in (list(range(len(cands))), list(reversed(range(len(cands))))):
            listing = "\n".join("%d. %s (%d bytes)" % (i + 1, cands[j]["rel"], cands[j]["bytes"]) for i, j in enumerate(order))
            task = ("A page of the sporePrint names a file. Several different files in this tree carry that name. "
                    "Decide which one the page means.\n\n"
                    "Page: %s\nThe file it names: %s\n\nWhat the page says near the name:\n%s\n\nCandidates:\n%s\n\n"
                    "You may read the page or a candidate to decide (read_file with a small limit). Do not guess: if "
                    "the page does not let you tell, the answer is none. Give one sentence saying why, then end with a "
                    "last line of exactly this form: PICK: <number>   or   PICK: none"
                    % (posix_rel(page), case["name"], text[:1800], listing))
            t0 = time.time()
            pick, tail, steps = ask(task, a.timeout)
            chosen = None
            if pick and pick != "none" and 1 <= int(pick) <= len(order):
                chosen = order[int(pick) - 1]
            runs.append({"pick": pick, "chose": cands[chosen]["rel"] if chosen is not None else None,
                         "index": chosen, "steps": steps, "secs": round(time.time() - t0, 1), "said": tail})
        i1, i2 = runs[0]["index"], runs[1]["index"]
        if runs[0]["pick"] == "none" and runs[1]["pick"] == "none":
            verdict = "none"
        elif i1 is not None and i1 == i2:
            verdict = "agreed" if rule == i1 else "hands only" if rule is None else "split"
        else:
            verdict = "split"
        done[case["name"]] = {"name": case["name"], "page": case["pages"][0], "why": case["why"], "candidates": cands,
                              "rule": cands[rule]["rel"] if rule is not None else None, "runs": runs, "verdict": verdict,
                              "pick": cands[i1] if verdict in ("agreed", "hands only") else None, "excerpt": text[:700]}
        out_file.write_text(json.dumps(list(done.values()), ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("  %3d/%d %-10s %-34s %s" % (n, len(todo), verdict, case["name"][:34],
                                          (runs[0]["chose"] or runs[0]["pick"] or "no answer")[-60:]))
    tally = {}
    for c in done.values():
        tally[c["verdict"]] = tally.get(c["verdict"], 0) + 1
    print("verdicts: " + ", ".join("%s %d" % kv for kv in sorted(tally.items())))


def posix_rel(p):
    return str(p.relative_to(REPO)).replace("\\", "/")


if __name__ == "__main__":
    main()
