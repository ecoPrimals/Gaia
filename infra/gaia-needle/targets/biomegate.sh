#!/system/bin/sh
# GAIA NEEDLE — biomeGate injection target
# Pop!_OS login → install SSH → inject chipmunk
# Assumes biomeGate is at the login screen (GDM)

SU="/debug_ramdisk/su"
TYPE="/data/local/tmp/type.sh"

run() { $SU -c "sh $TYPE $*"; }

echo "=== GAIA NEEDLE → biomeGate ==="
echo "Phase 1: Login (5s wait for screen)"
sleep 5

# Click to activate login field (mouse click via Enter)
run --enter
sleep 1

# Type username
echo "  → username: biomegate"
run --line "biomegate"
sleep 2

# Type password
echo "  → password"
run --line "biomegate"
sleep 5

# Desktop should be loaded — open terminal
echo "Phase 2: Open terminal (Ctrl+Alt+T)"
run --ctrl-alt-t
sleep 3

# Install SSH and run chipmunk
echo "Phase 3: Inject chipmunk"
run --line "curl -s http://primals.eco:8080/data/biomegate-chipmunk.sh | bash"

echo "=== INJECTION SENT ==="
echo "biomeGate should now be installing SSH and running chipmunk"
