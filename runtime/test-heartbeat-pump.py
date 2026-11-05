"""Test 429 Heartbeat Pump — hammer the gate until the pulse fires."""
import socket, time, json

def req(path="/pi", host="gaia", port=8443):
    """Fast request with proper read."""
    s = socket.socket()
    s.settimeout(3)
    s.connect(("127.0.0.1", port))
    s.send(f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
    time.sleep(0.1)
    data = s.recv(16384).decode(errors="replace")
    s.close()
    parts = data.split(" ", 2)
    status = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return status, data

print("Hammering 80 rapid requests to trigger heartbeat pump...")
t0 = time.time()
for i in range(80):
    try:
        code, data = req()
        if i < 3 or i % 20 == 0:
            print(f"  #{i+1}: HTTP {code}")
        if code == 429:
            elapsed = time.time() - t0
            print(f"\n  429 HIT at request #{i+1} ({elapsed:.1f}s)")
            body_start = data.find("{")
            if body_start >= 0:
                body = data[body_start:]
                try:
                    j = json.loads(body)
                    print()
                    print("═══ HEARTBEAT PUMP (429) ═══")
                    print(f"  lub: {j.get('lub')}")
                    print(f"  message: {j.get('message')}")
                    hb = j.get("heartbeat", {})
                    print(f"  total_beats: {hb.get('total_beats')}")
                    print(f"  bpm: {hb.get('bpm')}")
                    print(f"  total_breaths: {hb.get('total_breaths')}")
                    print(f"  uptime_hours: {hb.get('uptime_hours')}")
                    sun = j.get("sun", {})
                    print(f"  sun: {sun.get('phase')} @ {sun.get('elevation')} deg")
                    print(f"  chord: {sun.get('chord')}, {sun.get('color_k')}K")
                    ports = j.get("ports", {})
                    print(f"  onion: {str(ports.get('onion', ''))[:40]}...")
                    print(f"  pump: {ports.get('pump')}")
                    wf = j.get("waveform", {})
                    print(f"  waves/min: {wf.get('waves_per_minute')}")
                    print(f"  hat: {wf.get('hat')}")
                    for line in data.split("\r\n"):
                        if "Heartbeat" in line or "BPM" in line or "Schrodinger" in line:
                            print(f"  HEADER: {line}")
                except Exception as e:
                    print(f"  Parse error: {e}")
                    print(body[:500])
            break
    except Exception as e:
        if i < 3:
            print(f"  #{i+1}: ERROR {e}")
else:
    elapsed = time.time() - t0
    print(f"\nNever hit 429 in 80 requests ({elapsed:.1f}s)")
    print("Rate may be too low — check burst/minute limits")
