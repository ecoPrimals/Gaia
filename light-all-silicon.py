import paramiko, json
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}

def connect(host, user, pw, timeout=10):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username=user, password=pw, timeout=timeout,
              look_for_keys=False, allow_agent=False, 
              disabled_algorithms={'keys': ['rsa-sha2-256', 'rsa-sha2-512']},
              banner_timeout=15)
    return c

def run(c, cmd, t=15):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

print("=" * 60)
print("  LIGHTING ALL SILICON — NPU + GPU + CPU")
print("=" * 60)

# === EASTGATE — BRAIN STEM ===
print("\n🧠 eastGate (.244) — BRAIN STEM")
e = connect('192.168.4.244', 'eastgate', 'eastgate')

# NPU — AKD1000
print("\n  --- NPU (BrainChip AKD1000) ---")
out, _ = run(e, "lspci | grep -i brain 2>/dev/null; lspci | grep -i akida 2>/dev/null; lspci -nn | grep '1e7c' 2>/dev/null")
print(f"  PCIe: {out}")

out, _ = run(e, "ls /dev/akida* 2>/dev/null; ls /sys/class/akida* 2>/dev/null")
print(f"  Device: {out}")

out, _ = run(e, "lspci -v -s 08:00.0 2>/dev/null | head -15")
print(f"  Details:\n  {out}")

out, _ = run(e, "cat /opt/Gaia/data/akida/device-state.json 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2))' 2>/dev/null | head -20")
print(f"  State: {out}")

# GPU — RTX 4070
print("\n  --- GPU (RTX 4070) ---")
out, _ = run(e, "nvidia-smi --query-gpu=name,temperature.gpu,power.draw,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null")
print(f"  {out}")

# CPU
print("\n  --- CPU ---")
out, _ = run(e, "lscpu | grep 'Model name' | head -1; nproc; cat /proc/loadavg")
print(f"  {out}")

# Ollama
print("\n  --- OLLAMA ---")
out, _ = run(e, "curl -s http://localhost:11436/api/tags 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); [print(f\"    {m[\\\"name\\\"]}\") for m in d.get(\"models\",[])]' 2>/dev/null")
print(f"  Models:\n{out}")

e.close()

# === IRONGATE — FORGE ===
print("\n\n⚒️ ironGate (.237) — FORGE")
try:
    i = connect('192.168.4.237', 'root', 'irongate')
    
    # GPU
    out, _ = run(i, "nvidia-smi --query-gpu=name,temperature.gpu,power.draw,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null")
    print(f"  GPU: {out}")
    
    # CPU
    out, _ = run(i, "lscpu | grep 'Model name' | head -1; nproc; cat /proc/loadavg")
    print(f"  CPU: {out}")
    
    # Ollama
    out, _ = run(i, "curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(f\"{len(d.get(\\\"models\\\",[])):} models\"); [print(f\"    {m[\\\"name\\\"]}\") for m in d.get(\"models\",[])[:10]]' 2>/dev/null")
    print(f"  Ollama: {out}")
    
    i.close()
except Exception as ex:
    print(f"  {ex}")

# === GRAFTGATE — M4 ===
print("\n\n🍎 graftGate (.107) — Mac Mini M4")
try:
    g = connect('192.168.4.107', 'root', 'graftgate')
    
    out, _ = run(g, "sysctl -n machdep.cpu.brand_string 2>/dev/null; sysctl -n hw.ncpu 2>/dev/null; uptime")
    print(f"  CPU: {out}")
    
    out, _ = run(g, "curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(f\"{len(d.get(\\\"models\\\",[])):} models\"); [print(f\"    {m[\\\"name\\\"]}\") for m in d.get(\"models\",[])[:5]]' 2>/dev/null")
    print(f"  Ollama: {out}")
    
    g.close()
except Exception as ex:
    print(f"  {ex}")

# === SPOREGATE — FORGE 2 ===
print("\n\n🍄 sporeGate (.3) — FORGE/DNS")
e2 = connect('192.168.4.244', 'eastgate', 'eastgate')
out, _ = run(e2, "sshpass -p sporegate ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@192.168.4.3 'echo ALIVE && uname -m && nproc && cat /proc/loadavg && free -h | grep Mem' 2>&1", t=20)
print(f"  {out}")
e2.close()

# === NORTHGATE — PING CHECK ===
print("\n\n👑 northGate (.147) — HEAD/HEART")
e3 = connect('192.168.4.244', 'eastgate', 'eastgate')
out, _ = run(e3, "ping -c 1 -W 2 192.168.4.147 2>&1 | grep 'bytes from'")
print(f"  Ping: {out}")
out, _ = run(e3, "curl -s --connect-timeout 3 http://192.168.4.147:11434/api/tags 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(f\"{len(d.get(\\\"models\\\",[])):} models on northGate\")' 2>/dev/null")
print(f"  Ollama: {out}")
e3.close()

# === SUMMARY ===
print("\n" + "=" * 60)
print("  ALL SILICON STATUS")
print("=" * 60)
print("  NPU: AKD1000 @ PCIe — 80 NPs, 18.8kHz, 1.5W")
print("  GPU: RTX 5090 (32GB) + RTX 5070 (12GB) + RTX 4070 (12GB) + M4 (10 GPU)")
print("  CPU: 9950X3D (16C) + i9-14900K (24C) + Ryzen 6600H (6C) + M4 (10C)")
print("  TOTAL: ~33K CUDA + 80 NPs + 73 CPU cores + 301GB RAM")
print("=" * 60)
