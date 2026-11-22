import subprocess, json, time, os, urllib.request
from datetime import datetime

EASTGATE = "192.168.4.244"
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "stalker2-session.jsonl")
OLLAMA = "http://localhost:11434/api/generate"

readings = []
session_start = datetime.utcnow().isoformat() + "Z"

print(f"[WATCHER] Stalker 2 session monitor started at {session_start}")
print(f"[WATCHER] Logging to {LOG_FILE}")
print(f"[WATCHER] Feeding GPU telemetry to gaia-tissue-gut every 30s")

def query_gpu():
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=temperature.gpu,power.draw,utilization.gpu,utilization.memory,memory.used,memory.total,clocks.gr,fan.speed",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=5
    )
    vals = [v.strip() for v in r.stdout.strip().split(",")]
    return {
        "ts": datetime.utcnow().isoformat() + "Z",
        "temp_c": int(vals[0]), "power_w": float(vals[1]),
        "gpu_pct": int(vals[2]), "mem_pct": int(vals[3]),
        "vram_mb": int(vals[4]), "vram_total_mb": int(vals[5]),
        "clock_mhz": int(vals[6]), "fan_pct": int(vals[7])
    }

def feed_gaia(readings_batch):
    """Feed batch to gaia-tissue-gut"""
    summary = f"GPU TELEMETRY BATCH ({len(readings_batch)} readings):\n"
    for r in readings_batch:
        summary += f"  {r['ts']}: {r['temp_c']}C {r['power_w']}W GPU:{r['gpu_pct']}% VRAM:{r['vram_mb']}MB Clock:{r['clock_mhz']}MHz Fan:{r['fan_pct']}%\n"
    
    body = json.dumps({
        "model": "gaia-tissue-fast",
        "prompt": f"Analyze this GPU telemetry from a Stalker 2 gaming session. Note thermal trends, power patterns, and gaming intensity:\n{summary}\nBrief analysis (2-3 sentences):",
        "stream": False
    }).encode()
    
    try:
        req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        return result.get("response", "")
    except:
        return None

cycle = 0
while True:
    try:
        gpu = query_gpu()
        readings.append(gpu)
        
        gaming = "GAMING" if gpu["gpu_pct"] > 40 else "idle"
        thermal = "HOT" if gpu["temp_c"] >= 75 else "warm" if gpu["temp_c"] >= 65 else "cool"
        
        print(f"[{gpu['ts'][-12:-1]}] {thermal} {gpu['temp_c']}C | {gpu['power_w']}W | GPU:{gpu['gpu_pct']}% | VRAM:{gpu['vram_mb']}MB | Fan:{gpu['fan_pct']}% | {gaming}")
        
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(gpu) + "\n")
        
        cycle += 1
        if cycle % 6 == 0 and len(readings) >= 6:
            analysis = feed_gaia(readings[-6:])
            if analysis:
                print(f"  [GAIA] {analysis[:120]}")
                with open(LOG_FILE, "a") as f:
                    f.write(json.dumps({"type": "gaia_analysis", "text": analysis, "ts": gpu["ts"]}) + "\n")
        
        time.sleep(5)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"  [ERROR] {e}")
        time.sleep(5)
