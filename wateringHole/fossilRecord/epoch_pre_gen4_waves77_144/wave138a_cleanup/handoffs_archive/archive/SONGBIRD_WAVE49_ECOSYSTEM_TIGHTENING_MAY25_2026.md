# Songbird — Wave 49 Ecosystem Tightening

**Date**: May 25, 2026  
**From**: Songbird evolution team  
**Audit**: primalSpring Wave 49  
**Status**: ALL ITEMS RESOLVED

---

## Pipeline Debt Resolution

### 1. `mesh.init` with `bootstrap_peers` (HIGH)

**Was**: `mesh.init` only accepted `bootstrap_onions` (Tor relay addresses). Cross-gate TCP
discovery required external wiring.

**Now**: `bootstrap_peers` param accepts `[{node_id, address}]` objects. Each valid peer is
added as a `Direct` endpoint to `BeaconMesh` at init time. Invalid entries (malformed addresses,
missing fields) are silently skipped. Cross-gate discovery now works at `mesh.init` call.

**Tests**: 2 new — valid peers added + invalid peers skipped gracefully. 21 mesh handler tests total.

### 2. `--security-socket` CLI flag (MEDIUM)

**Was**: plasmidBin binary had no CLI flag for security provider endpoint; required env var.

**Now**: `--security-socket <endpoint>` global flag on orchestrator binary. Sets
`SECURITY_PROVIDER_ENDPOINT` via `songbird_process_env` overlay (zero `unsafe`, thread-safe).
Existing 5-tier env var discovery chain remains as fallback.

### 3. Sled DB corruption (N/A)

**Status**: Not applicable. Sled was fully eliminated in Wave 135 (SB-03 resolved).
No sled dependency, no corruption risk. Only a historical comment in `domain_methods.rs`
references its removal.

---

## Cleanup Vectors Verified

| Vector | Status |
|--------|--------|
| A: Stale deployment patterns | CLEAN — `deployment/relay/README.md` updated from `target/release/songbird` to `plasmidBin/songbird`; only `specs/archived/` references old paths |
| B: Local wateringHole | CLEAN — no local `wateringHole/` tree; all handoffs in central `infra/wateringHole/handoffs/` |
| C: Showcase fossilization | CLEAN — songbird has never had a `showcase/` directory |

---

## Verification Checklist

- [x] No `showcase/` directory
- [x] No local `wateringHole/` — clean
- [x] No `which songbird` or `target/release/songbird` in active scripts
- [x] `notify-plasmidbin.yml` active in `.github/workflows/`
- [x] Commit references Wave 49 ecosystem tightening

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 7,803+ lib passed |
| Clippy | pedantic + nursery, zero warnings (May 25 verified) |
| Format | `cargo fmt --check` clean |
| Unsafe | 0 (`forbid(unsafe_code)` × 31 crates) |
| Debt | Zero — all primalSpring items resolved through Wave 49 |

---

## Remaining Horizon (operational, not code)

- NAT traversal field testing on residential NAT (flockGate deployment)
- VPS relay shadow run (cellMembrane VPS rendezvous)
- Live STUN/TURN integration tests with real servers

*Post-primordial. plasmidBin is the channel.*
