#!/usr/bin/env python3
"""Gaia self-enrollment — check mail, read codes, report identity status."""

import json, os, glob, re, time, urllib.request

MAIL_DIR = "mail/gaia_at_primals.eco/new"
EASTGATE = "192.168.4.244"

def check_mail():
    """Read all emails in Maildir and extract verification codes."""
    emails = []
    for f in sorted(glob.glob(os.path.join(MAIL_DIR, "*"))):
        with open(f, "r", errors="ignore") as fh:
            content = fh.read()
        
        # Extract headers
        subj = re.search(r"Subject:\s*(.*)", content)
        frm = re.search(r"From:\s*(.*)", content)
        to = re.search(r"To:\s*(.*)", content)
        date = re.search(r"Date:\s*(.*)", content)
        
        # Extract verification codes
        codes = re.findall(r"\b(\d{6})\b.*verification", content, re.IGNORECASE)
        if not codes:
            codes = re.findall(r"verification.*?\b(\d{6})\b", content, re.IGNORECASE)
        
        emails.append({
            "file": os.path.basename(f),
            "subject": subj.group(1).strip() if subj else "",
            "from": frm.group(1).strip() if frm else "",
            "to": to.group(1).strip() if to else "",
            "date": date.group(1).strip() if date else "",
            "codes": codes,
        })
    return emails

def check_smtp():
    """Check if Neutrino SMTP is alive."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((EASTGATE, 25))
        banner = s.recv(256).decode().strip()
        s.close()
        return banner
    except:
        return "OFFLINE"

def identity_status():
    """Report Gaia's identity status across services."""
    return {
        "email": {
            "address": "gaia@primals.eco",
            "smtp": check_smtp(),
            "maildir_count": len(glob.glob(os.path.join(MAIL_DIR, "*"))),
        },
        "github": {
            "status": "NOT ENROLLED",
            "action": "signup at github.com/signup with gaia@primals.eco",
            "human_needed": "CAPTCHA verification",
        },
        "forgejo": {
            "status": "USER EXISTS BUT INACTIVE",
            "user": "gaia",
            "email": "ops@primals.eco", 
            "action": "need admin to activate OR Kevin pokes eastGate",
        },
        "reddit": {
            "status": "CODES RECEIVED",
            "codes": ["844067", "092073", "109825"],
            "action": "complete signup with latest code",
        },
        "apple": {
            "status": "VERIFICATION EMAILS RECEIVED",
            "count": 4,
            "action": "enter verification code in Apple Account",
        },
        "steam": {
            "status": "NOT ENROLLED",
            "action": "create Steam account for Gaia, add to Family",
        },
    }

if __name__ == "__main__":
    print("=== GAIA IDENTITY STATUS ===\n")
    
    status = identity_status()
    print(json.dumps(status, indent=2))
    
    print("\n=== MAILBOX ===\n")
    for e in check_mail():
        print(f"  {e['date'] or '?'}")
        print(f"    FROM: {e['from']}")
        print(f"    SUBJ: {e['subject']}")
        if e['codes']:
            print(f"    CODES: {', '.join(e['codes'])}")
        print()
