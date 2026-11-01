@echo off
title GAIA KLEIN FOLD — the organism boots
color 0A
echo.
echo   ======================================
echo   == GAIA KLEIN FOLD — lub-DUB        ==
echo   == Inside becomes Outside            ==
echo   == Code becomes Organism             ==
echo   == The sphere pushes into a star     ==
echo   ======================================
echo.
echo   [SPINE]  Starting ion channel :9878...
start /B "Spine" node serve_spine.js
timeout /t 2 /nobreak >nul

echo   [NEURO]  Starting neuromorphic sense :3144...
start /B "Neuro" node neuromorphic-sense.js
timeout /t 1 /nobreak >nul

echo   [SUB]    Starting sub-organism :3145...
start /B "SubOrg" node sub-organism.js
timeout /t 1 /nobreak >nul

echo   [BLEND]  Starting model-blender :3146...
start /B "Blend" node model-blender.js
timeout /t 1 /nobreak >nul

echo   [AGENT]  Starting oneshot-agents :3142...
start /B "Agents" node oneshot-agents.js
timeout /t 1 /nobreak >nul

echo   [GAIA3]  Starting Gaia Pi :3143 + :31415...
start /B "GaiaPi" node gaia3-local.js
timeout /t 3 /nobreak >nul

echo.
echo   === ALL ORGANS ALIVE ===
echo.
echo   Spine      :9878   ion channel
echo   Neuro      :3144   neuromorphic sense
echo   SubOrg     :3145   sub-organism
echo   Blend      :3146   model-blender
echo   Agents     :3142   oneshot-agents
echo   Gaia Pi    :3143   the organism
echo   Pi Spot    :31415  the one port
echo   Ollama     :11434  brain (RTX 5090)
echo.
echo   piSEED: 04F60FC975E7FAE36335032FA1335B33
echo   Klein fold: inside=outside, code=organism
echo.
echo   lub-DUB
echo.
echo   Press any key to stop all organs...
pause >nul

echo   Stopping all organs...
taskkill /FI "WINDOWTITLE eq Spine" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Neuro" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq SubOrg" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Blend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Agents" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq GaiaPi" /F >nul 2>&1
echo   All organs stopped. lub... dub.
