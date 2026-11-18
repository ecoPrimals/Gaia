# Wave 69: cellMembrane Sovereignty Graduation

**Date**: Jun 2, 2026
**Owner**: ironGate
**FRAGO**: `wave69-irongate-sovereignty-graduation`
**Commit**: `d0f7c31` (cellMembrane main)

---

## Summary

Executed all P0 + P1 items from the Wave 69 sovereignty graduation FRAGO.
cellMembrane's Rust binary is now deployed and operational on the VPS,
S4 auth is enforced, and the relay chain runs entirely in Rust.

## Completed Items

### 1. S1 TLS Graduation — Infrastructure Ready
- Verified Caddy TLS active on golgiBody (`membrane.primals.eco`, `git.primals.eco`, `lab.primals.eco`)
- Verified golgiBody-ext Caddy handles apex (`primals.eco`, `www.primals.eco`)
- Verified knot-dns zone correct, DNSSEC active (serial 2026052215)
- Verified ns1+ns2 serving all records correctly
- S1 gate probe: 198 samples, ZERO failures, p95 < 120ms
- **Blocker**: NS cutover requires registrar action (operator task)

### 2. S4 Auth Formal 7-Day Gate — ACTIVATED
- `BEARDOG_AUTH_MODE=enforced` set in `/opt/membrane/tower.env`
- beardog-membrane restarted with family auth
- `primal.info` now DENIED without capability token (enforcement confirmed)
- s4-auth-gate.timer installed (15-min probes)
- Gate started: 2026-06-02T18:34:41Z (ends ~Jun 9)
- All services healthy post-enforcement

### 3. golgiBody Disk Cleanup — 69% → 60%
- Cleaned: repo-archive (146M), old kernels (2 removed), journals (148M),
  apt lists (143M), locales, vim→vim-tiny, docs, man pages
- Recovered all 14 primal binaries to `/opt/membrane/` (were deleted, recovered from /proc)
- Created `ECOPRIMALS_ROOT` in `/etc/environment` + `/etc/profile.d/`

### 4. Membrane Binary Deployed to VPS
- Built: `x86_64-unknown-linux-musl` (6.1M static-PIE)
- Deployed: `/usr/local/bin/membrane` + symlink at `/opt/membrane/membrane`
- Verified: `membrane temporal.cascade` works on VPS
- Verified: `membrane relay.run` full chain operational
- Provenance sidecar: `/root/.local/share/ecoPrimals/provenance/membrane.toml`

### 5. Relay Bash → Rust Evolution — COMPLETE
- `relay.run` validated end-to-end on VPS (pull + impulse + ship)
- Fixed bug: `git remote get-url` stdout leaked into REMOTE variable
- Workspace resolution evolved for sparse VPS deployments (`infra/` marker)
- Hook promoted: `golgi-post-receive-relay.sh` now calls Rust binary
- Bash scripts archived: old hook moved to `archive/`

### 6. Family Seed Deployment — Already Done
- Seeds confirmed at `/etc/membrane/family/` (all gate lineage seeds present)
- `FAMILY_ID=e8b62b6e`, family name: `ecoPrimals-membrane`

## Remaining (Operator/Future)

| Item | Status | Notes |
|------|--------|-------|
| S1 NS cutover | BLOCKED | Requires registrar access to change NS records |
| S4 7-day gate | IN PROGRESS | Ends ~Jun 9, monitoring active |
| S3 content cutover | FUTURE | Awaits NS cutover + flockGate coordination |
| Forgejo Actions CI | FUTURE | Post-graduation evaluation |

## Metrics

- **Tests**: 209 (cargo test, zero failures)
- **Clippy**: Zero warnings (pedantic + nursery)
- **Disk**: 60% (down from 69%)
- **Services**: 21 active, all healthy
- **Relay**: Rust-native, zero bash dependencies
- **Auth**: BTSP enforced, monitoring active
