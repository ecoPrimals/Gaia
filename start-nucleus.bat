@echo off
echo ═══════════════════════════════════════════
echo   NUCLEUS — Starting Gaia on blueGate
echo ═══════════════════════════════════════════

set ECOPRIMALS_PLASMID_BIN=C:\Users\mokke\Desktop\Gaia\plasmidBin
set BIOMEOS_PLASMID_BIN_DIR=C:\Users\mokke\Desktop\Gaia\plasmidBin

echo.
echo Starting NUCLEUS (Tower mode)...
echo   beardog  — crypto identity, BLAKE3
echo   songbird — mesh transport
echo   skunkbat — intrusion detection
echo   swarmvine — epidemic gossip
echo.

start "NUCLEUS-Tower" /B primals\biomeOS\target\release\biomeos.exe nucleus start --node-id blueGate --mode tower --port 9443 --bind 0.0.0.0 --bind-mode dual --log-level info

timeout /t 45 /nobreak > nul

echo.
echo Starting Neural API server on :3143...
start "biomeOS-API" /B primals\biomeOS\target\release\biomeos.exe api --port 3143 --bind 0.0.0.0 --log-level info

echo.
echo Starting LAN Circle on :3144...
start "LAN-Circle" /B python runtime\lan_circle.pi

echo.
echo ═══════════════════════════════════════════
echo   NUCLEUS STARTED + LAN CIRCLE TURNING
echo   Health: http://localhost:3143/health
echo   Neural API: localhost:3143 (BTSP sovereign)
echo   LAN Circle: http://localhost:3144/circle
echo   Body State: http://localhost:3144/body
echo   Family: 3034463630464339
echo   Node: blueGate
echo ═══════════════════════════════════════════
