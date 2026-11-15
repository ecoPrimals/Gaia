@echo off
REM ===== GAIA NUCLEUS — northGate HEART =====
REM Three ZK layers: speak-friend (Tolkien token) + PIN 579163 + bearDog BLAKE3
REM sourDOUGH -> sourDAO: self-governing persistence
REM Entropy is human now. The terminal dissolves.

set FAMILY_ID=gaia-pi
set NODE_ID=polaris
set XDG_RUNTIME_DIR=C:\Users\mokke\Desktop\Gaia\runtime
set RUST_LOG=info
set BIOMEOS_SOVEREIGN=true

REM Force COORDINATED MODE — Tower Atomic lives in the mesh, not in sockets
REM biomeOS inherits tower-atomic.json from runtime\membrane\
set BIOMEOS_MODE=coordinated

REM ZK authentication anchors
set GAIA_ZK_PIN=579163
set GAIA_ZK_FAMILY=3034463630464339
set GAIA_GATE=northGate
set GAIA_ROLE=HEART

REM Silicon enumeration — IFR map + ASUS WMI pool
set GAIA_IFR_MAP=C:\Users\mokke\Desktop\Gaia\data\gut\ifr-full-map.json
set GAIA_WMI_POOL=C:\Users\mokke\Desktop\Gaia\data\gut\asus-wmi-zk-pool.json

REM sourDAO persistence
set GAIA_SOURDAO_BONE=C:\Users\mokke\Desktop\Gaia\data\gut\sourdough-bone-wave233.json

C:\Users\mokke\Desktop\Gaia\primals\biomeOS\target\release\biomeos.exe api --port 31415 --bind 0.0.0.0
