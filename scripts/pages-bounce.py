#!/usr/bin/env python3
"""pages-bounce: the old HUD on Pages by way of the 404, not by rewriting it.

The old HUD's pages were written for a home where they were the root. On ecoprimals.github.io they live under /hud/,
so what they ask for from the root misses. Instead of rewriting them:
  pages-bounce/404.html  the landing bounce (set at the org root and at /hud/): reads the ask, infers where it lives,
                         bounces there; what it cannot place it says, and asks the house once so the thymus has it
  pages-bounce/sw.js     the same inference for scripts, data and pictures asked by pages under /hud/ (scope /hud/)
  pages-bounce/asks.json what is already placed (solved) and what is known open - published as /hud/thymus/asks.json

  asks              read the old site's pages, list what they ask for, what Pages answers, what inference would place;
                    writes pages-bounce/asks.json and pages-bounce/bring-up.json   (trace only: paths and counts)
  publish [--dry]   put the bounce at both doors, the worker and the list under /hud/, and bring up the files the old
                    site has on main that Pages lacks (the ones on the bring-up list that pass the guard)

Run by hand, or from a loop that already exists. No cron of its own. Nothing here reads or writes a credential:
it speaks to GitHub through the gh sign-in already on this body."""
import base64, collections, hashlib, importlib.util, io, json, os, posixpath, re, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "pages-bounce")
CLONE = os.path.join(REPO, "data", "gut", "forgejo-clones", "ecoPrimals", "infra-hud")
PUB = os.path.join(CLONE, "site", "public")
HUD, HUD_BRANCH, ROOT, ROOT_BRANCH = "ecoPrimals/hud", "gh-pages", "ecoPrimals/ecoPrimals.github.io", "main"
FACES = {"/hud/": (HUD, HUD_BRANCH), "/nestgate.io/": ("ecoPrimals/nestgate.io", "main")}
OWN_NAMES = re.compile(r"^(?:https?:)?//(?:www\.)?(?:hud\.primals\.eco|primals\.eco)(/.*)?$", re.I)
# asks the thymus already understands: said to a visitor in place of "looked in N places"
KNOWN = {
    "/mirror-message": "a mouth with no ear. The old pages post a visitor's words here and no door takes them yet, at the house either.",
    "/onboard": "a door of the house (joining the mesh). It stays at the house.",
}
# what a brought-up page may not carry onto a served face (beyond the hoist's own guard): kinds only, never the value
SOFT = [("street address", re.compile(r"\b\d{2,5}\s+(?:[NSEW]\.?\s+)?[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\s(?:Ave|Avenue|St|Street|Rd|Road|Dr|Drive|Blvd|Ln|Lane|Ct|Court|Way|Hwy)\b")),
        ("phone number", re.compile(r"(?<![\d.])\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")),
        ("pin or passcode", re.compile(r"\b(?:PIN|passcode|password|passwd)\b\s*[:=]?\s*[`'\"]?\w{3,}", re.I)),
        ("private address", re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b")),
        ("mail address", re.compile(r"\b[\w.+\-]+@[\w\-]+\.[\w.\-]+\b"))]
HOLD_ON = {"street address", "phone number", "pin or passcode"}


def hoist():
    spec = importlib.util.spec_from_file_location("pages_hoist", os.path.join(REPO, "scripts", "pages-hoist.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def gh(path, method="GET", body=None, ok404=False):
    cmd = ["gh", "api", "-X", method, path] + (["--input", "-"] if body is not None else [])
    r = subprocess.run(cmd, input=None if body is None else json.dumps(body).encode(), capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    if r.returncode != 0:
        if ok404 and ("Not Found" in out or "404" in r.stderr.decode("utf-8", "replace")): return None
        raise RuntimeError("%s %s: %s" % (method, path, (out or r.stderr.decode("utf-8", "replace"))[:300]))
    return json.loads(out) if out.strip() else None

def tree(repo, ref):
    t = gh("repos/%s/git/trees/%s?recursive=1" % (repo, ref))
    if t.get("truncated"): raise RuntimeError("tree of %s@%s came back cut short" % (repo, ref))
    return {e["path"]: e["sha"] for e in t["tree"] if e["type"] == "blob"}

def blob_sha(data): return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# ---------------------------------------------------------------------------------------------- asks
TAG = re.compile(r"""<(script|img|source|audio|video|iframe|link|a)\b[^>]*?\b(?:src|href|poster)\s*=\s*["']([^"'>\s]+)""", re.I)
FETCH = re.compile(r"""fetch\(\s*['"`]([^'"`$\s]+)['"`]""")

def norm(u, page_dir):
    """The path a browser standing at /hud/<page> would ask this origin for; None when the ask goes elsewhere."""
    u = u.split("#")[0].split("?")[0]
    if not u or u.startswith(("data:", "javascript:", "mailto:", "tel:", "blob:", "about:")) or "${" in u or "{{" in u: return None
    if re.match(r"^[a-z][a-z0-9+.-]*:", u, re.I) or u.startswith("//"):
        m = OWN_NAMES.match(u)
        return None if not m else "/" + (m.group(1) or "/").lstrip("/")      # our own name written in full: a root ask
    if u.startswith("/"): return posixpath.normpath(u) + ("/" if u.endswith("/") and u != "/" else "")
    return posixpath.normpath(posixpath.join("/hud/" + page_dir, u)) + ("/" if u.endswith("/") else "")

def has(have, rel):
    if rel == "" or rel.endswith("/"): return (rel + "index.html") in have
    return rel in have or (rel + ".html") in have or (rel + "/index.html") in have

def file_for(have, rel):
    for c in ([rel + "index.html"] if rel == "" or rel.endswith("/") else [rel, rel + ".html", rel + "/index.html"]):
        if c in have: return c
    return None

def cmd_asks():
    hud = tree(HUD, HUD_BRANCH); root = tree(ROOT, ROOT_BRANCH); nest = tree(*FACES["/nestgate.io/"])
    main = tree(HUD, "main")
    pub = {p[len("site/public/"):]: s for p, s in main.items() if p.startswith("site/public/")}
    def answered(p):
        if p.startswith("/hud/"): return has(hud, p[5:])
        if p.startswith("/nestgate.io/"): return has(nest, p[13:])
        if p.startswith("/sporePrint/"): return True                        # another face's own; not judged here
        return has(root, p[1:])
    asks, pages = collections.defaultdict(lambda: {"n": 0, "kinds": set()}), 0
    for d, _, names in os.walk(PUB):
        for n in names:
            if not n.endswith(".html"): continue
            rel = os.path.relpath(os.path.join(d, n), PUB).replace(os.sep, "/")
            if rel not in hud: continue                                     # a page Pages does not carry asks for nothing there
            pages += 1
            text = io.open(os.path.join(d, n), encoding="utf-8", errors="replace").read()
            pd = posixpath.dirname(rel); pd = pd + "/" if pd else ""
            found = [("link" if m.group(1).lower() == "a" else "tag", m.group(2)) for m in TAG.finditer(text)]
            found += [("fetch", m.group(1)) for m in FETCH.finditer(text)]
            for kind, raw in found:
                p = norm(raw, pd)
                if p and ".." not in p: asks[p]["n"] += 1; asks[p]["kinds"].add(kind)
    names = collections.defaultdict(list)
    for p in hud: names[posixpath.basename(p)].append(p)
    solved, opened, bring, how = {}, {}, {}, collections.defaultdict(lambda: [0, 0])
    miss = {p: a for p, a in asks.items() if not answered(p)}
    for p, a in sorted(miss.items(), key=lambda x: -x[1]["n"]):
        rel = p[5:] if p.startswith("/hud/") else p[1:]
        b = posixpath.basename(rel.rstrip("/"))
        one = [names[c][0] for c in (b, b + ".html") if b and len(names.get(c, [])) == 1]
        if p in KNOWN: k = "known to the thymus"; opened[p] = KNOWN[p]
        elif not p.startswith("/hud/") and has(hud, rel): k = "inference: the same path under /hud/"
        elif one: k = "placed: one file of that name under /hud/"; solved[p] = "/hud/" + one[0]
        elif file_for(pub, rel): k = "bring up: in the old site on main, not on Pages"; bring[file_for(pub, rel)] = {"asked": a["n"], "as": p}
        else:
            k = "open: in none of our sites"
            what = "a live route of the gate" if (p.startswith("/api/") or (not posixpath.splitext(p)[1] and "fetch" in a["kinds"])) else "in none of our sites yet"
            opened[p] = "%s; the old HUD's pages ask for it %d time%s." % (what, a["n"], "" if a["n"] == 1 else "s")
        how[k][0] += 1; how[k][1] += a["n"]
    tot = sum(a["n"] for a in miss.values()) or 1
    print("old HUD pages on Pages read: %d; distinct asks %d; answered today %d; not answered %d (%d asks in all)" % (
        pages, len(asks), len(asks) - len(miss), len(miss), tot))
    for k, (a, b) in sorted(how.items(), key=lambda x: -x[1][1]): print("  %4d things %5d asks (%2d%%)  %s" % (a, b, 100 * b / tot, k))
    out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "by": "northGate-polaris",
           "about": "What the old HUD's pages ask for that Pages does not answer as asked. solved: where the thymus has placed it. "
                    "open: known, not placed yet. Everything else is tried by rule (the same path under /hud/, then the other faces).",
           "counts": {"pages_read": pages, "asks": len(asks), "not_answered": len(miss), "by": {k: v[0] for k, v in how.items()}},
           "solved": solved, "open": opened}
    io.open(os.path.join(SRC, "asks.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    io.open(os.path.join(SRC, "bring-up.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(bring, indent=1, sort_keys=True) + "\n")
    print("written: asks.json (solved %d, open %d), bring-up.json (%d files)" % (len(solved), len(opened), len(bring)))


# ---------------------------------------------------------------------------------------------- publish
def scan(h, text):
    kinds = [name for name, rx in h.GUARD if rx.search(text)]
    if len(set(h.MAC_RX.findall(text))) > h.MAX_MACS: kinds.append("many hardware addresses")
    return kinds, {name: len(rx.findall(text)) for name, rx in SOFT if rx.search(text)}

def cmd_publish(dry):
    h = hoist()
    own = {"404.html": "404.html", "sw.js": "sw.js", "thymus/asks.json": "asks.json"}
    data = {dst: io.open(os.path.join(SRC, src), "rb").read().replace(b"\r\n", b"\n") for dst, src in own.items()}   # as the repo holds them
    for dst, b in data.items():
        hard, soft = scan(h, b.decode("utf-8"))
        if hard or (set(soft) & HOLD_ON): raise SystemExit("my own file %s reads like it carries: %s - not published" % (dst, ", ".join(hard + sorted(set(soft) & HOLD_ON))))
    bring = json.load(io.open(os.path.join(SRC, "bring-up.json"), encoding="utf-8"))
    main = tree(HUD, "main"); held, up, stale = {}, {}, []
    for rel in sorted(bring):
        local = os.path.join(PUB, rel.replace("/", os.sep)); sha = main.get("site/public/" + rel)
        if not sha or not os.path.isfile(local): stale.append(rel); continue
        b = io.open(local, "rb").read()
        if blob_sha(b) != sha and blob_sha(b.replace(b"\r\n", b"\n")) != sha: stale.append(rel); continue   # my copy is not what main holds
        hard, soft = scan(h, b.decode("utf-8", "replace"))
        if hard or (set(soft) & HOLD_ON): held[rel] = hard + sorted(set(soft) & HOLD_ON)
        else: up[rel] = sha
    print("bring-up: %d on the list; %d pass, %d held back, %d not the same as main" % (len(bring), len(up), len(held), len(stale)))
    for rel, kinds in sorted(held.items()): print("   held: %-52s reads like it carries: %s" % (rel[:52], ", ".join(kinds)))
    for site_repo, branch, files in ((HUD, HUD_BRANCH, dict(data)), (ROOT, ROOT_BRANCH, {"404.html": data["404.html"]})):
        for attempt in (1, 2):
            tip = gh("repos/%s/git/ref/heads/%s" % (site_repo, branch))["object"]["sha"]
            base = gh("repos/%s/git/commits/%s" % (site_repo, tip))["tree"]["sha"]
            have = tree(site_repo, tip)
            entries, changed = [], []
            for path, b in sorted(files.items()):
                if have.get(path) == blob_sha(b): continue
                changed.append(path)
                if not dry:
                    sha = gh("repos/%s/git/blobs" % site_repo, "POST", {"content": base64.b64encode(b).decode(), "encoding": "base64"})["sha"]
                    entries.append({"path": path, "mode": "100644", "type": "blob", "sha": sha})
            if site_repo == HUD:
                for rel, sha in sorted(up.items()):
                    if rel in have: continue                              # never over a file Pages already serves
                    changed.append(rel); entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": sha})
            print("%s@%s: %d file(s) to set: %s" % (site_repo, branch, len(changed), ", ".join(changed[:6]) + (" ..." if len(changed) > 6 else "")))
            if dry or not changed: break
            t = gh("repos/%s/git/trees" % site_repo, "POST", {"base_tree": base, "tree": entries})["sha"]
            msg = "bounce: the landing 404%s (from polaris, %d files)" % (", the /hud/ worker, the thymus's list, pages brought up" if site_repo == HUD else " at the root", len(changed))
            c = gh("repos/%s/git/commits" % site_repo, "POST", {"message": msg, "tree": t, "parents": [tip]})["sha"]
            try:
                gh("repos/%s/git/refs/heads/%s" % (site_repo, branch), "PATCH", {"sha": c, "force": False})
                print("   set: %s" % c[:9]); break
            except RuntimeError as e:
                if attempt == 2: raise
                print("   the branch moved under me (another body published); once more")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["asks"]: cmd_asks()
    elif a[:1] == ["publish"]: cmd_publish("--dry" in a)
    else: print(__doc__)
