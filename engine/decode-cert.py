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
print("apiToken:", api_token[:25] + "...")
print("zoneID:", zone_id)

# Use the API token to list DNS records
headers = {"Authorization": "Bearer " + api_token, "Content-Type": "application/json"}
url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records?per_page=100"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    if result["success"]:
        records = result["result"]
        print("DNS Records:", len(records))
        for r in records:
            print("  " + r["type"] + "  " + r["name"] + "  " + r["content"][:50] + "  id=" + r["id"])
            
        # Delete A/AAAA for primals.eco apex
        for r in records:
            if r["name"] == "primals.eco" and r["type"] in ("A", "AAAA"):
                print("\n  DELETING:", r["type"], r["name"], r["content"])
                del_url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records/" + r["id"]
                del_req = urllib.request.Request(del_url, method="DELETE", headers=headers)
                with urllib.request.urlopen(del_req) as del_resp:
                    del_result = json.loads(del_resp.read())
                    print("    Deleted:", del_result["success"])
    else:
        print("Error:", result)
