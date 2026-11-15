#!/data/data/com.termux/files/usr/bin/bash
export HOME="/data/data/com.termux/files/home"
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
export LD_LIBRARY_PATH="/data/data/com.termux/files/usr/lib"

echo "=== SENSOR TEST ==="
echo "PATH: $PATH"
which python3
echo "---wifi---"
termux-wifi-scaninfo 2>&1 | head -3
echo "---pressure raw---"
termux-sensor -s "ICP20100 Pressure Sensor" -n 1 2>&1 | head -10
echo "---pressure parsed---"
termux-sensor -s "ICP20100 Pressure Sensor" -n 1 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(round(list(d.values())[0]['values'][0],2))" 2>&1
echo "---done---"
