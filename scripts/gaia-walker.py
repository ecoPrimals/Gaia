#!/usr/bin/env python3
"""GAIA WALKER - walk a gate the way a visitor does and report what is broken.

Starts at the front door and the hub, follows every internal link, and checks two things
on the way:

  LINK PATHS   every href / src / stylesheet / fetch('/...') a page points at is requested
               once; anything that does not answer 200 is listed with the pages that point
               at it. Static pages that no route serves, and pages that nothing links to,
               are listed too.

  RENDER       per page, without a browser: which classes the markup uses that no stylesheet
               defines (a page that lost its CSS shows up here), and any animation that
               cycles faster than 3 times a second (photosensitivity limit).
               With --render, a headless Chrome/Edge also loads every page: JavaScript
               errors and failed loads are collected, a screenshot is taken, and a page
               that paints almost nothing is flagged BLANK. A contact sheet (index.html)
               puts every screenshot on one page so a human can check them at a glance.

Run by hand - it is not a cron and starts nothing that stays running:

  python scripts/gaia-walker.py                                   # this gate, links + static render check
  python scripts/gaia-walker.py --render                          # plus real browser renders and screenshots
  python scripts/gaia-walker.py --base http://192.168.4.248:8443  # another gate on the LAN

Only the gate named by --base is requested. External links are counted, never fetched
(water lock). Forms are never submitted and links that look like actions are not followed.
Output goes to data/gut/walker/<gate>/ (report.json, shots/, index.html); that directory
ignores itself in git. Standard library only; Pillow is used for thumbnails if present.
"""
import argparse
import concurrent.futures as cf
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UA = "gaia-walker/1 (LAN self-check)"
SKIP_SCHEMES = ("#", "mailto:", "javascript:", "data:", "tel:", "blob:", "about:", "sms:")
# links that act rather than show: never followed
ACTS = re.compile(r"(?i)/[^?#]*\b(kill|restart|reboot|shutdown|delete|purge|wipe|exec|deploy|write|send|inject|trigger)\b")
FETCH_CALL = re.compile(r"""(?:fetch\w*|getJSON|loadJSON|EventSource)\(\s*(['"`])(/[^'"`\s$<>]{1,200})\1""")
PAGE_TYPES = ("text/html", "application/xhtml")
CONSOLE = re.compile(r'INFO:CONSOLE[:(]\d+\)?\]\s*"(.*)", source: (\S*)')
BAD_CONSOLE = re.compile(r"(?i)uncaught|failed to load resource|is not defined|syntaxerror|typeerror|referenceerror|net::err_")


# ───────────────────────── fetching ─────────────────────────
def fetch(url, timeout, limit=1_500_000):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(limit)
            return {"status": r.status, "ctype": (r.headers.get("Content-Type") or "").split(";")[0].strip().lower(),
                    "body": body, "ms": int((time.time() - t0) * 1000), "final": r.geturl()}
    except urllib.error.HTTPError as e:
        try:
            body = e.read(limit)
        except Exception:
            body = b""
        return {"status": e.code, "ctype": (e.headers.get("Content-Type") or "").split(";")[0].strip().lower(),
                "body": body, "ms": int((time.time() - t0) * 1000), "final": url}
    except Exception as e:  # refused, timed out, reset
        return {"status": 0, "ctype": "", "body": b"", "ms": int((time.time() - t0) * 1000), "final": url,
                "error": type(e).__name__}


# ───────────────────────── page reading ─────────────────────────
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.classes, self.styles, self.scripts, self.sheets = [], set(), [], [], []
        self.title, self._in, self._buf = "", None, []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if a.get("class"):
            self.classes.update(a["class"].split())
        if tag == "a" and a.get("href"):
            self.links.append(("href", a["href"]))
        elif tag == "link" and a.get("href"):
            if "stylesheet" in a.get("rel", "").lower():
                self.sheets.append(a["href"])
                self.links.append(("css", a["href"]))
            elif "icon" in a.get("rel", "").lower() or "manifest" in a.get("rel", "").lower():
                self.links.append(("src", a["href"]))
        elif tag in ("script", "img", "iframe", "source", "video", "audio", "embed") and a.get("src"):
            self.links.append(("src", a["src"]))
        if tag in ("style", "script", "title"):
            self._in, self._buf = tag, []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self._in = None

    def handle_endtag(self, tag):
        if tag == self._in:
            text = "".join(self._buf)
            if tag == "style":
                self.styles.append(text)
            elif tag == "script":
                self.scripts.append(text)
            else:
                self.title = " ".join(text.split())
            self._in = None

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)


