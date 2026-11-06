#!/data/data/com.termux/files/usr/bin/bash
# GAIA ROVER BEACON — grapheneGate sensor stream
# Collects all sensor data and writes to /sdcard/gaia/beacon.json

OUT=/sdcard/gaia/beacon.json
TMP=/sdcard/gaia/beacon-tmp.json

while true; do
  # Collect all sensors
  BATT=$(termux-battery-status 2>/dev/null)
  WIFI=$(termux-wifi-connectioninfo 2>/dev/null)
  ACCEL=$(termux-sensor -s "LSM6DSV Accelerometer" -n 1 2>/dev/null)
  LIGHT=$(termux-sensor -s "TMD3719 Ambient Light" -n 1 2>/dev/null)
  PRESS=$(termux-sensor -s "ICP20100 Pressure Sensor" -n 1 2>/dev/null)
  GYRO=$(termux-sensor -s "LSM6DSV Gyroscope" -n 1 2>/dev/null)
  MAG=$(termux-sensor -s "MMC56X3X Magnetometer" -n 1 2>/dev/null)
  PROX=$(termux-sensor -s "TMD3719 Proximity" -n 1 2>/dev/null)
  TEMP=$(termux-sensor -s "LSM6DSV Temperature" -n 1 2>/dev/null)

  # Build JSON
  echo "{" > $TMP
  echo "  \"ts\": \"$(date -Iseconds)\"," >> $TMP
  echo "  \"gate\": \"grapheneGate\"," >> $TMP
  echo "  \"device\": \"Pixel 8a\"," >> $TMP
  echo "  \"battery\": $BATT," >> $TMP
  echo "  \"wifi\": $WIFI," >> $TMP
  echo "  \"accelerometer\": $ACCEL," >> $TMP
  echo "  \"light\": $LIGHT," >> $TMP
  echo "  \"pressure\": $PRESS," >> $TMP
  echo "  \"gyroscope\": $GYRO," >> $TMP
  echo "  \"magnetometer\": $MAG," >> $TMP
  echo "  \"proximity\": $PROX," >> $TMP
  echo "  \"temperature\": $TEMP" >> $TMP
  echo "}" >> $TMP
  
  mv $TMP $OUT
  echo "[$(date)] beacon written"
  sleep 30
done
