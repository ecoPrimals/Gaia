"""att-deep.py — Deep dive into ATT modem: IP Passthrough + all devices."""
import urllib.request
import ssl
import re

BASE = "http://192.168.1.254"

def get(path, timeout=20):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

# 1. IP Passthrough page
print("=" * 70)
print("  IP PASSTHROUGH — /cgi-bin/ippass.ha")
print("=" * 70)
page = get("/cgi-bin/ippass.ha")
if not page.startswith("ERROR"):
    print(f"  Size: {len(page)} bytes")
    # Extract form elements
    selects = re.findall(r'<select[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</select>', page, re.I | re.S)
    for name_attr, options_html in selects:
        opts = re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>(.*?)</option>', options_html, re.I)
        selected = re.findall(r'<option[^>]*selected[^>]*value=["\']([^"\']*)["\']', options_html, re.I)
        print(f"  Select '{name_attr}':")
        for val, label in opts:
            marker = " <<<" if val in selected else ""
            print(f"    [{val}] {label}{marker}")

    inputs = re.findall(r'<input[^>]*(?:name=["\']([^"\']+)["\'])[^>]*', page, re.I)
    for inp in inputs:
        print(f"  Input: {inp}")

    # Look for current passthrough status
    if "disabled" in page.lower():
        print("  Status: PASSTHROUGH APPEARS DISABLED")
    if "enabled" in page.lower():
        print("  Status: PASSTHROUGH MAY BE ENABLED")

    # Find any MAC addresses shown
    macs = re.findall(r'([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})', page)
    if macs:
        print(f"  MACs on page: {macs}")
else:
    print(f"  {page}")
    print("  Trying alternate: /cgi-bin/pshosts.ha")
    page = get("/cgi-bin/pshosts.ha")
    if not page.startswith("ERROR"):
        print(f"  pshosts.ha: {len(page)} bytes")
    else:
        print(f"  {page}")

# 2. Full device list
print("\n" + "=" * 70)
print("  DEVICE LIST")
print("=" * 70)
page = get("/cgi-bin/devices.ha")
if not page.startswith("ERROR"):
    # Parse device entries - ATT modems typically have table rows
    # Try to find device name + MAC + IP patterns
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', page, re.I | re.S)
    devices = []
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.I | re.S)
        if cells and len(cells) >= 2:
            text = " | ".join(re.sub(r'<[^>]+>', '', c).strip() for c in cells)
            if text.strip(" |"):
                devices.append(text)

    # Also look for specific patterns
    all_macs = re.findall(r'([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', page)
    all_ips = re.findall(r'(192\.168\.\d+\.\d+)', page)
    all_names = re.findall(r'"name"\s*:\s*"([^"]+)"', page)

    # Try JSON parsing (some ATT modems embed JSON)
    json_match = re.search(r'var\s+deviceList\s*=\s*(\[.*?\]);', page, re.S)
    if json_match:
        import json
        try:
            devs = json.loads(json_match.group(1))
            for d in devs:
                name = d.get("name", "?")
                mac = d.get("mac", "?")
                ip = d.get("ip", "?")
                conn = d.get("connection", "?")
                status = d.get("status", "?")
                print(f"  {name:30s} {mac:20s} {ip:16s} {conn:10s} {status}")
        except:
            pass

    # Look for JSON data blocks
    json_blocks = re.findall(r'(\{[^{}]*"mac"[^{}]*\})', page)
    if json_blocks:
        import json
        for block in json_blocks[:20]:
            try:
                d = json.loads(block)
                print(f"  Device: {d}")
            except:
                pass

    # Print raw MACs and IPs found
    print(f"\n  Total MACs found: {len(all_macs)}")
    for mac in all_macs:
        print(f"    {mac}")
    print(f"\n  Total IPs found: {len(all_ips)}")
    for ip in sorted(set(all_ips), key=lambda x: int(x.split(".")[-1])):
        # Match IP to MAC if possible
        idx = page.find(ip)
        nearby = page[max(0, idx-200):idx+200] if idx >= 0 else ""
        nearby_mac = re.findall(r'([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', nearby)
        nearby_name = re.findall(r'"name"\s*:\s*"([^"]*)"', nearby)
        mac_str = nearby_mac[0] if nearby_mac else "?"
        name_str = nearby_name[0] if nearby_name else ""
        print(f"    {ip:16s} {mac_str:20s} {name_str}")

# 3. System info
print("\n" + "=" * 70)
print("  SYSTEM INFO")
print("=" * 70)
page = get("/cgi-bin/sysinfo.ha")
if not page.startswith("ERROR"):
    # Find firmware, model, serial
    for pattern in [r'Model\s*</td>\s*<td[^>]*>(.*?)</td>',
                    r'Firmware\s*</td>\s*<td[^>]*>(.*?)</td>',
                    r'Serial\s*</td>\s*<td[^>]*>(.*?)</td>',
                    r'Hardware\s*</td>\s*<td[^>]*>(.*?)</td>']:
        m = re.search(pattern, page, re.I | re.S)
        if m:
            print(f"  {re.sub(r'<[^>]+>', '', m.group(0)).strip()}")

    # Also look for WAN IP, gateway
    ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', page)
    public = [ip for ip in ips if not ip.startswith(("192.", "10.", "0.", "255."))]
    if public:
        print(f"  Public IPs: {public[:5]}")

# 4. Broadband config
print("\n" + "=" * 70)
print("  BROADBAND CONFIG")
print("=" * 70)
page = get("/cgi-bin/broadbandconfig.ha")
if not page.startswith("ERROR"):
    for pattern in ["vlan", "mode", "type", "speed", "fiber", "ont"]:
        matches = re.findall(rf'({pattern}[^<\n]{{0,100}})', page, re.I)
        for m in matches[:3]:
            clean = re.sub(r'<[^>]+>', ' ', m).strip()
            if clean:
                print(f"  {clean}")
else:
    print(f"  {page}")

# 5. Fiber stats
print("\n" + "=" * 70)
print("  FIBER STATS")
print("=" * 70)
page = get("/cgi-bin/fiberstat.ha")
if not page.startswith("ERROR"):
    rows = re.findall(r'<td[^>]*>(.*?)</td>', page, re.I | re.S)
    for i in range(0, len(rows)-1, 2):
        label = re.sub(r'<[^>]+>', '', rows[i]).strip()
        val = re.sub(r'<[^>]+>', '', rows[i+1]).strip()
        if label and val:
            print(f"  {label}: {val}")
else:
    print(f"  {page}")
