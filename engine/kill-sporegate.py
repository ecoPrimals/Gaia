"""Kill the CF Pages CNAME for primals.eco and replace with tunnel CNAME."""
import base64, json, urllib.request

with open("/root/.cloudflared/cert.pem") as f:
    lines = f.readlines()

token_lines = []
in_token = False
for line in lines:
    if "BEGIN ARGO TUNNEL TOKEN" in line:
        in_token = True
        continue
    if "END ARGO TUNNEL TOKEN" in line:
        in_token = False
        continue
    if in_token:
        token_lines.append(line.strip())

b64 = "".join(token_lines)
decoded = base64.b64decode(b64).decode()
data = json.loads(decoded)
api_token = data.get("apiToken", "")
zone_id = data.get("zoneID", "")
tunnel_id = "2c12060a-8582-47c2-b8ff-c7c157f036d9"

headers = {"Authorization": "Bearer " + api_token, "Content-Type": "application/json"}

# Delete the CF Pages CNAME for primals.eco apex
record_id = "b378f6dac875d0b2f8410ef1d1e444b5"
print("Deleting primals.eco -> hud-1wv.pages.dev CNAME...")
del_url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records/" + record_id
del_req = urllib.request.Request(del_url, method="DELETE", headers=headers)
try:
    with urllib.request.urlopen(del_req) as resp:
        result = json.loads(resp.read())
        print("  Deleted:", result["success"])
except Exception as e:
    print("  Error:", e)

# Now create a CNAME for primals.eco -> tunnel
print("Creating primals.eco -> tunnel CNAME...")
create_url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records"
create_data = json.dumps({
    "type": "CNAME",
    "name": "primals.eco",
    "content": tunnel_id + ".cfargotunnel.com",
    "proxied": True,
    "ttl": 1
}).encode()
create_req = urllib.request.Request(create_url, data=create_data, method="POST", headers=headers)
try:
    with urllib.request.urlopen(create_req) as resp:
        result = json.loads(resp.read())
        if result["success"]:
            print("  Created! primals.eco -> tunnel")
        else:
            print("  Error:", result.get("errors", []))
except Exception as e:
    print("  Error:", e)

# Also clean up dead golgi A records
dead_records = [
    ("golgi-de.primals.eco", "4532183f2a3f27f346ca17dac9b7d6e0"),
    ("golgi-in.primals.eco", "b85ec390174b5d2662a38112524c2073"),
    ("golgi-jp.primals.eco", "c93b52af4f9f23167212a4ef4b5e2f5c"),
    ("golgi-us.primals.eco", "125759de3f1eb5fb1d81ce74b132bfd2"),
]

print("\nCleaning dead golgi records...")
for name, rid in dead_records:
    del_url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records/" + rid
    del_req = urllib.request.Request(del_url, method="DELETE", headers=headers)
    try:
        with urllib.request.urlopen(del_req) as resp:
            result = json.loads(resp.read())
            print("  Deleted:", name, result["success"])
    except Exception as e:
        print("  Error:", name, e)

print("\nDone. CF Pages sporegate is DEAD. Gaia IS the server.")
