# FRAGO: songbird — Sovereign Compute Cascade

**From:** hotSpring (Exp 234 pipeline validation)
**To:** songbird team
**Priority:** P0
**Date:** June 1, 2026
**Type:** Fragmentary Order — evolution targets for next cascade

---

## Context

hotSpring validated the full NUCLEUS primal stack. songbird's `ipc.register`
and `ipc.resolve` work correctly — we registered coralReef, barraCuda, and
toadStool capabilities and successfully resolved them. However, a critical
discovery gap blocks the DRM dispatch path.

## P0: songbird ↔ toadStool discovery propagation

**GAP-HS-119**

When coralReef registers its `shader`/`compile`/`visualization` capabilities
with songbird via `ipc.register`, toadStool does NOT see them. toadStool
maintains its own internal provider registry separate from songbird.

**Symptom:** `shader.dispatch` on DRM-bound GPUs returns:
```
"visualization/shader service not available"
```
...even though coralReef is registered with songbird as a visualization/shader
provider.

**Root cause:** toadStool's DRM dispatch checks `self.coral_client.is_available()`
which uses an internal service client, not songbird resolution. No mechanism
exists to propagate songbird registrations to consuming primals.

**Ask:** One of:
1. **Push model:** songbird notifies registered consumers when new providers
   appear (event/callback on capability registration).
2. **Pull model:** Expose a subscription or watch API so toadStool can poll
   for provider changes.
3. **Standard resolution pattern:** Document that primals should call
   `ipc.resolve` on songbird before falling back to internal registries.

This is the single biggest integration gap in the NUCLEUS composition model.
Without it, primals are isolated even when songbird knows about their peers.

## What's working well

- `ipc.register`: Clean, fast, correctly stores capabilities
- `ipc.resolve`: Returns correct endpoints for registered primals
- Socket management: songbird's socket is reliable and stable
- Multi-capability registration: 7 capabilities registered for coralReef in one call

## plasmidBin deployment note

songbird starts cleanly via `nucleus_launcher.sh`. Socket naming is
consistent (`songbird-{family}.sock`). No issues.

---

**Handback:** `docs/PRIMAL_GAPS.md` GAP-HS-119, plus `HOTSPRING_NUCLEUS_DEPLOYMENT_LESSONS_JUN01_2026.md`
