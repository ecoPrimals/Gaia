"""Append one note to the tracked neutron inbox, keeping the file's own line ends.
usage: neutron_note.py <repo> <author> <body-file>"""
import json, os, sys, time

repo, author, body_file = sys.argv[1], sys.argv[2], sys.argv[3]
body = " ".join(open(body_file, encoding="utf-8").read().split())
inbox = os.path.join(repo, "data", "neutron", "inbox.jsonl")
raw = open(inbox, "rb").read()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
if body.encode("utf-8") in raw:
    print("already in the inbox")
    raise SystemExit
line = json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "author": author, "body": body, "channel": "inbox"}, ensure_ascii=False)
json.loads(line)
with open(inbox, "ab") as f:
    if raw and not raw.endswith(b"\n"):
        f.write(eol)
    f.write(line.encode("utf-8") + eol)
print("inbox: %d -> %d lines; line ends %s; note %d chars" % (raw.count(b"\n"), raw.count(b"\n") + 1, "CRLF" if eol == b"\r\n" else "LF", len(body)))
