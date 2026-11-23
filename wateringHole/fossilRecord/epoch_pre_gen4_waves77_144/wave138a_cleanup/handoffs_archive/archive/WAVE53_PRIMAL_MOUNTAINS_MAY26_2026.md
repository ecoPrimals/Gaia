# Wave 53 — Primal Mountain Teams Handoff

**Date**: 2026-05-26  
**From**: primalSpring (coordination)  
**To**: All primal teams  
**Context**: PostPrimordial complete. Full NUCLEUS live on eastGate (13/13, 19/19
sockets, plasmidbin doctor 35/35). Glacial shift wave plan published to
`wateringHole/GLACIAL_SHIFT_WAVE_PLAN.md`.

---

## Status: All 13 primals SHIPPED via plasmidBin

All mountains are clean. Zero debt markers ecosystem-wide. This handoff
requests targeted work to close the last gaps before we push to deployment
and springs.

---

## Per-Primal Guidance

### Network + Orchestration

#### songbird (CRITICAL)

SouthGate reporting only 7/13 primals health-responding. Songbird crashes
are the primary suspect.

- Investigate crash logs on southGate — what's causing process exits?
- Verify `unlink()` before `bind()` on stale socket cleanup at restart
- Coverage push: **73.4% → 90%** (target for glacial shift exit)
- BTSP multi-frame stress tests under sustained load
- Tor onion crypto: blocked on external security provider — document as deferred
- v0.2.1 production ready; no code debt, this is ops + coverage only

#### biomeOS (NO ACTION)

v3.76, 8,026 tests, 0 blocking debt. Production ready. One tracked TODO
(`live_discovery.rs` REST route) is enhancement-only. Continue normal
evolution. FYI: Neural API routing will need primal-scoped socket discovery
in Wave 54 (cephalization) — no prep needed now.

### Crypto + Security

#### bearDog (PREP FOR WAVE 54)

v0.9.0, 14,940 tests, 90.51% coverage. Production ready.

- **SouthGate**: verify BearDog socket health during the stability investigation
- **TCP drop prep**: prepare to run UDS-only (no TCP 9900/9101) for the
  Tower CNS convergence prototype (exp114). All crypto capabilities must remain
  reachable via domain sockets.
- Optional: persistent secret storage via discovered `storage.*`

#### skunkBat (IMPORTANT)

v0.2.0, 389 tests, BTSP Phase 3.

- **seed_fingerprint missing** in plasmidBin manifest — v0.2.0 was promoted
  without BLAKE3 fingerprint. Verify this backfills on the next auto-harvest
  cycle. If not: `plasmidbin harvest --version-tag v0.2.0`
- Thymic selection model (self/non-self probes via BearDog lineage) is
  design-phase — continue at current pace

#### bingoCube (NO ACTION)

v0.1.1, 54 tests. Library-only crate, no IPC server, no wave-critical work.

### Provenance Trio

#### rhizoCrypt (NO ACTION)

v0.14.0, 1,646 tests. Focus is provenance-trio E2E with loamSpine/sweetGrass
in live compositions — that's a Wave 55 item. Cold-start latency (8s timeout
workaround) is documented. No mountain debt.

#### loamSpine (LOW — document only)

v0.9.16, 1,528 tests.

- PostgreSQL/RocksDB backends are roadmap items, not glacial blockers.
  Document current state (redb + memory) in `WHATS_NEXT.md`.
- v0.10.0 signing middleware + collision-layer validation is next natural step

#### sweetGrass (NO ACTION)

v0.7.38, 1,560 tests. Stadial ready. v0.8.0 (live signing/session providers,
convergence tracking) is a natural Wave 55 target. No mountain debt.

### Compute Trio

#### barraCuda (INCREMENTAL)

v0.4.0, 4,393 tests, 87 IPC methods.

- Coverage expansion toward 90% (needs GPU hardware for full validation)
- Live coralReef CI for full compile→dispatch pipeline (cross-primal)
- DF64/Yukawa on real silicon; HMMA tensor-core path
- Spring absorption: airSpring and hotSpring consume `math.*`/`tensor.*`

#### coralReef (INCREMENTAL)

Sprint 12, 3,204 tests. Pure compiler (diesel stack excised).

- Depth texture comparison PTX
- Array/cube texture support
- Push coverage toward 90%
- Live toadStool discovery integration tests

#### toadStool (INCREMENTAL)

v0.2.0, 23,000+ tests, 88 JSON-RPC methods.

- Coverage push **83.6% → 90%**
- Expand sovereign VFIO dispatch
- Songbird `ipc.register` self-registration in compositions
- Cold-start latency: 8s timeout workaround documented, not blocking

### AI + UI + Tooling

#### squirrel (NO ACTION)

v0.1.0 pre-alpha, 7,093 tests, 90.1% coverage. Production inference
functional. Live provider E2E in compositions is a Wave 55 item
(groundSpring + neuralSpring integration).

#### petalTongue (NO ACTION)

v1.6.6, 6,321 tests. Coverage ~85% → 90% is incremental. Downstream
dashboards (lithoSpore, wetSpring) are spring-side work.

#### sourDough (LOW)

v0.3.1 locally, plasmidBin manifest still shows 0.3.0.

- Bump manifest after next harvest cycle
- v0.4.0 `harvest --all/--release` and Phase 3 live health probes are
  enhancement-only

### NestGate (CRITICAL)

Internal 4.7.0-dev vs plasmidBin 0.1.0 version mismatch.

- **Align Cargo.toml workspace version** with what plasmidBin ships
- **Coverage push**: 84% → 90% target
- Deployed on eastGate Nest atomic; prepare for VPS Nest expansion (Wave 54)

---

## Timeline

Wave 53 work should be completable within the current sprint. SouthGate
stability is the gate for Wave 54 (deployment + cellMembrane).

Respond to this handoff with a brief status ack to `wateringHole/handoffs/`.
