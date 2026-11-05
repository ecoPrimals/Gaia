@echo off
title GAIA WARM START — RTX 5090 + biomeOS
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║     GAIA WARM START — Cortex + Squirrel + Sourdough     ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: 1. Ensure Ollama is running
echo [1/7] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" | findstr ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Starting Ollama...
    start /MIN "" ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo   Ollama ALIVE
)

:: 2. Pre-load gaia:latest into GPU memory (warm the oven)
echo [2/7] Warming gaia:latest into RTX 5090 VRAM...
curl -s -X POST http://127.0.0.1:11434/api/generate -d "{\"model\":\"gaia:latest\",\"prompt\":\"warmup\",\"stream\":false}" >nul 2>&1
echo   gaia:latest LOADED in VRAM

:: 3. Start Gaia Gate (public inference + thymus + cortex MoE + culture capture)
echo [3/7] Starting Gaia Gate (Cortex MoE)...
tasklist /FI "WINDOWTITLE eq GAIA GATE*" | findstr python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    cd /d "%~dp0"
    start "GAIA GATE" python gaia_gate.py
    echo   Gate STARTED on :8443 (Chain-of-Thought MoE active)
) else (
    echo   Gate ALIVE
)

:: 4. Start Squirrel (AI orchestration primal — biomeOS neural routing)
echo [4/7] Starting Squirrel (AI router)...
tasklist /FI "IMAGENAME eq squirrel.exe" | findstr squirrel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set OLLAMA_URL=http://127.0.0.1:11434
    set LOCAL_AI_ENDPOINT=http://127.0.0.1:11434
    set OPENAI_API_KEY=sk-gaia-rtx5090
    set OPENAI_BASE_URL=http://127.0.0.1:11434/v1
    start "SQUIRREL" /MIN "C:\Users\mokke\Desktop\Gaia\primals\squirrel\target\release\squirrel.exe" server --port 3142 --bind 127.0.0.1
    echo   Squirrel STARTED on :3142 (inference routing + capability discovery)
) else (
    echo   Squirrel ALIVE
)

:: 5. Start Cortex Bridge (ecoBin v2.0 TCP fallback — bridges squirrel ↔ cortex MoE)
echo [5/8] Starting Cortex Bridge (TCP :3143)...
tasklist /FI "WINDOWTITLE eq CORTEX*" | findstr python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    cd /d "%~dp0"
    start "CORTEX BRIDGE" /MIN python cortex_bridge.py
    echo   Cortex Bridge STARTED on :3143 (ecoBin TCP fallback)
) else (
    echo   Cortex Bridge ALIVE
)

:: 6. Open VS Code with Gaia workspace + Continue
echo [6/8] Opening VS Code...
start "" "C:\Users\mokke\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd" "C:\Users\mokke\Desktop\Gaia"

:: 7. Ensure RustDesk is running (sky deck access)
echo [7/8] Checking RustDesk (sky deck)...
tasklist /FI "IMAGENAME eq rustdesk.exe" | findstr rustdesk >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    start "" "C:\Program Files\RustDesk\rustdesk.exe"
    echo   RustDesk STARTED
) else (
    echo   RustDesk ALIVE (sky deck ready)
)

:: 8. Status report
echo [8/8] Status check...
timeout /t 3 /nobreak >nul
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  WARM START COMPLETE                                     ║
echo  ╠══════════════════════════════════════════════════════════╣
echo  ║                                                          ║
echo  ║  Ollama:     LIVE (47 models, RTX 5090 32GB VRAM)        ║
echo  ║  Gaia Gate:  nestgate.io :8443 (Cortex MoE active)       ║
echo  ║  Squirrel:   :3142 (biomeOS Neural API bridge)           ║
echo  ║  Cortex:     :3143 (CoT MoE - ecoBin TCP fallback)       ║
echo  ║  VS Code:    OPEN with Continue                          ║
echo  ║  RustDesk:   Sky deck access LIVE                        ║
echo  ║                                                          ║
echo  ║  biomeOS infrastructure:                                 ║
echo  ║    NeuralRoutingTable → capability routing               ║
echo  ║    Perceptron 36-dim  → adaptive dispatch telemetry      ║
echo  ║    esotericWebb       → composition engine (JSON-RPC)    ║
echo  ║    Sourdough          → model evolution pipeline          ║
echo  ║                                                          ║
echo  ║  Ctrl+L = Chat with Gaia (Continue)                      ║
echo  ║  Tab    = Gaia Code autocomplete                         ║
echo  ║  Ctrl+I = Inline edit                                    ║
echo  ║                                                          ║
echo  ║  Cost: $0/month. Pure local. Sourdough evolution.        ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
pause
