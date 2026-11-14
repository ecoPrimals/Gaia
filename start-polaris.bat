@echo off
echo.
echo  ================================================================
echo   POLARIS :: northGate :: RTX 5090 :: PI IN THE SKY
echo   Dissolved startup — no rigid order, primals find each other
echo   sunCloud governor active — gaming + compute sharing
echo  ================================================================
echo.

:: ─── IDENTITY ───────────────────────────────────────────────
set FAMILY_ID=gaia-pi
set NODE_ID=polaris
set FAMILY_SEED=04F60FC975E7FAE36335032FA1335B33ABCA230F357807E18E9C95E7D012536E
set BEARDOG_FAMILY_SEED=%FAMILY_SEED%
set BIOMEOS_SOVEREIGN=true
set RUST_LOG=info
set PRIMAL_BIND_MODE=dual

:: ─── PATHS ──────────────────────────────────────────────────
set GAIA=C:\Users\mokke\Desktop\Gaia
set PRIMALS=%GAIA%\primals
set RUNTIME=%GAIA%\runtime
set MEMBRANE=%RUNTIME%\membrane
set XDG_RUNTIME_DIR=%RUNTIME%

:: ─── CREATE SOCKET DIR ──────────────────────────────────────
if not exist "%MEMBRANE%" mkdir "%MEMBRANE%"

echo [LAYER 0] SPINE — the backbone
echo.

:: biomeOS orchestrator (NUCLEUS)
echo   [META] biomeOS :: orchestrator (pi=31415)...
start /MIN "biomeOS" "%PRIMALS%\biomeOS\target\release\biomeos.exe" nucleus start --node-id polaris --port 31415 --bind 0.0.0.0 --bind-mode dual --verbose
timeout /t 3 /nobreak > nul

:: loamSpine — data persistence
echo   [SPINE] loamSpine :: persistence (:9878)...
start /MIN "loamSpine" "%PRIMALS%\loamSpine\target\release\loamspine.exe" server --port 9878
timeout /t 2 /nobreak > nul

echo [LAYER 1] SENSES — eyes, ears, immune
echo.

:: squirrel — AI agent dispatch
echo   [SENSE] squirrel :: AI dispatch (:3141)...
start /MIN "squirrel" "%PRIMALS%\squirrel\target\release\squirrel.exe" server --port 3141
timeout /t 1 /nobreak > nul

:: nestGate — data gateway
echo   [SENSE] nestGate :: data gateway (:8092)...
start /MIN "nestGate" "%PRIMALS%\nestGate\target\release\nestgate.exe" server --port 8092
timeout /t 1 /nobreak > nul

:: skunkBat — intrusion detection
echo   [IMMUNE] skunkBat :: IDS...
start /MIN "skunkBat" "%PRIMALS%\skunkBat\target\release\skunkbat.exe" server --bind-mode dual
timeout /t 1 /nobreak > nul

echo [LAYER 2] COMPUTE — GPU + math + shaders
echo.

:: barraCuda — GPU math (RTX 5090!)
echo   [GPU] barraCuda :: GPU compute (RTX 5090)...
start /MIN "barraCuda" "%PRIMALS%\barraCuda\target\release\barracuda.exe" server --port 8094
timeout /t 1 /nobreak > nul

:: coralReef — shader compiler
echo   [GPU] coralReef :: shader compiler...
start /MIN "coralReef" "%PRIMALS%\coralReef\target\release\coralreef.exe" server --port 8095
timeout /t 1 /nobreak > nul

echo [LAYER 3] CRYPTO + STORAGE
echo.

:: bearDog — crypto identity
echo   [CRYPTO] bearDog :: BLAKE3/BTSP identity...
start /MIN "bearDog" "%PRIMALS%\bearDog\target\release\beardog.exe" server --bind-mode dual
timeout /t 1 /nobreak > nul

:: rhizoCrypt — encrypted storage
echo   [CRYPTO] rhizoCrypt :: encrypted vaults...
start /MIN "rhizoCrypt" "%PRIMALS%\rhizoCrypt\target\release\rhizocrypt.exe" server
timeout /t 1 /nobreak > nul

