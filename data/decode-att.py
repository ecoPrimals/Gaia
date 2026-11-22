"""decode-att.py — Decode all 34 MACs on ATT modem + get passthrough page details."""
import urllib.request
import re

BASE = "http://192.168.1.254"

# Known MAC-to-device mappings (from ecosystem map + HARDWARE.md)
KNOWN_MACS = {
    "94:83:c4:e0:62:b0": "GL-MT6000 (enp5s0 / wired)",
    "94:83:c4:e0:63:58": "GL-MT6000 (WiFi radio 1)",
    "94:83:c4:e0:63:5a": "GL-MT6000 (WiFi radio 2 / .8.1)",
    "ec:75:0c:4c:98:08": "TP-Link JetStream (.111) — House 2 switch",
    "1c:86:0b:37:63:19": "eastGate (.244/.248) — Intel NIC",
    "50:0a:52:0b:87:81": "Huiwan device (sporeGate or similar)",
    "04:f4:1c:e6:7c:e8": "MikroTik (.4.2) — L2 backbone",
    "84:47:09:38:97:55": "sporeGate (.3/.195)",
    "d4:80:8b:1b:9f:01": "EPSON ET-2400 printer",
    "90:09:d0": "Synology NAS (OUI prefix)",
}

# OUI prefix database (common ones)
OUI = {
    "94:83:c4": "GL-iNet (GL-MT6000 router)",
    "ec:75:0c": "TP-Link",
    "1c:86:0b": "Intel (likely eastGate/PC NIC)",
    "50:0a:52": "Huiwan Technology",
    "04:f4:1c": "MikroTik",
    "84:47:09": "unassigned (sporeGate known)",
    "d4:80:8b": "EPSON",
    "90:09:d0": "Synology",
    "a0:d0:dc": "ASUS (could be motherboard NIC)",
    "64:16:66": "Samsung (phone/tablet)",
    "b4:2e:99": "Atheros/Qualcomm (WiFi adapter)",
    "ac:f2:3c": "Intel WiFi (likely northGate Wi-Fi 3)",
    "c8:5e:a9": "unknown",
    "bc:fc:e7": "unknown",
    "98:40:d4": "Intel Wireless (older)",
    "e0:bb:9e": "unknown",
    "4c:50:dd": "unknown (SSH-only device)",
    "10:7c:61": "Apple (possible iPhone/Mac)",
    "10:c7:53": "unknown",
    "1c:f6:4c": "unknown",
    "0e:3c:40": "randomized MAC (Android/iOS privacy)",
    "0e:60:24": "randomized MAC",
    "16:2b:00": "randomized MAC",
    "1e:28:67": "randomized MAC",
    "3e:ec:cd": "randomized MAC",
    "4e:1e:b7": "randomized MAC",
    "66:73:e4": "randomized MAC",
    "6a:6d:89": "randomized MAC",
    "86:ba:0b": "randomized MAC",
    "a2:65:bd": "randomized MAC",
    "a6:a9:ca": "randomized MAC",
    "ae:7a:0c": "randomized MAC",
    "d6:ed:36": "randomized MAC",
    "da:05:91": "randomized MAC",
    "ea:72:d6": "randomized MAC",
}

# Check for randomized MAC (bit 1 of first octet = locally administered)
def is_random_mac(mac):
    first_byte = int(mac.split(":")[0], 16)
    return bool(first_byte & 0x02)

# All devices from ATT modem
devices = [
    ("192.168.1.64", "a0:d0:dc:ee:ee:39"),
    ("192.168.1.66", "50:0a:52:0b:87:81"),
    ("192.168.1.67", "ea:72:d6:7f:10:83"),
    ("192.168.1.68", "16:2b:00:eb:e7:ed"),
    ("192.168.1.69", "1e:28:67:1d:b7:52"),
    ("192.168.1.70", "0e:60:24:73:2c:d0"),
    ("192.168.1.71", "4e:1e:b7:e2:5b:19"),
    ("192.168.1.73", "66:73:e4:4f:df:fc"),
    ("192.168.1.74", "1c:f6:4c:5a:5d:ed"),
    ("192.168.1.75", "4c:50:dd:9b:c1:ec"),
    ("192.168.1.77", "da:05:91:e8:b3:89"),
    ("192.168.1.85", "ec:75:0c:4c:98:08"),
    ("192.168.1.222", "86:ba:0b:05:45:e4"),
    ("192.168.1.223", "a2:65:bd:50:84:87"),
    ("192.168.1.226", "6a:6d:89:47:b7:b7"),
    ("192.168.1.227", "d6:ed:36:7e:b4:46"),
    ("192.168.1.228", "a6:a9:ca:55:f8:6d"),
    ("192.168.1.230", "ae:7a:0c:22:53:72"),
    ("192.168.1.231", "ac:f2:3c:25:fc:c1"),
    ("192.168.1.232", "b4:2e:99:a7:91:a3"),
    ("192.168.1.233", "b4:2e:99:a7:91:a5"),
    ("192.168.1.234", "64:16:66:a4:82:0a"),
    ("192.168.1.253", "10:c7:53:73:51:12"),
]

