import socket, urllib.request, json

ip = "192.168.1.136"
ports = [22, 53, 80, 443, 3000, 3141, 8080, 8082, 8443, 11434, 11436]

print(f"Probing {ip}...")
open_ports = []
for p in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((ip, p))
        s.close()
        open_ports.append(p)
        print(f"  {p}: OPEN")
    except:
        pass

if not open_ports:
    print("  No signature ports open — trying broader range...")
    for p in [21, 23, 25, 135, 139, 445, 548, 631, 5353, 5900, 9090, 49152]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((ip, p))
            s.close()
            open_ports.append(p)
            print(f"  {p}: OPEN")
        except:
            pass

if 11434 in open_ports:
    try:
        body = urllib.request.urlopen(f"http://{ip}:11434/api/tags", timeout=3).read()
        data = json.loads(body)
        models = [m["name"] for m in data.get("models", [])]
        print(f"  Ollama: {len(models)} models: {models[:10]}")
    except Exception as e:
        print(f"  Ollama probe: {e}")

if 8080 in open_ports:
    try:
        body = urllib.request.urlopen(f"http://{ip}:8080/", timeout=3).read(500)
        print(f"  :8080 = {body[:200]}")
    except Exception as e:
        print(f"  :8080 = {e}")

if 8443 in open_ports:
    try:
        body = urllib.request.urlopen(f"http://{ip}:8443/pulse", timeout=3).read(500)
        print(f"  :8443/pulse = {body[:200]}")
    except Exception as e:
        print(f"  :8443 = {e}")

print(f"\nResult: {ip} has ports {open_ports}")
if not open_ports:
    print("  GRAY body — ARP present, no ports. Ghost in the spaghetti.")
