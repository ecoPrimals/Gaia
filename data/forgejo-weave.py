"""forgejo-weave.py — Pull old Forgejo archives, weave into the new DAG."""
import urllib.request
import json

BASE = "http://192.168.4.248:3000"

def api(path):
    try:
        req = urllib.request.Request(f"{BASE}{path}", headers={"User-Agent": "Gaia-Weave"})
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

print("=" * 70)
print("  FORGEJO WEAVE — old archives into the new DAG")
print("=" * 70)

# Full repo list
print("\n--- ALL REPOS (full catalog) ---")
all_repos = []
page = 1
while True:
    data = api(f"/api/v1/repos/search?limit=50&page={page}")
    if "error" in data or not data.get("data"):
        break
    all_repos.extend(data["data"])
    if len(data["data"]) < 50:
        break
    page += 1

print(f"  Total repos: {len(all_repos)}")

# Organize by org + identify archive/data repos
by_org = {}
archives = []
for r in all_repos:
    org = r["full_name"].split("/")[0]
    by_org.setdefault(org, []).append(r["name"])
    name_low = r["name"].lower()
    desc_low = (r.get("description") or "").lower()
    # Identify archive/memory/data repos
    if any(k in name_low or k in desc_low for k in
           ["data", "memory", "archive", "state", "gut", "forgejo", "reagent", "fossil", "record", "seed"]):
        archives.append({
            "name": r["full_name"],
            "desc": r.get("description", ""),
            "size": r.get("size", 0),
            "updated": r.get("updated_at", ""),
        })

print(f"\n--- BY ORG ---")
for org, repos in sorted(by_org.items()):
    print(f"  {org}: {len(repos)} repos")
    print(f"    {', '.join(repos[:8])}{'...' if len(repos) > 8 else ''}")

print(f"\n--- ARCHIVE / MEMORY / DATA REPOS (to weave) ---")
for a in sorted(archives, key=lambda x: -x["size"]):
    size_mb = a["size"] / 1024 if a["size"] else 0
    print(f"  {a['name']:40s} {size_mb:8.1f}MB  {a['desc'][:40]}")

# Look at the main Gaia repo structure
print(f"\n--- GAIA REPO CONTENTS (root tree) ---")
tree = api("/api/v1/repos/gaia/Gaia/contents")
if isinstance(tree, list):
    for item in tree[:30]:
        print(f"  [{item.get('type', '?'):4s}] {item.get('name', '?')}")
else:
    print(f"  {tree}")

# Check ecoPrimals repo (the big one — 3.6M lines)
print(f"\n--- ecoPrimals REPO (3.6M lines, 17 primals) ---")
eco = api("/api/v1/repos/gaia/ecoPrimals")
if "error" not in eco:
    print(f"  Size: {eco.get('size', 0)/1024:.1f}MB")
    print(f"  Default branch: {eco.get('default_branch', '?')}")
    print(f"  Updated: {eco.get('updated_at', '?')}")

# Recent commits across Gaia repo = the weave history
print(f"\n--- RECENT GAIA COMMITS (the weave) ---")
commits = api("/api/v1/repos/gaia/Gaia/commits?limit=10")
if isinstance(commits, list):
    for c in commits[:10]:
        msg = c.get("commit", {}).get("message", "").split("\n")[0][:60]
        author = c.get("commit", {}).get("author", {}).get("name", "?")
        date = c.get("commit", {}).get("author", {}).get("date", "")[:10]
        print(f"  [{date}] {author:15s} {msg}")

# Weave summary
print(f"\n{'=' * 70}")
print("  WEAVE PLAN")
print(f"{'=' * 70}")
print(f"""
  OLD ARCHIVES ({len(archives)} repos) → NEW DAG WEAVE:
  
  The repos ARE the branches. The LAN is the root.
  Old Forgejo memory ({sum(a['size'] for a in archives)/1024:.0f}MB) weaves back through:
  
    repos (branches) → Forgejo :3000 (trunk) → eastGate (brain)
                     → MikroTik SFP+2 10G → northGate (heart)
                     → LAN root (anchor)
  
  To mix old into new weave:
    1. Press Corps reads BOTH recent JSONL + old Forgejo commit history
    2. organism-tree.json links repos → services → backbone → root
    3. The mail atom (electron/proton/neutron) tags historical messages too
""")

# Save the weave catalog
weave = {
    "repos_total": len(all_repos),
    "by_org": by_org,
    "archives": archives,
    "orgs": list(by_org.keys()),
}
with open("c:/Users/mokke/Desktop/Gaia/data/forgejo-weave.json", "w") as f:
    json.dump(weave, f, indent=2)
print(f"  Saved weave catalog to data/forgejo-weave.json")
