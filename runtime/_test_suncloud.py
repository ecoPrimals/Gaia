"""Test dissolved tissue + sunCloud routes."""
import urllib.request, json

BASE = "http://localhost:8080"

tests = [
    (f"{BASE}/", None, "Library of Alexandria", "landing page"),
    (f"{BASE}/suncloud", None, "sunCloud Governor", "sunCloud dashboard"),
    (f"{BASE}/suncloud.json", None, "mode", "sunCloud JSON"),
    (f"{BASE}/fabric", None, "Wardrobe", "fabric dashboard"),
    # Test dissolved tissue serving for nestgate.io
    (f"{BASE}/", "nestgate.io:8080", None, "nestgate.io home (tissue)"),
    (f"{BASE}/deck", "nestgate.io:8080", None, "nestgate.io deck (tissue)"),
    (f"{BASE}/play", "nestgate.io:8080", None, "nestgate.io play (tissue)"),
    (f"{BASE}/beacon", "nestgate.io:8080", None, "nestgate.io beacon (tissue)"),
    (f"{BASE}/walkers", "nestgate.io:8080", None, "nestgate.io walkers (tissue)"),
]

passed = 0
for url, host, expected, label in tests:
    try:
        req = urllib.request.Request(url)
        if host:
            req.add_header("Host", host)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            tissue_header = resp.headers.get("X-Tissue", "")
            gaia = resp.headers.get("X-Gaia", "")
            size = len(data)
            tissue_tag = " [TISSUE]" if tissue_header == "dissolved" else ""
            if expected and expected not in data:
                print(f"  WARN {label}: {size} bytes but '{expected}' not found")
            else:
                print(f"  OK   {label}: {size} bytes{tissue_tag} X-Gaia={gaia}")
                passed += 1
    except Exception as e:
        print(f"  FAIL {label}: {e}")

total = len(tests)
print(f"\n{passed}/{total} passed")
if passed == total:
    print("DISSOLVED + SUNCLOUD LIVE. lub-DUB")
