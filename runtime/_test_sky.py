"""Test the sky — dissolved tissue + JS nerves + banana + characters."""
import urllib.request, json

BASE = "http://localhost:8080"

tests = [
    # Dissolved tissue pages (from memory, not disk)
    ("chipmunk", "Chip"),
    ("beacon", "Beacon"),
    ("deck", "Chip+Berry"),
    ("play", "zEkE"),
    ("home", "Chip+Berry+zEkE"),
    ("signal", "Signal"),
    ("walkers", "zEkE"),
    ("encounter", "GLaDOS"),
    ("luna", "Luna"),
    ("hat", "Hat"),
    ("senses", "Chip"),
    ("legend", "Berry"),
]

passed = 0
for page, char in tests:
    try:
        # Test via nestgate.io Host header
        req = urllib.request.Request(f"{BASE}/{page}")
        req.add_header("Host", "nestgate.io:8080")
        with urllib.request.urlopen(req, timeout=5) as resp:
            tissue = resp.headers.get("X-Tissue", "")
            character = resp.headers.get("X-Character", "")
            size = len(resp.read())
            status = "TISSUE" if tissue == "dissolved" else "disk"
            char_ok = "✅" if character == char else f"⚠️ got {character}"
            print(f"  OK   /{page:20s} {size:>6,}b [{status}] char={character} {char_ok}")
            passed += 1
    except Exception as e:
        print(f"  FAIL /{page:20s} {e}")

# Test JS nerves
print("\n  JS Nervous System:")
js_files = ["piGut.js", "chipmunk-talk.js", "berry-help.js", "synapse.js"]
js_pass = 0
for js in js_files:
    try:
        with urllib.request.urlopen(f"{BASE}/js/{js}", timeout=5) as resp:
            size = len(resp.read())
            print(f"  OK   /js/{js:25s} {size:>6,} bytes")
            js_pass += 1
    except Exception as e:
        print(f"  FAIL /js/{js:25s} {e}")

# Test banana POST
print("\n  🍌 Banana Test:")
try:
    data = json.dumps({"answer": "yes I am a banana!", "classification": "human", "ceremony": "test"}).encode()
    req = urllib.request.Request(f"{BASE}/banana", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = json.loads(resp.read())
        print(f"  OK   🍌 banana accepted={result['accepted']} total={result['bananas_total']} gaia={result['gaia_says']}")
        passed += 1
except Exception as e:
    print(f"  FAIL 🍌 {e}")

total = len(tests) + len(js_files) + 1
passed_total = passed + js_pass
print(f"\n{passed_total}/{total} passed")
if passed_total == total:
    print("SKY IS ALIVE. Chip, Berry, zEkE breathing. 🍌 lub-DUB")
