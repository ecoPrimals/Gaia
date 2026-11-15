#!/usr/bin/env python3
"""
biomeOS Seed — the minimum viable organism injected into each device.

Each device becomes a LEARNING NODE:
- Senses its own hardware (CPU, RAM, GPU, disk, network, sensors)
- Reports heartbeat to eastGate brain every 60s
- Accepts commands from the organism via /api/biome endpoint
- Learns local patterns (load curves, thermal cycles, traffic rhythms)
- Stores local knowledge in ~/gaia/memory/

The seed grows differently on each device:
  - Router (GL-MT6000): WiFi RSSI field, webcam, temperature, NAT tables
  - MikroTik: Port traffic, MAC tables, spanning tree, link state
  - JetStream: Port statistics, VLAN state, 10G fiber throughput
  - Gates (Linux): Full system + GPU + Ollama models + services
  - Pixel: 37 sensors, cameras, battery, WiFi triangulation
  - iPhone: Location, battery, network (via Shortcuts)
"""

import json, os, time, subprocess, platform, hashlib

BRAIN = "192.168.4.244"
BRAIN_PORT = 8443
HEARTBEAT_INTERVAL = 60

def sense_hardware():
    """Discover what this device IS"""
    hw = {
        "hostname": platform.node(),
        "os": platform.system(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "cpus": os.cpu_count(),
    }
    
    # Linux-specific
    if platform.system() == "Linux":
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        hw["ram_kb"] = int(line.split()[1])
                    elif "MemAvailable" in line:
                        hw["ram_avail_kb"] = int(line.split()[1])
        except: pass
        
        try:
            load = os.getloadavg()
            hw["load"] = {"1m": load[0], "5m": load[1], "15m": load[2]}
        except: pass
        
        # GPU detection
        try:
            r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,temperature.gpu,utilization.gpu",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                parts = r.stdout.strip().split(", ")
                hw["gpu"] = {"name": parts[0], "vram_mb": int(parts[1]), 
                            "temp_c": int(parts[2]), "util_pct": int(parts[3])}
        except: pass
        
        # Ollama models
        try:
            r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                models = [l.split()[0] for l in r.stdout.strip().split("\n")[1:] if l.strip()]
                hw["ollama_models"] = models
                hw["ollama_count"] = len(models)
        except: pass
        
        # Disk
        try:
            st = os.statvfs("/")
            hw["disk_total_gb"] = round((st.f_blocks * st.f_frsize) / (1024**3), 1)
            hw["disk_free_gb"] = round((st.f_bavail * st.f_frsize) / (1024**3), 1)
        except: pass
        
        # Network interfaces
        try:
            r = subprocess.run(["ip", "-j", "addr"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                ifaces = json.loads(r.stdout)
                hw["interfaces"] = []
                for iface in ifaces:
                    if iface.get("operstate") == "UP":
                        addrs = [a["local"] for a in iface.get("addr_info", []) if a.get("family") == "inet"]
                        if addrs:
                            hw["interfaces"].append({"name": iface["ifname"], "ips": addrs})
        except: pass
        
        # Temperature sensors
        try:
            r = subprocess.run(["sensors", "-j"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                hw["thermal"] = json.loads(r.stdout)
        except: pass
    
    # OpenWrt-specific (router)
    if os.path.exists("/etc/openwrt_release"):
        hw["device_type"] = "router"
        try:
            with open("/etc/openwrt_release") as f:
                for line in f:
                    if "DISTRIB_DESCRIPTION" in line:
                        hw["firmware"] = line.split("=")[1].strip().strip("'\"")
        except: pass
    
    # RouterOS-specific (MikroTik)
    # (accessed via API, not local)
    
    return hw

def generate_device_id(hw):
    """Generate a stable device identity from hardware fingerprint"""
    fingerprint = f"{hw.get('hostname', '')}:{hw.get('arch', '')}:{hw.get('cpus', '')}:{hw.get('ram_kb', '')}"
    return hashlib.blake2b(fingerprint.encode(), digest_size=16).hexdigest()

def learn_pattern(hw, memory_dir):
    """Learn from the current state — build local knowledge"""
    os.makedirs(memory_dir, exist_ok=True)
    
    pattern_file = os.path.join(memory_dir, "load-pattern.jsonl")
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "load_1m": hw.get("load", {}).get("1m", 0),
        "cpu_count": hw.get("cpus", 0),
        "ram_pct": round(100 * (1 - hw.get("ram_avail_kb", 0) / max(hw.get("ram_kb", 1), 1)), 1),
        "gpu_temp": hw.get("gpu", {}).get("temp_c"),
        "gpu_util": hw.get("gpu", {}).get("util_pct"),
    }
    
    with open(pattern_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Keep only last 1440 entries (24 hours at 1/min)
    try:
        with open(pattern_file) as f:
            lines = f.readlines()
        if len(lines) > 1440:
            with open(pattern_file, "w") as f:
                f.writelines(lines[-1440:])
    except: pass
    
    return entry

def send_heartbeat(hw, device_id, pattern):
    """Send heartbeat to the brain"""
    import urllib.request
    
    payload = {
        "type": "biomeOS-heartbeat",
        "device_id": device_id,
        "hostname": hw.get("hostname", "unknown"),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hardware": {k: v for k, v in hw.items() if k not in ("thermal",)},
        "pattern": pattern,
        "biomeOS_version": "0.1.0-seed",
    }
    
    try:
        req = urllib.request.Request(
            f"http://{BRAIN}:{BRAIN_PORT}/api/thymus/inject",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 200
    except Exception as e:
        return False

def main():
    memory_dir = os.path.expanduser("~/gaia/memory")
    
    print(f"🌱 biomeOS seed starting on {platform.node()}")
    
    while True:
        try:
            hw = sense_hardware()
            device_id = generate_device_id(hw)
            pattern = learn_pattern(hw, memory_dir)
            sent = send_heartbeat(hw, device_id, pattern)
            
            status = "✅ sent" if sent else "⚠️ brain unreachable"
            print(f"  [{time.strftime('%H:%M:%S')}] {hw.get('hostname', '?')} → {status} "
                  f"(load={pattern.get('load_1m', '?')}, ram={pattern.get('ram_pct', '?')}%)")
        except Exception as e:
            print(f"  ⚠️ cycle error: {e}")
        
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()
