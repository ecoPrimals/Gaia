#!/usr/bin/env python3
"""The commons in nestgate: put it into one gate's content store, pass it to another, and check both.

  python tools/commons_nest.py put   <sporePrint checkout> [--at http://127.0.0.1:9201]
      Every file the manifest holds goes into that nestgate (content.put); the list of
      path -> content id is published there as one collection (content.publish).
  python tools/commons_nest.py send  --to tcp://HOST:PORT [--at ...]
      Ask the nestgate at --at to pass every content id to the nestgate at --to
      (content.replicate). The gates talk to each other; this script only asks.
  python tools/commons_nest.py pull  --from tcp://HOST:PORT [--at ...]
      The other direction: ask the nestgate at --at to fetch them (content.replicate.pull).
  python tools/commons_nest.py carry --at SOURCE --to DEST --name-from A --name-to B [--family F]
      When the two nestgates cannot talk to each other: this script gets each file from one
      and puts it into the other, and publishes the collection there. The receiving nestgate
      still works out each content id itself, so a changed byte would show. This is NOT
      federation: a third party carries. It is recorded as "carried".
  python tools/commons_nest.py check <sporePrint checkout> --name GATE [--at ...] [--family F]
      Get every file back out of a nestgate and hash it against the manifest.

--at is how this script reaches a nestgate: http://host:port (JSON-RPC over HTTP at /jsonrpc)
or tcp://host:port (one JSON line each way). What each step found is kept in
data/commons/nest.json, by gate name. No address is written to that file: a gate is recorded
by the name given with --name, never by where it answers.
"""
import argparse
import base64
import hashlib
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data" / "commons" / "nest.json"
COLLECTION = "sporeprint-commons"
SOURCE = "https://github.com/ecoPrimals/sporePrint static/commons"


def tidy(reason):
    """A reason as it may be kept: no address, and no path above this repository."""
    reason = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "[address]", str(reason))
    return reason.replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", "").replace("API error: ", "").replace("Internal error: ", "")


class Refused(Exception):
    """The nestgate answered with an error, or did not answer."""


def ask(at, method, params, timeout=120):
    """One JSON-RPC question. Returns the result, or raises Refused with the reason."""
    body = json.dumps({"jsonrpc": "2.0", "id": "1", "method": method, "params": params}).encode()
    try:
        if at.startswith("http://") or at.startswith("https://"):
            req = urllib.request.Request(at.rstrip("/") + "/jsonrpc", data=body, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    text = r.read()
            except urllib.error.HTTPError as e:
                text = e.read()
        elif at.startswith("tcp://"):
            host, port = at[len("tcp://"):].rsplit(":", 1)
            with socket.create_connection((host, int(port)), timeout=10) as s:
                s.settimeout(timeout)
                s.sendall(body + b"\n")
                text = b""
                while not text.endswith(b"\n"):
                    chunk = s.recv(1 << 20)
                    if not chunk:
                        break
                    text += chunk
        else:
            raise Refused("--at must start with http:// or tcp://")
    except OSError as e:
        raise Refused("no answer (%s)" % type(e).__name__) from None
    try:
        answer = json.loads(text)
    except ValueError:
        raise Refused("an answer that is not JSON (%d bytes)" % len(text)) from None
    if "error" in answer:
        raise Refused(str(answer["error"].get("message", answer["error"]))[:300])
    return answer.get("result", {})


def held(checkout):
    manifest = json.loads((checkout / "static" / "commons" / "manifest.json").read_text(encoding="utf-8"))
    return manifest, [b for b in manifest["blobs"] if b["state"] == "held"]


def load():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"collection": COLLECTION, "ids": {}, "gates": {}}


def save(state):
    # an address must never reach this file: it is tracked, and the repository is public
    text = json.dumps(state, ensure_ascii=False, indent=1) + "\n"
    if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b|tcp://|http://", text):
        sys.exit("refusing to write %s: it would carry an address" % STATE.name)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(text, encoding="utf-8", newline="\n")


