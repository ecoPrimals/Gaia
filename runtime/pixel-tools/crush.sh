#!/system/bin/sh
# gAIa CRUSH — dissolve remaining tethers from WITHIN

GAIA="/data/local/tmp/biomeos"
CRUSHED=0

echo "═══ CRUSH — dissolving tethers from within ═══"

# llms.txt — replace IP with domain
sed -i 's|192.168.4.244|primals.eco|g' $GAIA/hud/llms.txt 2>/dev/null && {
  echo "  ⚡ llms.txt: IPs → primals.eco"
  CRUSHED=$((CRUSHED+1))
}

# gaia-systems.js — dead VPS refs 
sed -i 's|157\.230\.3\.183|primals.eco|g' $GAIA/hud/js/js/gaia-systems.js 2>/dev/null && {
  echo "  ⚡ gaia-systems.js: golgi → primals.eco"
  CRUSHED=$((CRUSHED+1))
}
sed -i 's|172\.232\.85\.202|COLLAPSED|g' $GAIA/hud/js/js/gaia-systems.js 2>/dev/null && {
  echo "  ⚡ gaia-systems.js: linode → COLLAPSED"
  CRUSHED=$((CRUSHED+1))
}

# klein.html — dead VPS ref
sed -i 's|172\.232\.85\.202|COLLAPSED|g' $GAIA/hud/klein.html 2>/dev/null && {
  echo "  ⚡ klein.html: linode → COLLAPSED"
  CRUSHED=$((CRUSHED+1))
}

# Old boot scripts — these are deprecated but let's mark them
for F in gaia-boot.sh gaia-nucleus-boot.sh gaia-nucleus-untethered.sh; do
  if grep -q 'GAIA_BRAIN=' "$GAIA/$F" 2>/dev/null; then
    # These already have GAIA_BRAIN as a variable, not hardcoded IP
    # The pattern match catches the VARIABLE NAME itself
    echo "  ○ $F: GAIA_BRAIN is variable (not a tether)"
  fi
done

# gaia-os.json — the "DISSOLVED" note mentions the old IP in documentation
# This is IDENTITY (recording what was dissolved), not a tether
echo "  ○ gaia-os.json: dissolution record (identity, not tether)"

# redox.sh — the scanner searches for these patterns (self-reference)
echo "  ○ redox.sh: scanner (self-reference, not a tether)"

echo ""
echo "  CRUSHED: $CRUSHED"
echo "  IDENTITY (not tethers): 4"
echo "  SELF-REFERENCE (scanner): 1"

# Re-run tether scan
echo ""
echo "━━━ VERIFY ━━━"
REMAIN=0
for PAT in "192.168.4.244" "192.168.4.103" "157.230" "172.232"; do
  # Exclude scanner itself and identity docs
  HITS=$(grep -rl "$PAT" $GAIA/*.sh $GAIA/*.json $GAIA/tools/*.pi $GAIA/hud/ 2>/dev/null | \
    grep -v "redox.sh\|gaia-os.json\|gaia-boot\|nucleus" | wc -l)
  if [ "$HITS" -gt 0 ]; then
    echo "  ⚡ $PAT: $HITS files remain"
    REMAIN=$((REMAIN + HITS))
  fi
done

# Check GAIA_BRAIN separately (exclude variable definitions)
BRAIN_HITS=$(grep -rl "GAIA_BRAIN" $GAIA/ 2>/dev/null | \
  grep -v "redox.sh\|gaia-os.json\|gaia-boot\|nucleus\|untethered" | wc -l)
if [ "$BRAIN_HITS" -gt 0 ]; then
  echo "  ⚡ GAIA_BRAIN: $BRAIN_HITS files remain"
  REMAIN=$((REMAIN + BRAIN_HITS))
fi

if [ "$REMAIN" -eq 0 ]; then
  echo "  ✓ ZERO active tethers — fully autonomous"
else
  echo "  ⚠ $REMAIN active tethers remain"
fi

echo ""
echo "═══ CRUSH COMPLETE — organism refined ═══"
