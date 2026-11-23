# AAR: westGate NUCLEUS + Provenance 7/7 — Wave 155k

**Date**: Jul 30, 2026 10:00 EDT
**Gate**: westGate
**Wave**: 155k
**Author**: westGate overwatch (AI-assisted)
**Classification**: DISSEMINATE — all teams

---

## EXECUTIVE SUMMARY

westGate is now the second gate running a full NUCLEUS composition (13/13 primals, 29 sockets, 654 capabilities) and the **first gate to achieve Provenance Trio 7/7** — a full E2E signed provenance chain from CAS storage through DAG, Merkle, certificate spine, Ed25519 cryptographic signature, and attribution braid. ALL on live hardware backed by ZFS.

This wave's three milestones:
1. **biomeOS v4.47 NUCLEUS orchestrator deployed** — riboCipher fix, socket unification, composition lifecycle
2. **Provenance trio 7/7 COMPLETE** — first ever full signed chain on live hardware
3. **westGate NUCLEUS achieved** — 13/13 primals, second gate after strandGate

---

## WHAT WORKED

### 1. Cascade Pipeline — 12 Repos in One Shot
- 12 repositories pulled from golgiBody in a single cascade operation
- biomeOS (+6 commits, +2,974/-2,302 lines), bearDog (+2 commits, +766 lines), cellMembrane (+2 commits), sweetGrass (+1 commit UUID fix) — all landed cleanly
- wateringHole pulled 76 commits of fossilized handoffs — the ecosystem's memory
- Zero merge conflicts

### 2. biomeOS v4.47 Depot Binary — Drop-In Upgrade
- Binary grew from 15,935 KB → 20,257 KB (composition lifecycle code is real)
- Drop-in replacement: `curl → chmod → mv → systemctl restart` — took seconds
- Neural API entered **Coordinated mode** with 654 capabilities across all 13 primals
- Socket unification (`/run/user/1000/biomeos/`) is cleaner in v4.47

### 3. bearDog `crypto.sign_ed25519` — LIVE
- Direct IPC test confirmed real Ed25519 signatures (not health stub)
- Returns: `algorithm`, `key_id`, `public_key`, `signature` (base64)
- Accepts base64-encoded message in `params.message`
- The P1 that blocked Provenance for weeks is resolved

### 4. Provenance Trio 7/7 — First Full Signed Chain
```
  1. content.put → nestgate CAS                ✓  BLAKE3 content-addressed
  2. dag.session.create → rhizocrypt            ✓  Session tracking
  3. dag.event.append → rhizocrypt              ✓  DataCreate event
  4. dag.merkle.root → rhizocrypt               ✓  Cryptographic proof
  5. spine.create → loamspine                   ✓  Certificate spine
  6. entry.append → loamspine (bearDog sign)    ✓  Ed25519 SIGNATURE
  7. braid.create → sweetgrass                  ✓  Attribution braid (JSON-LD)
```
Full chain: PDB data → CAS → DAG → Merkle → Spine → SIGNED Entry → Attribution Braid

### 5. NUCLEUS Composition — 13/13 Services
```
  Tower:   bearDog ✓  songBird ✓  skunkBat ✓
  Nest:    nestGate ✓  loamSpine ✓  sweetGrass ✓  rhizoCrypt ✓
  Node:    barraCuda ✓  coralReef ✓  toadStool ✓
  Viz:     petalTongue ✓
  AI:      squirrel ✓
  Orch:    biomeOS ✓ (COORDINATED, 654 caps)
```
13/13 active | 29 sockets | biomeOS Coordinated mode

### 6. ZFS Storage — Continues Healthy
- Pool: 25.4TB, ONLINE, healthy
- CAS: 3,252 objects (grew from 3,216)
- Compression ratio: 1.56×
- L2ARC operational on SSD

---

## WHAT DIDN'T WORK / ISSUES FOUND

### 1. BEARDOG_SOCKET Pointed to Wrong Socket (P2 — config)
- **Root Cause**: `nest.env` had `BEARDOG_SOCKET=/run/user/1000/biomeos/beardog-default.sock` — the generic/legacy socket that still returns health stubs for `crypto.sign_ed25519`
- **The Real Socket**: `beardog-westgate-tower-155f.sock` (family-scoped) has the actual crypto.sign implementation
- **Fix**: Updated `nest.env` and `nestgate.env` to point to `beardog-westgate-tower-155f.sock`
- **Impact**: This was the final blocker for Provenance 7/7 step 6 (entry.append)
- **Upstream Action**: bearDog should deprecate or unify the `beardog-default.sock` — having two sockets with different capability sets is a footgun. The `--family-id` flag should make the family-scoped socket the primary one and the default socket an alias

### 2. Socket Evaporation on Service Restart (Known P2)
- Restarting loamSpine/nestGate caused `beardog-westgate-tower-155f.sock` to disappear
- Had to restart bearDog to regenerate the socket
- This also invalidated in-memory state (spine IDs became "not found" after loamSpine restart)
- **Upstream Action**: Socket lifecycle should be independent of service restart ordering. Consider persistent socket registration or socket supervisor

### 3. Neural API Capability Wipe Cycle (Known P2)
- Capabilities drop to 0 periodically during re-discovery sweep
- Cycle: 654 → 0 → 187 → 654 (over ~60s)
- During the wipe window, graph dispatch would fail
- **Upstream Action**: biomeOS should use additive discovery (register new, keep existing) rather than clear-and-rescan

### 4. membrane/ vs biomeos/ Socket Directory Mismatch (Known P2)
- Neural API v4.47 still looks in `/run/user/1000/membrane/` for its own socket
- Primals register in `/run/user/1000/biomeos/`
- Symlinks bridge the gap but add fragility
- **Upstream Action**: Socket unification was supposed to fix this in v4.47 but the Neural API's own socket path is still hardcoded to membrane/

