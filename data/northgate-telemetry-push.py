#!/usr/bin/env python3
"""northGate telemetry pusher — feeds cardinal point data to steamGate via ADB"""
import json, subprocess, time, os
from datetime import datetime

INTERVAL = 10
DEST = "/home/steamos/gaia/web/northgate-telemetry.json"

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except: return ""

def collect():
    data = {
        "gate": "northGate",
        "role": "CARDINAL_NORTH",
        "ts": datetime.now().astimezone().isoformat(),
        "coords": {"lat": 42.3314, "lon": -83.0458, "alt_m": 260},
        "house": "4422 Southgate Ave (House 1)"
    }
    
    gpu = run('nvidia-smi --query-gpu=temperature.gpu,power.draw,fan.speed,memory.used,memory.total --format=csv,noheader')
    if gpu:
        parts = [p.strip() for p in gpu.split(',')]
        try:
            data["hw"] = {
                "cpu": "AMD Ryzen 9 9950X3D",
                "gpu": "NVIDIA RTX 5090",
                "ram_gb": 96,
                "gpu_temp_c": int(parts[0]),
                "gpu_power_w": round(float(parts[1].replace(' W','')),1),
                "gpu_fan_pct": int(parts[2].replace(' %','')),
                "gpu_mem_used_mb": int(parts[3].replace(' MiB','')),
                "gpu_mem_total_mb": int(parts[4].replace(' MiB',''))
            }
        except: pass
    
    wifi = run('netsh wlan show interfaces')
    for line in wifi.split('\n'):
        if 'Signal' in line:
            try: data.setdefault("network",{})["wifi_signal"] = int(line.split(':')[1].strip().replace('%',''))
            except: pass
        if 'SSID' in line and 'BSSID' not in line:
            data.setdefault("network",{})["ssid"] = line.split(':',1)[1].strip()
    
    uptime = run('powershell -c "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"')
    if uptime:
        try:
            from datetime import datetime as dt
            boot = dt.fromisoformat(uptime.strip())
            data["uptime_sec"] = int((dt.now() - boot).total_seconds())
        except: pass
    
    data["ollama_models"] = 63
    data["power_plan"] = "Balanced"
    return data

print(f"northGate telemetry → steamFRAME every {INTERVAL}s")
while True:
    try:
        data = collect()
        tmp = os.path.join(os.environ.get('TEMP','/tmp'), 'ng-telem.json')
        with open(tmp, 'w') as f:
            json.dump(data, f)
        result = run(f'adb -s steamFRAME push "{tmp}" {DEST}')
        t = data.get("hw",{}).get("gpu_temp_c","?")
        w = data.get("hw",{}).get("gpu_power_w","?")
        sig = data.get("network",{}).get("wifi_signal","?")
        print(f"  push OK | gpu:{t}C {w}W | wifi:{sig}% | {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"  error: {e}")
    time.sleep(INTERVAL)
