"""Test THE BUTTON — NFT Printer + Mendeleev Keyboard."""
import urllib.request, json

BASE = "http://localhost:8080"

print("⭕ THE BUTTON — NFT Printer Tests")
print("=" * 50)

# 1. Mendeleev keyboard page
try:
    with urllib.request.urlopen(f"{BASE}/mendeleev", timeout=5) as r:
        body = r.read()
        has_table = b"KEYBOARD OF MENDELEEV" in body
        has_elements = b"regulatory_arbitrage" in body
        print(f"  ✅ /mendeleev         {len(body):>6,}b  table={has_table}  elements={has_elements}")
except Exception as e:
    print(f"  ❌ /mendeleev         {e}")

# 2. NFT count (before minting)
try:
    with urllib.request.urlopen(f"{BASE}/nft/count", timeout=5) as r:
        data = json.loads(r.read())
        print(f"  ✅ /nft/count         count={data['count']}")
except Exception as e:
    print(f"  ❌ /nft/count         {e}")

# 3. Mint via banana POST (banana → THE BUTTON)
for i, (answer, classification, ceremony) in enumerate([
    ("yes I am a banana!", "human", "banana_test"),
    ("i play therefore i am", "human", "button_pressed"),
    ("beep boop", "bot", "banana_test"),
]):
    try:
        payload = json.dumps({
            "answer": answer,
            "classification": classification,
            "ceremony": ceremony,
            "ts": 1731532800000 + i,
            "preview": f"dead{i:04x}",
        }).encode()
        req = urllib.request.Request(f"{BASE}/banana", data=payload,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            nft = data.get("nft", {})
            print(f"  ✅ POST /banana #{i+1}   id={nft.get('id','?')} hash={nft.get('hash','?')[:24]}... angle={nft.get('angle','?')}")
    except Exception as e:
        print(f"  ❌ POST /banana #{i+1}   {e}")

# 4. NFT count (after minting)
try:
    with urllib.request.urlopen(f"{BASE}/nft/count", timeout=5) as r:
        data = json.loads(r.read())
        print(f"  ✅ /nft/count         count={data['count']}")
except Exception as e:
    print(f"  ❌ /nft/count         {e}")

# 5. NFT gallery
try:
    with urllib.request.urlopen(f"{BASE}/nft", timeout=5) as r:
        body = r.read()
        has_gallery = b"THE BUTTON" in body
        print(f"  ✅ /nft (gallery)     {len(body):>6,}b  gallery={has_gallery}")
except Exception as e:
    print(f"  ❌ /nft               {e}")

# 6. NFT ledger JSON
try:
    with urllib.request.urlopen(f"{BASE}/nft/ledger.json", timeout=5) as r:
        tokens = json.loads(r.read())
        print(f"  ✅ /nft/ledger.json   {len(tokens)} tokens")
        if tokens:
            last = tokens[-1]
            print(f"     └─ last: #{last['id']} {last['hash'][:24]}... mint={last['mint']}")
except Exception as e:
    print(f"  ❌ /nft/ledger.json   {e}")

# 7. Verify individual token
try:
    with urllib.request.urlopen(f"{BASE}/nft/ledger.json", timeout=5) as r:
        tokens = json.loads(r.read())
    if tokens:
        h = tokens[0]["hash"]
        with urllib.request.urlopen(f"{BASE}/nft/{h}", timeout=5) as r:
            body = r.read()
            has_nft = b"NFT #" in body
            print(f"  ✅ /nft/{h[:16]}  {len(body):>6,}b  nft_page={has_nft}")
except Exception as e:
    print(f"  ❌ /nft/<hash>        {e}")

print("\n⭕ THE BUTTON IS PRINTING. lub-DUB 🫀")