# Also MACs without IPs in our list
no_ip_macs = [
    "0e:3c:40:5b:0d:a5",
    "10:7c:61:23:4f:4e",
    "3e:ec:cd:2f:4b:01",
    "94:83:c4:e0:62:b0",
    "94:83:c4:e0:63:58",
    "94:83:c4:e0:63:5a",
    "98:40:d4:75:04:90",
    "bc:fc:e7:ea:d9:34",
    "c8:5e:a9:c9:6f:80",
    "e0:bb:9e:d5:30:5a",
    "1c:86:0b:37:63:19",
]

print("=" * 80)
print("  ATT MODEM DEVICE DECODER — 34 devices, WHO ARE YOU?")
print("=" * 80)

print("\n--- DEVICES WITH IPs ---")
real_count = 0
random_count = 0
for ip, mac in devices:
    prefix = mac[:8]
    known = KNOWN_MACS.get(mac, "")
    oui = OUI.get(prefix, "???")
    rand = is_random_mac(mac)
    if rand:
        random_count += 1
        tag = "RANDOM MAC"
    else:
        real_count += 1
        tag = known or oui
    print(f"  {ip:16s} {mac:20s} → {tag}")

print(f"\n  Real MACs: {real_count} | Randomized MACs: {random_count}")
print(f"  (Randomized = phones/tablets with privacy MAC rotation)")

print("\n--- DEVICES WITHOUT IPs (seen historically) ---")
for mac in no_ip_macs:
    prefix = mac[:8]
    known = KNOWN_MACS.get(mac, "")
    oui = OUI.get(prefix, "???")
    rand = is_random_mac(mac)
    tag = "RANDOM" if rand else (known or oui)
    print(f"  {mac:20s} → {tag}")

# Key identifications
print("\n" + "=" * 80)
print("  IDENTIFIED GATES ON ATT NETWORK")
print("=" * 80)
print("""
  CONFIRMED:
    .231 (ac:f2:3c:25:fc:c1) = northGate Wi-Fi 3 (Intel WiFi)
    .85  (ec:75:0c:4c:98:08) = TP-Link JetStream — House 2 switch!
    .66  (50:0a:52:0b:87:81) = Huiwan device (sporeGate? or other gate)
    .64  (a0:d0:dc:ee:ee:39) = ASUS NIC (ironGate? westGate? has ASUS mobo)
    .75  (4c:50:dd:9b:c1:ec) = SSH-only device (a gate with SSH enabled)

  GL-MT6000 ROUTER (3 MACs, no IP assigned on ATT):
    94:83:c4:e0:62:b0 = wired WAN port
    94:83:c4:e0:63:58 = WiFi radio 1
    94:83:c4:e0:63:5a = WiFi radio 2

  PHONES/TABLETS (randomized MACs — 13 of them!):
    .67, .68, .69, .70, .71, .73, .77, .222, .223, .226, .227, .228, .230
    These are Kevin's phones, tablets, guests rotating MACs

  UNKNOWN REAL DEVICES:
    .74  (1c:f6:4c:5a:5d:ed) = ??? (not randomized)
    .232 (b4:2e:99:a7:91:a3) = Atheros/Qualcomm WiFi adapter (gate?)
    .233 (b4:2e:99:a7:91:a5) = Atheros/Qualcomm WiFi adapter (companion to .232)
    .234 (64:16:66:a4:82:0a) = Samsung device
    .253 (10:c7:53:73:51:12) = ??? high IP (admin/static?)
""")

# Now get the passthrough page raw HTML
print("=" * 80)
print("  IP PASSTHROUGH PAGE — RAW CONTENT")
print("=" * 80)
req = urllib.request.Request(f"{BASE}/cgi-bin/ippass.ha",
                             headers={"User-Agent": "Mozilla/5.0"})
page = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="replace")

# Strip excessive HTML/CSS/JS and just show the form-related content
# Find the main content area
content = re.sub(r'<script[^>]*>.*?</script>', '', page, flags=re.S)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.S)
content = re.sub(r'<head>.*?</head>', '', content, flags=re.S)
content = re.sub(r'<!--.*?-->', '', content, flags=re.S)

# Find form elements and their context
forms = re.findall(r'<form[^>]*>(.*?)</form>', content, re.S | re.I)
if forms:
    for i, form in enumerate(forms):
        clean = re.sub(r'<[^>]+>', ' ', form)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean:
            print(f"\n  Form {i}: {clean[:500]}")
else:
    # No form tags — look for select/input directly
    for tag in re.finditer(r'<(select|input|button)[^>]*(?:name=["\']([^"\']+)["\'])?[^>]*>', content, re.I):
        print(f"  Found: {tag.group(0)[:200]}")

# Look for specific passthrough keywords in context
for keyword in ["passthrough", "allocation", "dhcps", "fixed", "mode"]:
    for m in re.finditer(rf'[^<>]{{0,80}}{keyword}[^<>]{{0,80}}', content, re.I):
        clean = re.sub(r'\s+', ' ', m.group(0)).strip()
        if clean:
            print(f"  [{keyword}]: {clean}")