def css_classes(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\{[^{}]*\}", "{}", css)
    return set(re.findall(r"\.(-?[A-Za-z_][\w-]*)", css))


def fast_animations(css):
    """Infinite animations that flash more than 3 times a second."""
    out = []
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"animation\s*:\s*([^;}]+)", css):
        v = " ".join(m.group(1).split())
        if "infinite" not in v:
            continue
        times = [float(x) * (0.001 if u == "ms" else 1.0) for x, u in re.findall(r"(?<![\w.-])(\d*\.?\d+)(ms|s)\b", v)]
        if not times or times[0] <= 0:
            continue
        cycle = times[0] * (2 if "alternate" in v else 1)
        stepped = bool(re.search(r"steps\(\s*[12]\s*[,)]", v)) or "step-" in v
        if cycle < 1 / 3.0 or (stepped and cycle < 2 / 3.0):
            out.append("%s  (%.1f/s)" % (v[:60], 1 / cycle))
    return out


# ───────────────────────── the walk ─────────────────────────
def walk(base, starts, static_dir, max_urls, timeout, workers, log):
    origin = urllib.parse.urlsplit(base)
    root = "%s://%s" % (origin.scheme, origin.netloc)

    def norm(page_url, raw):
        raw = raw.strip()
        if not raw or raw.lower().startswith(SKIP_SCHEMES):
            return None, None
        u = urllib.parse.urlsplit(urllib.parse.urljoin(page_url, raw))
        if u.scheme not in ("http", "https"):
            return None, None
        clean = urllib.parse.urlunsplit((u.scheme, u.netloc, u.path or "/", u.query, ""))
        return clean, u.netloc == origin.netloc

    seen, refs, kinds, depth = {}, {}, {}, {}
    external, acting, queue = {}, {}, []
    seeds = set()
    for s in starts:
        u = root + (s if s.startswith("/") else "/" + s)
        queue.append(u)
        depth[u] = 0
    if static_dir and os.path.isdir(static_dir):
        for name in sorted(os.listdir(static_dir)):
            if name.endswith(".html"):
                u = root + "/" + name[:-5]
                seeds.add(u)
                if u not in depth:
                    queue.append(u)
                    depth[u] = 0
    pages = {}
    sheet_cache = {}
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        while queue and len(seen) < max_urls:
            batch = []
            for u in queue:
                if u not in seen and u not in batch:
                    batch.append(u)
            batch = batch[:max_urls - len(seen)]
            queue = []
            for u, r in zip(batch, pool.map(lambda x: fetch(x, timeout), batch)):
                seen[u] = r
                is_page = r["status"] == 200 and r["ctype"].startswith(PAGE_TYPES)
                if not is_page:
                    r["body"] = b""
                    continue
                p = Page()
                try:
                    p.feed(r["body"].decode("utf-8", "replace"))
                except Exception as e:  # malformed markup: keep what was read
                    r["parse_error"] = type(e).__name__
                r["body"] = b""
                pages[u] = p
                found = list(p.links)
                for s in p.scripts:
                    found += [("fetch", m.group(2)) for m in FETCH_CALL.finditer(s)]
                for kind, raw in found:
                    t, internal = norm(u, raw)
                    if not t:
                        continue
                    if not internal:
                        host = urllib.parse.urlsplit(t).netloc
                        external[host] = external.get(host, 0) + 1
                        continue
                    if kind in ("href", "fetch") and ACTS.search(urllib.parse.urlsplit(t).path):
                        acting.setdefault(t, set()).add(u)
                        continue
                    refs.setdefault(t, set()).add(u)
                    kinds.setdefault(t, set()).add(kind)
                    if t not in seen and t not in depth:
                        depth[t] = depth[u] + 1
                        queue.append(t)
            log("  walked %d urls, %d pages, %d queued" % (len(seen), len(pages), len(queue)))
        # stylesheets the pages link to (for the class check)
        sheets = set()
        for u, p in pages.items():
            for raw in p.sheets:
                t, internal = norm(u, raw)
                if t and internal:
                    sheets.add(t)
        for t, r in zip(sorted(sheets), pool.map(lambda x: fetch(x, timeout), sorted(sheets))):
            sheet_cache[t] = r["body"].decode("utf-8", "replace") if r["status"] == 200 else ""

    def rel(u):
        return u[len(root):] or "/"

    out_pages = []
    for u, p in sorted(pages.items()):
        css = "\n".join(p.styles)
        for raw in p.sheets:
            t, internal = norm(u, raw)
            if t and internal:
                css += "\n" + sheet_cache.get(t, "")
        defined = css_classes(css)
        bare = sorted(c for c in p.classes if c not in defined)
        title = p.title
        out_pages.append({
            "path": rel(u), "status": seen[u]["status"], "ms": seen[u]["ms"], "title": title[:120],
            "depth": depth.get(u, 0), "linked_from": len(refs.get(u, ())), "seed_only": u in seeds and not refs.get(u),
            "soft_404": bool(re.search(r"(?i)\bnot found\b", title)),
            "classes_used": len(p.classes), "classes_bare": len(bare), "bare_sample": bare[:12],
            "unstyled": len(p.classes) >= 6 and len(bare) / max(1, len(p.classes)) >= 0.6,
            "fast_animations": fast_animations(css), "links": len(p.links),
        })
    broken, no_route = [], []
    for u, r in sorted(seen.items()):
        if r["status"] == 200:
            continue
        entry = {"target": rel(u), "status": r["status"], "error": r.get("error", ""),
                 "kinds": sorted(kinds.get(u, ())), "from": sorted(rel(x) for x in refs.get(u, ()))[:12],
                 "from_count": len(refs.get(u, ()))}
        if not refs.get(u):
            if u in seeds:
                no_route.append(rel(u))
            elif depth.get(u) == 0:
                broken.append(entry)       # a start page itself is down
            continue
        q = urllib.parse.urlsplit(u)
        if q.query:
            bare_u = urllib.parse.urlunsplit((q.scheme, q.netloc, q.path, "", ""))
            st = seen[bare_u]["status"] if bare_u in seen else fetch(bare_u, timeout)["status"]
            if st == 200:
                entry["note"] = "answers 200 without the query string"
        broken.append(entry)
    return {
        "pages": out_pages, "broken": broken, "no_route": no_route,
        "external": dict(sorted(external.items(), key=lambda kv: -kv[1])),
        "not_followed": {rel(k): sorted(rel(x) for x in v)[:6] for k, v in sorted(acting.items())},
        "urls": len(seen), "truncated": bool(queue),
    }, root


