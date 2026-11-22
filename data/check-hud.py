import urllib.request, json
r = urllib.request.urlopen("http://localhost:8888/stats", timeout=5)
s = json.loads(r.read())
g = s.get("gpu", {})
k = s.get("kenshi", {})
ram = s.get("ram", {})
sq = s.get("squad", [])
print(f'  GPU: {g.get("temp","?")}C, {g.get("util","?")}% load, {g.get("vram_used",0)//1024}/{g.get("vram_total",0)//1024} GB VRAM')
print(f'  Power: {g.get("power",0):.0f}W, Clocks: {g.get("clock_core","?")} / {g.get("clock_mem","?")} MHz')
print(f'  CPU: {s.get("cpu_load","?")}%')
print(f'  RAM: {ram.get("used_gb","?")}/{ram.get("total_gb","?")} GB')
running = "ALIVE" if k.get("running") else "DOWN"
print(f'  Kenshi: {running} (PID {k.get("pid","-")}, {k.get("mem_mb",0)} MB)')
print(f'  Squad: {len(sq)} members')
for m in sq:
    print(f'    {m["name"]}: {m["temperament"]} (trust {m["trust"]}, {m["taps"]} taps)')
    if m.get("last_memory"):
        print(f'      last: {m["last_memory"][:80]}')
