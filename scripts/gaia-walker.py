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
  python scripts/gaia-walker.py --faces --dom                     # the front page of each name, at home and hoisted

  FACES        the front page a name shows (hud, nestgate, primals.eco on this gate; hud and nestgate on GitHub
               Pages), one link deep: each link is dead, fine, or brings the same page back again, and each
               asset the page pulls in loads or does not. --dom adds the links a script writes. The short form
               goes to runtime/membrane/dead-links.json, which the gate's /thymus and /klein carry. The same
               findings go on as trace only (paths, answers, counts): to skunkBat as one observation of the walk,
               and to swarmVine as a gossip entry (--tell says it again; the gate's loop does that between walks).

Only the gate named by --base is requested. External links are counted, never fetched
(water lock). Forms are never submitted and links that look like actions are not followed.
Output goes to data/gut/walker/<gate>/ (report.json, shots/, index.html); that directory
ignores itself in git. Standard library only; Pillow is used for thumbnails if present.
"""
import argparse
import concurrent.futures as cf
import hashlib
import html
import socket
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
def fetch(url, timeout, limit=1_500_000, host=None, accept="*/*"):
    t0 = time.time()
    headers = {"User-Agent": UA, "Accept": accept}
    if host:
        headers["Host"] = host
    req = urllib.request.Request(url, headers=headers)
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


# ───────────────────────── the faces ─────────────────────────
# One front page per name, at home and where it is hoisted. For each: every link and asset the front page
# carries is requested once, the way a browser would ask for it, and sorted into what a visitor would meet.
FACES_SUMMARY = os.path.join(REPO, "runtime", "membrane", "dead-links.json")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_PLAIN = urllib.request.build_opener(_NoRedirect)


def plain_status(url, host=None, accept="text/html,*/*", timeout=6):
    """Status of one request with no redirect followed (a redirect is not the page)."""
    headers = {"User-Agent": UA, "Accept": accept}
    if host:
        headers["Host"] = host
    try:
        with _PLAIN.open(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def default_faces(gate):
    # where a path that is dead on Pages may still be alive: this gate under the WAN name, and the data servers
    # (the old HUD site lives on eastGate's). A door that says yes to a path that cannot exist is not asked.
    home = [(gate, "primals.eco")]
    for d in dict.fromkeys(["http://%s:8080" % urllib.parse.urlsplit(gate).hostname, "http://192.168.4.248:8080"]):
        if plain_status(d + "/gaia-walker-no-such-path-%d.none" % os.getpid(), timeout=4) == 404:
            home.append((d, None))
    # the door a name really opens at home is port 80 (where the WAN forward lands), not the gate's own port:
    # this body's if it has one, else eastGate's. What sits there may hand the gate a different host name than
    # the visitor typed, so asking the gate directly would describe a page no visitor gets.
    def front(name):
        try:                                   # where this body's own name table sends the name (a browser here goes there)
            ip = socket.gethostbyname(name)
        except Exception:
            ip = ""
        tried = ["http://" + ip] if re.match(r"^(192\.168\.|10\.|127\.)", ip) else []
        for d in dict.fromkeys(tried + ["http://%s" % urllib.parse.urlsplit(gate).hostname, "http://192.168.4.248"]):
            if plain_status(d + "/gaia-walker-no-such-path-%d.none" % os.getpid(), host=name, accept="*/*", timeout=4) == 404:
                return d
        return gate
    return [
        {"name": "hud at home", "url": front("hud.primals.eco") + "/", "host": "hud.primals.eco"},
        {"name": "nestgate at home", "url": front("nestgate.io") + "/", "host": "nestgate.io"},
        {"name": "primals.eco at home", "url": front("primals.eco") + "/", "host": "primals.eco"},
        {"name": "hud on Pages", "url": "https://ecoprimals.github.io/hud/", "home_doors": home},
        {"name": "nestgate on Pages", "url": "https://ecoprimals.github.io/nestgate.io/", "home_doors": home},
    ]


def dom_after_scripts(browser, face, budget_ms, timeout):
    """The front page as it stands once its scripts have run (links a script writes are only here)."""
    u = urllib.parse.urlsplit(face["url"])
    args = [browser, "--headless=new", "--disable-gpu", "--mute-audio", "--no-first-run", "--no-default-browser-check",
            "--disable-extensions", "--virtual-time-budget=%d" % budget_ms, "--dump-dom"]
    url = face["url"]
    if face.get("host"):   # ask the gate by the face's own name without touching this body's name table
        args.append("--host-resolver-rules=MAP %s %s" % (face["host"], u.hostname))
        url = urllib.parse.urlunsplit((u.scheme, "%s:%d" % (face["host"], u.port or 80), u.path, u.query, ""))
    profile = tempfile.mkdtemp(prefix="gaia-walker-dom-")
    try:
        r = subprocess.run(args + ["--user-data-dir=" + profile, url], capture_output=True, timeout=timeout)
        text = r.stdout.decode("utf-8", "replace")
        return (text, url) if "<" in text else (None, url)
    except Exception:
        return None, url
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def walk_face(face, timeout, workers, browser, budget_ms):
    u = urllib.parse.urlsplit(face["url"])
    door = "%s://%s" % (u.scheme, u.netloc)                    # where requests really go
    names = {u.hostname, face.get("host")} - {None}            # hosts that count as this face
    scope = u.path[:u.path.rfind("/") + 1] or "/"              # the folder the face lives in
    front = fetch(face["url"], timeout, host=face.get("host"), accept="text/html,*/*")
    out = {"name": face["name"], "url": face["url"], "host": face.get("host", ""), "status": front["status"]}
    if front["status"] != 200:
        out.update(error=front.get("error", ""), links=0, ok=0, dead=[], folds=[], home_only=[], left=[], assets=0,
                   assets_dead=[], after_scripts=False)
        return out
    front_sha, front_len = hashlib.sha1(front["body"]).hexdigest(), len(front["body"])
    page = Page()
    page.feed(front["body"].decode("utf-8", "replace"))
    found, seen_dom, page_url = [(k, raw, False) for k, raw in page.links], False, face["url"]
    if browser:
        dom, dom_url = dom_after_scripts(browser, face, budget_ms, timeout=max(60, budget_ms // 1000 + 45))
        if dom:
            seen_dom = True
            live = Page()
            try:
                live.feed(dom)
            except Exception:
                pass
            have = set(found_raw for _k, found_raw, _d in found)
            found += [(k, raw, True) for k, raw in live.links if raw not in have]
    targets = {}
    external = {}
    for kind, raw, by_script in found:
        raw = raw.strip()
        if not raw or raw.lower().startswith(SKIP_SCHEMES):
            continue
        t = urllib.parse.urlsplit(urllib.parse.urljoin(page_url, raw))
        if t.scheme not in ("http", "https"):
            continue
        if t.hostname not in names:
            external[t.hostname or "?"] = external.get(t.hostname or "?", 0) + 1
            continue
        path = t.path or "/"
        if kind == "href" and ACTS.search(path):
            continue
        if kind == "href" and path in (u.path, u.path + "index.html"):
            continue                                           # the front page itself (a view of it, or its top)
        key = path + ("?" + t.query if t.query else "")
        e = targets.setdefault(key, {"path": key, "kind": "link" if kind == "href" else "asset", "as_written": raw[:120],
                                     "by_script": by_script})
        if kind == "href":
            e["kind"] = "link"

    def ask(e):
        r = fetch(door + e["path"], timeout, host=face.get("host"),
                  accept="text/html,*/*" if e["kind"] == "link" else "*/*")
        body = r.pop("body", b"")
        e["bytes"] = len(body)
        same = bool(body) and (hashlib.sha1(body).hexdigest() == front_sha or
                               (r["ctype"].startswith(PAGE_TYPES) and abs(len(body) - front_len) <= 64))
        return r["status"], r.get("error", ""), same

    items = sorted(targets.values(), key=lambda e: e["path"])
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for e, (status, err, same) in zip(items, pool.map(ask, items)):
            e["status"] = status or err
            e["outside"] = not e["path"].startswith(scope)
            e["state"] = "dead" if status != 200 else "same page again" if (same and e["kind"] == "link") else "ok"
        if face.get("home_doors"):                             # dead where it is hoisted: is it alive at home?
            def at_home(e):
                p = "/" + e["path"][len(scope):] if e["path"].startswith(scope) else e["path"]
                return any(plain_status(base + p, host, "text/html,*/*" if e["kind"] == "link" else "*/*") == 200
                           for base, host in face["home_doors"])
            gone = [e for e in items if e["state"] == "dead"]
            for e, yes in zip(gone, pool.map(at_home, gone)):
                if yes:
                    e["state"] = "at home only"
    links = [e for e in items if e["kind"] == "link"]
    assets = [e for e in items if e["kind"] == "asset"]
    brief = lambda e: {"path": e["path"], "status": e["status"], "as_written": e["as_written"],
                       "by_script": e["by_script"], "outside_the_site": e["outside"]}
    out.update(
        links=len(links), ok=sum(1 for e in links if e["state"] == "ok"),
        dead=[brief(e) for e in links if e["state"] == "dead"],
        folds=[e["path"] for e in links if e["state"] == "same page again"],
        home_only=[brief(e) for e in items if e["state"] == "at home only"],
        left=[e["path"] for e in links if e["outside"] and e["state"] == "ok"],
        assets=len(assets), assets_dead=[brief(e) for e in assets if e["state"] == "dead"],
        external_hosts=dict(sorted(external.items(), key=lambda kv: -kv[1])), after_scripts=seen_dom,
        requests=len(items) + 1, bytes=front_len + sum(e.get("bytes", 0) for e in items),
        port=u.port or (443 if u.scheme == "https" else 80),
        answers_4xx=sum(1 for e in items if isinstance(e["status"], int) and 400 <= e["status"] < 500),
        answers_5xx=sum(1 for e in items if isinstance(e["status"], int) and e["status"] >= 500))
    return out


# ───────────────────────── trace feed ─────────────────────────
# What a walk found is handed on as TRACE ONLY: which path, what it answered, how many. Never a page's text, a header,
# a query string, a token or an address of a visitor. Three places take it:
#   thymus / klein   the short form on disk (runtime/membrane/dead-links.json), carried by the gate
#   skunkBat         one observation per walk (baseline.observe): what my own walker looks like on the wire, so a
#                    walk is known traffic and not a stranger scanning for holes
#   swarmVine        one gossip entry per body (gossip.inject, topic "tower", key "dead-links:<body>")
TRACE_PATH = re.compile(r"[^A-Za-z0-9_\-./~%]")
PEER_GATES = {"eastgate": "http://192.168.4.248:8443", "polaris": "http://192.168.4.147:8443"}


def trace_path(p):
    return TRACE_PATH.sub("", str(p).split("?")[0].split("#")[0])[:96]


def trace_of(short):
    """The short form reduced to trace: names of faces, counts, and paths with nothing after a '?'."""
    num = lambda v: int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0
    out = {"ts": str(short.get("ts", ""))[:20], "by": re.sub(r"[^a-z0-9-]", "", str(short.get("by", "")).lower())[:24],
           "after_scripts": bool(short.get("after_scripts"))}
    for k in ("dead", "same_page_again", "assets_dead", "at_home_only"):
        out[k] = num(short.get(k))
    out["faces"] = [{"face": re.sub(r"[^A-Za-z0-9 .-]", "", str(f.get("face", "")))[:32], "answers": bool(f.get("answers")),
                     "links": num(f.get("links")), "ok": num(f.get("ok")), "dead": num(f.get("dead")),
                     "same_page_again": num(f.get("same_page_again")), "at_home_only": num(f.get("at_home_only")),
                     "assets": num(f.get("assets")), "assets_dead": num(f.get("assets_dead")),
                     "dead_paths": [trace_path(x) for x in (f.get("dead_paths") or [])[:8]]}
                    for f in (short.get("faces") or [])[:12] if isinstance(f, dict)]
    return out


def _rpc(target, method, params, wait=4.0):
    """One JSON-RPC line to a primal's door (a ("host", port) pair or a socket path); the result, or raises."""
    req = (json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}) + "\n").encode("utf-8")
    if isinstance(target, tuple):
        s = socket.create_connection(target, wait)
    else:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(wait)
        s.connect(target)
    try:
        s.settimeout(wait)
        s.sendall(req)
        buf = b""
        while not buf.endswith(b"\n") and len(buf) < (1 << 20):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    finally:
        s.close()
    j = json.loads(buf.decode("utf-8", "replace").strip().split("\n")[0])
    if "error" in j and j["error"]:
        raise RuntimeError(str((j["error"] or {}).get("message", j["error"]))[:80])
    r = j.get("result")
    if isinstance(r, dict) and r.get("error"):
        raise RuntimeError(str(r["error"])[:80])
    return r


