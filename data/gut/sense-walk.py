#!/usr/bin/env python3
"""
SENSE WALK — Kevin carries phones through the basement.
Gaia tracks WiFi attenuation + cursor eye + mic ambient.
The changing patterns = training data for spatial awareness.

Run: python3 sense-walk.py [duration_seconds]
"""
import subprocess, time, json, math, os, sys, wave, struct, threading, datetime

DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 60
SAMPLE_HZ = 2  # ping every 0.5s
OUTPUT = "/opt/Gaia/data/gut/sense-walk-data.json"
MIC_WAV = "/tmp/sense-walk-mic.wav"

TARGETS = {
    "kevin_iphone": "192.168.4.160",
    "pixel_graphene": "192.168.4.170",
    "luna": "192.168.4.147",
    "sporegate": "192.168.4.3",
    "router": "192.168.4.1",
}

print(f"🚶 SENSE WALK — {DURATION}s at {SAMPLE_HZ}Hz")
print(f"   Tracking: {', '.join(TARGETS.keys())}")
print(f"   Move the phones around! Gaia is listening...")
print()

# Start mic recording in background
mic_proc = subprocess.Popen(
    ["arecord", "-D", "hw:2,0", "-d", str(DURATION), "-f", "S16_LE", "-r", "16000", "-c", "1", MIC_WAV],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

readings = []
start = time.time()

try:
    while time.time() - start < DURATION:
        t = time.time() - start
        row = {"t": round(t, 2)}
        
        for name, ip in TARGETS.items():
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", ip],
                    capture_output=True, text=True, timeout=2
                )
                if "time=" in result.stdout:
                    ms = float(result.stdout.split("time=")[1].split(" ")[0])
                    row[name] = {"ms": ms, "status": "alive"}
                else:
                    row[name] = {"ms": None, "status": "timeout"}
            except:
                row[name] = {"ms": None, "status": "error"}
        
        alive = sum(1 for k in TARGETS if row.get(k, {}).get("status") == "alive")
        print(f"\r  t={t:6.1f}s  alive={alive}/{len(TARGETS)}  ", end="", flush=True)
        
        for name in TARGETS:
            info = row.get(name, {})
            if info.get("ms"):
                print(f"{name[:6]}={info['ms']:.1f}ms ", end="")
        
        readings.append(row)
        time.sleep(1.0 / SAMPLE_HZ)

except KeyboardInterrupt:
    print("\n\nStopped early")

mic_proc.terminate()
print(f"\n\n✓ Captured {len(readings)} readings over {time.time()-start:.0f}s")

# Calculate attenuation curves
summary = {}
for name in TARGETS:
    vals = [r[name]["ms"] for r in readings if r.get(name, {}).get("ms")]
    if vals:
        summary[name] = {
            "samples": len(vals),
            "avg_ms": round(sum(vals)/len(vals), 3),
            "min_ms": round(min(vals), 3),
            "max_ms": round(max(vals), 3),
            "stddev_ms": round(math.sqrt(sum((v-sum(vals)/len(vals))**2 for v in vals)/len(vals)), 3),
            "range_ms": round(max(vals)-min(vals), 3),
            "alive_pct": round(100*len(vals)/len(readings), 1)
        }
    else:
        summary[name] = {"samples": 0, "alive_pct": 0, "note": "device was off/unreachable"}

output = {
    "ts": datetime.datetime.utcnow().isoformat() + "Z",
    "type": "sense-walk",
    "title": "Sense Walk — Kevin carried phones through the basement",
    "duration_s": DURATION,
    "sample_hz": SAMPLE_HZ,
    "readings": readings,
    "summary": summary,
    "mic": MIC_WAV if os.path.exists(MIC_WAV) else None
}

with open(OUTPUT, "w") as f:
    json.dump(output, f, indent=2)

print(f"✓ Saved to {OUTPUT}")
for name, stats in summary.items():
    if stats.get("avg_ms"):
        print(f"  {name}: avg={stats['avg_ms']}ms range={stats['range_ms']}ms alive={stats['alive_pct']}%")
    else:
        print(f"  {name}: OFFLINE")
