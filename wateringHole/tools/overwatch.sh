#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# overwatch.sh — eastGate ecosystem monitoring & study system
#
# The central nervous system of ecoPrimals overwatch.
# Monitors: local primals, beehive mesh, fleet activity, gate health.
# Runs from eastGate only (requires local socket access + WG mesh).
#
# Usage:
#   ./overwatch.sh                # full dashboard
#   ./overwatch.sh primals        # local primal health
#   ./overwatch.sh mesh           # beehive sensor mesh status
#   ./overwatch.sh fleet          # fleet activity across all sensors
#   ./overwatch.sh gates          # gate liveness
#   ./overwatch.sh matrix         # sensor × entity cross-matrix
#   ./overwatch.sh temporal       # repo sync divergence
#   ./overwatch.sh study          # deep study mode (all data, verbose)
#   ./overwatch.sh watch          # continuous refresh
#
# Requirements: curl, python3, socat (for UDS health checks)
# WireGuard tunnel to golgiBody for internal checks.

set -euo pipefail

# ── Configuration ──
SOCKET_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/biomeos"
SIGNAL="https://signal.primals.eco"
GOLGI_DE="https://golgi-de.primals.eco"   # Hetzner Falkenstein
GOLGI_JP="https://golgi-jp.primals.eco"   # Vultr Tokyo
GOLGI_US="https://golgi-us.primals.eco"   # OVH Virginia
GOLGI_IN="https://golgi-in.primals.eco"   # Linode Mumbai
WG_GOLGI="10.13.37.1"
FORGEJO="https://git.primals.eco"

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
CYN='\033[0;36m'
MAG='\033[0;35m'
RST='\033[0m'
BLD='\033[1m'
DIM='\033[2m'

MODE="${1:-all}"

fetch_json() {
    curl -sf --connect-timeout 5 --max-time 10 "$1" 2>/dev/null
}

