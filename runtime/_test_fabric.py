"""Test fabric layer routes on webpi."""
import urllib.request, json, time

BASE = "http://localhost:8080"

tests = [
    # (url, host_header, expected_in_response, label)
    (f"{BASE}/", None, "Library of Alexandria", "primals.eco landing"),
    (f"{BASE}/", "gaia.primals.eco:8080", "Personal Space", "gaia.primals.eco"),
    (f"{BASE}/", "sporeprint.primals.eco:8080", None, "sporeprint.primals.eco"),
    (f"{BASE}/", "thesis.primals.eco:8080", None, "thesis.primals.eco"),
    (f"{BASE}/", "detroit.primals.eco:8080", None, "detroit.primals.eco"),
    (f"{BASE}/", "cogen.primals.eco:8080", None, "cogen.primals.eco"),
    (f"{BASE}/", "hypothesis.primals.eco:8080", None, "hypothesis.primals.eco"),
    (f"{BASE}/", "water.primals.eco:8080", None, "water.primals.eco"),
    (f"{BASE}/", "signal.primals.eco:8080", None, "signal.primals.eco"),
    (f"{BASE}/", "nestgate.io:8080", None, "nestgate.io"),
    (f"{BASE}/fabric", None, "Wardrobe", "fabric manifest page"),
    (f"{BASE}/fabric.json", None, "garments", "fabric JSON"),
    (f"{BASE}/attribution/", None, "sunCloud", "attribution"),
    (f"{BASE}/robots.txt", None, "User-agent", "robots.txt"),
    (f"{BASE}/llms.txt", None, "ecoPrimals", "llms.txt"),
    (f"{BASE}/sitemap.xml", None, "urlset", "sitemap.xml"),
]

passed = 0
failed = 0
for url, host, expected, label in tests:
    try:
        req = urllib.request.Request(url)
        if host:
            req.add_header("Host", host)
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = resp.status
            data = resp.read().decode("utf-8", errors="replace")
            size = len(data)
            gaia_header = resp.headers.get("X-Gaia", "")
            if expected and expected not in data:
                print(f"  WARN {label}: HTTP {code} ({size} bytes) but '{expected}' not found")
                failed += 1
            else:
                print(f"  OK   {label}: HTTP {code} ({size} bytes) X-Gaia={gaia_header}")
                passed += 1
    except Exception as e:
        print(f"  FAIL {label}: {e}")
        failed += 1

print(f"\n{passed}/{passed+failed} passed")
if failed == 0:
    print("ALL DRESSED. lub-DUB")