def _doors(name, port):
    """Where a primal may be listening on this body: its socket (where there are sockets), then its loopback port."""
    out = []
    if hasattr(socket, "AF_UNIX") and os.name != "nt":
        dirs = [os.path.join(os.environ.get("XDG_RUNTIME_DIR") or "/run/user/%d" % os.getuid(), "biomeos"), "/run/membrane"]
        for d in dirs:
            for fn in (name + ".sock", name.lower() + ".sock"):
                if os.path.exists(os.path.join(d, fn)) and os.path.join(d, fn) not in out:
                    out.append(os.path.join(d, fn))
    return ([("127.0.0.1", port)] + out) if name.lower() == "swarmvine" else (out + [("127.0.0.1", port)])


def _first_door(name, port, method, params):
    last = "no door on this body"
    for door in _doors(name, port):
        try:
            return _rpc(door, method, params), None
        except (OSError, ValueError) as e:
            last = "no door on this body" if isinstance(e, (ConnectionRefusedError, FileNotFoundError)) else type(e).__name__
        except RuntimeError as e:
            return None, "refused: %s" % e
    return None, last


def feed_bat(faces, seconds):
    """One observation of the walk itself, in skunkBat's own shape. No source address is named, so nothing can be
    quarantined on account of it."""
    reqs = sum(f.get("requests", 0) for f in faces)
    if not reqs:
        return "nothing walked"
    secs = max(float(seconds), 1.0)
    now = time.time()
    obs = {"connection_rate": round(reqs / secs, 3), "traffic_volume": int(sum(f.get("bytes", 0) for f in faces) / secs),
           "ports_accessed": sorted({int(f["port"]) for f in faces if f.get("port")}),
           "timestamp": {"secs_since_epoch": int(now), "nanos_since_epoch": int((now % 1) * 1e9)},
           "http": {"request_rate": round(reqs / secs, 3),
                    "error_rate_4xx": round(sum(f.get("answers_4xx", 0) for f in faces) / reqs, 4),
                    "error_rate_5xx": round(sum(f.get("answers_5xx", 0) for f in faces) / reqs, 4),
                    "path_diversity": reqs, "avg_payload_bytes": 0, "method_diversity": 1}}
    r, why = _first_door("skunkbat", 9750, "baseline.observe", obs)
    return "observed" if isinstance(r, dict) and r.get("status") == "ok" else (why or "unexpected answer")


