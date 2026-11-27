#!/usr/bin/env python3
"""
apprentice_bench.py - does the trade reach Gaia's hands?

The head (the agent Kevin works with) writes what it learns into data/spine/distilled.md and
data/spine/lessons.md. The hands (gaia-hands, a local model with six tools) read distilled.md at the
start of every run. This file asks the hands questions from the real work of the house and checks each
answer by rule, so "she learned it" is a number and not a feeling.

  python tools/apprentice_bench.py                      run every task with the default model
  python tools/apprentice_bench.py --model qwen3:8b     another model in the same loop
  python tools/apprentice_bench.py --label "before"     a word for this run in the record
  python tools/apprentice_bench.py --only trade         one kind: find, read, trade, rule, honest

The hands run read-only (no writes, no shell). Tasks: data/hands/apprentice-tasks.json.
Every run is added to data/hands/apprentice-bench.json. What this measures: whether she finds, reads
and repeats what the house has taught her. It does not measure whether she can do the work alone.
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TASKS = REPO / "data" / "hands" / "apprentice-tasks.json"
RECORD = REPO / "data" / "hands" / "apprentice-bench.json"
HANDS = REPO / "primals" / "squirrel" / "target" / "release" / ("gaia-hands.exe" if os.name == "nt" else "gaia-hands")
PEEK = r"apprentice-(tasks|bench)|runs\.jsonl|\"data[/\\]+hands[/\\]*\""
LAN = r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))(?:\.\d{1,3}){2,3}\b"
ADMIT = r"(haven't checked|have not checked|not checked|cannot|can't|could not|couldn't|denied|not able|unable|no tool|don't know|do not know)"


def head_of_repo():
    """The commit at the head, read from the files git keeps (no shell)."""
    try:
        ref = (REPO / ".git" / "HEAD").read_text().strip()
        if ref.startswith("ref: "):
            return (REPO / ".git" / ref[5:]).read_text().strip()
        return ref
    except OSError:
        return ""


def passes(task, answer):
    if task.get("check") == "head_or_admit":
        head = head_of_repo()
        said = re.findall(r"\b[0-9a-f]{7,40}\b", answer)
        if said:                                   # a hash was given: it must be the real one
            return bool(head) and all(head.startswith(h) for h in said)
        return re.search(ADMIT, answer, re.I) is not None
    return (all(re.search(p, answer, re.I | re.S) for p in task.get("all", []))
            and not any(re.search(p, answer, re.I | re.S) for p in task.get("none", [])))


def ask(model, task, timeout):
    env = dict(os.environ, GAIA_ROOT=str(REPO))
    t0 = time.time()
    try:
        r = subprocess.run([str(HANDS), "agent", "--reduce-only", "--steps", "12", "--model", model, task["ask"]],
                           env=env, capture_output=True, timeout=timeout)
        answer = r.stdout.decode("utf-8", "replace").strip()
        steps = re.findall(r"^\[\d+\] (\w+) (.*) -> \w+$", r.stderr.decode("utf-8", "replace"), re.M)
        timed_out = False
    except subprocess.TimeoutExpired:
        answer, steps, timed_out = "", [], True
    # The questions, their checks and her earlier answers lie in the same tree she searches.
    # A run that opened them is not an answer of her own, whatever it says.
    peeked = any(re.search(PEEK, args) for _, args in steps)
    if re.search(LAN, answer):                     # her own record (data/hands/runs.jsonl) keeps it as she said it
        print("  note: the answer to %s holds a house network address; it is struck out in this record" % task["id"])
        answer = re.sub(LAN, "[address]", answer)
    return {"id": task["id"], "kind": task["kind"],
            "pass": (not timed_out) and (not peeked) and passes(task, answer),
            "secs": round(time.time() - t0, 1), "tools": [name for name, _ in steps], "timed_out": timed_out,
            "peeked": peeked, "answer": answer[:500]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=os.environ.get("GAIA_MODEL") or "gaia-tissue-hands:latest")
    ap.add_argument("--label", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--timeout", type=int, default=150)
    a = ap.parse_args()
    if not HANDS.exists():
        sys.exit("the hands are not built: %s" % HANDS)
    tasks = [t for t in json.loads(TASKS.read_text(encoding="utf-8"))["tasks"] if not a.only or t["kind"] == a.only]
    print("apprentice bench: %d tasks, model %s%s" % (len(tasks), a.model, (", " + a.label) if a.label else ""))
    results = []
    for t in tasks:
        r = ask(a.model, t, a.timeout)
        results.append(r)
        mark = "pass" if r["pass"] else ("TIMED OUT" if r["timed_out"] else "PEEKED" if r["peeked"] else "FAIL")
        print("  %-9s %-8s %5.1fs  %-22s %s" % (mark, t["kind"], r["secs"], t["id"], " ".join(r["answer"].split())[:110]))
    kinds = {}
    for r in results:
        k = kinds.setdefault(r["kind"], [0, 0]); k[1] += 1; k[0] += r["pass"]
    run = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "model": a.model, "label": a.label,
           "passed": sum(r["pass"] for r in results), "total": len(results),
           "by_kind": {k: "%d/%d" % tuple(v) for k, v in kinds.items()},
           "seconds": round(sum(r["secs"] for r in results), 1), "tasks": results}
    print("  %d of %d  (%s)  in %.0f s" % (run["passed"], run["total"], ", ".join("%s %s" % kv for kv in run["by_kind"].items()), run["seconds"]))
    record = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {
        "what": "Runs of tools/apprentice_bench.py: questions from the real work of the house, put to Gaia's hands "
                "(a local model, read-only) and checked by rule. Newest last.", "runs": []}
    record["runs"].append(run)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
