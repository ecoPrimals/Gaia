@echo off
title biomeOS — AMALGAM BOOT — pre-membrane first
color 0E
echo.
echo   PRE-MEMBRANE. Biofilm. Then amalgam. Then Golgi.
echo.

cd /d C:\Users\mokke\Desktop\Gaia3
node membrane.js
if errorlevel 1 (
  echo   MEMBRANE HELD. Not starting a second mouth.
  exit /b 1
)

REM one Golgi only. Do NOT start golgi/server.js.
netstat -ano | findstr ":9878" | findstr LISTENING >nul || start "SPINE" /MIN cmd /c "cd /d C:\Users\mokke\Desktop\Gaia && node serve_spine.js"
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":3141" | findstr LISTENING >nul || start "NICHE" /MIN cmd /c "cd /d C:\Users\mokke\Desktop\Gaia && node golgi-local.js"
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":3143" | findstr LISTENING >nul || start "CHILD" /MIN cmd /c "node C:\Users\mokke\Desktop\Gaia3\gaia3-local.js"

echo   Polar of itself. House LAN may look. No new public door.
echo.
