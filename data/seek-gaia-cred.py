#!/usr/bin/env python3
"""
SEEK THE GAIA CREDENTIAL — find every stored gaia/Forgejo credential,
test each against the LIVE Forgejo (.4.248:3000), report WHICH works.
Never prints the secret itself — only its source, length, fingerprint,
and whether it authenticates.
"""
import subprocess, re, json, os, hashlib, base64, urllib.request, urllib.error

LIVE = "http://192.168.4.248:3000"
found = {}  # fingerprint -> {user, source, secret}

def fp(s):
    return hashlib.blake2b(s.encode(), digest_size=4).hexdigest()

# 1. git remotes (embedded user:pass)
try:
    out = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True).stdout
    for m in re.finditer(r"http://([^:@/]+):([^@/]+)@([\d.]+):3000", out):
        user, secret, host = m.group(1), m.group(2), m.group(3)
        found.setdefault(fp(secret), {"user": user, "secret": secret, "sources": set()})["sources"].add(f"git-remote@{host}")
except Exception as e:
    print("  git remotes:", e)

# 2. git credential store files
for path in [os.path.expanduser("~/.git-credentials"),
             os.path.expanduser("~/.config/git/credentials")]:
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = re.search(r"http://([^:@/]+):([^@/]+)@", line)
                if m:
                    found.setdefault(fp(m.group(2)), {"user": m.group(1), "secret": m.group(2), "sources": set()})["sources"].add("git-credentials")

# 3. personal store portal-keys.json
store = r"C:\Users\mokke\AppData\Local\Cursor\AgentStores\cursor_agent_stores\u230150301\files\portal-keys.json"
if os.path.exists(store):
    try:
        with open(store, encoding="utf-8") as f:
            data = json.load(f)
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, path + "/" + k)
            elif isinstance(o, str) and 6 <= len(o) <= 80 and ("forge" in path.lower() or "gaia" in path.lower() or "pass" in path.lower() or "token" in path.lower()):
                found.setdefault(fp(o), {"user": "?", "secret": o, "sources": set()})["sources"].add("personal-store" + path)
        walk(data)
    except Exception as e:
        print("  personal store:", e)

print("=== CANDIDATES FOUND (secrets never shown) ===")
if not found:
    print("  none")
cands = list(found.items())
for i, (f, info) in enumerate(cands):
    kind = "token" if len(info["secret"]) >= 32 and re.fullmatch(r"[0-9a-f]+", info["secret"]) else "password"
    print(f"  [{i}] user={info['user']:8s} kind={kind:8s} len={len(info['secret']):2d} fp={f}  src={sorted(info['sources'])}")

# 4. test each against live Forgejo
print(f"\n=== TESTING against LIVE Forgejo {LIVE} ===")
def test(user, secret):
    # try as basic-auth password AND as token
    results = []
    # basic auth
    try:
        req = urllib.request.Request(LIVE + "/api/v1/user")
        tok = base64.b64encode(f"{user}:{secret}".encode()).decode()
        req.add_header("Authorization", "Basic " + tok)
        with urllib.request.urlopen(req, timeout=6) as r:
            body = json.loads(r.read())
            results.append(("basic", True, body.get("login", "?")))
    except urllib.error.HTTPError as e:
        results.append(("basic", False, e.code))
    except Exception as e:
        results.append(("basic", False, str(e).split(":")[0]))
    # token header
    try:
        req = urllib.request.Request(LIVE + "/api/v1/user")
        req.add_header("Authorization", "token " + secret)
        with urllib.request.urlopen(req, timeout=6) as r:
            body = json.loads(r.read())
            results.append(("token", True, body.get("login", "?")))
    except urllib.error.HTTPError as e:
        results.append(("token", False, e.code))
    except Exception as e:
        results.append(("token", False, str(e).split(":")[0]))
    return results

any_ok = False
for i, (f, info) in enumerate(cands):
    for user in {info["user"], "gaia", "ecoPrimal"}:
        if user == "?":
            continue
        for mode, ok, detail in test(user, info["secret"]):
            if ok:
                print(f"  [{i}] WORKS  user={user} via {mode}  -> logged in as '{detail}'  (fp={f})")
                any_ok = True
if not any_ok:
    print("  NONE of the stored credentials authenticate against the live Forgejo.")
    print("  -> the credential rotated when eastGate was reborn. A fresh token is needed.")
