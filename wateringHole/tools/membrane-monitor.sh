#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# membrane-monitor.sh — Remote membrane health monitor
#
# Runs from ANY gate (northGate, eastGate, sporeGate, blueGate) to check
# bloom, fleet topology, dashboard, layer health — without SSH.
# All data fetched from public HTTPS endpoints.
#
# Usage:
#   ./membrane-monitor.sh              # full dashboard
#   ./membrane-monitor.sh bloom        # bloom status only
#   ./membrane-monitor.sh topology     # entity topology only
#   ./membrane-monitor.sh layers       # layer health only
#   ./membrane-monitor.sh fleet        # fleet activity only
#   ./membrane-monitor.sh watch        # continuous 10s refresh
#
# Requirements: curl, python3 (for JSON formatting)
# No SSH keys needed. No access to sporeGate or golgiBody required.

set -euo pipefail

# ── Endpoints ──
SIGNAL="https://signal.primals.eco"
GOLGI_DE="https://golgi-de.primals.eco"
GOLGI_JP="https://golgi-jp.primals.eco"
GOLGI_US="https://golgi-us.primals.eco"
GOLGI_IN="https://golgi-in.primals.eco"

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
CYN='\033[0;36m'
RST='\033[0m'
BLD='\033[1m'
DIM='\033[2m'

MODE="${1:-all}"

fetch_json() {
    curl -sf --connect-timeout 5 --max-time 10 "$1" 2>/dev/null
}

# ── Dashboard / Bloom ──
show_bloom() {
    local d
    d=$(fetch_json "${SIGNAL}/dashboard.json")
    if [ -z "$d" ]; then
        echo -e "${RED}✗ Dashboard unreachable${RST}"
        return 1
    fi
    python3 << PYEOF
import json, sys
d = json.loads('''$d''')
rps = d.get("rps", 0)
fleet = d.get("fleet_ips", 0)
humans = d.get("human_ips", 0)
total = d.get("total_requests", 0)
uptime = d.get("uptime_secs", 0)
pct = d.get("fleet_pct", 0)
cv = d.get("timing", {}).get("cv", 0)
mc = d.get("timing", {}).get("machine_confidence", "?")
avg_ms = d.get("timing", {}).get("avg_interval_ms", 0)

print("\033[1m🌸 BLOOM STATUS\033[0m")
print("  RPS: \033[1m%.1f\033[0m  |  Fleet IPs: \033[31m%d\033[0m  |  Humans: \033[32m%d\033[0m  |  Fleet%%: %.1f%%" % (rps, fleet, humans, pct))
print("  Total: %d req  |  Uptime: %ds  |  Timing: %sms (CV=%.3f, %s)" % (total, uptime, avg_ms, cv, mc))

pt = d.get("path_types", {})
if pt:
    parts = ["  Paths: "]
    for k, v in sorted(pt.items(), key=lambda x: -x[1]):
        parts.append("%s=%d" % (k, v))
    print(" ".join(parts))

subs = d.get("subnets", [])
if subs:
    print("  Subnets:")
    for s in subs[:5]:
        print("    %-20s %5d req, %2d IPs  %s" % (s["subnet"], s["requests"], s["unique_ips"], s.get("org", "")))

h = d.get("humans", [])
if h:
    print("  Recent humans:")
    for ev in h[-3:]:
        print("    %s  %s  %s" % (ev.get("time", "?"), ev.get("host", "?"), ev.get("country", "?")))
PYEOF
}

# ── Entity Topology ──
show_topology() {
    local d
    d=$(fetch_json "${SIGNAL}/topology.json")
    if [ -z "$d" ]; then
        echo -e "${RED}✗ Topology unreachable${RST}"
        return 1
    fi
    python3 << PYEOF
import json
d = json.loads('''$d''')
print("\033[1m🗺️  ENTITY TOPOLOGY\033[0m  (%d entities, %d log entries analyzed)" % (
    len(d.get("entities", [])), d.get("log_entries_analyzed", 0)))
print()
for e in d.get("entities", []):
    if e["total_requests"] < 2:
        continue
    fleet = "\033[31m⚡ FLEET\033[0m" if e.get("is_fleet") else ""
    honest = "\033[32m✓\033[0m" if e.get("is_honest") else "\033[31m✗\033[0m"
    blame = ""
    if e.get("blame_pct", 0) > 5:
        blame = " | \033[31mblame=%.1f%%\033[0m" % e["blame_pct"]
    print("  %-35s %6d req | %2d IPs | %s %s%s" % (
        e["label"], e["total_requests"], e["unique_ips"], honest, fleet, blame))
    for ss in e.get("sub_systems", []):
        print("    \033[36m⚙ %s\033[0m" % ss["name"])

comp = d.get("comparative_fingerprints", [])
if comp:
    print()
    print("  \033[2m%-28s %4s  %-7s  %-7s  %-22s  %s\033[0m" % (
        "Entity", "IPs", "Chrome", "SecFetch", "Accept-Encoding", "Targets"))
    for c in comp:
        h = "\033[32m✓\033[0m" if c.get("honest") else "\033[31m✗\033[0m"
        print("  %-28s %4d  %-7s  %-7s  %-22s  %s %s" % (
            c["entity"][:28], c["ips"], c["chrome"][:7], c["sec_fetch"],
            c["accept_encoding"][:22], c["target_type"], h))
PYEOF
}

