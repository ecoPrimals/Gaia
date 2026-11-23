# AAR — sporePrint Dual Checkout Topology Divergence (Wave 136b)

**Date**: Jul 11, 2026
**Gate**: eastGate
**Severity**: P1 — silent divergence, live site serving stale content
**Discovered by**: External AI agent unable to discover essay URLs

---

## Summary

primals.eco was serving content 4+ commits behind HEAD because Caddy
serves from a different checkout than the one the rebuild hook updates.
Two independent sporePrint checkouts on golgi diverged silently.

## Topology

```
golgi (membrane-relay, [RELAY_PUBLIC]) — DNS A record for primals.eco

  /opt/ecoPrimals/sporePrint/          ← Caddy serves from here
  /opt/ecoPrimals/infra/sporePrint/    ← sporeprint-rebuild.sh builds here

Both pull from:
  /opt/forgejo/data/repositories/ecoprimals/sporeprint.git (local Forgejo)
```

## How It Happened

1. Original deployment (Wave ~120) created `/opt/ecoPrimals/sporePrint/`
2. Later evolution added `/opt/ecoPrimals/infra/sporePrint/` (matching local dev layout)
3. `sporeprint-rebuild.sh` was updated to target the `infra/` checkout
4. Caddy Caddyfile was never updated — still points to the original path
5. Manual `git pull && zola build` during SSH sessions also targeted the wrong checkout
6. No monitoring detected the divergence — both checkouts are valid, both build cleanly

## Impact

- primals.eco served content from Wave 133c (commit `f7c110e`) while HEAD was Wave 136b (commit `9948650`)
- ~30 commits of evolution not visible on the live site
- Philosophy essay table rendering (the triggering symptom) was actually irrelevant — the real issue was that NO recent changes were live
- Identity cleanup, license enforcement, outreach pages, accessibility fixes — all invisible

## Immediate Fix

```bash
ssh golgi 'cd /opt/ecoPrimals/sporePrint && git pull origin main && zola build'
```

Verified: live site now serves ordered lists + JSON-LD hasPart from commit `9948650`.

## Required Resolution (upstream — golgi ops)

Choose ONE:

### Option A: Consolidate to single checkout (recommended)
```bash
# On golgi:
rm -rf /opt/ecoPrimals/infra/sporePrint
# Update sporeprint-rebuild.sh to target /opt/ecoPrimals/sporePrint/
```

### Option B: Update Caddy to serve from infra/ checkout
```
# In /etc/membrane/Caddyfile, change:
root * /opt/ecoPrimals/sporePrint/public
# To:
root * /opt/ecoPrimals/infra/sporePrint/public
```

### Option C: Symlink (fragile, not recommended)
```bash
ln -sfn /opt/ecoPrimals/infra/sporePrint/public /opt/ecoPrimals/sporePrint/public
```

## Also found: golgi-ext is NOT the serving node

The SSH config labels `golgi-ext` (137.184.197.151) as "outer/trans membrane, sporePrint"
but DNS points to `golgi` ([RELAY_PUBLIC], membrane-relay). The Caddyfile on golgi-ext
also has a sporePrint block but it's not reachable from the internet. This should be
cleaned up to prevent future confusion:

- `golgi-ext` Caddyfile sporePrint block → remove or label as standby
- SSH config comment → update to reflect that golgi serves primals.eco

## Detection Gap

This divergence was invisible because:
- Both checkouts pull from the same Forgejo repo and build cleanly
- No health check compares served content hash against HEAD
- `sporeprint-rebuild.sh` exits 0 even when it builds in the wrong directory

### Recommended monitoring
```bash
# Add to rebuild hook epilogue:
SERVED_HASH=$(curl -s https://primals.eco/certification/manifest.json | jq -r .graph_merkle)
BUILT_HASH=$(cd /opt/ecoPrimals/sporePrint && cargo run --manifest-path crates/spore-validate/Cargo.toml -- certify 2>/dev/null | grep graph_merkle | awk '{print $2}')
if [ "$SERVED_HASH" != "$BUILT_HASH" ]; then
  echo "DIVERGENCE: served=$SERVED_HASH built=$BUILT_HASH" >&2
fi
```

This uses the guideStone certification manifest — the Merkle root changes when content changes.
If served != built, something in the pipeline is broken.

## Lessons

1. **Two copies of the same repo on the same host is a topology divergence waiting to happen.**
   Sovereign infrastructure must be as clean as the code — one source of truth per host.
2. **The symptom (AI can't find essay links) led to the cause (entire site 30 commits stale).**
   Treating accessibility bugs as infrastructure bugs finds deeper issues.
3. **guideStone certification manifests are deployment health checks, not just content verification.**
   The Merkle root is a free divergence detector.