# ───────────────────────── real renders ─────────────────────────
def find_browser():
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


def ink(png_path, thumb_path):
    """Share of the picture that is not background (0..1), and write a thumbnail. Needs Pillow."""
    try:
        from PIL import Image
    except Exception:
        return None
    try:
        im = Image.open(png_path).convert("RGB")
        t = im.copy()
        t.thumbnail((460, 460))
        t.save(thumb_path, "JPEG", quality=70)
        g = im.convert("L").resize((280, 180))
        px = list(g.tobytes())
        bg = max(set(px), key=px.count)
        return round(sum(1 for v in px if abs(v - bg) > 12) / float(len(px)), 4)
    except Exception:
        return None


def render_one(browser, url, png, profile, size, budget_ms, timeout):
    args = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio", "--no-first-run",
            "--no-default-browser-check", "--disable-extensions", "--user-data-dir=" + profile,
            "--enable-logging=stderr", "--v=0", "--window-size=%d,%d" % size,
            "--virtual-time-budget=%d" % budget_ms, "--screenshot=" + png, url]
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout)
        err = r.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return {"render_error": "browser timed out"}
    msgs, bad = [], []
    for line in err.splitlines():
        m = CONSOLE.search(line)
        if m:
            msgs.append(m.group(1))
            if BAD_CONSOLE.search(m.group(1)) and m.group(1)[:160] not in bad:
                bad.append(m.group(1)[:160])
    return {"console_messages": len(msgs), "console_errors": bad[:8], "shot": os.path.exists(png)}


