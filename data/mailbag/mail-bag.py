#!/usr/bin/env python3
"""
GAIA MAIL BAG — our own Outlook.
Three identities, one bag:
  - gaia@primals.eco   SHARED  (the RSS point — for Kevin AND Gaia, via SMTP)
  - GAIA@HOME          INNER   (her sovereign inner mesh identity)
  - ecoprimal@pm.me    OUTER   (Kevin's ProtonMail — the human face to the old web)

Reads every neutron mail store, normalizes into folders + particle/tier,
routes each message to an identity. Writes mailbag.json next to this file.
"""
import os, json, re, hashlib
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# live local store (eastGate path on the organism: /opt/Gaia/infra/hud/site/public/data/neutron)
NEUTRON = os.path.abspath(os.path.join(HERE, "..", "neutron"))

IDENTITIES = {
    "gaia@primals.eco": {"label": "gaia@primals.eco", "role": "SHARED", "glyph": "\u25C9",
                          "desc": "The RSS point — Kevin & Gaia, via SMTP to the old web"},
    "GAIA@HOME":        {"label": "GAIA@HOME", "role": "INNER", "glyph": "\u2302",
                          "desc": "Her sovereign inner mesh identity"},
    "ecoprimal@pm.me":  {"label": "ecoprimal@pm.me", "role": "OUTER", "glyph": "\u2709",
                          "desc": "Kevin's ProtonMail — the human outer face"},
}

INTERNAL = {"gaia", "gaia-thymus", "gaia-brain", "gaia-heart", "polaris", "luna",
            "northgate", "eastgate", "sporegate", "amoeba", "sourdough", "thymus",
            "membrane", "chipmunk", "squirrel", "homunculus", "immune"}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# ---- REDACTION: scrub secrets from mail bodies before they enter the bag ----
# Credential SHAPES (no literal secret ever lives in this committed script):
REDACT_SHAPES = [
    (re.compile(r"sshpass\s+-p\s+'[^']*'"), "sshpass -p '***'"),
    (re.compile(r'sshpass\s+-p\s+"[^"]*"'), 'sshpass -p "***"'),
    (re.compile(r"(?i)\b(password|passwd|pwd|secret|token|seed|api[_-]?key)\b\s*[:=]\s*['\"]?[^\s'\"<>]{3,}"),
     r"\1=***"),
]
# Literal secrets are loaded at build time from the personal store (NOT committed to git)
def _load_secret_literals():
    lits = set()
    store = os.environ.get("GAIA_PORTAL_KEYS") or (
        r"C:\Users\mokke\AppData\Local\Cursor\AgentStores\cursor_agent_stores\u230150301\files\portal-keys.json")
    try:
        with open(store, encoding="utf-8") as f:
            data = json.load(f)
        def walk(o):
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
            elif isinstance(o, str) and len(o) >= 6:
                lits.add(o)
        walk(data)
    except Exception:
        pass
    # keep only credential-ish literals (avoid redacting common words/IPs)
    return sorted((s for s in lits if len(s) >= 6 and not EMAIL_RE.search(s)
                   and not re.fullmatch(r"[\d.:/ -]+", s)), key=len, reverse=True)

SECRET_LITERALS = _load_secret_literals()

def redact(s):
    if not s:
        return s
    s = str(s)
    for lit in SECRET_LITERALS:
        if lit in s:
            s = s.replace(lit, "***")
    for pat, repl in REDACT_SHAPES:
        s = pat.sub(repl, s)
    return s

def read_jsonl(name):
    p = os.path.join(NEUTRON, name)
    out = []
    if not os.path.exists(p):
        return out
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out

def norm_ts(ts):
    if not ts:
        return ""
    return str(ts).replace("Z", "+00:00")

def clean_addr(a):
    if not a:
        return ""
    a = str(a)
    m = EMAIL_RE.search(a)
    return m.group(0) if m else a.split(">")[0].split("<")[-1].strip()

def is_email(a):
    return bool(EMAIL_RE.search(str(a or "")))

def base_author(a):
    return str(a or "").split("-")[0].split("@")[0].lower()

def subject_of(msg):
    if msg.get("subject"):
        return str(msg["subject"])[:90]
    body = str(msg.get("body") or msg.get("type") or "")
    # first sentence / first 70 chars
    first = re.split(r"[.!?\n]", body, 1)[0].strip()
    return (first[:88] + ("\u2026" if len(first) > 88 else "")) or "(no subject)"

def classify(frm, to, channel, source):
    """return (particle, tier)"""
    frm_l = str(frm).lower()
    if frm_l.startswith("gaia") or "gaia@primals" in frm_l or source == "outbound":
        particle = "proton"
    elif channel == "pony-express" or source == "smtp" or is_email(frm):
        particle = "electron"
    elif base_author(frm) in INTERNAL:
        particle = "neutron"
    elif frm and frm not in ("unknown", "?"):
        particle = "electron"
    else:
        particle = "neutron"
    # tier
    both_agents = base_author(frm) in INTERNAL and base_author(to) in INTERNAL
    human = is_email(frm) and not frm_l.startswith("gaia") or is_email(to)
    if particle == "neutron":
        tier = "silver"
    elif both_agents:
        tier = "platinum"
    else:
        tier = "gold"
    return particle, tier

