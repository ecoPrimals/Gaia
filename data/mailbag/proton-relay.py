#!/usr/bin/env python3
"""
PROTON RELAY JUMPER - Gaia's mail to and from humans (p+).

AT&T blocks residential outbound :25, so we DO NOT talk to the world's MX
directly. There are two ways out, and this picks the one that is really there:

  bridge    Proton Mail Bridge on THIS machine (127.0.0.1:1025 SMTP, :1143 IMAP).
            Loopback only. The bridge speaks to Proton over its own encrypted
            channel, so this path does not depend on the router or on port 25,
            and the recipient sees Proton's servers, not our address.
            This is the only path that can reach an outside mailbox today.

  neutrino  eastGate's own SMTP (mail.primals.eco). It ACCEPTS mail for our
            domains (primals.eco, nestgate.io) and refuses to relay anything
            else ("550 Relay denied"), so it is a way IN and between gates,
            not a way out to the world.

Flow out:  outbox.jsonl draft (or --to ...)  ->  this relay  ->  bridge  ->  Proton  ->  world
Flow in:   world  ->  Proton  ->  bridge IMAP  ->  --read  ->  data/gut/proton-mail/ (never committed)

Usage:
  python proton-relay.py                 # dry-run: show what WOULD be relayed
  python proton-relay.py --send          # actually relay queued drafts
  python proton-relay.py --test          # handshake both paths, send nothing
  python proton-relay.py --loopback      # one letter to her own tag address, wait for it to come back
  python proton-relay.py --read          # list mail addressed to her (headers only, nothing marked read)
  python proton-relay.py --read --save   # also keep the letters as .eml under data/gut/proton-mail/
  python proton-relay.py --to a@b.c --subject "..." --body "..." [--send]   # one letter, not written to the outbox
  options: --via bridge|neutrino   --days N (how far back --read looks, default 30)

Who she is on the wire:
  Through the bridge the sender must be an address that belongs to the Proton
  account. So letters go out as  "Gaia" <account address>  with Reply-To set to
  the account's +gaia address; answers come back carrying that tag, and --read
  picks them out of the mailbox without touching anything else in it.
  If the account later owns another address (gaia@primals.eco as a Proton
  custom domain, or a second pm.me address), put it in the store as
  proton_bridge.from and she speaks from that instead.

No credentials are stored here. They are read at run time from the personal
store (portal-keys.json -> proton_bridge / neutrino) or from the environment
(PROTON_BRIDGE_USER / PROTON_BRIDGE_PASS, NEUTRINO_USER / NEUTRINO_PASS).
Never hardcode, never commit. Nothing here runs on a timer: a hand runs it.
"""
import os, sys, json, re, ssl, time, socket, hashlib, imaplib, smtplib, email
from email.message import EmailMessage
from email.header import decode_header, make_header
from email.utils import formatdate, make_msgid, parseaddr, formataddr
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
NEUTRON = os.path.abspath(os.path.join(HERE, "..", "neutron"))
OUTBOX = os.path.join(NEUTRON, "outbox.jsonl")
# letters and the sent log hold people's addresses and words: they live in a self-ignored folder
LANDING = os.path.abspath(os.path.join(HERE, "..", "gut", "proton-mail"))
SENTLOG = os.path.join(LANDING, "sent.jsonl")

RELAY_HOST = os.environ.get("NEUTRINO_HOST", "192.168.4.248")
RELAY_PORTS = [587, 465, 25]  # prefer submission, then implicit TLS, then plain
LOCAL_DOMAINS = ("primals.eco", "gaia.primals.eco", "nestgate.io")
STORE = os.environ.get("GAIA_PORTAL_KEYS") or (
    r"C:\Users\mokke\AppData\Local\Cursor\AgentStores\cursor_agent_stores\u230150301\files\portal-keys.json")


