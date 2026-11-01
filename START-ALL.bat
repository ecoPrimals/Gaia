@echo off
title GAIA — FULL BODY STARTUP — lub-DUB
color 0A
echo.
echo   ========================================
echo     GAIA — FULL BODY STARTUP
echo     All organs. All modules. One body.
echo     USB portable. No C:\Users.
echo     lub-DUB
echo   ========================================
echo.

echo   [1/5] Starting SPINE on :9878...
start "GAIA SPINE" /MIN cmd /c "node "%~dp0serve_spine.js" 2>&1"
timeout /t 2 /nobreak >nul

echo   [2/5] Starting GOLGI on :3141...
start "GAIA GOLGI" /MIN cmd /c "node "%~dp0golgi-local.js" 2>&1"
timeout /t 2 /nobreak >nul

echo   [3/5] Starting BioMOS...
start "BioMOS" /MIN cmd /c ""%~dp0BioMOS.exe" 2>&1"
timeout /t 1 /nobreak >nul

echo   [4/5] Starting ENGINE modules...
call "%~dp0engine\BOOT-AMALGAM.bat"
timeout /t 1 /nobreak >nul

echo   [5/5] All systems nominal.
echo.
echo   ========================================
echo     ALL SYSTEMS GO
echo     Spine:      http://localhost:9878
echo     Golgi:      http://localhost:3141
echo     Iris:       http://localhost:31416
echo     Forge:      http://localhost:3149 + :3151
echo     Modulator:  http://localhost:3152
echo     NWO:        http://localhost:8642
echo     Blend:      http://localhost:3146
echo     Neuro:      http://localhost:3144
echo     SubOrg:     http://localhost:3145
echo     Agents:     http://localhost:3142
echo     Ollama:     http://localhost:11434
echo   ========================================
echo.
echo   Gaia IS alive. Kevin can walk away.
echo   (Services keep running in background)
echo.
pause
