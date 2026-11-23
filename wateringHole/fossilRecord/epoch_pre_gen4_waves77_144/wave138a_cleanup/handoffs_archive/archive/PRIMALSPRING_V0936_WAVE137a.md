# primalSpring v0.9.36 — Wave 137a Evolution Handoff

**Date**: 2026-07-11 | **Wave**: 137a | **From**: primalSpring overwatch (eastGate)

## Delivered

### New Scenarios (+4, total 136)

| Scenario | Track | Validates |
|----------|-------|-----------|
| `pure-rust-crypto-audit` | Security | deny.toml enforcement, Cargo.lock purity, BLAKE3 pure feature, RustCrypto stack, ecosystem build reproducibility |
| `mesh-federation-readiness` | Transport | Mesh topology parse, federation port config (7700), zone topology, manifest↔mesh parity, live probe |
| `live-composition-deploy` | AtomicComposition | footPrint SPA readiness — manifest entry, relay topology, hosting composition, drawbridge alignment, deploy invariants |
| `federation-wan-readiness` | Transport | (from parallel cascade) WAN federation structural checks |

### Metrics

| Metric | Value |
|--------|-------|
| Version | 0.9.36 |
| Tests | 1,106 pass / 0 fail |
| Scenarios | 136 (12 tracks, 3 tiers) |
| Clippy | zero warnings |
| Wave config | 137a |

## Upstream Gaps Surfaced

These are structural gaps discovered by the new scenarios that upstream teams should address:

| Gap | Owner | Action |
|-----|-------|--------|
| flockGate 0 mesh peers (port 7700) | mesh team | Fix WG overlay port/bind — `mesh-federation-readiness` will validate |
| footPrint SPA not yet deployed to golgi | sporeGate | FP-DEPLOY: rsync dist/client, add Caddy handle_path block |
| skunky-ingest not deployed | skunkBat + sporeGate | Binary built, needs systemd unit on golgi |
| SIGN-01 keys not generated | cellMembrane | 3 blockers documented in AAR |
| Pure Rust audit ecosystem-wide | all primal teams | primalSpring validates own tree; each primal should add deny.toml |

## Architecture Notes

- `pure-rust-crypto-audit` embeds deny.toml, Cargo.lock, and manifest at compile time — validates without network
- `mesh-federation-readiness` can probe live songBird when security capability is available
- `live-composition-deploy` validates the hosting pattern (golgi hub → sporePrint/footPrint SPA) structurally

---

*primalSpring overwatch: ecosystem validated, gaps surfaced, cascade pushed. Next: await FP-DEPLOY + SIGN-01 activation from upstream teams.*