### 5. toadStool Transport Protocol Mismatch
- toadStool uses tarpc (binary protocol) not JSON-RPC
- `health.liveness` calls return "no response"
- Socket IS created and Neural API discovers it, so toadStool IS in the composition
- Logs show "could not read from the transport" when other primals probe it with JSON-RPC
- **Not a blocker**: toadStool runs workloads via `biome.yaml`, not interactive JSON-RPC
- **Upstream Action**: Consider adding a thin JSON-RPC health endpoint alongside tarpc for uniform health monitoring

### 6. petalTongue `--family-id` Not Supported
- petalTongue server doesn't accept `--family-id` flag
- Had to remove it from the service unit; it reads `FAMILY_ID` from environment instead
- **Upstream Action**: All primals should accept `--family-id` for UniBin v1.1 compliance

### 7. loamSpine `spine.create` Returns Dict, Not String
- Previous code assumed `spine.create` returns a plain string session ID
- Actually returns `{"spine_id":"...", "genesis_hash":[...]}` dict
- Required parser update — API documentation gap
- **Upstream Action**: Standardize response shapes across primals. Consider a `primal.method_schema` introspection method

---

## METRICS

| Metric | Before (155i) | After (155k) | Delta |
|--------|--------------|--------------|-------|
| Services active | 8 | **13** | +5 |
| Sockets | 20 | **29** | +9 |
| Capabilities | 715 → 187 (cycling) | **654** (stable) | normalized |
| Neural API mode | Coordinated | **Coordinated** | stable |
| Provenance Trio | 6/7 | **7/7** | **+1 (COMPLETE)** |
| CAS objects | 3,216 | **3,252** | +36 |
| ZFS pool | 25.4TB ONLINE | **25.4TB ONLINE** | stable |
| biomeOS version | v4.45 (15.9MB) | **v4.47 (20.3MB)** | +4.3MB |
| bearDog crypto.sign | health stub | **REAL Ed25519** | RESOLVED |
| New primals | — | toadStool, barraCuda, coralReef, petalTongue, squirrel | +5 |

---

## WHAT NEEDS TO BE ABSTRACTED AND EVOLVED

### P2 Actions for Upstream Teams

1. **bearDog**: Unify `beardog-default.sock` and `beardog-{family_id}.sock` — the default socket should be a symlink to the family-scoped socket, not a separate instance with different capabilities
2. **biomeOS**: Additive capability discovery (don't wipe registry on rescan cycle)
3. **biomeOS**: Unify socket directories — `biomeos/` should be the canonical path everywhere including the Neural API's own listener
4. **biomeOS**: Socket lifecycle independence — sockets should survive service restarts of neighboring primals
5. **toadStool**: Add JSON-RPC health endpoint alongside tarpc for uniform monitoring
6. **petalTongue**: Accept `--family-id` CLI flag for UniBin v1.1 compliance
7. **All primals**: Standardize response shapes (string vs dict) for common patterns like session/spine creation

### Patterns to Disseminate

1. **Boot Order is CRITICAL**: Tower → Nest → Node → biomeOS LAST. This was proven on both strandGate and now westGate. cellMembrane's `boot_order` support should be the default deployment pattern.
2. **Direct IPC works; Signal graphs need BTSP broker**: Individual primal-to-primal IPC is reliable. The composition broker pattern for cross-atomic orchestration needs more hardening.
3. **Provenance 7/7 pattern is portable**: The same 7-step sequence (content.put → dag.session → dag.event → merkle.root → spine.create → entry.append → braid.create) works on any gate with Nest Atomic deployed. This is the standard data provenance recipe.
4. **`--no-gpu-probe` and `--headless` flags**: Essential for gates without GPU hardware. barraCuda and toadStool both support CPU-only degraded mode.
5. **Environment file split**: `tower.env` for Tower primals, `nest.env` for Nest primals with bearDog socket path — this separation prevents config collisions.

### Next Steps (westGate)

1. **E2E `nest.ingest_dataset` signal graph** with biomeOS v4.47 — now that Provenance 7/7 is proven, test the orchestrated pipeline
2. **AlphaFold bulk ingestion** (~1TB from northGate) through the Nest Atomic pipeline
3. **Enable all 13 services on boot**: `systemctl --user enable` all tower services
4. **Cross-gate federation test**: songBird mesh visibility + `content.replicate.pull` to strandGate

---

## CONFIGURATION CHANGES MADE

- `~/.config/systemd/user/nest.env`: `BEARDOG_SOCKET` → `beardog-westgate-tower-155f.sock`
- `~/.config/systemd/user/nestgate.env`: Same BEARDOG_SOCKET fix
- New service units: `toadstool-tower.service`, `barracuda-tower.service`, `coralreef-tower.service`, `petaltongue-tower.service`, `squirrel-tower.service`
- Depot binaries updated: biomeOS (20,257 KB), bearDog (8,543 KB), sweetGrass (8,336 KB), loamSpine (4,802 KB), rhizoCrypt (7,604 KB)
- New depot binaries fetched: toadStool (13,135 KB), barraCuda (11,410 KB), coralReef (7,585 KB)

---

*westGate NUCLEUS ACHIEVED — second gate after strandGate. 13/13 primals, 29 sockets, 654 capabilities. Provenance Trio 7/7 COMPLETE — first full E2E signed provenance chain on live hardware. biomeOS v4.47 + bearDog crypto.sign + ZFS 25.4TB. ZERO P0s. The ecosystem is alive.*