def render_all(report, root, out_dir, workers, size, budget_ms, log):
    browser = find_browser()
    if not browser:
        log("  --render: no Chrome/Edge/Chromium found; skipped")
        return False
    shots = os.path.join(out_dir, "shots")
    if os.path.isdir(shots):
        shutil.rmtree(shots)
    os.makedirs(shots)
    tmp = tempfile.mkdtemp(prefix="gaia-walker-")
    targets = [p for p in report["pages"] if p["status"] == 200 and not p["soft_404"]]

    def job(i_p):
        i, p = i_p
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", p["path"].strip("/")) or "_root"
        png = os.path.join(shots, name + ".png")
        res = render_one(browser, root + p["path"], png, os.path.join(tmp, "p%d" % (i % workers)), size, budget_ms, 90)
        if res.get("shot"):
            res["ink"] = ink(png, os.path.join(shots, name + ".jpg"))
            res["shot"] = "shots/" + name + ".png"
            res["thumb"] = "shots/" + name + ".jpg" if os.path.exists(os.path.join(shots, name + ".jpg")) else res["shot"]
        return p, res

    # one browser profile per worker slot; slots are reused serially within a worker
    done = 0
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        slots = [[] for _ in range(workers)]
        for i, p in enumerate(targets):
            slots[i % workers].append((i, p))
        futures = [pool.submit(lambda s: [job(x) for x in s], s) for s in slots]
        for f in futures:
            for p, res in f.result():
                p.update(res)
                p["blank"] = res.get("ink") is not None and res["ink"] < 0.004
                done += 1
    shutil.rmtree(tmp, ignore_errors=True)
    log("  rendered %d pages with %s" % (done, os.path.basename(browser)))
    return True


def contact_sheet(report, out_dir, base):
    def flags(p):
        f = []
        if p.get("blank"):
            f.append(("BLANK", "bad"))
        if p.get("console_errors"):
            f.append(("%d script error%s" % (len(p["console_errors"]), "" if len(p["console_errors"]) == 1 else "s"), "bad"))
        if p.get("unstyled"):
            f.append(("unstyled %d/%d classes" % (p["classes_bare"], p["classes_used"]), "bad"))
        if p.get("fast_animations"):
            f.append(("fast animation", "bad"))
        if p.get("render_error"):
            f.append((p["render_error"], "bad"))
        if p.get("seed_only"):
            f.append(("nothing links here", "warn"))
        return f

    cards = []
    for p in sorted(report["pages"], key=lambda p: (-len([1 for _, k in flags(p) if k == "bad"]), p["path"])):
        if not p.get("shot"):
            continue
        badges = "".join('<span class="b %s">%s</span>' % (k, html.escape(t)) for t, k in flags(p)) or '<span class="b ok">ok</span>'
        errs = "".join("<li>%s</li>" % html.escape(e) for e in p.get("console_errors", [])[:4])
        cards.append('<div class="card"><a href="%s"><img loading="lazy" src="%s" alt=""></a>'
                     '<div class="meta"><a class="p" href="%s%s">%s</a> %s<div class="t">%s</div>%s</div></div>'
                     % (html.escape(p["shot"]), html.escape(p.get("thumb", p["shot"])), html.escape(base), html.escape(p["path"]),
                        html.escape(p["path"]), badges, html.escape(p["title"]), "<ul>%s</ul>" % errs if errs else ""))
    rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (html.escape(b["target"]), b["status"] or html.escape(b["error"]),
                                                                    html.escape(", ".join(b["from"][:6]) + (" ..." if b["from_count"] > 6 else "")))
                   for b in report["broken"])
    c = report["counts"]
    doc = """<!doctype html><meta charset="utf-8"><title>Gaia walker - %s</title>
<style>body{background:#0b0d10;color:#d8d4cc;font:14px/1.5 system-ui,sans-serif;margin:24px}
h1{font-size:20px;font-weight:500}h2{font-size:15px;font-weight:500;margin:28px 0 8px;color:#d4a574}
.sum{color:#8a857e}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:#14171a;border:1px solid #23272e;border-radius:8px;overflow:hidden}
.card img{width:100%%;display:block;background:#000;aspect-ratio:14/9;object-fit:cover;object-position:top}
.meta{padding:8px 10px}.p{color:#d4a574;text-decoration:none;font-family:ui-monospace,monospace}
.t{color:#8a857e;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.b{font-size:11px;padding:1px 7px;border-radius:99px;margin-left:4px;border:1px solid}
.ok{color:#5aad72;border-color:#2d5e3a}.bad{color:#e0a05a;border-color:#7a5f3e}.warn{color:#8a857e;border-color:#3a3f48}
ul{margin:6px 0 0 16px;padding:0;color:#b9a38a;font-size:11px}table{border-collapse:collapse;font-size:13px}
td{border-bottom:1px solid #23272e;padding:4px 14px 4px 0;vertical-align:top}td:first-child{font-family:ui-monospace,monospace;color:#d4a574}</style>
<h1>Gaia walker &mdash; %s</h1>
<div class="sum">%s &middot; %d pages &middot; %d urls &middot; %d broken link paths &middot; %d unstyled &middot; %d blank &middot; %d with script errors &middot; %d static pages without a route</div>
<h2>Renders (pages with problems first; click a picture for full size)</h2><div class="grid">%s</div>
<h2>Broken link paths</h2><table>%s</table>
""" % (html.escape(base), html.escape(base), report["ts"], c["pages"], c["urls"], c["broken_link_paths"], c["unstyled"],
       c["blank"], c["script_errors"], c["no_route"], "".join(cards), rows or "<tr><td>none</td></tr>")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)