# ── Local Primal Health ──
show_primals() {
    echo -e "${BLD}🧬 LOCAL PRIMALS${RST}  (eastGate)"
    echo

    local total=0 running=0 failed=0 restarting=0

    while IFS= read -r line; do
        local unit=$(echo "$line" | awk '{print $1}')
        local load=$(echo "$line" | awk '{print $2}')
        local active=$(echo "$line" | awk '{print $3}')
        local sub=$(echo "$line" | awk '{print $4}')
        local name=$(echo "$unit" | sed 's/membrane-nucleus@//;s/\.service//')

        total=$((total + 1))

        if [ "$active" = "active" ] && [ "$sub" = "running" ]; then
            running=$((running + 1))
            local icon="${GRN}✓${RST}"
        elif [ "$sub" = "auto-restart" ]; then
            restarting=$((restarting + 1))
            local icon="${YLW}↻${RST}"
        else
            failed=$((failed + 1))
            local icon="${RED}✗${RST}"
        fi

        # Check UDS socket
        local sock_status=""
        if [ -S "${SOCKET_DIR}/${name}.sock" ]; then
            local health=$(echo '{"jsonrpc":"2.0","method":"health.ping","id":1}' | timeout 1 socat - UNIX-CONNECT:"${SOCKET_DIR}/${name}.sock" 2>/dev/null | head -1)
            if [ -n "$health" ]; then
                sock_status="${GRN}●${RST}"
            else
                sock_status="${YLW}○${RST}"
            fi
        else
            sock_status="${RED}○${RST}"
        fi

        printf "  %b %b %-18s %s/%s\n" "$icon" "$sock_status" "$name" "$active" "$sub"
    done < <(systemctl --user list-units "membrane-nucleus@*" --no-legend 2>/dev/null)

    echo
    printf "  Total: %d  |  ${GRN}Running: %d${RST}" "$total" "$running"
    [ "$restarting" -gt 0 ] && printf "  |  ${YLW}Restarting: %d${RST}" "$restarting"
    [ "$failed" -gt 0 ] && printf "  |  ${RED}Failed: %d${RST}" "$failed"
    echo

    # Socket count
    local sock_count=$(ls "${SOCKET_DIR}"/*.sock 2>/dev/null | wc -l)
    local tarpc_count=$(ls "${SOCKET_DIR}"/*.tarpc.sock 2>/dev/null | wc -l)
    echo -e "  Sockets: ${sock_count} UDS + ${tarpc_count} tarpc"

    # System resources
    echo
    echo -e "  ${DIM}CPU: $(nproc) cores | Load: $(awk '{print $1"/"$2"/"$3}' /proc/loadavg)"
    echo -e "  RAM: $(free -h | awk '/Mem:/ {print $3 " used / " $2 " total (" $7 " available)"}')"
    echo -e "  Disk: $(df -h / | tail -1 | awk '{print $3 " used / " $2 " (" $5 " full)"}')"
    echo -e "  Uptime: $(uptime -p)${RST}"
}

# ── Beehive Mesh Status ──
show_mesh() {
    echo -e "${BLD}🐝 BEEHIVE MESH${RST}"
    echo

    # golgiBody via WG
    local wg_ms=$(ping -c 1 -W 2 "${WG_GOLGI}" 2>/dev/null | awk -F'time=' '/time=/{print $2}' | awk '{print $1}')
    if [ -n "$wg_ms" ]; then
        echo -e "  ${GRN}✓${RST} WireGuard tunnel: ${WG_GOLGI} (${wg_ms}ms)"
    else
        echo -e "  ${RED}✗${RST} WireGuard tunnel: ${WG_GOLGI} unreachable"
    fi
    echo

    # golgiBody (primary)
    local dash=$(fetch_json "${SIGNAL}/dashboard.json")
    if [ -n "$dash" ]; then
        python3 << PYEOF
import json
d = json.loads('''$dash''')
rps = d.get("rps", 0)
fleet = d.get("fleet_ips", 0)
humans = d.get("human_ips", 0)
uptime = d.get("uptime_secs", 0)
total = d.get("total_requests", 0)
pct = d.get("fleet_pct", 0)
print("  \033[32m✓\033[0m golgiBody (NYC \033[2m40.71°N\033[0m)")
print("    RPS: \033[1m%.1f\033[0m | Fleet: \033[31m%d\033[0m IPs | Humans: \033[32m%d\033[0m | Fleet%%: %.1f%%" % (rps, fleet, humans, pct))
print("    Total: %d req | Uptime: %ds" % (total, uptime))

# Recent events
h = d.get("humans", [])
if h:
    latest = h[-1]
    print("    Last human: %s from %s (%s)" % (latest.get("time","?"), latest.get("host","?"), latest.get("country","?")))
PYEOF
    else
        echo -e "  ${RED}✗${RST} golgiBody — unreachable"
    fi

    # golgiHetzner (DE)
    local l2=$(fetch_json "${GOLGI_DE}/metrics")
    if [ -n "$l2" ]; then
        python3 << PYEOF
import json
d = json.loads('''$l2''')
print("  \033[32m✓\033[0m golgiHetzner (DE \033[2m50.47°N\033[0m)")
print("    Req: %d | RPS: %.2f | Scatter: %d | Plasmid: %d | Honeytoken: %d" % (
    d.get("total_requests",0), d.get("requests_per_second",0),
    d.get("breakdown",{}).get("scatter",0),
    d.get("breakdown",{}).get("plasmid",0),
    d.get("breakdown",{}).get("honeytoken",0)))
PYEOF
    else
        echo -e "  ${RED}✗${RST} golgiHetzner — unreachable"
    fi

    # golgiVultr (JP)
    local l3=$(fetch_json "${GOLGI_JP}/metrics")
    if [ -n "$l3" ]; then
        python3 << PYEOF
import json
d = json.loads('''$l3''')
print("  \033[32m✓\033[0m golgiVultr (JP \033[2m35.68°N\033[0m)")
print("    Req: %d | RPS: %.2f" % (d.get("total_requests",0), d.get("requests_per_second",0)))
PYEOF
    else
        echo -e "  ${RED}✗${RST} golgiVultr (JP) — unreachable"
    fi

    # golgiOVH (US-VA)
    local l4=$(fetch_json "${GOLGI_US}/metrics")
    if [ -n "$l4" ]; then
        python3 << PYEOF
import json
d = json.loads('''$l4''')
print("  \033[32m✓\033[0m golgiOVH (US-VA \033[2m38.95°N\033[0m)")
print("    Req: %d | RPS: %.2f" % (d.get("total_requests",0), d.get("requests_per_second",0)))
PYEOF
    else
        echo -e "  ${RED}✗${RST} golgiOVH (US-VA) — unreachable"
    fi

    # golgiLinode (IN)
    local l5=$(fetch_json "${GOLGI_IN}/metrics")
    if [ -n "$l5" ]; then
        python3 << PYEOF
import json
d = json.loads('''$l5''')
print("  \033[32m✓\033[0m golgiLinode (IN \033[2m19.08°N\033[0m)")
print("    Req: %d | RPS: %.2f" % (d.get("total_requests",0), d.get("requests_per_second",0)))
PYEOF
    else
        echo -e "  ${RED}✗${RST} golgiLinode (IN) — unreachable"
    fi

    echo
    # Plasmid federation
    local plasmid=$(fetch_json "${SIGNAL}/feed/conserved-plasmid.json")
    if [ -n "$plasmid" ]; then
        python3 << PYEOF
import json
d = json.loads('''$plasmid''')
fed = d.get("federation", {})
epi = d.get("conserved_epitopes", [])
print("  \033[1m🧬 Plasmid Federation\033[0m")
print("    Layers: %d | Epitopes: %d | Rules: %d" % (
    fed.get("layer_count",0), len(epi),
    len(d.get("detection_rules",{}).get("rules",[]))))
for e in epi[:4]:
    print("    • %-25s %3d%%" % (e["name"], e["frequency_pct"]))
if len(epi) > 4:
    print("    ... +%d more" % (len(epi) - 4))
PYEOF
    fi
}

# ── Fleet Activity ──
show_fleet() {
    echo -e "${BLD}🦨 FLEET ACTIVITY${RST}"
    echo

    local topo=$(fetch_json "${SIGNAL}/topology.json")
    if [ -z "$topo" ]; then
        echo -e "  ${RED}✗ Topology unreachable${RST}"
        return 1
    fi

    python3 << PYEOF
import json
d = json.loads('''$topo''')
entities = d.get("entities", [])
total_req = sum(e["total_requests"] for e in entities)
total_ips = sum(e["unique_ips"] for e in entities)
fleet_entities = [e for e in entities if e.get("is_fleet")]
honest_entities = [e for e in entities if e.get("is_honest")]

print("  Entities: %d | Fleet: %d | Honest: %d | Total req: %d | Total IPs: %d" % (
    len(entities), len(fleet_entities), len(honest_entities), total_req, total_ips))
print()

for e in entities:
    if e["total_requests"] < 2:
        continue
    fleet = "\033[31m⚡\033[0m" if e.get("is_fleet") else " "
    honest = "\033[32m✓\033[0m" if e.get("is_honest") else "\033[31m✗\033[0m"
    blame = ""
    if e.get("blame_pct", 0) > 5:
        blame = " \033[31mblame=%.1f%%\033[0m" % e["blame_pct"]

    # Timing classification
    timing = e.get("timing", {})
    tc = timing.get("classification", "?")
    cv = timing.get("cv", 0)
    timing_str = "%s (CV=%.3f)" % (tc, cv) if cv > 0 else ""

    print("  %s %s %-32s %6d req | %2d IPs | %s%s" % (
        fleet, honest, e["label"][:32], e["total_requests"], e["unique_ips"],
        timing_str, blame))

    # Sub-systems
    for ss in e.get("sub_systems", []):
        print("       \033[36m⚙ %s\033[0m" % ss["name"])

    # Top repos
    repos = e.get("top_repos", [])
    if repos:
        real = [r for r in repos if r.get("is_real")]
        scatter = [r for r in repos if not r.get("is_real")]
        if real:
            top3 = ", ".join(r["repo"] for r in real[:3])
            print("       📂 Real: %s" % top3)
        if scatter:
            print("       🎭 Scatter: %d fake repos consumed" % len(scatter))
    print()

# Comparative fingerprints table
comp = d.get("comparative_fingerprints", [])
if comp:
    print("  \033[2m%-28s %4s  %-8s  %-8s  %-20s  %s\033[0m" % (
        "Entity", "IPs", "Chrome", "SecFetch", "Accept-Enc", "Targets"))
    for c in comp:
        h = "\033[32m✓\033[0m" if c.get("honest") else "\033[31m✗\033[0m"
        print("  %-28s %4d  %-8s  %-8s  %-20s  %s %s" % (
            c["entity"][:28], c["ips"], c["chrome"][:8],
            c["sec_fetch"][:8], c["accept_encoding"][:20],
            c["target_type"][:12], h))
PYEOF
}

# ── Gate Health ──
show_gates() {
    echo -e "${BLD}🏛️  GATE HEALTH${RST}"
    echo

    # eastGate (local)
    echo -e "  ${GRN}✓${RST} ${BLD}eastGate${RST} (local) — $(uptime -p)"
    local primal_count=$(systemctl --user list-units "membrane-nucleus@*" --no-legend 2>/dev/null | grep -c "running")
    echo "    Primals: ${primal_count} running | CPU: $(nproc) cores | RAM: $(free -h | awk '/Mem:/ {print $7}') avail"
    echo

    # golgiBody via WG
    local wg_ms=$(ping -c 1 -W 2 "${WG_GOLGI}" 2>/dev/null | awk -F'time=' '/time=/{print $2}' | awk '{print $1}')
    if [ -n "$wg_ms" ]; then
        echo -e "  ${GRN}✓${RST} ${BLD}golgiBody${RST} (WG: ${wg_ms}ms)"
        # Check Forgejo
        local forgejo_status=$(curl -sf -o /dev/null -w "%{http_code}" --connect-timeout 3 "${FORGEJO}/api/v1/version" 2>/dev/null)
        [ "$forgejo_status" = "200" ] && echo "    Forgejo: online" || echo "    Forgejo: ${forgejo_status}"
        # Check membrane
        local dash=$(fetch_json "${SIGNAL}/dashboard.json")
        if [ -n "$dash" ]; then
            local rps=$(echo "$dash" | python3 -c "import sys,json; print(json.load(sys.stdin).get('rps',0))")
            echo "    Membrane: ${rps} RPS"
        fi
    else
        echo -e "  ${RED}✗${RST} ${BLD}golgiBody${RST} — WG unreachable"
    fi
    echo

    # sporeGate (check via Forgejo API if any recent pushes)
    echo -e "  ${DIM}?${RST} ${BLD}sporeGate${RST} — no direct link (downstream via Forgejo)"

    # Other gates (dormant)
    for gate in westGate ironGate strandGate blueGate northGate; do
        echo -e "  ${DIM}○${RST} ${DIM}${gate} — dormant${RST}"
    done
}

# ── Cross-Matrix ──
show_matrix() {
    echo -e "${BLD}🌍 SENSOR × ENTITY CROSS-MATRIX${RST}"
    echo

    # Gather data from all available sensors
    python3 << 'PYEOF'
import json, urllib.request, sys

sensors = {
    "NYC": {"url": "https://signal.primals.eco/topology.json", "lat": 40.71, "lon": -74.01, "status": "live"},
    "DE":  {"url": None, "lat": 50.47, "lon": 12.37, "status": "live (no topology yet)"},
    "IN":  {"url": None, "lat": 19.08, "lon": 72.88, "status": "hardened"},
}

# Fetch NYC topology (the only one with entity data so far)
try:
    with urllib.request.urlopen("https://signal.primals.eco/topology.json", timeout=10) as r:
        nyc_data = json.loads(r.read())
except Exception as e:
    print(f"  ✗ Could not fetch NYC topology: {e}")
    sys.exit(0)

entities = [e for e in nyc_data.get("entities", []) if e["total_requests"] >= 2]

# Header
cols = ["NYC 🇺🇸", "DE 🇩🇪", "IN 🇮🇳", "VA 🇺🇸", "UK 🇬🇧"]
header = "  %-30s" % "Entity"
for c in cols:
    header += "  %-14s" % c
print(header)
print("  " + "─" * 100)

for e in entities:
    row = "  %-30s" % e["label"][:30]
    # NYC column (have data)
    nyc_cell = "%dIP %.1fr/s" % (e["unique_ips"], e.get("avg_rps", 0))
    row += "  %-14s" % nyc_cell
    # Other columns (pending)
    for _ in range(4):
        row += "  \033[2m%-14s\033[0m" % "(pending)"
    print(row)

    # Detail row
    blame = e.get("blame_pct", 0)
    timing = e.get("timing", {})
    cv = timing.get("cv", 0)
    chrome = max((int(k) for k in e.get("chrome_versions", {}).keys()), default=0) if e.get("chrome_versions") else 0
    detail = "    "
    if blame > 0:
        detail += "blame=%.0f%% " % blame
    if cv > 0:
        detail += "cv=%.3f " % cv
    if chrome > 0:
        detail += "chrome=%d " % chrome
    if e.get("targets_real_only"):
        detail += "\033[31mREAL\033[0m "
    elif e.get("targets_scatter_only"):
        detail += "\033[32mSCATTER\033[0m "
    if detail.strip():
        print(detail)

print()
print("  \033[2mLegend: IP=unique IPs, r/s=requests/sec")
print("  Columns fill as sensors come online and fleet discovers them via CT logs\033[0m")
PYEOF
}

# ── Temporal Divergence ──
show_temporal() {
    echo -e "${BLD}📜 REPO SYNC STATUS${RST}  (via Forgejo API)"
    echo

    local script="/home/eastgate/Development/ecoPrimals/infra/wateringHole/scripts/overwatch-temporal.sh"
    if [ -x "$script" ]; then
        bash "$script" 2>/dev/null | head -30
    else
        echo "  (overwatch-temporal.sh not found — run manually)"
    fi
}

# ── Study Mode (everything, verbose) ──
show_study() {
    show_primals
    echo
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo
    show_mesh
    echo
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo
    show_fleet
    echo
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo
    show_matrix
    echo
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo
    show_gates
}

# ── Full Dashboard ──
show_all() {
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo -e "${BLD}  🛡️  eastGate overwatch — $(date -u '+%Y-%m-%d %H:%M:%S UTC')${RST}"
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo
    show_primals
    echo
    show_mesh
    echo
    show_gates
    echo
}

# ── Watch Mode ──
watch_mode() {
    while true; do
        clear
        show_all
        echo -e "${DIM}refreshing in 15s... (Ctrl+C to stop)${RST}"
        sleep 15
    done
}

# ── Dispatch ──
case "$MODE" in
    primals)   show_primals ;;
    mesh)      show_mesh ;;
    fleet)     show_fleet ;;
    gates)     show_gates ;;
    matrix)    show_matrix ;;
    temporal)  show_temporal ;;
    study)     show_study ;;
    watch)     watch_mode ;;
    all)       show_all ;;
    *)
        echo "Usage: $0 [primals|mesh|fleet|gates|matrix|temporal|study|watch|all]"
        exit 1
        ;;
esac
