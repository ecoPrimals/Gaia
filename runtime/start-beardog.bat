@echo off
set FAMILY_SEED=04F60FC975E7FAE36335032FA1335B33ABCA230F357807E18E9C95E7D012536E
set BEARDOG_FAMILY_SEED=04F60FC975E7FAE36335032FA1335B33ABCA230F357807E18E9C95E7D012536E
set FAMILY_ID=gaia-pi
set NODE_ID=polaris
set XDG_RUNTIME_DIR=C:\Users\mokke\Desktop\Gaia\runtime
set RUST_LOG=info
C:\Users\mokke\Desktop\Gaia\primals\bearDog\target\release\beardog.exe server --socket C:\Users\mokke\Desktop\Gaia\runtime\membrane\beardog-gaia-pi.sock --family-id gaia-pi