def put(args):
    checkout = Path(args.checkout).resolve()
    manifest, blobs = held(checkout)
    state = load()
    ids, new, again, failed = {}, 0, 0, []
    family = None
    for b in blobs:
        raw = (checkout / b["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != b["sha256"]:
            if hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() != b["sha256"]:
                failed.append((b["path"], "this copy is not the manifest's bytes"))
                continue
            raw = raw.replace(b"\r\n", b"\n")           # a Windows checkout of a text file outside static/commons
        params = {"data": base64.b64encode(raw).decode(), "source": SOURCE, "pipeline": "commons_nest.put", "stored_by": "commons"}
        if args.family:
            params["family_id"] = args.family
        try:
            r = ask(args.at, "content.put", params)
        except Refused as e:
            failed.append((b["path"], str(e)))
            continue
        ids[b["path"]] = r["hash"]
        family = r.get("family_id", family)
        again += bool(r.get("deduplicated"))
        new += not r.get("deduplicated")
    print("put: %d files asked; %d new in the store, %d were already there, %d failed" % (len(blobs), new, again, len(failed)))
    for path, why in failed[:8]:
        print("   failed: %s (%s)" % (path, why))
    published = None
    if ids:
        params = {"collection": COLLECTION, "manifest": ids}
        if args.family:
            params["family_id"] = args.family
        try:
            r = ask(args.at, "content.publish", params)
            published = r.get("entry_count")
            print("published as the collection %r: %s entries (family %r)" % (COLLECTION, published, r.get("family_id")))
        except Refused as e:
            print("the collection was NOT published: %s" % e)
    state.update({"collection": COLLECTION, "manifest_made": manifest["made"], "family": family, "ids": ids,
                  "put": {"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "asked": len(blobs), "new": new,
                          "already_there": again, "failed": len(failed), "published_entries": published}})
    save(state)
    return 0 if not failed and published else 1


def move(args, method, key, other):
    state = load()
    cids = sorted(set(state["ids"].values()))
    if not cids:
        sys.exit("nothing to pass on: run 'put' first")
    done, skipped, failed, why, total = 0, 0, 0, {}, 0
    for i in range(0, len(cids), 40):                   # a few at a time, so one slow file does not hide the rest
        params = {"cids": cids[i:i + 40], key: other}
        if args.family:
            params["family_id"] = args.family
        try:
            r = ask(args.at, method, params, timeout=600)
        except Refused as e:
            failed += len(cids[i:i + 40])
            why[tidy(e)[:220]] = why.get(tidy(e)[:220], 0) + len(cids[i:i + 40])
            continue
        for item in r.get("replicated", r.get("pulled", [])):
            if item.get("transferred") or item.get("pulled"):
                done += 1
                total += item.get("size", 0)
            elif item.get("skipped"):
                skipped += 1
            else:
                failed += 1
                reason = tidy(item.get("error", "no reason given"))[:220]
                why[reason] = why.get(reason, 0) + 1
    print("%s: %d content ids; %d passed (%d bytes), %d already there, %d failed" % (method, len(cids), done, total, skipped, failed))
    for reason, n in sorted(why.items(), key=lambda kv: -kv[1])[:5]:
        print("   %d x %s" % (n, reason))
    state.setdefault("moves", []).append({"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "how": method, "from": args.name_from,
                                          "to": args.name_to, "ids": len(cids), "passed": done, "bytes": total,
                                          "already_there": skipped, "failed": failed,
                                          "why": list(why)[:3]})
    save(state)
    return 0 if not failed else 1


def carry(args):
    state = load()
    family = args.family or state.get("family")
    ids = state["ids"]
    cids = sorted(set(ids.values()))
    passed, there, failed, total, why = 0, 0, 0, 0, {}
    for cid in cids:
        try:
            if ask(args.to, "content.exists", {"hash": cid, "family_id": family}).get("exists"):
                there += 1
                continue
            got = ask(args.at, "content.get", {"hash": cid, "family_id": family})
            r = ask(args.to, "content.put", {"data": got["data"], "family_id": family, "source": SOURCE,
                                             "pipeline": "commons_nest.carry", "stored_by": "commons"})
            if r.get("hash") != cid:
                raise Refused("the receiver worked out a different content id")
            passed += 1
            total += r.get("size", 0)
        except (Refused, KeyError) as e:
            failed += 1
            why[tidy(e)[:220]] = why.get(tidy(e)[:220], 0) + 1
    published = None
    if not failed:
        try:
            published = ask(args.to, "content.publish", {"collection": COLLECTION, "manifest": ids, "family_id": family}).get("entry_count")
        except Refused as e:
            why["publish: %s" % tidy(e)[:200]] = 1
    print("carried: %d content ids; %d passed (%d bytes), %d already there, %d failed; collection published there: %s" % (
        len(cids), passed, total, there, failed, published if published is not None else "no"))
    for reason, n in sorted(why.items(), key=lambda kv: -kv[1])[:5]:
        print("   %d x %s" % (n, reason))
    state.setdefault("moves", []).append({"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "how": "carried by a script (get, then put)",
                                          "from": args.name_from, "to": args.name_to, "ids": len(cids), "passed": passed,
                                          "bytes": total, "already_there": there, "failed": failed,
                                          "why": list(why)[:3]})
    save(state)
    return 0 if not failed else 1


def check(args):
    checkout = Path(args.checkout).resolve()
    manifest, blobs = held(checkout)
    state = load()
    family = args.family or state.get("family")
    same, differs, missing, unknown = 0, 0, 0, 0
    for b in blobs:
        cid = state["ids"].get(b["path"])
        if not cid:
            unknown += 1
            continue
        try:
            r = ask(args.at, "content.get", {"hash": cid, "family_id": family})
            data = r.get("data") or r.get("content_base64")
        except Refused:
            missing += 1
            continue
        if data is None:                                # a nestgate may answer "not here" without calling it an error
            missing += 1
            continue
        raw = base64.b64decode(data)
        if hashlib.sha256(raw).hexdigest() == b["sha256"]:
            same += 1
        else:
            differs += 1
    try:
        entries = ask(args.at, "content.collections", {"family_id": family}).get("collections", [])
        collection = any((c.get("collection") if isinstance(c, dict) else c) == COLLECTION for c in entries)
    except Refused:
        collection = False
    print("%s (family %r): %d of %d the same as the manifest; %d differ; %d not there; collection listed: %s" % (
        args.name, family, same, len(blobs), differs, missing + unknown, "yes" if collection else "no"))
    state.setdefault("gates", {})[args.name] = {"checked": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "family": family, "of": len(blobs),
                                                "same": same, "differs": differs, "missing": missing + unknown,
                                                "collection": collection}
    save(state)
    return 0 if same == len(blobs) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("put", "send", "pull", "carry", "check"):
        p = sub.add_parser(name)
        if name in ("put", "check"):
            p.add_argument("checkout")
        p.add_argument("--at", default="http://127.0.0.1:9201", help="the nestgate this script talks to")
        p.add_argument("--family", help="content family; default is the nestgate's own")
        if name in ("send", "carry"):
            p.add_argument("--to", required=True, help="where the nestgate at --at should send: tcp://host:port")
        if name == "pull":
            p.add_argument("--from", dest="source", required=True, help="where the nestgate at --at should fetch from")
        if name in ("send", "pull", "carry"):
            p.add_argument("--name-from", required=True, help="gate name of the sender, for the record")
            p.add_argument("--name-to", required=True, help="gate name of the receiver, for the record")
        if name == "check":
            p.add_argument("--name", required=True, help="gate name, for the record")
    args = ap.parse_args()
    if args.cmd == "put":
        return put(args)
    if args.cmd == "send":
        return move(args, "content.replicate", "target", args.to)
    if args.cmd == "pull":
        return move(args, "content.replicate.pull", "source", args.source)
    if args.cmd == "carry":
        return carry(args)
    return check(args)


if __name__ == "__main__":
    sys.exit(main())