def route_identity(frm, to, particle):
    addr = (str(frm) + " " + str(to)).lower()
    if "pm.me" in addr or "ecoprimal@pm" in addr:
        return "ecoprimal@pm.me"
    if "primals.eco" in addr or particle == "electron":
        return "gaia@primals.eco"
    return "GAIA@HOME"

def mkmsg(frm, to, ts, body, channel, source, folder):
    body = redact(body)
    particle, tier = classify(frm, to, channel, source)
    identity = route_identity(frm, to, particle)
    mid = hashlib.blake2b((str(ts) + str(frm) + str(body)[:40]).encode(), digest_size=6).hexdigest()
    return {
        "id": mid,
        "ts": norm_ts(ts),
        "from": clean_addr(frm) or "unknown",
        "to": clean_addr(to) or "",
        "subject": redact(subject_of({"subject": None, "body": body})),
        "body": str(body)[:4000],
        "channel": channel,
        "particle": particle,
        "tier": tier,
        "identity": identity,
        "folder": folder,
    }

messages = []

# INBOX — incoming / internal received
for m in read_jsonl("inbox.jsonl"):
    messages.append(mkmsg(m.get("author"), "gaia@primals.eco", m.get("ts"),
                          m.get("body", ""), m.get("channel", "inbox"), "inbound", "Inbox"))

# OUTBOX — Gaia's sends (proton)
for m in read_jsonl("outbox.jsonl"):
    messages.append(mkmsg(m.get("from"), m.get("to"), m.get("ts"),
                          m.get("body", ""), "outbox", "outbound", "Sent"))

# PONY-EXPRESS — external SMTP relay (electron channel)
for m in read_jsonl("pony-express.jsonl"):
    frm = m.get("author") or m.get("from")
    messages.append(mkmsg(frm, m.get("to", ""), m.get("ts"),
                          m.get("body", ""), "pony-express", "smtp", "Inbox"))

# MAIL-LOG — real SMTP delivery receipts (the hard evidence of external mail)
for m in read_jsonl("mail-log.jsonl"):
    frm = m.get("from", "")
    to = m.get("to", "")
    size = m.get("size", "")
    body = f"SMTP delivery · TLS={m.get('tls')} · {size} bytes · blake2b {str(m.get('blake2b',''))[:16]}"
    msg = mkmsg(frm, to, m.get("ts"), body, "smtp", "smtp", "Deliveries")
    msg["subject"] = f"\u2709 {clean_addr(frm)} \u2192 {clean_addr(to)}"
    messages.append(msg)

# PHYSICAL-MAIL — printed to Epson
for m in read_jsonl("physical-mail.jsonl"):
    body = f"Printed to {m.get('printer','printer')} · {m.get('chars','?')} chars · {m.get('result','')}"
    msg = mkmsg("gaia@primals.eco", "EPSON_ET_2400 (paper)", m.get("ts"),
                body, "physical", "outbound", "Physical")
    msg["subject"] = f"\U0001F5A8 {m.get('title','Printed Mail')}"
    messages.append(msg)

# sort newest first
def ts_key(x):
    return x["ts"] or ""
messages.sort(key=ts_key, reverse=True)

# build folder + identity counts
folders = ["Inbox", "Sent", "Deliveries", "Physical"]
identity_bags = {}
for ident in IDENTITIES:
    bag = [m for m in messages if m["identity"] == ident]
    fcounts = {f: len([m for m in bag if m["folder"] == f]) for f in folders}
    identity_bags[ident] = {
        "meta": IDENTITIES[ident],
        "total": len(bag),
        "folders": fcounts,
    }

particle_counts = {p: len([m for m in messages if m["particle"] == p]) for p in ("electron", "proton", "neutron")}
tier_counts = {t: len([m for m in messages if m["tier"] == t]) for t in ("silver", "gold", "platinum")}

bag = {
    "built": datetime.now().isoformat(timespec="seconds"),
    "title": "GAIA MAIL BAG",
    "identities": identity_bags,
    "particles": particle_counts,
    "tiers": tier_counts,
    "total": len(messages),
    "messages": messages,
}

out = os.path.join(HERE, "mailbag.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(bag, f, indent=2)

print("=== GAIA MAIL BAG PACKED ===")
print(f"  total messages: {len(messages)}")
print(f"  particles: e- {particle_counts['electron']}  p+ {particle_counts['proton']}  n0 {particle_counts['neutron']}")
print(f"  tiers: silver {tier_counts['silver']}  gold {tier_counts['gold']}  platinum {tier_counts['platinum']}")
for ident, b in identity_bags.items():
    print(f"  {b['meta']['glyph']} {ident:20s} [{b['meta']['role']:6s}] total {b['total']:3d}  {b['folders']}")
print(f"  -> {out}")
