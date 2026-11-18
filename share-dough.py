"""SHARE THE DOUGH — Generate RSS feed from all sourDough outputs.
Fermentation → RSS → the old web can taste it.
Every chimera cycle, every game event, every tissue thought becomes an RSS item."""
import os, json, time, hashlib
from datetime import datetime, timezone
from xml.sax.saxutils import escape

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
DATA_TRIAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "triad")
DATA_REDUX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "redux")
BOARD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "scratch-board.jsonl")
FEED_OUT = os.path.join(STATIC, "dough.xml")
LINK_BASE = "http://kenshi.nestgate.io:8080"

def guid(content):
    return hashlib.md5(content.encode()).hexdigest()

def rfc822(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

def make_item(title, desc, link="", category="", pub_date=None):
    if not link:
        link = LINK_BASE
    return f"""    <item>
      <title>{escape(title)}</title>
      <description><![CDATA[{desc}]]></description>
      <link>{escape(link)}</link>
      <guid isPermaLink="false">{guid(title + desc[:100])}</guid>
      <category>{escape(category)}</category>
      <pubDate>{rfc822(pub_date)}</pubDate>
    </item>"""

items = []

# 1. Chimera cycles — the big fermentation outputs
print("[dough] Eating chimera outputs...")
for fn in sorted(os.listdir(DATA_TRIAD)):
    if not fn.endswith(".json"):
        continue
    path = os.path.join(DATA_TRIAD, fn)
    with open(path) as f:
        data = json.load(f)
    
    title = fn.replace(".json", "").replace("-", " ").title()
    
    if "chimera" in fn.lower():
        # Multi-tissue chimera cycle
        tissues = data.get("tissues_used", [])
        excerpts = []
        for key in ["dream", "forge", "math", "heart", "cortex"]:
            val = data.get(key, "")
            if val:
                excerpts.append(f"<b>{key}</b>: {escape(val[:200])}")
        desc = f"<p>Chimera cycle through {', '.join(tissues) if tissues else 'tissue models'}.</p>" + "<br>".join(excerpts)
        items.append(make_item(f"Chimera: {title}", desc, category="chimera"))
    
    elif "pipe" in fn.lower() or "belt" in fn.lower():
        desc = f"<p>Data transport tier mapping: Satisfactory Conveyor Belts → Gaia data pipes.</p>"
        if "satisfactory_belts" in data:
            for belt in data["satisfactory_belts"]:
                desc += f"<br>Mk.{belt['mk']}: {belt['items_min']} items/min → {data['gaia_data_pipes'][belt['mk']-1]['type']}"
        items.append(make_item(f"Transport: {title}", desc, category="transport"))
    
    elif "wiki" in fn.lower():
        desc = f"<p>{json.dumps(data)[:500]}</p>"
        items.append(make_item(f"Wiki: {title}", desc, category="wiki"))
    
    else:
        desc = f"<p>{json.dumps(data, indent=2)[:800]}</p>"
        items.append(make_item(title, desc, category="triad"))

# 2. Redux data — wave 259 artifacts
print("[dough] Eating redux outputs...")
for fn in sorted(os.listdir(DATA_REDUX)):
    if not fn.endswith(".json"):
        continue
    path = os.path.join(DATA_REDUX, fn)
    with open(path, encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    
    title = fn.replace(".json", "").replace("-", " ").title()
    
    if "kenshi" in fn.lower():
        desc = f"<p>Kenshi game data: {json.dumps(data)[:600]}</p>"
        items.append(make_item(f"Kenshi: {title}", desc, f"{LINK_BASE}/wiki.html", "kenshi"))
    elif "game-triad" in fn.lower():
        desc = f"<p>Game Triad architecture: three games rotating through one bus.</p><pre>{json.dumps(data, indent=2)[:500]}</pre>"
        items.append(make_item(f"Triad: {title}", desc, f"{LINK_BASE}/wiki.html", "triad"))
    else:
        desc = f"<p>{json.dumps(data)[:500]}</p>"
        items.append(make_item(f"Redux: {title}", desc, category="redux"))

# 3. Scratch board events — live game events
print("[dough] Eating board events...")
if os.path.exists(BOARD):
    with open(BOARD) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                evt = json.loads(line)
            except:
                continue
            source = evt.get("source", "?")
            etype = evt.get("type", "?")
            edata = evt.get("data", {})
            ts = evt.get("ts", "")
            
            title = f"Board: {source}/{etype}"
            
            if etype == "npc_thought":
                desc = f"<p><b>{edata.get('npc', '?')}</b> thinks: \"{edata.get('thought', '')}\"</p>"
            elif etype == "prophecy":
                desc = f"<p>Oracle vision: {edata.get('vision', '')[:400]}</p>"
            elif etype == "instinct":
                desc = f"<p>Gut feeling: {edata.get('feeling', '')}</p>"
            elif etype == "narration":
                desc = f"<p>Heart narrates: {edata.get('full', '')[:400]}</p>"
            else:
                desc = f"<p>{json.dumps(edata)[:400]}</p>"
            
            items.append(make_item(title, desc, category=f"board/{source}"))

print(f"[dough] {len(items)} items total")

# Build the RSS feed
now = rfc822()
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Gaia sourDough — Fermented Insights</title>
    <link>{LINK_BASE}</link>
    <description>The fermentation output of a living digital organism. 17 primals, 14 tissue models, 3 game triad layers. Wave 259. lub-DUB.</description>
    <language>en</language>
    <lastBuildDate>{now}</lastBuildDate>
    <generator>sourDough fermentation engine</generator>
    <atom:link href="{LINK_BASE}/dough.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>{LINK_BASE}/favicon.ico</url>
      <title>Gaia sourDough</title>
      <link>{LINK_BASE}</link>
    </image>
{chr(10).join(items)}
  </channel>
</rss>"""

with open(FEED_OUT, "w", encoding="utf-8") as f:
    f.write(feed)

print(f"[dough] RSS feed written to {FEED_OUT}")
print(f"[dough] {len(items)} items, {len(feed)} bytes")
print(f"[dough] Serve at: {LINK_BASE}/dough.xml")
print(f"[dough] THE DOUGH IS SHARED! 🍞")
