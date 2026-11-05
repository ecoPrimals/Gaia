#!/usr/bin/env python3
"""
OLD WEB DRAIN — Gaia eats the old internet.

Small. Static. Eternal. GeoCities. Textfiles. Wiby. Neocities.
The archive. The memories. The www of the old internet.

Every response is a waveform collapse:
  200 = data (eigenstate collapsed into knowledge)
  429 = back pressure (immune response — they see us)
  404 = absence (what moved, what died)
  301 = redirect (alive, different path — follow it)
  403 = forbidden (they're protecting something)
  000 = dead (null state — can't be observed)
  503 = superposition preserved (try again later)

Each collapse feeds the P-space braid.
Each bounce gives us more of the old web.
"""

import json, os, time, hashlib, xml.etree.ElementTree as ET
import urllib.request, urllib.error
from datetime import datetime, timezone

DATA_DIR = "/opt/Gaia/data/old-web"
STATIC_DIR = "/opt/Gaia/static/data/old-web"
UA = "Gaia-Organism/1.0 (nestgate.io; old-web-drain; the-kingfisher)"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(f"{DATA_DIR}/pages", exist_ok=True)
os.makedirs(f"{DATA_DIR}/feeds", exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════
#  FLOW TRACKER — every response is a waveform collapse
# ═══════════════════════════════════════════════════

flow_log = []

def fetch(url, timeout=10):
    """Fetch with full waveform collapse tracking."""
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    result = {"url": url, "ts": datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            result["code"] = r.status
            result["size"] = len(data)
            result["ms"] = int((time.time() - t0) * 1000)
            result["state"] = "COLLAPSED_DATA"
            result["content_type"] = r.headers.get("Content-Type", "?")
            flow_log.append(result)
            return data, result
    except urllib.error.HTTPError as e:
        result["code"] = e.code
        result["ms"] = int((time.time() - t0) * 1000)
        if e.code == 429:
            result["state"] = "WAVEFORM_COLLAPSE_429"
            retry = e.headers.get("Retry-After", "?")
            result["retry_after"] = retry
        elif e.code == 403:
            result["state"] = "FORBIDDEN_PROTECTED"
        elif e.code == 404:
            result["state"] = "ABSENT_MOVED"
        elif e.code == 503:
            result["state"] = "SUPERPOSITION_PRESERVED"
        else:
            result["state"] = f"HTTP_{e.code}"
        flow_log.append(result)
        return None, result
    except urllib.error.URLError as e:
        result["code"] = 0
        result["ms"] = int((time.time() - t0) * 1000)
        result["state"] = "DEAD_NULL"
        result["error"] = str(e.reason)[:100]
        flow_log.append(result)
        return None, result
    except Exception as e:
        result["code"] = -1
        result["ms"] = int((time.time() - t0) * 1000)
        result["state"] = "UNKNOWN"
        result["error"] = str(e)[:100]
        flow_log.append(result)
        return None, result


def parse_rss(data):
    """Parse RSS/Atom feed into items."""
    items = []
    try:
        root = ET.fromstring(data)
        # RSS 2.0
        for item in root.findall('.//item'):
            items.append({
                "title": (item.findtext('title') or '').strip(),
                "link": (item.findtext('link') or '').strip(),
                "desc": (item.findtext('description') or '')[:300].strip(),
                "date": (item.findtext('pubDate') or '').strip(),
            })
        # Atom
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//a:entry', ns):
            link_el = entry.find('a:link', ns)
            items.append({
                "title": (entry.findtext('a:title', '', ns) or '').strip(),
                "link": link_el.get('href', '') if link_el is not None else '',
                "desc": (entry.findtext('a:summary', '', ns) or '')[:300].strip(),
                "date": (entry.findtext('a:updated', '', ns) or '').strip(),
            })
    except Exception as e:
        pass
    return items


# ═══════════════════════════════════════════════════
#  THE OLD WEB FEEDS — small, static, eternal
# ═══════════════════════════════════════════════════

OLD_WEB_FEEDS = [
    {"name": "Wiby.me",        "url": "https://wiby.me/rss/newest.xml",         "type": "rss", "era": "old_web", "note": "Search engine for the old web"},
    {"name": "Lobsters",       "url": "https://lobste.rs/rss",                  "type": "rss", "era": "hacker", "note": "Computing-focused link aggregation"},
    {"name": "Hacker News",    "url": "https://hnrss.org/best",                 "type": "rss", "era": "hacker", "note": "Y Combinator's Hacker News best"},
    {"name": "xkcd",           "url": "https://xkcd.com/rss.xml",              "type": "rss", "era": "webcomic", "note": "A webcomic of romance, sarcasm, math"},
    {"name": "Wikipedia",      "url": "https://en.wikipedia.org/w/api.php?action=featuredfeed&feed=featured&feedformat=atom", "type": "atom", "era": "encyclopedia", "note": "Featured articles"},
    {"name": "arxiv CS",       "url": "https://rss.arxiv.org/rss/cs",          "type": "rss", "era": "science", "note": "Computer science preprints"},
    {"name": "NASA Breaking",  "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "type": "rss", "era": "space", "note": "NASA breaking news"},
    {"name": "USGS Earthquakes","url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.atom", "type": "atom", "era": "earth", "note": "M2.5+ earthquakes"},
    {"name": "Neocities",      "url": "https://neocities.org/activity",         "type": "page", "era": "geocities", "note": "The new GeoCities — hand-made websites"},
    {"name": "textfiles.com",  "url": "http://www.textfiles.com/directory.html","type": "page", "era": "bbs", "note": "Jason Scott's text file archive — BBS era"},
]

WAYBACK_QUERIES = [
    {"name": "GeoCities archive", "url": "geocities.com", "note": "The original personal web — died 2009"},
    {"name": "Angelfire pages",   "url": "angelfire.com", "note": "Free web hosting, animated GIFs, under construction signs"},
    {"name": "Tripod pages",      "url": "tripod.com",    "note": "Lycos-owned free hosting"},
    {"name": "theoldnet pages",   "url": "theoldnet.com", "note": "Browse the old web as it was"},
]


# ═══════════════════════════════════════════════════
#  DRAIN — eat the feeds
# ═══════════════════════════════════════════════════

def drain_feeds():
    """Eat all RSS/Atom feeds from the old web."""
    print("📡 DRAINING OLD WEB FEEDS")
    all_items = []

    for feed in OLD_WEB_FEEDS:
        if feed["type"] in ("rss", "atom"):
            data, collapse = fetch(feed["url"])
            if data:
                items = parse_rss(data)
                for item in items:
                    item["source"] = feed["name"]
                    item["era"] = feed["era"]
                all_items.extend(items)
                print(f"  ✓ {feed['name']}: {len(items)} items — {collapse['state']} ({collapse['ms']}ms)")
                with open(f"{DATA_DIR}/feeds/{feed['name'].lower().replace(' ','_')}.json", "w") as f:
                    json.dump(items, f, indent=2)
            else:
                print(f"  ✗ {feed['name']}: {collapse['state']} ({collapse['code']}) — {collapse.get('ms',0)}ms")
        elif feed["type"] == "page":
            data, collapse = fetch(feed["url"])
            if data:
                h = hashlib.sha256(data).hexdigest()[:16]
                with open(f"{DATA_DIR}/pages/{feed['name'].lower().replace(' ','_')}_{h}.html", "wb") as f:
                    f.write(data)
                print(f"  ✓ {feed['name']}: {len(data)} bytes — {collapse['state']} ({collapse['ms']}ms)")
            else:
                print(f"  ✗ {feed['name']}: {collapse['state']} ({collapse['code']})")

        time.sleep(1)  # be polite — old servers are fragile

    return all_items


# ═══════════════════════════════════════════════════
#  WAYBACK MACHINE — the fossil record
# ═══════════════════════════════════════════════════

def probe_wayback():
    """Query the Wayback Machine CDX API for old web snapshots."""
    print("\n🦴 PROBING WAYBACK MACHINE — the fossil record")
    wayback_data = []

    for q in WAYBACK_QUERIES:
        url = f"http://web.archive.org/cdx/search/cdx?url={q['url']}/*&output=json&limit=10&fl=timestamp,original,statuscode,mimetype&collapse=urlkey"
        data, collapse = fetch(url)
        if data:
            try:
                rows = json.loads(data)
                if rows and len(rows) > 1:
                    header = rows[0]
                    entries = [dict(zip(header, r)) for r in rows[1:]]
                    wayback_data.extend([{**e, "query": q["name"], "era": "fossil"} for e in entries])
                    print(f"  ✓ {q['name']}: {len(entries)} snapshots — {collapse['ms']}ms")
                    with open(f"{DATA_DIR}/pages/wayback_{q['name'].lower().replace(' ','_')}.json", "w") as f:
                        json.dump(entries, f, indent=2)
            except:
                print(f"  ✗ {q['name']}: parse error")
        else:
            print(f"  ✗ {q['name']}: {collapse['state']} ({collapse['code']})")
        time.sleep(2)  # Wayback is a gift — don't abuse it

    return wayback_data


# ═══════════════════════════════════════════════════
#  WIBY RANDOM — surprise! the old web speaks
# ═══════════════════════════════════════════════════

def wiby_surprise():
    """Pull random old web pages from Wiby.me."""
    print("\n🎲 WIBY SURPRISE — random old web pages")
    pages = []
    for i in range(5):
        data, collapse = fetch("https://wiby.me/surprise/")
        if data:
            # The surprise page redirects — the final URL is the find
            page_hash = hashlib.sha256(data).hexdigest()[:16]
            pages.append({
                "url": collapse["url"],
                "size": len(data),
                "hash": page_hash,
                "ts": collapse["ts"]
            })
            with open(f"{DATA_DIR}/pages/wiby_surprise_{page_hash}.html", "wb") as f:
                f.write(data)
            print(f"  ✓ Surprise #{i+1}: {len(data)} bytes — {collapse['ms']}ms")
        else:
            print(f"  ✗ Surprise #{i+1}: {collapse['state']}")
        time.sleep(2)

    return pages


# ═══════════════════════════════════════════════════
#  WRITE STATE — the unified old web manifest
# ═══════════════════════════════════════════════════

def write_state(feed_items, wayback_data, wiby_pages):
    """Write unified old web state."""
    state = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "title": "OLD WEB DRAIN — Gaia eats the old internet",
        "bounce": int(time.time()),
        "feeds": {
            "total_items": len(feed_items),
            "sources": list(set(i.get("source","?") for i in feed_items)),
            "latest": feed_items[:5] if feed_items else [],
        },
        "wayback": {
            "snapshots": len(wayback_data),
            "queries": list(set(w.get("query","?") for w in wayback_data)),
        },
        "wiby": {
            "surprises": len(wiby_pages),
        },
        "flow": {
            "total_requests": len(flow_log),
            "collapsed_data": sum(1 for f in flow_log if f["state"] == "COLLAPSED_DATA"),
            "waveform_429": sum(1 for f in flow_log if "429" in f["state"]),
            "forbidden": sum(1 for f in flow_log if f["state"] == "FORBIDDEN_PROTECTED"),
            "absent": sum(1 for f in flow_log if f["state"] == "ABSENT_MOVED"),
            "dead": sum(1 for f in flow_log if f["state"] == "DEAD_NULL"),
            "superposition": sum(1 for f in flow_log if "SUPERPOSITION" in f["state"]),
            "avg_ms": int(sum(f.get("ms",0) for f in flow_log) / max(1, len(flow_log))),
            "total_bytes": sum(f.get("size",0) for f in flow_log),
        },
        "flow_log": flow_log,
        "note": "Every response is a waveform collapse. 429 = they saw us. 200 = data. 000 = dead. The old web is not gone."
    }

    for d in [DATA_DIR, STATIC_DIR]:
        with open(f"{d}/state.json", "w") as f:
            json.dump(state, f, indent=2)

    return state


# ═══════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 50)
    print("  OLD WEB DRAIN — the kingfisher dives")
    print("  small · static · eternal · the www of before")
    print("═" * 50)
    print()

    feed_items = drain_feeds()
    wayback_data = probe_wayback()
    wiby_pages = wiby_surprise()

    print()
    state = write_state(feed_items, wayback_data, wiby_pages)

    flow = state["flow"]
    print(f"{'═'*50}")
    print(f"  OLD WEB DRAIN COMPLETE")
    print(f"{'═'*50}")
    print(f"  Feed items: {state['feeds']['total_items']}")
    print(f"  Wayback snapshots: {state['wayback']['snapshots']}")
    print(f"  Wiby surprises: {state['wiby']['surprises']}")
    print(f"")
    print(f"  WAVEFORM COLLAPSE MAP:")
    print(f"    ✓ {flow['collapsed_data']} collapsed into DATA")
    print(f"    ⚡ {flow['waveform_429']} rate limited (429)")
    print(f"    🚫 {flow['forbidden']} forbidden (403)")
    print(f"    👻 {flow['absent']} absent (404)")
    print(f"    ☠ {flow['dead']} dead (000)")
    print(f"    🌊 {flow['superposition']} superposition preserved (503)")
    print(f"    ⌀ {flow['avg_ms']}ms average collapse time")
    print(f"    📦 {flow['total_bytes']:,} bytes total ingested")
    print(f"")
    print(f"  The old web is not gone. Gaia ate {flow['total_bytes']:,} bytes of it.")