:: sweetGrass — knowledge graph
echo   [GRAPH] sweetGrass :: provenance/attribution...
start /MIN "sweetGrass" "%PRIMALS%\sweetGrass\target\release\sweetgrass.exe" server
timeout /t 1 /nobreak > nul

echo [LAYER 4] MESH + COMMS
echo.

:: songBird — mesh transport
echo   [MESH] songBird :: federation (:8091)...
start /MIN "songBird" "%PRIMALS%\songBird\target\release\songbird.exe" server --port 8091
timeout /t 1 /nobreak > nul

:: bingoCube — coordination
echo   [COORD] bingoCube :: coordination...
start /MIN "bingoCube" "%PRIMALS%\bingoCube\target\release\bingocube.exe" server
timeout /t 1 /nobreak > nul

:: sourDough — fermentation
echo   [FERM] sourDough :: fermentation...
start /MIN "sourDough" "%PRIMALS%\sourDough\target\release\sourdough.exe" server
timeout /t 1 /nobreak > nul

echo [LAYER 5] FACE — the surface
echo.

:: petalTongue — web face
echo   [FACE] petalTongue :: web renderer (:5926)...
start /MIN "petalTongue" "%PRIMALS%\petalTongue\target\release\petaltongue.exe" server --port 5926
timeout /t 1 /nobreak > nul

:: webpi — the sky server
echo   [SKY] webpi :: PI in the sky (:8080)...
start /MIN "webpi" python "%RUNTIME%\webpi.pi"
timeout /t 2 /nobreak > nul

:: sunCloud governor
echo   [GOV] sunCloud :: compute sharing governor...
start /MIN "sunCloud" python "%RUNTIME%\suncloud.pi"

echo.
echo  ================================================================
echo   POLARIS ALIVE :: %date% %time%
echo.
echo   biomeOS     :31415  NUCLEUS orchestrator
echo   loamSpine   :9878   data spine
echo   squirrel    :3141   AI dispatch
echo   nestGate    :8092   data gateway
echo   barraCuda   :8094   GPU compute (RTX 5090)
echo   coralReef   :8095   shader compiler
echo   songBird    :8091   mesh federation
echo   petalTongue :5926   web renderer
echo   webpi       :8080   PI in the sky
echo   sunCloud    governor (gaming awareness)
echo.
echo   13 primals :: 9 ports :: 1 GPU :: dissolved
echo   Kevin games, Gaia computes. lub-DUB.
echo  ================================================================
echo.
echo   Press any key to shut down all primals...
pause > nul

:: Shutdown
taskkill /FI "WINDOWTITLE eq biomeOS" /F 2>nul
taskkill /FI "WINDOWTITLE eq loamSpine" /F 2>nul
taskkill /FI "WINDOWTITLE eq squirrel" /F 2>nul
taskkill /FI "WINDOWTITLE eq nestGate" /F 2>nul
taskkill /FI "WINDOWTITLE eq skunkBat" /F 2>nul
taskkill /FI "WINDOWTITLE eq barraCuda" /F 2>nul
taskkill /FI "WINDOWTITLE eq coralReef" /F 2>nul
taskkill /FI "WINDOWTITLE eq bearDog" /F 2>nul
taskkill /FI "WINDOWTITLE eq rhizoCrypt" /F 2>nul
taskkill /FI "WINDOWTITLE eq sweetGrass" /F 2>nul
taskkill /FI "WINDOWTITLE eq songBird" /F 2>nul
taskkill /FI "WINDOWTITLE eq bingoCube" /F 2>nul
taskkill /FI "WINDOWTITLE eq sourDough" /F 2>nul
taskkill /FI "WINDOWTITLE eq petalTongue" /F 2>nul
taskkill /FI "WINDOWTITLE eq webpi" /F 2>nul
taskkill /FI "WINDOWTITLE eq sunCloud" /F 2>nul
echo   All primals stopped. lub-DUB.
