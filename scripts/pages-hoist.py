#!/usr/bin/env python3
"""pages-hoist - lift the face my gate serves for a WAN name onto GitHub Pages.

The house answers hud.primals.eco and nestgate.io when it is reachable: the gate (:8443) gives the page and
the live routes, the data server (:8080) gives the scripts and the data files. GitHub Pages can only serve
files, so for each name this walks the page the gate serves at "/", follows the scripts and assets it pulls
in, takes a snapshot of every live route and data file they read, and commits the lot to that name's Pages
repo in one commit.

    python scripts/pages-hoist.py status                 what is up, who published last, where DNS points
    python scripts/pages-hoist.py dry [site ...]         build only; say what would go up and what changed since
    python scripts/pages-hoist.py publish [site ...]     publish now, by hand
    python scripts/pages-hoist.py publish --create ...   also create the repo / turn Pages on if missing
    python scripts/pages-hoist.py refresh                what the gate's own loop calls: publish only if it is this
                                                         body's turn, and attach the name once DNS points at GitHub

One mesh, one publisher at a time. Bodies are ranked (BODIES); a body stands down while a higher-ranked
body's snapshot is fresh and takes over when it goes stale. Whoever publishes reads from every body that
answers, the highest-ranked first, so the snapshot is the organism's and not just the publisher's.
Nothing here holds a credential: every call to GitHub goes through `gh`, with the login already on the body.

What never goes up: any key named like a credential (token, zk, secret, seed, ...), and any file that trips
the guard below (credential shapes, or a list of the house's hardware addresses). The published page carries a small label saying it is a snapshot, from which body, and when.
"""
import base64, calendar, hashlib, json, os, re, socket, struct, subprocess, sys, time, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(REPO, "runtime", "membrane")
STATE = os.path.join(STATE_DIR, "pages-hoist.json")
BODIES = ["eastgate", "polaris"]          # who publishes first, and whose view is read first
WIRE = {"eastgate": "192.168.4.248", "polaris": "192.168.4.147"}
FRESH = 25 * 60                           # a higher-ranked body's snapshot younger than this means: stand down
MIN_GAP = 14 * 60                         # never publish more often than this from the loop (Pages build limit)
MAX_FILE, MAX_TOTAL, MAX_FILES, MAX_DEPTH = 4 << 20, 96 << 20, 2000, 3
PAGES_A = {"185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"}

SITES = {
    "hud": {"repo": "ecoPrimals/hud", "branch": "gh-pages", "domain": "hud.primals.eco",
            "root": "senses.html", "also_as": ["senses.html"], "keep_old_root_as": "pane.html"},
    "nestgate": {"repo": "ecoPrimals/nestgate.io", "branch": "main", "domain": "nestgate.io",
                 "root": "nestgate.html", "also_as": [], "nojekyll": True,
                 "about": "nestgate.io - the face Gaia's gate serves for this name, hoisted to GitHub Pages"},
}

DROP_KEYS = {"token", "zk", "secret", "secrets", "password", "passwd", "seed", "auth", "authorization",
             "cookie", "session", "api_key", "apikey", "private_key", "ssh_pass"}
TOKENISH = re.compile(r"^GAIA:[^\s]{8,}$")
GUARD = [("github token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}")),
         ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
         ("credential field", re.compile(r"\"(?:token|zk|ssh_pass|password|passwd|private_key|api_key)\"\s*:\s*\"")),
         ("gate token", re.compile(r"GAIA:[0-9A-Za-z]{4,}[:\-][^\s\"']{6,}"))]
MAC_RX, MAX_MACS = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"), 5

TEXT_EXT = (".js", ".css", ".mjs")
ASSET_EXT = r"(?:js|mjs|css|png|jpe?g|gif|svg|webp|ico|woff2?|ttf|json|jsonl|xml|txt|md|csv|mp3|ogg|wav|webmanifest)"
FETCH_RX = re.compile(r"""fetch\(\s*['"`](/[^'"`?#\s$<>]*)""")
TAG_RX = re.compile(r"""<(?:script|img|source|audio|video|iframe|link)\b[^>]*?\b(?:src|href|poster)\s*=\s*["']?(/[^\s"'>?#]+)""", re.I)
PATH_RX = re.compile(r"""['"`(=\s](/[A-Za-z0-9_\-./]+\.""" + ASSET_EXT + r""")(?=['"`)?#\s>])""", re.I)


