#!/usr/bin/env python3
"""Generate mail-api.json from all mail sources."""
import json, os, re, email as email_mod, hashlib
from email.utils import parsedate_to_datetime

MAIL_ROOT = "/opt/Gaia/mail"
PONY_FILE = "/opt/Gaia/data/neutron/pony-express.jsonl"
INBOX_FILE = "/opt/Gaia/data/neutron/inbox.jsonl"
OUTPUT = "/opt/Gaia/data/mail-api.json"

messages = []

# 1. SMTP emails
if os.path.isdir(MAIL_ROOT):
    for box_dir in os.listdir(MAIL_ROOT):
        box_path = os.path.join(MAIL_ROOT, box_dir)
        if not os.path.isdir(box_path): continue
        mailbox = box_dir.replace("_at_", "@")
        for sub in ["new", "cur"]:
            sub_path = os.path.join(box_path, sub)
            if not os.path.isdir(sub_path): continue
            for fname in os.listdir(sub_path):
                try:
                    with open(os.path.join(sub_path, fname), "r", errors="replace") as f:
                        raw = f.read()
                    fr = re.search(r'^From:\s*(.+)$', raw, re.M|re.I)
                    subj = re.search(r'^Subject:\s*(.+)$', raw, re.M|re.I)
                    dt = re.search(r'^Date:\s*(.+)$', raw, re.M|re.I)
                    ts = ""
                    if dt:
                        try: ts = parsedate_to_datetime(dt.group(1)).isoformat()
                        except: ts = dt.group(1)
                    messages.append({
                        "ts": ts, "train": "smtp",
                        "from": fr.group(1).strip() if fr else "unknown",
                        "subject": subj.group(1).strip() if subj else "(no subject)",
                        "body": "", "mailbox": mailbox
                    })
                except: pass

# 2. Pony express
if os.path.isfile(PONY_FILE):
    with open(PONY_FILE) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                if d.get("train") == "smtp": continue  # avoid duplicates
                messages.append({
                    "ts": d.get("ts",""), "train": "pony",
                    "from": d.get("author","?"), "subject": d.get("subject",""),
                    "body": str(d.get("body",""))[:300]
                })
            except: pass

# 3. Neutron inbox
if os.path.isfile(INBOX_FILE):
    with open(INBOX_FILE) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                messages.append({
                    "ts": d.get("ts",""), "train": "neutron",
                    "from": d.get("author","?"), "subject": "",
                    "body": str(d.get("body",""))[:300]
                })
            except: pass

messages.sort(key=lambda x: x.get("ts",""), reverse=True)

with open(OUTPUT, "w") as f:
    json.dump({"messages": messages[:100], "total": len(messages)}, f)

print(f"✅ mail-api.json: {len(messages)} messages")