# ── Fleet Activity ──
show_fleet() {
    local d
    d=$(fetch_json "${SIGNAL}/dashboard.json")
    if [ -z "$d" ]; then
        echo -e "${RED}✗ Dashboard unreachable${RST}"
        return 1
    fi
    python3 << PYEOF
import json
d = json.loads('''$d''')
print("\033[1m🦨 FLEET ACTIVITY\033[0m")
print()
offenders = d.get("top_offenders", [])
if offenders:
    print("  \033[2m%-16s %6s  %-25s  %s\033[0m" % ("IP", "Req", "Network", "Targeting"))
    for o in offenders[:15]:
        fleet_mark = "\033[31m●\033[0m" if o.get("is_fleet") else " "
        repos = list((o.get("top_repos") or {}).keys())[:2]
        target = ", ".join(repos) if repos else "?"
        print("  %s %-15s %6d  %-25s  %s" % (
            fleet_mark, o["ip"], o["requests"],
            "%s (%s)" % (o.get("org", "?"), o.get("country", "?")),
            target[:30]))

targets = d.get("targets", [])
if targets:
    print()
    print("  Target repos:")
    for t in targets[:8]:
        print("    %-40s %5d req" % (t["repo"], t["requests"]))
PYEOF
}

# ── Layer Health ──
show_layers() {
    echo -e "${BLD}🏗️  LAYER HEALTH${RST}"
    echo

    # golgiBody (via signal)
    local signal_dash
    signal_dash=$(fetch_json "${SIGNAL}/dashboard.json")
    if [ -n "$signal_dash" ]; then
        local rps
        rps=$(echo "$signal_dash" | python3 -c "import sys,json; print(json.load(sys.stdin).get('rps',0))")
        echo -e "  ${GRN}✓${RST} golgiBody (NYC)     ${SIGNAL}  RPS: ${rps}"
    else
        echo -e "  ${RED}✗${RST} golgiBody (NYC)     ${SIGNAL}  UNREACHABLE"
    fi

    # golgiHetzner (DE)
    local l2
    l2=$(fetch_json "${GOLGI_DE}/metrics")
    if [ -n "$l2" ]; then
        local l2_info
        l2_info=$(echo "$l2" | python3 -c "import sys,json; d=json.load(sys.stdin); print('%s: %d req, %.1f RPS' % (d.get('layer','?'), d.get('total_requests',0), d.get('requests_per_second',0)))")
        echo -e "  ${GRN}✓${RST} golgiHetzner (DE)   ${GOLGI_DE}  ${l2_info}"
    else
        echo -e "  ${RED}✗${RST} golgiHetzner (DE)   ${GOLGI_DE}  UNREACHABLE"
    fi

    # golgiVultr (JP)
    local l3
    l3=$(fetch_json "${GOLGI_JP}/metrics")
    if [ -n "$l3" ]; then
        local l3_info
        l3_info=$(echo "$l3" | python3 -c "import sys,json; d=json.load(sys.stdin); print('%s: %d req, %.1f RPS' % (d.get('layer','?'), d.get('total_requests',0), d.get('requests_per_second',0)))")
        echo -e "  ${GRN}✓${RST} golgiVultr (JP)     ${GOLGI_JP}  ${l3_info}"
    else
        echo -e "  ${RED}✗${RST} golgiVultr (JP)     ${GOLGI_JP}  UNREACHABLE"
    fi

    # golgiOVH (US-VA)
    local l4
    l4=$(fetch_json "${GOLGI_US}/metrics")
    if [ -n "$l4" ]; then
        local l4_info
        l4_info=$(echo "$l4" | python3 -c "import sys,json; d=json.load(sys.stdin); print('%s: %d req, %.1f RPS' % (d.get('layer','?'), d.get('total_requests',0), d.get('requests_per_second',0)))")
        echo -e "  ${GRN}✓${RST} golgiOVH (US-VA)    ${GOLGI_US}  ${l4_info}"
    else
        echo -e "  ${RED}✗${RST} golgiOVH (US-VA)    ${GOLGI_US}  UNREACHABLE"
    fi

    # golgiLinode (IN)
    local l5
    l5=$(fetch_json "${GOLGI_IN}/metrics")
    if [ -n "$l5" ]; then
        local l5_info
        l5_info=$(echo "$l5" | python3 -c "import sys,json; d=json.load(sys.stdin); print('%s: %d req, %.1f RPS' % (d.get('layer','?'), d.get('total_requests',0), d.get('requests_per_second',0)))")
        echo -e "  ${GRN}✓${RST} golgiLinode (IN)    ${GOLGI_IN}  ${l5_info}"
    else
        echo -e "  ${RED}✗${RST} golgiLinode (IN)    ${GOLGI_IN}  UNREACHABLE"
    fi

    # Plasmid federation
    local plasmid
    plasmid=$(fetch_json "${SIGNAL}/feed/conserved-plasmid.json")
    if [ -n "$plasmid" ]; then
        local fed_info
        fed_info=$(echo "$plasmid" | python3 -c "import sys,json; d=json.load(sys.stdin); print('%d bodies, %d epitopes, %d hashes' % (d['federation'].get('layer_count', d['federation'].get('body_count',0)), len(d['conserved_epitopes']), d['behavioral_hashes_summary']['total_unique']))")
        echo -e "  ${GRN}✓${RST} Plasmid Federation  ${fed_info}"
    else
        echo -e "  ${YLW}?${RST} Plasmid Federation  unavailable"
    fi
}

