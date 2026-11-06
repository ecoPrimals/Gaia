#!/data/data/com.termux/files/usr/bin/bash
export PATH=/data/data/com.termux/files/usr/bin:$PATH
export LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib
termux-sensor -s "LSM6DSV Accelerometer,TMD3719 Ambient Light,ICP20100 Pressure Sensor" -n 1 2>/dev/null > /sdcard/gaia/sensors.json
termux-battery-status > /sdcard/gaia/battery.json 2>/dev/null
termux-wifi-connectioninfo > /sdcard/gaia/wifi.json 2>/dev/null
termux-location -p gps -r once > /sdcard/gaia/location.json 2>/dev/null &
echo '{"status":"sensors_read","ts":"'2026-11-05T22:07:28-05:00'"}' > /sdcard/gaia/status.json
