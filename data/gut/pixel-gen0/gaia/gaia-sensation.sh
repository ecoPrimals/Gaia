#!/data/data/com.termux/files/usr/bin/bash
# GAIA SENSATION PANEL — Shadow Cast Signal Router
# Tracks all sensor streams, attenuates, writes to beacon

BEACON=/sdcard/gaia/sensation.json
LOG=/sdcard/gaia/sensation.log

sense_once() {
  local TS=$(date -Iseconds)
  
  # Battery (0dB — direct)
  local BATT=$(termux-battery-status 2>/dev/null)
  
  # WiFi (-33dB attenuation)
  local WIFI=$(termux-wifi-connectioninfo 2>/dev/null)
  
  # Motion sensors (accelerometer, gyro, magnetometer)
  local MOTION=$(termux-sensor -s "LSM6DSV Accelerometer,LSM6DSV Gyroscope,MMC56X3X Magnetometer" -n 1 2>/dev/null)
  
  # Environment sensors (light, pressure, temperature, proximity)
  local ENV=$(termux-sensor -s "TMD3719 Ambient Light,ICP20100 Pressure Sensor,LSM6DSV Temperature,TMD3719 Proximity" -n 1 2>/dev/null)
  
  # Compose
  echo "{" > $BEACON
  echo "  \"ts\": \"$TS\"," >> $BEACON
  echo "  \"gate\": \"grapheneGate\"," >> $BEACON  
  echo "  \"cast\": \"shadow\"," >> $BEACON
  echo "  \"battery\": $BATT," >> $BEACON
  echo "  \"wifi\": $WIFI," >> $BEACON
  echo "  \"motion\": $MOTION," >> $BEACON
  echo "  \"environment\": $ENV" >> $BEACON
  echo "}" >> $BEACON
  
  echo "[$TS] sensation written" >> $LOG
}

echo "[$(date -Iseconds)] SENSATION PANEL ACTIVE" >> $LOG
sense_once
echo "done"
