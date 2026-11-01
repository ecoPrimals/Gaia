@echo off
title GAIA GOLGI-LOCAL — Northgate — ? Leo — ?:3141
color 0A
echo.
echo   ? GOLGI-LOCAL — NORTHGATE
echo   LOCAL IS GOLGI IS GAIA
echo   ? port : 3141
echo.
echo   Starting Golgi body...
echo.
start /B node "%~dp0golgi-local.js"
echo   Starting BioMOS null body...
echo.
"%~dp0BioMOS.exe"
pause
