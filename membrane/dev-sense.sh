#!/system/bin/sh
SENSORIUM="/data/local/tmp/biomeos/sensorium"
mkdir -p "$SENSORIUM"

full_sense() {
    ts=$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)
    focus=$(dumpsys window 2>/dev/null | grep mCurrentFocus | head -1 | sed "s/.*{[^ ]* [^ ]* \([^}]*\)}.*/\1/")
    pkg=$(echo "$focus" | cut -d/ -f1)
    
    gfx=$(dumpsys gfxinfo "$pkg" 2>/dev/null)
    total_frames=$(echo "$gfx" | grep "Total frames rendered" | awk "{print \$NF}")
    janky_count=$(echo "$gfx" | grep "Janky frames" | awk "{print \$3}")
    render_p50=$(echo "$gfx" | grep "50th percentile" | awk "{print \$NF}")
    
    load=$(cat /proc/loadavg 2>/dev/null | awk "{print \$1}")
    mem_free=$(cat /proc/meminfo 2>/dev/null | grep MemAvailable | awk "{print \$2}")
    mem_total=$(cat /proc/meminfo 2>/dev/null | grep MemTotal | awk "{print \$2}")
    
    batt_level=$(dumpsys battery 2>/dev/null | grep "level:" | tr -d " " | cut -d: -f2)
    batt_temp=$(dumpsys battery 2>/dev/null | grep "temperature:" | tr -d " " | cut -d: -f2)
    
    layer_count=$(dumpsys SurfaceFlinger --list 2>/dev/null | wc -l)
    overdraw=$(settings get global debug.hwui.overdraw 2>/dev/null)
    layout_b=$(getprop debug.layout 2>/dev/null)
    brightness=$(settings get system screen_brightness 2>/dev/null)
    pointer_loc=$(settings get system pointer_location 2>/dev/null)
    show_t=$(settings get system show_touches 2>/dev/null)
    force_msaa=$(settings get global force_msaa 2>/dev/null)
    force_gpu=$(settings get global force_hw_ui 2>/dev/null)
    disable_ovl=$(settings get global disable_overlays 2>/dev/null)
    proc_count=$(ps -e 2>/dev/null | wc -l)
    bio_procs=$(ps -ef 2>/dev/null | grep -c biomeos)
    
    if [ -z "$mem_total" ] || [ "$mem_total" = "0" ]; then
        mem_pct=0
    else
        mem_pct=$(( (mem_total - mem_free) * 100 / mem_total ))
    fi
    
    if [ -n "$batt_temp" ]; then
        temp_whole=$((batt_temp / 10))
        temp_frac=$((batt_temp % 10))
        batt_temp_c="${temp_whole}.${temp_frac}"
    else
        batt_temp_c="0"
    fi
    
    cat > "$SENSORIUM/dev-sense.json" << ENDJSON
{
  "timestamp": "$ts",
  "sense": "dev-innerface",
  "cycle_s": 30,
  "focus": "$focus",
  "rendering": {
    "total_frames": ${total_frames:-0},
    "janky_frames": ${janky_count:-0},
    "render_time_50th": "${render_p50:-unknown}",
    "surface_layers": ${layer_count:-0},
    "gpu_overdraw": "${overdraw:-off}",
    "layout_bounds": "${layout_b:-false}",
    "msaa_4x": ${force_msaa:-0},
    "hw_overlays_disabled": ${disable_ovl:-0},
    "force_gpu": ${force_gpu:-0}
  },
  "input": {
    "pointer_location": ${pointer_loc:-0},
    "show_touches": ${show_t:-0}
  },
  "body": {
    "cpu_load": ${load:-0},
    "mem_free_kb": ${mem_free:-0},
    "mem_total_kb": ${mem_total:-0},
    "mem_pct": ${mem_pct:-0},
    "battery_pct": ${batt_level:-0},
    "battery_temp_c": ${batt_temp_c:-0},
    "process_count": ${proc_count:-0},
    "biomeos_procs": ${bio_procs:-0}
  },
  "display": {
    "brightness": ${brightness:-0}
  }
}
ENDJSON
    echo "[dev-sense] $ts focus=$focus frames=${total_frames:-0} janky=${janky_count:-0} layers=${layer_count:-0} load=${load:-0}"
}

if [ "$1" = "daemon" ]; then
    echo "[dev-sense] Starting innerface learning daemon (30s cycle)"
    while true; do
        full_sense
        sleep 30
    done
else
    full_sense
fi