# ───────────────────────── main ─────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Walk a Gaia gate: link paths and renders.")
    ap.add_argument("--base", default="http://127.0.0.1:8443", help="gate to walk (default: this machine's gate)")
    ap.add_argument("--start", nargs="*", default=["/", "/hub"], help="paths to start from")
    ap.add_argument("--static-dir", default=os.path.join(REPO, "static"),
                    help="also try /<name> for every <name>.html here ('' to skip)")
    ap.add_argument("--max", type=int, default=1500, help="most urls to request")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--render", action="store_true", help="load every page in a headless browser and take screenshots")
    ap.add_argument("--render-workers", type=int, default=4)
    ap.add_argument("--size", default="1400x900")
    ap.add_argument("--settle-ms", type=int, default=5000, help="virtual time a page gets to finish loading")
    ap.add_argument("--out", default="", help="output directory (default data/gut/walker/<gate>)")
    ap.add_argument("--lines", type=int, default=40, help="most single broken paths to print (all are in report.json)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    def log(s):
        if not a.quiet:
            print(s, flush=True)

    base = a.base.rstrip("/")
    gate = re.sub(r"[^A-Za-z0-9.-]+", "_", urllib.parse.urlsplit(base).netloc)
    top = os.path.join(REPO, "data", "gut", "walker")
    out_dir = a.out or os.path.join(top, gate)
    os.makedirs(out_dir, exist_ok=True)
    if not a.out:
        gi = os.path.join(top, ".gitignore")
        if not os.path.exists(gi):
            with open(gi, "w", encoding="ascii") as f:
                f.write("# walker output is regenerated on every run\n*\n")

    log("GAIA WALKER  %s" % base)
    t0 = time.time()
    report, root = walk(base, a.start, a.static_dir, a.max, a.timeout, a.workers, log)
    rendered = False
    if a.render:
        w, h = (int(x) for x in a.size.lower().split("x"))
        rendered = render_all(report, root, out_dir, a.render_workers, (w, h), a.settle_ms, log)
    pages = report["pages"]
    report["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    report["base"] = base
    report["seconds"] = round(time.time() - t0, 1)
    report["counts"] = {
        "urls": report["urls"], "pages": len(pages), "broken_link_paths": len(report["broken"]),
        "no_route": len(report["no_route"]), "soft_404": sum(1 for p in pages if p["soft_404"]),
        "unstyled": sum(1 for p in pages if p["unstyled"]),
        "fast_animations": sum(1 for p in pages if p["fast_animations"]),
        "nothing_links_here": sum(1 for p in pages if p["seed_only"]),
        "blank": sum(1 for p in pages if p.get("blank")),
        "script_errors": sum(1 for p in pages if p.get("console_errors")),
        "external_hosts": len(report["external"]), "rendered": rendered,
    }
    c = report["counts"]
    max_lines = a.lines
    log("")
    log("  %d urls requested, %d pages read, %.0f s%s" % (c["urls"], c["pages"], report["seconds"],
                                                         "  (stopped at --max; more were queued)" if report["truncated"] else ""))
    log("  LINK PATHS  broken: %d   static pages with no route: %d   pages nothing links to: %d   external hosts (not fetched): %d"
        % (c["broken_link_paths"], c["no_route"], c["nothing_links_here"], c["external_hosts"]))
    # group the broken paths by where they point, so a mirrored section with 200 dead links reads as one line
    groups = {}
    for b in report["broken"]:
        seg = "/" + b["target"].lstrip("/").split("/")[0].split("?")[0]
        if b["target"].count("/") < 2 and not b["target"].endswith("/"):
            seg = "(single paths)"
        g = groups.setdefault(seg, {"n": 0, "status": {}, "from": set(), "items": []})
        g["n"] += 1
        key = str(b["status"] or b["error"])
        g["status"][key] = g["status"].get(key, 0) + 1
        g["from"].update(b["from"])
        g["items"].append(b)
    report["broken_groups"] = {k: {"count": v["n"], "status": v["status"], "from": sorted(v["from"])[:12]}
                               for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["n"])}
    for seg, g in sorted(groups.items(), key=lambda kv: (kv[0] == "(single paths)", -kv[1]["n"])):
        if seg == "(single paths)":
            continue
        log("     %-26s %4d dead  (%s)  linked from: %s" % (seg + "/...", g["n"],
            ", ".join("%s x%d" % kv for kv in sorted(g["status"].items())), ", ".join(sorted(g["from"])[:5])))
    for b in groups.get("(single paths)", {"items": []})["items"][:max_lines]:
        log("     %-34s %-4s %-9s from %d page(s): %s%s" % (b["target"][:34], b["status"] or b["error"], "/".join(b["kinds"]),
                                                             b["from_count"], ", ".join(b["from"][:4]),
                                                             "  [" + b["note"] + "]" if b.get("note") else ""))
    extra = len(groups.get("(single paths)", {"items": []})["items"]) - max_lines
    if extra > 0:
        log("     ... %d more single paths in report.json" % extra)
    if report["no_route"]:
        log("     no route: " + ", ".join(report["no_route"][:30]) + (" ..." if len(report["no_route"]) > 30 else ""))
    log("  RENDER      unstyled: %d   fast animations: %d   soft 404: %d%s"
        % (c["unstyled"], c["fast_animations"], c["soft_404"],
           "   blank: %d   script errors: %d" % (c["blank"], c["script_errors"]) if rendered else "   (no browser pass; add --render)"))
    for p in pages:
        notes = []
        if p["unstyled"]:
            notes.append("unstyled %d/%d classes (%s)" % (p["classes_bare"], p["classes_used"], ", ".join(p["bare_sample"][:5])))
        if p["fast_animations"]:
            notes.append("fast animation: " + "; ".join(p["fast_animations"][:2]))
        if p.get("blank"):
            notes.append("BLANK render (ink %.2f%%)" % (100 * p["ink"]))
        if p.get("console_errors"):
            notes.append("%d script error(s): %s" % (len(p["console_errors"]), p["console_errors"][0][:110]))
        if p.get("render_error"):
            notes.append(p["render_error"])
        if notes:
            log("     %-26s %s" % (p["path"][:26], " | ".join(notes)))
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    if rendered:
        contact_sheet(report, out_dir, base)
    log("  report: %s" % os.path.join(out_dir, "report.json"))
    if rendered:
        log("  contact sheet: %s" % os.path.join(out_dir, "index.html"))
    problems = c["broken_link_paths"] + c["unstyled"] + c["fast_animations"] + c["blank"] + c["script_errors"] + c["soft_404"]
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
