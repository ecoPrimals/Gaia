# Reach eastGate via HTTP gate — no SSH needed!
# eastGate has a data server at :8080 and gate at :8443
import urllib.request, json

print("=== Reaching eastGate via HTTP ===")

# Try data server
for url in [
    "http://192.168.4.244:8080/data/now.json",
    "http://192.168.4.244:8443/pulse",
]:
    try:
        r = urllib.request.urlopen(url, timeout=5)
        data = r.read().decode('utf-8')[:500]
        print(f"\n{url}:")
        print(f"  Status: {r.status}")
        print(f"  Data: {data[:300]}")
    except Exception as e:
        print(f"\n{url}: {e}")

# Can eastGate run a command via its API?
print("\n=== Trying gate endpoint ===")
for ep in ["/api/gate/enumerate", "/topology", "/now.json", "/pulse"]:
    url = f"http://192.168.4.244:8443{ep}"
    try:
        r = urllib.request.urlopen(url, timeout=5)
        print(f"  {ep}: {r.status} — {r.read().decode()[:200]}")
    except Exception as e:
        print(f"  {ep}: {e}")