class Gh(Exception):
    pass


def gh(method, path, body=None, ok404=False):
    cmd = ["gh", "api", "-X", method, path]
    if body is not None:
        cmd += ["--input", "-"]
    try:
        r = subprocess.run(cmd, input=json.dumps(body) if body is not None else None, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=180)
    except FileNotFoundError:
        raise Gh("gh is not installed on this body")
    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "").strip().replace("\n", " ")[:240]
        if ok404 and ("404" in msg or "Not Found" in msg):
            return None
        raise Gh("%s %s: %s" % (method, path, msg))
    return json.loads(r.stdout) if r.stdout.strip() else {}


def body_name():
    return socket.gethostname().split(".")[0].lower()


def rank(name):
    return BODIES.index(name) if name in BODIES else len(BODIES)


def sources():
    """Every door that can answer for the organism, the highest-ranked body first; only the ones that are open."""
    me = body_name()
    names = sorted(set(BODIES) | {me}, key=rank)
    out = []
    for n in names:
        ip = "127.0.0.1" if n == me else WIRE.get(n)
        if not ip:
            continue
        for port in (8443, 8080):
            s = socket.socket()
            s.settimeout(1.5)
            try:
                s.connect((ip, port))
                out.append(("http://%s:%d" % (ip, port), n))
            except Exception:
                pass
            finally:
                s.close()
    return out