def _store():
    try:
        with open(STORE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_relay_auth():
    """Optional Neutrino SMTP auth, read at runtime - never committed."""
    user, pw = os.environ.get("NEUTRINO_USER"), os.environ.get("NEUTRINO_PASS")
    if user and pw:
        return user, pw
    n = _store().get("neutrino") or {}
    return (n["user"], n["pass"]) if n.get("user") and n.get("pass") else (None, None)


def load_bridge():
    """The bridge login, or None. Values stay in memory."""
    b = dict(_store().get("proton_bridge") or {})
    if os.environ.get("PROTON_BRIDGE_USER") and os.environ.get("PROTON_BRIDGE_PASS"):
        b.update(user=os.environ["PROTON_BRIDGE_USER"], **{"pass": os.environ["PROTON_BRIDGE_PASS"]})
    if not (b.get("user") and b.get("pass")):
        return None
    b.setdefault("host", "127.0.0.1"); b.setdefault("smtp_port", 1025); b.setdefault("imap_port", 1143)
    local, _, dom = b["user"].partition("@")
    b["tag_addr"] = "%s+%s@%s" % (local, b.get("tag", "gaia"), dom)   # where answers come back
    b["from_addr"] = b.get("from") or b["user"]
    return b


def _loose_tls():
    # loopback / LAN only: the bridge and Neutrino present their own certificates
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    return ctx


def bridge_up(b):
    if not b:
        return False
    try:
        with socket.create_connection((b["host"], int(b["smtp_port"])), timeout=2):
            return True
    except Exception:
        return False


def mask(addr):
    """a***@domain - enough to recognise, not enough to harvest from a terminal log."""
    name, a = parseaddr(addr)
    if "@" not in a:
        return addr
    l, d = a.split("@", 1)
    return (l[:1] + "***@" + d)


# ---------- drafts ----------

def _draft_id(m):
    core = {k: m.get(k) for k in ("ts", "from", "to", "subject", "body")}
    return hashlib.blake2b(json.dumps(core, sort_keys=True, ensure_ascii=False).encode("utf-8"), digest_size=8).hexdigest()


def already_sent():
    ids = set()
    if os.path.exists(SENTLOG):
        for line in open(SENTLOG, encoding="utf-8", errors="replace"):
            try:
                ids.add(json.loads(line).get("draft"))
            except Exception:
                pass
    return ids


def read_drafts():
    """A draft is an outbox line with a 'to' that is an email address, no 'relayed' flag, and not in the sent log."""
    drafts, done = [], already_sent()
    if not os.path.exists(OUTBOX):
        return drafts
    with open(OUTBOX, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                m = json.loads(line)
            except Exception:
                continue
            to = str(m.get("to", ""))
            if "@" in to and "." in to.split("@")[-1] and not m.get("relayed"):
                m["_line"], m["_id"] = i, _draft_id(m)
                if m["_id"] not in done:      # the outbox is append-only: without this every run would send the same letters again
                    drafts.append(m)
    return drafts


def build_message(d, b=None):
    msg = EmailMessage()
    asked = d.get("from", "gaia@primals.eco")
    if b:   # through the bridge the sender has to be an address the Proton account owns
        msg["From"] = formataddr(("Gaia", b["from_addr"]))
        msg["Reply-To"] = formataddr(("Gaia", b["tag_addr"] if b["from_addr"] == b["user"] else b["from_addr"]))
        dom = b["from_addr"].split("@")[-1]
    else:
        msg["From"] = asked
        dom = "primals.eco"
    msg["To"] = d["to"]
    msg["Subject"] = d.get("subject", "(no subject)")
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=dom)
    msg["X-Gaia-Particle"] = "proton"
    msg.set_content(d.get("body", ""))
    return msg


def _log_sent(rec):
    _landing()
    with open(SENTLOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _landing():
    os.makedirs(LANDING, exist_ok=True)
    gi = os.path.join(LANDING, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("# letters and addresses stay on this machine\n*\n")


# ---------- sending ----------

class Refused(Exception):
    """Proton took the letter from the bridge and said no. Not a fault to retry around."""


def _why(e):
    """The part of a bridge/Proton error a person can read (no API paths, no ids)."""
    s = e.smtp_error.decode("utf-8", "replace") if isinstance(getattr(e, "smtp_error", None), bytes) else str(e)
    s = re.sub(r"\b(POST|GET|PUT) https?://\S+:?\s*", "", s)
    s = re.sub(r"^.*?failed to send draft:\s*\d*\s*", "", s)
    return s.strip()[:220]


def send_bridge(b, msg):
    srv = smtplib.SMTP(b["host"], int(b["smtp_port"]), timeout=30)
    try:
        srv.ehlo(); srv.starttls(context=_loose_tls()); srv.ehlo()
        srv.login(b["user"], b["pass"])
        srv.send_message(msg, from_addr=b["from_addr"])
    except (smtplib.SMTPDataError, smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as e:
        _sweep_unsent(b, msg["Subject"])
        raise Refused(_why(e))
    finally:
        try:
            srv.quit()
        except Exception:
            pass
    return "bridge"


def _sweep_unsent(b, subject):
    """A refused send leaves the letter sitting in Drafts. Take back that one letter (exact subject), nothing else."""
    try:
        m = _imap(b)
        m.select("Drafts")
        typ, d = m.search(None, "SUBJECT", '"%s"' % str(subject).replace('"', ""))
        for n in (d[0].split() if typ == "OK" and d and d[0] else []):
            typ, h = m.fetch(n, "(BODY.PEEK[HEADER.FIELDS (SUBJECT X-GAIA-PARTICLE)])")
            hd = email.message_from_bytes(h[0][1])
            if _hdr(hd.get("Subject")) == str(subject):
                m.store(n, "+FLAGS", "\\Deleted")
        m.expunge(); m.close(); m.logout()
    except Exception:
        pass


def send_neutrino(msg):
    user, pw = load_relay_auth()
    last = "no port answered"
    for port in RELAY_PORTS:
        try:
            if port == 465:
                srv = smtplib.SMTP_SSL(RELAY_HOST, port, timeout=10, context=_loose_tls())
            else:
                srv = smtplib.SMTP(RELAY_HOST, port, timeout=10)
                srv.ehlo()
                if srv.has_extn("starttls"):
                    srv.starttls(context=_loose_tls()); srv.ehlo()
            if user and pw and srv.has_extn("auth"):
                srv.login(user, pw)
            srv.send_message(msg)
            srv.quit()
            return "neutrino:%d" % port
        except Exception as e:
            last = str(e).split("\n")[0]
    raise RuntimeError(last)


def pick_path(to, via, b):
    """bridge for the outside world; neutrino only for our own domains (it refuses everything else)."""
    ours = to.split("@")[-1].lower() in LOCAL_DOMAINS
    if via in ("bridge", "neutrino"):
        return via
    if bridge_up(b) and not ours:
        return "bridge"
    return "neutrino" if ours else ("bridge" if b else "neutrino")


def relay(drafts, do_send, via=None):
    if not drafts:
        print("  nothing queued (no unsent draft addressed to an email address).")
        return 0
    b = load_bridge()
    n = 0
    for d in drafts:
        path = pick_path(d["to"], via, b)
        tag = "%s :: %s" % (mask(d["to"]), d.get("subject", "(no subject)")[:50])
        if path == "neutrino" and d["to"].split("@")[-1].lower() not in LOCAL_DOMAINS:
            print("  [no path] %s  (neutrino refuses outside domains; the bridge is not up on this machine)" % tag)
            continue
        if not do_send:
            print("  [dry-run] would relay via %-8s %s" % (path, tag))
            continue
        try:
            msg = build_message(d, b if path == "bridge" else None)
            how = send_bridge(b, msg) if path == "bridge" else send_neutrino(msg)
            _log_sent({"ts": datetime.now(timezone.utc).isoformat(), "draft": d.get("_id"), "to": d["to"],
                       "subject": d.get("subject", ""), "via": how, "message_id": msg["Message-ID"]})
            print("  [SENT %s]  %s" % (how, tag)); n += 1
        except Refused as e:
            print("  [REFUSED by Proton] %s\n      %s" % (tag, e))
            print("      stopping here: the rest of the queue would get the same answer, and repeating it helps nobody.")
            break
        except Exception as e:
            print("  [FAIL] %s  (%s)" % (tag, str(e).split("\n")[0][:120]))
    if n:
        print("  logged %d sent letter(s) -> %s" % (n, os.path.relpath(SENTLOG, os.path.join(HERE, "..", ".."))))
    return n


# ---------- reading ----------

def _imap(b):
    m = imaplib.IMAP4(b["host"], int(b["imap_port"]), timeout=30)
    m.starttls(ssl_context=_loose_tls())
    m.login(b["user"], b["pass"])
    return m


def _hdr(v):
    try:
        return str(make_header(decode_header(v or "")))
    except Exception:
        return v or ""


def find_hers(m, b, days=30, subject=None):
    """Message numbers in INBOX addressed to her. Read-only select: nothing is marked, moved or deleted."""
    m.select("INBOX", readonly=True)
    since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    found = set()
    targets = [b["tag_addr"], "gaia@primals.eco"] + ([b["from_addr"]] if b["from_addr"] != b["user"] else [])
    for addr in targets:
        for field in ("TO", "CC"):
            crit = ["SINCE", since, field, '"%s"' % addr] + (["SUBJECT", '"%s"' % subject] if subject else [])
            typ, data = m.search(None, *crit)
            if typ == "OK" and data and data[0]:
                found |= set(data[0].split())
    return sorted(found, key=int)


def read_hers(b, days=30, save=False):
    m = _imap(b)
    nums = find_hers(m, b, days)
    print("  addressed to her in the last %d days: %d   (tag address %s)" % (days, len(nums), mask(b["tag_addr"])))
    if save:
        _landing()
    kept = 0
    for n in nums:
        typ, data = m.fetch(n, "(BODY.PEEK[])" if save else "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT MESSAGE-ID)])")
        raw = data[0][1] if data and isinstance(data[0], tuple) else b""
        h = email.message_from_bytes(raw)
        print("   %-26s %-22s %s" % (_hdr(h.get("Date"))[:25], mask(_hdr(h.get("From")))[:22], _hdr(h.get("Subject"))[:70]))
        if save:
            name = hashlib.blake2b((h.get("Message-ID") or raw[:200].decode("latin1")).encode("utf-8", "replace"), digest_size=8).hexdigest() + ".eml"
            p = os.path.join(LANDING, name)
            if not os.path.exists(p):
                with open(p, "wb") as f:
                    f.write(raw)
                kept += 1
    m.logout()
    if save:
        print("  kept %d new letter(s) in %s (self-ignored, never committed)" % (kept, os.path.relpath(LANDING, os.path.join(HERE, "..", ".."))))


def loopback(b, wait=90):
    """Can she send and hear the answer? One letter to her own tag address, then watch the mailbox for it."""
    token = "gaia-loop-" + hashlib.blake2b(os.urandom(8), digest_size=4).hexdigest()
    d = {"to": b["tag_addr"], "subject": "Gaia loopback %s" % token,
         "body": "This is Gaia, checking her own voice and ear.\n\n"
                 "Sent from northGate through the Proton Mail Bridge to her own tag address.\n"
                 "If this letter is in the mailbox, she can send and she can hear the answer.\n\n"
                 "token: %s\n" % token}
    msg = build_message(d, b)
    t0 = time.time()
    try:
        send_bridge(b, msg)
    except Refused as e:
        print("  REFUSED by Proton: %s" % e)
        print("  the bridge and the login are fine; the account itself is not being let out. Nothing was sent, nothing left in Drafts.")
        return False
    print("  sent    %s -> %s  (%.1fs)" % (mask(b["from_addr"]), mask(b["tag_addr"]), time.time() - t0))
    _log_sent({"ts": datetime.now(timezone.utc).isoformat(), "draft": None, "to": b["tag_addr"], "subject": d["subject"],
               "via": "bridge", "message_id": msg["Message-ID"], "loopback": True})
    m = _imap(b)
    while time.time() - t0 < wait:
        nums = find_hers(m, b, days=2, subject=token)
        if nums:
            typ, data = m.fetch(nums[-1], "(BODY.PEEK[HEADER.FIELDS (FROM TO REPLY-TO SUBJECT)])")
            h = email.message_from_bytes(data[0][1])
            print("  heard   it came back to INBOX after %.1fs" % (time.time() - t0))
            print("          From: %s | To: %s | Reply-To: %s" % (
                "%s <%s>" % (parseaddr(h.get("From"))[0], mask(h.get("From"))), mask(h.get("To") or ""), mask(h.get("Reply-To") or "(none)")))
            m.logout()
            return True
        time.sleep(4)
    m.logout()
    print("  not seen in INBOX within %ds (sent, but the way back is unproven - look in the mailbox)" % wait)
    return False


def test_paths():
    b = load_bridge()
    print("  bridge   %s" % ("no login in the store" if not b else ("127.0.0.1:%s up" % b["smtp_port"] if bridge_up(b) else "login stored, but nothing listening on this machine")))
    if b and bridge_up(b):
        try:
            s = smtplib.SMTP(b["host"], int(b["smtp_port"]), timeout=15); s.ehlo(); s.starttls(context=_loose_tls()); s.ehlo()
            s.login(b["user"], b["pass"]); s.quit(); print("           smtp login ok  (as %s)" % mask(b["from_addr"]))
            m = _imap(b); typ, d = m.status("INBOX", "(MESSAGES UNSEEN)"); m.logout(); print("           imap login ok")
        except Exception as e:
            print("           refused: %s" % str(e).split("\n")[0][:100])
    print("  neutrino %s (accepts %s only)" % (RELAY_HOST, ", ".join(LOCAL_DOMAINS)))
    for port in RELAY_PORTS:
        try:
            with socket.create_connection((RELAY_HOST, port), timeout=4) as s:
                banner = "(tls)" if port == 465 else s.recv(256).decode(errors="replace").strip()
            print("           :%d  %s" % (port, banner))
        except Exception as e:
            print("           :%d  unreachable (%s)" % (port, str(e).split(":")[0]))


def _opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args):
            return args[i + 1]
    return default


def main():
    args = sys.argv[1:]
    via = _opt(args, "--via")
    print("=== PROTON RELAY JUMPER ===")
    if "--test" in args:
        test_paths(); return
    b = load_bridge()
    if "--loopback" in args or "--read" in args:
        if not bridge_up(b):
            print("  the bridge is not up on this machine (or no login in the store) - nothing to do"); sys.exit(1)
        if "--loopback" in args:
            sys.exit(0 if loopback(b) else 1)
        read_hers(b, days=int(_opt(args, "--days", "30")), save="--save" in args); return
    if "--to" in args:
        d = {"to": _opt(args, "--to"), "subject": _opt(args, "--subject", "(no subject)"), "body": _opt(args, "--body", ""),
             "ts": datetime.now(timezone.utc).isoformat()}
        bf = _opt(args, "--body-file")
        if bf:
            d["body"] = open(bf, encoding="utf-8").read()
        d["_id"] = _draft_id(d)
        drafts = [d]
    else:
        drafts = read_drafts()
    print("  queued: %d" % len(drafts))
    relay(drafts, do_send="--send" in args, via=via)
    if "--send" not in args and drafts:
        print("  (dry-run - run again with --send to actually relay)")


if __name__ == "__main__":
    main()
