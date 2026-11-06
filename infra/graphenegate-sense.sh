#!/bin/bash
# DEPRECATED (Wave 222): grapheneGate is dissolved into Gaia - the phone is a peripheral.
# The collector now lives in /opt/Gaia/runtime/graphene_depot.pi (USB-first, serial-verified
# WiFi ADB fallback, atomic writes). This shim only forwards for any stale caller.
exec python3 /opt/Gaia/runtime/graphene_depot.pi amoeba "$@"