def feed_vine(trace):
    """The trace as one gossip entry under this body's name. Entries age out of the vine after ten minutes; the
    gate's loop tells it again (--tell) so the latest walk stays on the vine between walks."""
    key = "dead-links:%s" % (trace.get("by") or "unknown")
    r, why = _first_door("swarmvine", 7800, "gossip.inject", {"topic": "tower", "key": key, "payload": trace})
    if isinstance(r, dict) and r.get("result"):
        return str(r["result"])[:24].lower()
    return why or "unexpected answer"


def tell_pass(log):
    """Say the latest walk again on the vine (this body's, and the other body's as its own gate shows it)."""
    told = {}
    try:
        with open(FACES_SUMMARY, encoding="utf-8") as f:
            mine = json.load(f)
        told[mine.get("by", "?")] = feed_vine(trace_of(mine))
    except (OSError, ValueError):
        mine = None
    me = socket.gethostname().split(".")[0].lower()
    if not mine or not str(told.get(mine.get("by", "?"), "")).startswith("no door"):   # a vine is here: carry the others
        for body, base in PEER_GATES.items():
            if body == me or body in told:
                continue
            try:
                with _PLAIN.open(urllib.request.Request(base + "/thymus", headers={"User-Agent": UA, "Accept": "application/json"}), timeout=6) as r:
                    theirs = (json.loads(r.read(4 << 20).decode("utf-8", "replace")) or {}).get("dead_links") or {}
                if theirs.get("faces") and theirs.get("by") == body:
                    told[body] = feed_vine(trace_of(theirs))
            except Exception:
                continue
    for k, v in told.items():
        log("  vine  dead-links:%-10s %s" % (k, v))
    if mine is not None:
        mine.setdefault("fed", {})["swarmvine"] = told.get(mine.get("by", "?"), "")
        mine["fed"]["told_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if len(told) > 1:
            mine["fed"]["carried_for"] = sorted(k for k in told if k != mine.get("by"))
        with open(FACES_SUMMARY, "w", encoding="utf-8") as f:
            json.dump(mine, f, indent=1, ensure_ascii=False)
    return 0


def faces_pass(a, log):
    gate = a.base.rstrip("/")
    browser = find_browser() if a.dom else None
    log("GAIA WALKER  faces  (gate %s%s)" % (gate, ", links written by scripts included" if browser else ", static links only"))
    t0 = time.time()
    faces = [walk_face(f, a.timeout, a.workers, browser, a.settle_ms) for f in default_faces(gate)]
    log("")
    log("  %-22s %6s %5s %5s %10s %10s %7s %12s" % ("face", "links", "ok", "dead", "same page", "home only", "assets", "assets dead"))
    for f in faces:
        if f["status"] != 200:
            log("  %-22s front page did not answer (%s)" % (f["name"], f["status"] or f.get("error")))
            continue
        log("  %-22s %6d %5d %5d %10d %10d %7d %12d%s" % (
            f["name"], f["links"], f["ok"], len(f["dead"]), len(f["folds"]), len(f.get("home_only", [])),
            f["assets"], len(f["assets_dead"]), "" if f["after_scripts"] or not browser else "   (browser pass failed)"))
    for f in faces:
        for word, key in (("dead", "dead"), ("home only", "home_only")):
            for d in f.get(key, [])[:a.lines]:
                log("     %-20s %-9s %-44s %s%s%s" % (f["name"], word, d["path"][:44], d["status"],
                                                      "  written by a script" if d["by_script"] else "",
                                                      "  leaves the site's folder" if d["outside_the_site"] else ""))
    report = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "by": socket.gethostname().split(".")[0].lower(),
              "gate": gate, "seconds": round(time.time() - t0, 1), "faces": faces}
    top = os.path.join(REPO, "data", "gut", "walker")
    os.makedirs(top, exist_ok=True)
    gi = os.path.join(top, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="ascii") as f:
            f.write("# walker output is regenerated on every run\n*\n")
    with open(os.path.join(top, "faces.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    # the short form the thymus reads: counts per face and the first dead paths of each
    short = {"ts": report["ts"], "by": report["by"], "after_scripts": bool(browser),
             "dead": sum(len(f.get("dead", [])) for f in faces), "same_page_again": sum(len(f.get("folds", [])) for f in faces),
             "assets_dead": sum(len(f.get("assets_dead", [])) for f in faces),
             "at_home_only": sum(len(f.get("home_only", [])) for f in faces),
             "faces": [{"face": f["name"], "answers": f["status"] == 200, "links": f.get("links", 0), "ok": f.get("ok", 0),
                        "dead": len(f.get("dead", [])), "same_page_again": len(f.get("folds", [])),
                        "at_home_only": len(f.get("home_only", [])),
                        "assets": f.get("assets", 0), "assets_dead": len(f.get("assets_dead", [])),
                        "dead_paths": [d["path"] for d in f.get("dead", [])[:12]],
                        "at_home_only_paths": [d["path"] for d in f.get("home_only", [])[:12]]} for f in faces]}
    # hand the trace on: skunkBat sees the walk as an observation, swarmVine carries the findings as gossip
    short["fed"] = {"skunkbat": feed_bat(faces, report["seconds"]), "swarmvine": feed_vine(trace_of(short)),
                    "told_at": report["ts"]}
    os.makedirs(os.path.dirname(FACES_SUMMARY), exist_ok=True)
    with open(FACES_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(short, f, indent=1, ensure_ascii=False)
    log("  fed on (trace only):  skunkBat %s   swarmVine %s" % (short["fed"]["skunkbat"], short["fed"]["swarmvine"]))
    log("  %.0f s   detail: %s   short form: %s" % (report["seconds"], os.path.join(top, "faces.json"), FACES_SUMMARY))
    return 1 if short["dead"] or short["assets_dead"] else 0


# ───────────────────────── main ─────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Walk a Gaia gate: link paths and renders.")
    ap.add_argument("--faces", action="store_true",
                    help="walk the front page of each name, at home and where it is hoisted, one link deep")
    ap.add_argument("--tell", action="store_true",
                    help="say the latest faces walk again on swarmVine (entries age out after ten minutes); walks nothing")
    ap.add_argument("--dom", action="store_true",
                    help="with --faces: also load each front page in a headless browser, so links written by scripts are seen")
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

    if a.tell:
        return tell_pass(log)
    if a.faces:
        return faces_pass(a, log)
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
