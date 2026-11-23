# -*- coding: utf-8 -*-
"""PNS AMOEBA — Agglutinate all peripherals into one reusable body image.
Every gate runs this. The PNS (Peripheral Nervous System) maps to the CNS.
Agglutination: each device binds by VID/PID/serial = cell identity."""
import subprocess, json, hashlib, time, os

GATE = os.environ.get("GAIA_GATE", "northGate")

def ps(cmd):
    r = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

def get_devices(class_name):
    """Get PnP devices by class with properties."""
    raw = ps(f"""
        Get-PnpDevice -Class {class_name} -ErrorAction SilentlyContinue | ForEach-Object {{
            $bt = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_BusReportedDeviceDesc' -ErrorAction SilentlyContinue).Data
            [PSCustomObject]@{{
                Name=$_.FriendlyName; Status=$_.Status; ID=$_.InstanceId; BusDesc=$bt
            }} | ConvertTo-Json -Compress
        }}
    """)
    devices = []
    for line in raw.split('\n'):
        line = line.strip()
        if line.startswith('{'):
            try:
                devices.append(json.loads(line))
            except:
                pass
    return devices

print(f"=== PNS AMOEBA — {GATE} ===")

# Collect all organ systems
organs = {}

# HANDS — keyboards
print("  Agglutinating HANDS...")
keyboards = get_devices("Keyboard")
organs["hands"] = {
    "type": "input/keyboard",
    "cells": [{"name": d["Name"], "status": d["Status"], "id": d["ID"],
               "vid_pid": d["ID"].split("\\")[1] if "\\" in d["ID"] else ""} 
              for d in keyboards if "Keyboard" in d.get("Name", "")]
}

# EARS + VOICE — audio
print("  Agglutinating EARS+VOICE...")
audio = get_devices("AudioEndpoint")
organs["ears_voice"] = {
    "type": "audio/io",
    "cells": [{"name": d["Name"], "status": d["Status"]}
              for d in audio if d.get("Status") == "OK"]
}

# GRIP — mouse
print("  Agglutinating GRIP...")
mice = get_devices("Mouse")
organs["grip"] = {
    "type": "input/pointer",
    "cells": [{"name": d["Name"], "status": d["Status"], "id": d["ID"]}
              for d in mice if d.get("Status") == "OK"]
}

# EYES — displays + GPUs
print("  Agglutinating EYES...")
displays = get_devices("Display")
monitors = get_devices("Monitor")
organs["eyes"] = {
    "type": "display/gpu",
    "gpus": [{"name": d["Name"], "status": d["Status"], "pci": d["ID"]}
             for d in displays],
    "monitors": [{"name": d["Name"], "status": d["Status"]}
                 for d in monitors if d.get("Status") == "OK"]
}

# TAIL — Steam/USB displays
print("  Agglutinating TAIL...")
steam_devices = []
for d in get_devices("MEDIA"):
    if "Steam" in d.get("Name", ""):
        steam_devices.append({"name": d["Name"], "status": d["Status"]})
organs["tail"] = {
    "type": "display/stream",
    "cells": steam_devices
}

# SPINE — network
print("  Agglutinating SPINE...")
net = get_devices("Net")
organs["spine"] = {
    "type": "network",
    "cells": [{"name": d["Name"], "status": d["Status"]}
              for d in net if d.get("Status") == "OK"]
}

# USB NERVE — special devices (Pixel, dongles)
print("  Agglutinating USB NERVE...")
usb_raw = ps("""
    Get-PnpDevice -Class USB | Where-Object { $_.Status -eq 'OK' -and $_.FriendlyName -notmatch 'Root Hub|Host Controller|Generic.*Hub' } | ForEach-Object {
        $bt = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName 'DEVPKEY_Device_BusReportedDeviceDesc' -ErrorAction SilentlyContinue).Data
        [PSCustomObject]@{ Name=$_.FriendlyName; BusDesc=$bt; ID=$_.InstanceId } | ConvertTo-Json -Compress
    }
""")
usb_cells = []
for line in usb_raw.split('\n'):
    line = line.strip()
    if line.startswith('{'):
        try:
            d = json.loads(line)
            usb_cells.append({"name": d.get("BusDesc") or d["Name"], "id": d["ID"]})
        except:
            pass
organs["usb_nerve"] = {
    "type": "usb/composite",
    "cells": usb_cells
}

# BRAIN — CPU + Memory + NVMe (from gate-enumerate)
print("  Agglutinating BRAIN...")
cpu = ps("(Get-CimInstance Win32_Processor).Name")
mem = ps("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB)")
organs["brain"] = {
    "type": "compute",
    "cpu": cpu,
    "memory_gb": int(mem) if mem.isdigit() else 0,
    "nvme": []
}
nvme_raw = ps("Get-PnpDevice -Class DiskDrive | ForEach-Object { $_.FriendlyName + '|' + $_.Status }")
for line in nvme_raw.split('\n'):
    if '|' in line:
        parts = line.strip().split('|')
        organs["brain"]["nvme"].append({"name": parts[0], "status": parts[1]})

# DIAMOND LENS — Pixel ADB (if connected)
print("  Agglutinating DIAMOND LENS...")
pixel = ps("Get-PnpDevice | Where-Object { $_.InstanceId -match '18D1' } | ForEach-Object { $_.FriendlyName + '|' + $_.Status + '|' + $_.InstanceId }")
if pixel:
    parts = pixel.strip().split('|')
    organs["diamond_lens"] = {
        "type": "sensor/phone",
        "name": parts[0] if len(parts) > 0 else "",
        "status": parts[1] if len(parts) > 1 else "",
        "usb_id": parts[2] if len(parts) > 2 else "",
        "wifi_adb": "192.168.4.114:5555",
        "sensors": 37
    }

# Build the PNS Amoeba
amoeba = {
    "type": "pns-amoeba",
    "gate": GATE,
    "wave": 233,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "organ_count": len(organs),
    "total_cells": sum(
        len(v.get("cells", [])) + len(v.get("gpus", [])) + len(v.get("monitors", [])) + len(v.get("nvme", []))
        for v in organs.values() if isinstance(v, dict)
    ),
    "organs": organs,
}

# BLAKE3 identity
content = json.dumps(amoeba, sort_keys=True)
amoeba["blake3_id"] = hashlib.blake2b(content.encode(), digest_size=32).hexdigest()

# Save
out = os.path.join("data", "gut", f"pns-amoeba-{GATE}.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(amoeba, f, indent=2, ensure_ascii=False)
print(f"\n  Saved: {out}")
print(f"  Organs: {amoeba['organ_count']}")
print(f"  Cells: {amoeba['total_cells']}")
print(f"  BLAKE3: {amoeba['blake3_id'][:16]}...")
print(json.dumps(amoeba, indent=2))
