"""EXECUTE — Full sweep, launch everything."""
import subprocess
import socket
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def ping(ip):
    try:
        r = subprocess.run(f"ping -n 1 -w 500 {ip}", capture_output=True, text=True, timeout=3, shell=True)
        if "TTL=" in r.stdout:
            ms = "?"
            for part in r.stdout.split():
                if part.startswith("time="):
                    ms = part.split("=")[1].rstrip("ms")
            return ip, True, ms
        return ip, False, None
    except:
        return ip, False, None

def tcp_check(ip, port):
    try:
        s = socket.create_connection((ip, port), timeout=1)
        s.close()
        return True
    except:
        return False

print("=" * 70)
print("  EXECUTE — FULL MESH SWEEP + LAUNCH")
print("=" * 70)

# 1. MESH SWEEP
targets = [
    ("ATT modem", "192.168.1.254"),
    ("Router .4.1", "192.168.4.1"),
    ("MikroTik .4.2", "192.168.4.2"),
    ("eastGate .248", "192.168.4.248"),
    ("eastGate .244", "192.168.4.244"),
    ("sporeGate .1.75", "192.168.1.75"),
    ("ASUS gate .1.64", "192.168.1.64"),
    ("biomegate .1.232", "192.168.1.232"),
    ("JetStream .1.85", "192.168.1.85"),
    ("Google DNS", "8.8.8.8"),
]

print("\n--- MESH SWEEP ---")
ips = [t[1] for t in targets]
with ThreadPoolExecutor(20) as ex:
    results = dict((ip, (alive, ms)) for ip, alive, ms in ex.map(ping, ips))

alive_gates = []
for name, ip in targets:
    alive, ms = results[ip]
    status = f"ALIVE ({ms}ms)" if alive else "DARK"
    print(f"  {status:16s} {name:20s} {ip}")
    if alive and ip != "8.8.8.8":
        alive_gates.append((name, ip))

# 2. Deep probe alive gates
print("\n--- DEEP PROBE ---")
for name, ip in alive_gates:
    ports = [22, 80, 443, 3000, 8080, 8443]
    open_ports = [p for p in ports if tcp_check(ip, p)]
    if open_ports:
        print(f"  {name} ({ip}): ports {open_ports}")

# 3. GPU STATUS
print("\n--- GPU ---")
try:
    r = subprocess.run("nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits",
                       capture_output=True, text=True, timeout=5, shell=True)
    vals = [v.strip() for v in r.stdout.strip().split(",")]
    print(f"  RTX 5090: {vals[0]}C, {vals[1]}% load, {vals[2]}/{vals[3]} MB VRAM, {vals[4]}W")
except Exception as e:
    print(f"  GPU error: {e}")

# 4. KENSHI STATUS
print("\n--- KENSHI ---")
try:
    r = subprocess.run("tasklist /fi \"imagename eq kenshi_x64.exe\" /fo csv /nh",
                       capture_output=True, text=True, timeout=5, shell=True)
    if "kenshi_x64" in r.stdout:
        print(f"  KENSHI: ALIVE")
    else:
        print(f"  KENSHI: NOT RUNNING")
except:
    print(f"  KENSHI: check failed")

# 5. HUD SERVER
print("\n--- HUD SERVER ---")
try:
    r = subprocess.run("netstat -ano", capture_output=True, text=True, timeout=5, shell=True)
    if ":8888" in r.stdout and "LISTEN" in r.stdout:
        print("  HUD: ALIVE on :8888")
    else:
        print("  HUD: DOWN — RELAUNCHING...")
        subprocess.Popen(
            ["python", r"c:\Users\mokke\Desktop\Gaia\gardens\springs\ludoSpring\kenshi\game-mode-hud.py"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(2)
        # Verify
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:8888/stats", timeout=3)
            print("  HUD: RELAUNCHED OK")
        except:
            print("  HUD: RELAUNCH FAILED")
except Exception as e:
    print(f"  HUD error: {e}")

# 6. THINKING SQUADS
print("\n--- THINKING SQUADS ---")
try:
    r = subprocess.run("tasklist /fo csv /nh", capture_output=True, text=True, timeout=5, shell=True)
    if "thinking_squads" in r.stdout:
        print("  THINKING SQUADS: RUNNING")
    else:
        # Check if minds exist
        minds_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Gaia" / "kenshi" / "minds.json"
        if minds_path.exists():
            minds = json.loads(minds_path.read_text(encoding="utf-8"))
            voiced = [n for n in minds if minds[n].get("voice")]
            print(f"  THINKING SQUADS: NOT RUNNING — {len(voiced)} minds ready")
            print("  LAUNCHING thinking squads...")
            subprocess.Popen(
                ["python", r"c:\Users\mokke\Desktop\Gaia\gardens\springs\ludoSpring\kenshi\thinking_squads.py", "watch"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(3)
            print("  THINKING SQUADS: LAUNCHED in watch mode")
        else:
            print("  No minds found — need Kenshi running + kenshi_eyes.py")
except Exception as e:
    print(f"  Squads error: {e}")

# 7. SQUAD STATUS
print("\n--- SQUAD MINDS ---")
try:
    minds_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Gaia" / "kenshi" / "minds.json"
    minds = json.loads(minds_path.read_text(encoding="utf-8"))
    for name, m in minds.items():
        v = m.get("voice", {})
        mem = m.get("memory", [])
        last = mem[-1][:60] if mem else "no memories"
        print(f"  {name}: {v.get('temperament','?')} | trust {m.get('trust',0):.1f} | {last}")
except:
    print("  No minds loaded")

# 8. OPEN HUD IN BROWSER
print("\n--- LAUNCHING BROWSER ---")
try:
    subprocess.Popen(["cmd", "/c", "start", "http://localhost:8888"], shell=True,
                     creationflags=subprocess.CREATE_NO_WINDOW)
    print("  Browser opened: http://localhost:8888")
except:
    print("  Browser launch failed")

print("\n" + "=" * 70)
print("  EXECUTION COMPLETE")
print("=" * 70)
