import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)

def run(cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=== steamFRAME — PINEAL EYE CHECK ===\n")

# BT adapter status
out, _ = run("hciconfig hci0 2>/dev/null")
print(f"BT Adapter:\n{out}\n")

# steamFRAME paired?
out, _ = run("bluetoothctl info 90:82:C3:74:12:CB 2>/dev/null")
print(f"steamFRAME info:\n{out}\n")

# Is it connected right now?
out, _ = run("bluetoothctl devices Connected 2>/dev/null")
print(f"Connected devices: {out}")

# Try to reconnect if not connected
out, _ = run("bluetoothctl connect 90:82:C3:74:12:CB 2>/dev/null")
print(f"\nConnect attempt: {out}")

import time
time.sleep(3)

# Check again
out, _ = run("bluetoothctl info 90:82:C3:74:12:CB 2>/dev/null | grep -E 'Connected|Name|Paired|Trusted'")
print(f"\nPost-connect status:\n{out}")

# Check BNEP / PAN for IP-over-BT
out, _ = run("lsmod | grep bnep; ip link show bnep0 2>/dev/null")
print(f"\nBNEP: {out}")

# Check if we can reach frameGate over WiFi
out, _ = run("ping -c 2 -W 2 192.168.9.203 2>&1 | tail -3")
print(f"\nframeGate WiFi ping: {out}")

# BT scan for nearby
out, _ = run("timeout 5 bluetoothctl scan on 2>/dev/null &; sleep 4; bluetoothctl devices 2>/dev/null | grep -i steam")
print(f"\nBT scan for Steam: {out}")

c.close()
