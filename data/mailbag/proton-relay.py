#!/usr/bin/env python3
"""
PROTON RELAY JUMPER — Gaia's outgoing mail to humans (p+).

AT&T blocks residential outbound :25, so we DO NOT talk to the world's MX
directly. Instead we jump through eastGate's own Neutrino SMTP relay
(220 mail.primals.eco ESMTP Gaia Neutrino). Neutrino is the sovereign
smarthost — it decides the real path out (Tor .onion :25 OR the ProtonMail
bridge for ecoprimal@pm.me). We just hand the proton to our own body.

Flow:
  outbox.jsonl draft  ->  this relay  ->  eastGate Neutrino :587  ->  world
  (nothing seeps out except through our own gate — water lock honored)

Usage:
  python proton-relay.py            # dry-run: show what WOULD be relayed
  python proton-relay.py --send     # actually relay queued drafts
  python proton-relay.py --test     # just handshake the relay, no mail

No credentials are stored here. If the relay needs auth, it is read at
run time from the personal store (portal-keys.json -> neutrino) or the
env var NEUTRINO_PASS. Never hardcode, never commit.
"""
import os, sys, json, smtplib, ssl, socket
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
NEUTRON = os.path.abspath(os.path.join(HERE, "..", "neutron"))
OUTBOX = os.path.join(NEUTRON, "outbox.jsonl")
SENTLOG = os.path.join(NEUTRON, "proton-sent.jsonl")

RELAY_HOST = os.environ.get("NEUTRINO_HOST", "192.168.4.248")
RELAY_PORTS = [587, 465, 25]  # prefer submission, then implicit TLS, then plain
VALID_FROM = {"gaia@primals.eco", "GAIA@HOME", "ecoprimal@pm.me"}

def load_relay_auth():
    """Optional SMTP auth, read at runtime — never committed."""
    user = os.environ.get("NEUTRINO_USER")
    pw = os.environ.get("NEUTRINO_PASS")
    if user and pw:
        return user, pw
    store = os.environ.get("GAIA_PORTAL_KEYS") or (
        r"C:\Users\mokke\AppData\Local\Cursor\AgentStores\cursor_agent_stores\u230150301\files\portal-keys.json")
    try:
        with open(store, encoding="utf-8") as f:
            d = json.load(f)
        n = d.get("neutrino") or {}
        if n.get("user") and n.get("pass"):
            return n["user"], n["pass"]
    except Exception:
        pass
    return None, None

def read_drafts():
    """A draft is an outbox line with a 'to' that is an email address and no 'relayed' flag."""
    drafts = []
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
                m["_line"] = i
                drafts.append(m)
    return drafts

def test_relay():
    for port in RELAY_PORTS:
        try:
            with socket.create_connection((RELAY_HOST, port), timeout=4) as s:
                banner = s.recv(256).decode(errors="replace").strip()
            print(f"  :{port}  {banner}")
        except Exception as e:
            print(f"  :{port}  unreachable ({str(e).split(':')[0]})")

def build_message(d):
    msg = EmailMessage()
    msg["From"] = d.get("from", "gaia@primals.eco")
    msg["To"] = d["to"]
    msg["Subject"] = d.get("subject", "(no subject)")
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="primals.eco")
    msg["X-Gaia-Particle"] = "proton"
    msg.set_content(d.get("body", ""))
    return msg

def relay(drafts, do_send):
    if not drafts:
        print("  outbox has no queued proton drafts (nothing addressed to a human email).")
        return
    user, pw = load_relay_auth()
    sent = []
    for d in drafts:
        frm = d.get("from", "gaia@primals.eco")
        tag = f"{frm} -> {d['to']} :: {d.get('subject','(no subject)')[:50]}"
        if not do_send:
            print(f"  [dry-run] would relay  {tag}")
            continue
        msg = build_message(d)
        ok = False
        for port in RELAY_PORTS:
            try:
                if port == 465:
                    srv = smtplib.SMTP_SSL(RELAY_HOST, port, timeout=10,
                                           context=ssl.create_default_context())
                else:
                    srv = smtplib.SMTP(RELAY_HOST, port, timeout=10)
                    srv.ehlo()
                    if srv.has_extn("starttls"):
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE  # sovereign cert on the LAN
                        srv.starttls(context=ctx)
                        srv.ehlo()
                if user and pw and srv.has_extn("auth"):
                    srv.login(user, pw)
                srv.send_message(msg)
                srv.quit()
                print(f"  [SENT :{port}]  {tag}")
                sent.append({"ts": datetime.now(timezone.utc).isoformat(),
                             "from": frm, "to": d["to"], "subject": d.get("subject", ""),
                             "port": port, "relay": RELAY_HOST})
                ok = True
                break
            except Exception as e:
                last = str(e).split("\n")[0]
                continue
        if not ok:
            print(f"  [FAIL] {tag}  ({last})")
    if sent:
        with open(SENTLOG, "a", encoding="utf-8") as f:
            for s in sent:
                f.write(json.dumps(s) + "\n")
        print(f"  logged {len(sent)} relayed proton(s) -> {SENTLOG}")

def main():
    args = set(sys.argv[1:])
    print("=== PROTON RELAY JUMPER ===")
    print(f"  relay smarthost: {RELAY_HOST} (eastGate Neutrino)")
    if "--test" in args:
        print("  handshake:")
        test_relay()
        return
    drafts = read_drafts()
    print(f"  queued drafts: {len(drafts)}")
    relay(drafts, do_send="--send" in args)
    if "--send" not in args and drafts:
        print("  (dry-run — re-run with --send to actually relay)")

if __name__ == "__main__":
    main()
