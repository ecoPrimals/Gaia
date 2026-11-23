"""att-passthrough.py — Explore ATT BGW320 modem and find IP Passthrough settings."""
import urllib.request
import ssl
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "http://192.168.1.254"

def get(path, timeout=15):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

# Explore the modem's pages
pages = [
    ("/", "Home/Status"),
    ("/cgi-bin/home.ha", "Home"),
    ("/cgi-bin/status.ha", "Status"),
    ("/cgi-bin/broadbandstatistics.ha", "Broadband Stats"),
    ("/cgi-bin/ippassthrough.ha", "IP Passthrough"),
    ("/cgi-bin/firewall.ha", "Firewall"),
    ("/cgi-bin/dhcp.ha", "DHCP"),
    ("/cgi-bin/lanstatistics.ha", "LAN Stats"),
    ("/cgi-bin/wanstatus.ha", "WAN Status"),
    ("/cgi-bin/devices.ha", "Devices"),
    ("/cgi-bin/nat.ha", "NAT/Gaming"),
]

print("=" * 70)
print("  ATT BGW320 — MODEM EXPLORATION")
print("=" * 70)

for path, name in pages:
    page = get(path)
    if page.startswith("ERROR"):
        print(f"\n--- {name} ({path}) → {page}")
        continue

    title = ""
    if "<title>" in page.lower():
        m = re.search(r'<title>(.*?)</title>', page, re.I)
        title = m.group(1) if m else ""

    # Check for passthrough/bridge keywords
    has_passthrough = "passthrough" in page.lower()
    has_bridge = "bridge" in page.lower()
    has_dmz = "dmz" in page.lower()

    print(f"\n--- {name} ({path}) ---")
    print(f"  Title: {title}")
    print(f"  Size: {len(page)} bytes")
    print(f"  Passthrough: {has_passthrough} | Bridge: {has_bridge} | DMZ: {has_dmz}")

    # Extract links
    links = re.findall(r'href=["\']([^"\']+)["\']', page, re.I)
    cgi_links = [l for l in links if "cgi-bin" in l and l not in [p for p, _ in pages]]
    if cgi_links:
        print(f"  Links: {', '.join(cgi_links[:10])}")

    # If this is the passthrough page, extract form details
    if has_passthrough:
        print(f"\n  *** IP PASSTHROUGH PAGE FOUND ***")
        # Find select/input elements
        selects = re.findall(r'<select[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</select>', page, re.I | re.S)
        for name_attr, options_html in selects:
            opts = re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>(.*?)</option>', options_html, re.I)
            selected = re.findall(r'<option[^>]*selected[^>]*value=["\']([^"\']*)["\']', options_html, re.I)
            print(f"  Select '{name_attr}': {opts}")
            if selected:
                print(f"    Currently selected: {selected}")

        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*(?:value=["\']([^"\']*)["\'])?', page, re.I)
        for name_attr, val in inputs:
            print(f"  Input '{name_attr}' = '{val}'")

    # If this is the devices/DHCP page, look for connected devices
    if "device" in name.lower() or "dhcp" in name.lower():
        # Look for MAC addresses
        macs = re.findall(r'([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})', page)
        ips = re.findall(r'(192\.168\.\d+\.\d+)', page)
        if macs:
            print(f"  MACs found: {macs[:10]}")
        if ips:
            print(f"  IPs found: {ips[:10]}")

    # WAN Status — get the public IP info
    if "wan" in name.lower() or "broadband" in name.lower():
        # Look for IP addresses
        ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', page)
        public_ips = [ip for ip in ips if not ip.startswith("192.168") and not ip.startswith("10.") and not ip.startswith("0.")]
        if public_ips:
            print(f"  Public IPs: {public_ips[:5]}")

print("\n\n=== PASSTHROUGH PLAN ===")
print("""
To enable IP Passthrough on ATT BGW320:

1. Open browser: http://192.168.1.254
2. Enter Device Access Code (printed on modem label sticker)
3. Navigate: Firewall → IP Passthrough
4. Settings:
   - Allocation Mode: Passthrough
   - Passthrough Mode: DHCPS-fixed
   - Passthrough Fixed MAC: [GL-MT6000's WAN MAC]
5. Save & reboot

The GL-MT6000's WAN MAC is on the sticker on the router.
After this, GL-MT6000 gets 162.226.225.148 directly.
""")