# ── Conserved Plasmid ──
show_plasmid() {
    local d
    d=$(fetch_json "${SIGNAL}/feed/conserved-plasmid.json")
    if [ -z "$d" ]; then
        echo -e "${RED}✗ Plasmid feed unreachable${RST}"
        return 1
    fi
    python3 << PYEOF
import json
d = json.loads('''$d''')
print("\033[1m🧬 CONSERVED PLASMID FEED\033[0m  (v%s)" % d.get("schema", "?").split("/")[-1])
fed = d.get("federation", {})
print("  Layers: %d | Generated: %s" % (fed.get("layer_count", 0), d.get("generated_iso", "?")))
for layer in fed.get("layers", []):
    print("    %s: %d subgroups, %d obs, confidence=%.1f%%" % (
        layer["name"], layer["subgroups"], layer["observations"],
        layer["mean_confidence"] * 100))
pop = d.get("population", {})
print("  Population: %d subgroups, %d observations, mean confidence %.1f%%" % (
    pop.get("total_subgroups", 0), pop.get("total_observations", 0),
    pop.get("mean_confidence", 0) * 100))
epi = d.get("conserved_epitopes", [])
if epi:
    print("  Conserved epitopes:")
    for e in epi[:8]:
        print("    %-30s %3d%%  (observed in %d layers)" % (
            e["name"], e["frequency_pct"], e["layers_observed"]))
rules = d.get("detection_rules", {})
if rules:
    print("  Detection rules: %d (threshold: %d)" % (len(rules.get("rules", [])), rules.get("threshold", 0)))
PYEOF
}

# ── Live Feed (last lines) ──
show_live() {
    echo -e "${BLD}📡 LIVE FEED (last 15 lines)${RST}"
    curl -sf --connect-timeout 5 "${SIGNAL}/live" 2>/dev/null | tail -15
}

# ── Full Dashboard ──
show_all() {
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo -e "${BLD}  membrane-monitor — $(date -u '+%Y-%m-%d %H:%M:%S UTC')${RST}"
    echo -e "${BLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
    echo
    show_bloom
    echo
    show_topology
    echo
    show_layers
    echo
}

# ── Watch Mode ──
watch_mode() {
    while true; do
        clear
        show_all
        echo -e "${DIM}refreshing in 10s... (Ctrl+C to stop)${RST}"
        sleep 10
    done
}

# ── Dispatch ──
case "$MODE" in
    bloom)    show_bloom ;;
    topology) show_topology ;;
    fleet)    show_fleet ;;
    layers)   show_layers ;;
    plasmid)  show_plasmid ;;
    live)     show_live ;;
    watch)    watch_mode ;;
    all)      show_all ;;
    *)
        echo "Usage: $0 [bloom|topology|fleet|layers|plasmid|live|watch|all]"
        exit 1
        ;;
esac