def read(path, host, bases, want_json=False):
    """First door that answers 200 (and, for a live route, answers JSON). -> (bytes, body) or (None, why)."""
    why = "no door open"
    for base, name in bases:
        req = urllib.request.Request(base + path, headers={"Host": host, "Accept": "application/json" if want_json else "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read(MAX_FILE + 1)
        except urllib.error.HTTPError as e:
            why = "http %s" % e.code
            continue
        except Exception as e:
            why = type(e).__name__
            continue
        if len(data) > MAX_FILE:
            why = "larger than %d MB" % (MAX_FILE >> 20)
            continue
        if want_json:
            try:
                json.loads(data.decode("utf-8"))
            except Exception:
                why = "not JSON"
                continue
        return data, name
    return None, why


def blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def scrub(o):
    if isinstance(o, dict):
        return {k: scrub(v) for k, v in o.items()
                if str(k).lower() not in DROP_KEYS and not (isinstance(v, str) and TOKENISH.match(v))}
    if isinstance(o, list):
        return [scrub(v) for v in o if not (isinstance(v, str) and TOKENISH.match(v))]
    return o


def guard(data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    for label, rx in GUARD:
        if rx.search(text):
            return label
    if len(set(m.lower() for m in MAC_RX.findall(text))) > MAX_MACS:
        return "device inventory"                         # a list of the house's hardware addresses stays home
    return None


def dns_a(name, server="1.1.1.1"):
    """A records straight from a public resolver (this body's hosts file maps the names to the house)."""
    q = struct.pack(">HHHHHH", 0x6761, 0x0100, 1, 0, 0, 0)
    q += b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\0" + struct.pack(">HH", 1, 1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    try:
        s.sendto(q, (server, 53))
        d = s.recv(2048)
    except Exception:
        return None
    finally:
        s.close()
    n = struct.unpack(">H", d[6:8])[0]
    i = 12
    while d[i]:
        i += d[i] + 1
    i += 5
    out = []
    for _ in range(n):
        while True:
            if d[i] & 0xC0 == 0xC0:
                i += 2
                break
            if d[i] == 0:
                i += 1
                break
            i += d[i] + 1
        t, _c, _ttl, ln = struct.unpack(">HHIH", d[i:i + 10])
        i += 10
        if t == 1 and ln == 4:
            out.append(".".join(str(b) for b in d[i:i + 4]))
        i += ln
    return out


SHIM = """<script data-gaia-hoist>/* this page is a copy hoisted to GitHub Pages: live routes read snapshots */
(function(){var M=__MAP__,B=location.pathname.replace(/[^\\/]*$/,""),f=window.fetch;
function R(p){if(typeof p!=="string"||p.charAt(0)!=="/"||p.charAt(1)==="/")return p;if(B!=="/"&&p.indexOf(B)===0)return p;return B+p.slice(1)}
function S(u){var q=u.indexOf("?"),p=q<0?u:u.slice(0,q);return M[p]?B+M[p]+"?t="+Date.now():R(u)}
window.fetch=function(u,o){try{if(typeof u==="string")return f.call(window,S(u),o)}catch(e){}return f.call(window,u,o)};
try{var xo=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){if(typeof u==="string")arguments[1]=S(u);return xo.apply(this,arguments)}}catch(e){}
function P(c,k){try{var p=c.prototype,d=Object.getOwnPropertyDescriptor(p,k);if(d&&d.set)Object.defineProperty(p,k,{get:d.get,set:function(v){d.set.call(this,R(v))},configurable:true,enumerable:d.enumerable})}catch(e){}}
P(HTMLScriptElement,"src");P(HTMLImageElement,"src");P(HTMLLinkElement,"href");P(HTMLIFrameElement,"src");P(HTMLMediaElement,"src");P(HTMLSourceElement,"src");
try{var sa=Element.prototype.setAttribute;Element.prototype.setAttribute=function(k,v){if((k==="src"||k==="href"||k==="poster")&&this.tagName!=="A")v=R(v);return sa.call(this,k,v)}}catch(e){}
document.addEventListener("click",function(e){var a=e.target&&e.target.closest?e.target.closest('a[href^="/"]'):null;
if(a){var h=a.getAttribute("href");if(h.charAt(1)!=="/")a.setAttribute("href",R(h))}},true);
try{new MutationObserver(function(ms){for(var i=0;i<ms.length;i++)for(var j=0;j<ms[i].addedNodes.length;j++){var n=ms[i].addedNodes[j];if(n.nodeType!==1)continue;
var l=n.matches&&n.matches('img[src^="/"]')?[n]:[];if(n.querySelectorAll)l=l.concat([].slice.call(n.querySelectorAll('img[src^="/"]')));
for(var k=0;k<l.length;k++){var s=l[k].getAttribute("src");if(s.charAt(1)!=="/"&&R(s)!==s)l[k].src=s}}}).observe(document.documentElement,{childList:true,subtree:true})}catch(e){}
if(__HAS_SNAP__)document.addEventListener("DOMContentLoaded",function(){f.call(window,B+"snap/meta.json?t="+Date.now()).then(function(r){return r.json()}).then(function(m){
var d=document.createElement("div");d.textContent="snapshot \\u00b7 "+m.by+" \\u00b7 "+m.ts.replace("T"," ").slice(0,16)+" UTC \\u00b7 the live gate is at home";
d.style.cssText="position:fixed;right:8px;bottom:6px;z-index:99999;font:11px monospace;color:#ccc;background:rgba(0,0,0,.55);padding:2px 7px;border-radius:3px;pointer-events:none";
document.body.appendChild(d)}).catch(function(){})})})();</script>"""


def build(site):
    """Everything this site should hold. -> (files {path: bytes}, report)."""
    cfg = SITES[site]
    host = cfg["domain"]
    bases = sources()
    with open(os.path.join(REPO, "static", cfg["root"]), "rb") as fh:
        html = fh.read().decode("utf-8").replace("\r\n", "\n")   # the same bytes whichever body's checkout this is
    files, snap_map, misses, held, read_from = {}, {}, {}, {}, {}
    total = 0
    seen = set()
    queue = [(html, 0)]
    while queue:
        text, depth = queue.pop(0)
        found = set(TAG_RX.findall(text)) | set(PATH_RX.findall(text))
        routes = set(FETCH_RX.findall(text))
        for p in sorted(found | routes):
            if p in seen or p in ("/", "") or ".." in p:
                continue
            seen.add(p)
            if len(files) >= MAX_FILES or total >= MAX_TOTAL:
                misses[p] = "over the size budget"
                continue
            ext = os.path.splitext(p)[1].lower()
            is_route = ext == "" or p.endswith("/")
            if is_route and p not in routes:
                continue                                   # a link to another page, not something this page reads
            if ext in (".html", ".htm"):
                continue
            is_json = is_route or ext == ".json"
            data, who = read(p, host, bases, want_json=is_json)
            if data is None:
                misses[p] = who
                continue
            if is_json:
                data = json.dumps(scrub(json.loads(data.decode("utf-8"))), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            bad = guard(data)
            if bad:
                held[p] = bad
                continue
            if is_route:
                slug = "snap/" + (re.sub(r"[^a-z0-9]+", "-", p.strip("/").lower()) or "root") + ".json"
                files[slug] = data
                snap_map[p] = slug
            else:
                files[p.lstrip("/")] = data
            total += len(data)
            read_from[who] = read_from.get(who, 0) + 1
            if ext in TEXT_EXT and depth < MAX_DEPTH:
                try:
                    queue.append((data.decode("utf-8"), depth + 1))
                except UnicodeDecodeError:
                    pass

    page = re.sub(r"(<[a-zA-Z][^>]*?\b(?:src|href|action|poster)\s*=\s*[\"']?)/(?!/)", r"\1./", html)
    while True:                                            # a tag can carry more than one root-absolute attribute
        again = re.sub(r"(<[a-zA-Z][^>]*?\b(?:src|href|action|poster)\s*=\s*[\"']?)/(?!/)", r"\1./", page)
        if again == page:
            break
        page = again
    page = re.sub(r"(url\(\s*[\"']?)/(?!/)", r"\1./", page)
    shim = SHIM.replace("__MAP__", json.dumps(snap_map)).replace("__HAS_SNAP__", "true" if snap_map else "false")
    page, n = re.subn(r"(<head[^>]*>)", lambda m: m.group(1) + "\n" + shim, page, count=1, flags=re.I)
    if not n:
        page = shim + "\n" + page
    page = page.encode("utf-8")
    bad = guard(page)
    if bad:
        raise RuntimeError("the page itself looks like it carries a %s" % bad)
    files["index.html"] = page
    for extra in cfg.get("also_as", []):
        files[extra] = page
    if cfg.get("nojekyll"):
        files[".nojekyll"] = b""
    tip = subprocess.run(["git", "rev-parse", "--short=9", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    files["snap/meta.json"] = json.dumps({                 # every site carries it: it is how bodies know whose turn it is
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "by": body_name(), "tip": tip,
        "read_from": read_from, "files": len(files) + 1, "routes": len(snap_map),
        "not_read": len(misses), "held_back": len(held)}, indent=1).encode("utf-8")
    report = {"files": len(files), "bytes": sum(len(v) for v in files.values()), "routes": sorted(snap_map),
              "read_from": read_from, "not_read": misses, "held_back": held, "has_snap": bool(snap_map)}
    return files, report


def remote_tree(cfg):
    t = gh("GET", "repos/%s/git/trees/%s?recursive=1" % (cfg["repo"], cfg["branch"]))
    return {x["path"]: x["sha"] for x in t.get("tree", []) if x.get("type") == "blob"}


def remote_meta(cfg):
    r = gh("GET", "repos/%s/contents/snap/meta.json?ref=%s" % (cfg["repo"], cfg["branch"]), ok404=True)
    if not r or "content" not in r:
        return None
    try:
        return json.loads(base64.b64decode(r["content"]).decode("utf-8"))
    except Exception:
        return None


def meta_age(meta):
    try:
        return time.time() - calendar.timegm(time.strptime(meta["ts"], "%Y-%m-%dT%H:%M:%SZ"))
    except Exception:
        return None


def ensure_repo(site):
    cfg = SITES[site]
    made = []
    if gh("GET", "repos/" + cfg["repo"], ok404=True) is None:
        r = subprocess.run(["gh", "repo", "create", cfg["repo"], "--public", "--add-readme", "--description",
                            cfg.get("about", cfg["domain"])], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise Gh("create %s: %s" % (cfg["repo"], (r.stderr or r.stdout).strip()[:200]))
        made.append("created repo " + cfg["repo"])
        time.sleep(3)
    if gh("GET", "repos/%s/pages" % cfg["repo"], ok404=True) is None:
        gh("POST", "repos/%s/pages" % cfg["repo"], {"source": {"branch": cfg["branch"], "path": "/"}})
        made.append("turned Pages on for " + cfg["repo"])
    return made


def summary(report):
    nr, hb = report["not_read"], report["held_back"]
    return {"files": report["files"], "mb": round(report["bytes"] / 1e6, 1), "live_routes": len(report["routes"]),
            "read_from": report["read_from"], "not_read": len(nr), "not_read_sample": sorted(nr)[:8],
            "held_back": hb}


def publish(site, loop=False, create=False):
    cfg = SITES[site]
    me = body_name()
    res = {"site": site, "by": me, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if create:
        res["made"] = ensure_repo(site)
    if loop:
        meta = remote_meta(cfg)
        age = meta_age(meta) if meta else None
        if meta and age is not None:
            if meta.get("by") != me and rank(meta.get("by")) < rank(me) and age < FRESH:
                res["state"] = "stood down: %s published %d min ago" % (meta.get("by"), age // 60)
                return res
            if meta.get("by") == me and age < MIN_GAP:
                res["state"] = "nothing to do: my own snapshot is %d min old" % (age // 60)
                return res
    files, report = build(site)
    res.update(summary(report))
    ref = gh("GET", "repos/%s/git/ref/heads/%s" % (cfg["repo"], cfg["branch"]))
    parent = ref["object"]["sha"]
    base_tree = gh("GET", "repos/%s/git/commits/%s" % (cfg["repo"], parent))["tree"]["sha"]
    there = remote_tree(cfg)
    entries, changed = [], []
    keep = cfg.get("keep_old_root_as")
    if keep and keep not in there and there.get("index.html") and there["index.html"] != blob_sha(files["index.html"]):
        entries.append({"path": keep, "mode": "100644", "type": "blob", "sha": there["index.html"]})
        changed.append(keep)
    for name, data in sorted(files.items()):
        if there.get(name) == blob_sha(data):
            continue
        changed.append(name)
    real = [c for c in changed if c != "snap/meta.json"]
    if not real:
        res["state"] = "level: nothing changed"
        return res
    for name in changed:
        if name == keep and name not in files:
            continue
        b = gh("POST", "repos/%s/git/blobs" % cfg["repo"],
               {"content": base64.b64encode(files[name]).decode("ascii"), "encoding": "base64"})
        entries.append({"path": name, "mode": "100644", "type": "blob", "sha": b["sha"]})
    tree = gh("POST", "repos/%s/git/trees" % cfg["repo"], {"base_tree": base_tree, "tree": entries})
    msg = "hoist: %s from %s (%d file%s)" % (cfg["domain"], me, len(changed), "" if len(changed) == 1 else "s")
    commit = gh("POST", "repos/%s/git/commits" % cfg["repo"], {"message": msg, "tree": tree["sha"], "parents": [parent]})
    gh("PATCH", "repos/%s/git/refs/heads/%s" % (cfg["repo"], cfg["branch"]), {"sha": commit["sha"]})
    res.update(state="published", commit=commit["sha"][:9], changed=len(changed),
               changed_mb=round(sum(len(files[c]) for c in changed if c in files) / 1e6, 2))
    return res


def dry(site):
    files, report = build(site)
    man = {p: [blob_sha(d), len(d)] for p, d in files.items()}
    path = os.path.join(STATE_DIR, "pages-hoist-dry-%s.json" % site)
    res = {"site": site, **summary(report)}
    kinds = {}
    for p, d in files.items():
        k = os.path.splitext(p)[1].lower() or "(none)"
        kinds[k] = [kinds.get(k, [0, 0])[0] + 1, kinds.get(k, [0, 0])[1] + len(d)]
    res["by_kind"] = {k: "%d files, %.1f MB" % (v[0], v[1] / 1e6) for k, v in sorted(kinds.items(), key=lambda kv: -kv[1][1])}
    try:
        old = json.load(open(path, encoding="utf-8"))
        diff = [p for p in man if p != "snap/meta.json" and old["files"].get(p, [None])[0] != man[p][0]]
        res["since_last_dry"] = {"seconds": int(time.time() - old["t"]), "files_changed": len(diff),
                                 "kb_changed": round(sum(man[p][1] for p in diff) / 1e3, 1), "sample": sorted(diff)[:10]}
    except Exception:
        pass
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"t": time.time(), "files": man}, fh)
    return res


def domain(site, attach=False):
    """Where the name points, and whether Pages carries it. With attach: carry it once DNS points at GitHub."""
    cfg = SITES[site]
    pages = gh("GET", "repos/%s/pages" % cfg["repo"], ok404=True)
    a = dns_a(cfg["domain"])
    out = {"domain": cfg["domain"], "dns": a, "pages_url": pages.get("html_url") if pages else None,
           "pages_domain": pages.get("cname") if pages else None}
    if a is None:
        out["state"] = "DNS could not be read"
    elif a and set(a) <= PAGES_A:
        if pages and pages.get("cname") != cfg["domain"]:
            if attach:
                gh("PUT", "repos/%s/pages" % cfg["repo"], {"cname": cfg["domain"]})
                out["state"] = "DNS points at GitHub: name attached to the Pages site"
            else:
                out["state"] = "DNS points at GitHub; the name is not attached yet"
        else:
            out["state"] = "DNS points at GitHub and the name is attached"
            if attach and pages and not pages.get("https_enforced"):
                try:
                    gh("PUT", "repos/%s/pages" % cfg["repo"], {"https_enforced": True})
                    out["state"] += "; https now enforced"
                except Gh:
                    out["state"] += "; certificate not ready yet"
    else:
        out["state"] = "DNS still points at the house (%s)" % ", ".join(a or ["no record"])
    return out


def save(results):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        try:
            old = json.load(open(STATE, encoding="utf-8"))
        except Exception:
            old = {}
        for r in results:
            old[r.get("site", "?")] = r
        with open(STATE, "w", encoding="utf-8") as fh:
            json.dump(old, fh, indent=1)
    except Exception:
        pass


def main(argv):
    cmd = argv[0] if argv else "status"
    create = "--create" in argv
    names = [a for a in argv[1:] if not a.startswith("--")] or list(SITES)
    unknown = [n for n in names if n not in SITES]
    if unknown:
        print("unknown site: %s (known: %s)" % (", ".join(unknown), ", ".join(SITES)))
        return 2
    if cmd not in ("status", "dry", "publish", "refresh"):
        print(__doc__)
        return 2
    results = []
    for site in names:
        try:
            if cmd == "status":
                cfg = SITES[site]
                r = {"site": site, "repo": cfg["repo"], **domain(site)}
                meta = remote_meta(cfg) if r["pages_url"] else None
                if meta:
                    r["snapshot"] = "%s, %d min ago" % (meta.get("by"), (meta_age(meta) or 0) // 60)
            elif cmd == "dry":
                r = dry(site)
            else:
                loop = cmd == "refresh"
                if loop and gh("GET", "repos/" + SITES[site]["repo"], ok404=True) is None:
                    r = {"site": site, "state": "no repo yet: a hand creates it with publish --create"}
                else:
                    r = publish(site, loop=loop, create=create and not loop)
                    r["domain"] = domain(site, attach=True)["state"]
        except Gh as e:
            r = {"site": site, "state": "github said no", "error": str(e)}
        except Exception as e:
            r = {"site": site, "state": "failed", "error": "%s: %s" % (type(e).__name__, e)}
        results.append(r)
    if cmd in ("publish", "refresh"):
        save(results)
    print(json.dumps(results, indent=1, ensure_ascii=False))
    return 0 if all("error" not in r for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
