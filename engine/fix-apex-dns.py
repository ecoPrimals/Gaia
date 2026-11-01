"""Extract API key from cloudflared cert.pem and fix apex DNS for primals.eco"""
import json, subprocess, sys

# Read the cert.pem and extract the service key
with open("/root/.cloudflared/cert.pem") as f:
    content = f.read()

# The cert.pem has a JSON block at the end with the service key
idx = content.rfind("}")
if idx > 0:
    start = content.rfind("{", 0, idx + 1)
    if start > 0:
        data = json.loads(content[start:idx + 1])
        print("Keys found:", list(data.keys()))
        service_key = data.get("ServiceKey", data.get("APIToken", ""))
        zone_tag = data.get("ZoneID", "")
        account_tag = data.get("AccountTag", "")
        print(f"ServiceKey: {str(service_key)[:20]}...")
        print(f"ZoneID: {zone_tag}")
        print(f"AccountTag: {account_tag}")

        if service_key and zone_tag:
            import urllib.request, urllib.error

            headers = {
                "X-Auth-User-Service-Key": service_key,
                "Content-Type": "application/json"
            }

            # List DNS records for the zone
            url = f"https://api.cloudflare.com/client/v4/zones/{zone_tag}/dns_records?per_page=100"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req) as resp:
                    result = json.loads(resp.read())
                    if result["success"]:
                        records = result["result"]
                        print(f"\nDNS Records ({len(records)}):")
                        for r in records:
                            print(f"  {r['type']:6} {r['name']:35} {r['content'][:50]}  id={r['id'][:12]}")

                        # Find and delete A/AAAA records for primals.eco (apex)
                        # These conflict with the tunnel CNAME
                        for r in records:
                            if r["name"] == "primals.eco" and r["type"] in ("A", "AAAA", "CNAME"):
                                print(f"\n  DELETING: {r['type']} {r['name']} -> {r['content']}")
                                del_url = f"https://api.cloudflare.com/client/v4/zones/{zone_tag}/dns_records/{r['id']}"
                                del_req = urllib.request.Request(del_url, method="DELETE", headers=headers)
                                try:
                                    with urllib.request.urlopen(del_req) as del_resp:
                                        del_result = json.loads(del_resp.read())
                                        print(f"    Result: {del_result['success']}")
                                except Exception as e:
                                    print(f"    Error: {e}")
                    else:
                        print("API Error:", result)
            except Exception as e:
                print(f"Request error: {e}")
        else:
            print("Missing service key or zone ID")
    else:
        print("No JSON block found in cert.pem")
else:
    print("No closing brace found in cert.pem")
