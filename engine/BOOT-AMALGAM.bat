@echo off
title biomeOS — AMALGAM BOOT — all modules from engine/
color 0E
echo.
echo   GAIA ENGINE — AMALGAM BOOT
echo   All modules launch from engine/
echo   No C:\Users. No hardcoded paths. USB portable.
echo.

set ENGINE=%~dp0
set GAIA=%ENGINE%..

cd /d "%ENGINE%"
node membrane.js
if errorlevel 1 (
  echo   MEMBRANE HELD. Not starting a second mouth.
  exit /b 1
)

REM SPINE
netstat -ano | findstr ":9878" | findstr LISTENING >nul || start "SPINE" /MIN cmd /c "cd /d "%ENGINE%" && node serve_spine.js"
timeout /t 1 /nobreak >nul

REM GOLGI (parent niche on :3141)
netstat -ano | findstr ":3141" | findstr LISTENING >nul || start "NICHE" /MIN cmd /c "cd /d "%GAIA%" && node golgi-local.js"
timeout /t 1 /nobreak >nul

REM IRIS step function
netstat -ano | findstr ":31416" | findstr LISTENING >nul || start "IRIS" /MIN cmd /c "node "%ENGINE%iris.js""
timeout /t 1 /nobreak >nul

REM WireGuard proxy
start "WGPROXY" /MIN cmd /c "node "%ENGINE%wireguard-proxy.js""
timeout /t 1 /nobreak >nul

REM Archetype Forge
netstat -ano | findstr ":3149" | findstr LISTENING >nul || start "ARCHFORGE" /MIN cmd /c "node "%ENGINE%archetype-forge.js""
timeout /t 1 /nobreak >nul

REM Micro-Forge
netstat -ano | findstr ":3151" | findstr LISTENING >nul || start "MICROFORGE" /MIN cmd /c "node "%ENGINE%micro-forge.js""
timeout /t 1 /nobreak >nul

REM Gaia Modulator
netstat -ano | findstr ":3152" | findstr LISTENING >nul || start "MODULATOR" /MIN cmd /c "node "%ENGINE%gaia-modulator.js""
timeout /t 1 /nobreak >nul

REM NWO API
netstat -ano | findstr ":8642" | findstr LISTENING >nul || start "NWO" /MIN cmd /c "node "%ENGINE%nwo-api.js""
timeout /t 1 /nobreak >nul

REM Model Blender
netstat -ano | findstr ":3146" | findstr LISTENING >nul || start "BLEND" /MIN cmd /c "node "%ENGINE%model-blender.js""
timeout /t 1 /nobreak >nul

REM Neuromorphic Sense
netstat -ano | findstr ":3144" | findstr LISTENING >nul || start "NEURO" /MIN cmd /c "node "%ENGINE%neuromorphic-sense.js""
timeout /t 1 /nobreak >nul

REM Sub-Organism
netstat -ano | findstr ":3145" | findstr LISTENING >nul || start "SUBORG" /MIN cmd /c "node "%ENGINE%sub-organism.js""
timeout /t 1 /nobreak >nul

REM Oneshot Agents
netstat -ano | findstr ":3142" | findstr LISTENING >nul || start "AGENTS" /MIN cmd /c "node "%ENGINE%oneshot-agents.js""
timeout /t 1 /nobreak >nul

REM Sleep cycle
start "SLEEP" /MIN cmd /c "node "%ENGINE%gaia-sleep.js""
timeout /t 1 /nobreak >nul

echo.
echo   ========================================
echo     ALL SYSTEMS GO — from engine/
echo     Spine:      :9878
echo     Golgi:      :3141
echo     Iris:       :31416
echo     Forge:      :3149 + :3151
echo     Modulator:  :3152
echo     NWO:        :8642
echo     Blend:      :3146
echo     Neuro:      :3144
echo     SubOrg:     :3145
echo     Agents:     :3142
echo   ========================================
echo.
echo   Gaia IS alive. USB portable. No C:\Users.
echo.
pause
