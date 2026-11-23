# cellMembrane — plasmidBin Ownership Readiness (Wave 82c → Wave 83 DEPLOYED)

**Date**: 2026-06-06  
**Gate**: ironGate  
**Status**: DEPLOYED — plasmidBin ownership active, zero-touch pipeline live on VPS  

---

## What cellMembrane Now Owns (implemented + deployed)

| Capability | Implementation | Status |
|------------|---------------|--------|
| Binary fetch from Forgejo/GitHub releases | `membrane plasmid.fetch` | LIVE |
| Binary push to VPS (atomic replace + restart) | `membrane plasmid.refresh` | LIVE |
| Build from source, checksum, stage to depot | `membrane plasmid.harvest` | **LIVE (Wave 83)** |
| End-to-end zero-touch: harvest → refresh | `membrane plasmid.pipeline` | **LIVE (Wave 83)** |
| Depot freshness monitoring | `membrane plasmid.status` | **LIVE (Wave 83)** |
| Automated 30-min pipeline timer on VPS | `plasmid-pipeline.timer` | **LIVE (Wave 83)** |
| BLAKE3 checksum verification | `plasmid/fetch.rs` (native blake3 crate) | LIVE |
| Service registry derivation | `nucleus_primals()` from `MembraneService::all()` | LIVE |
| Source priority (Forgejo → GitHub → SSH) | `sources.toml` + `FetchSource` enum | LIVE |
| VPS deployment ops (systemd, bridges, firewall) | SSH/SCP transport in `ssh.rs` | LIVE |
| Caddy reverse proxy management | `cloudflare.rs` + manual wiring | LIVE |
| Temporal cascade (workspace sync) | `membrane temporal.cascade` | LIVE |
| K-Derm relay chain | `membrane relay.run` | LIVE |
| Gate health aggregation | `membrane gate.health` | LIVE |

## What Remains (P2 — future waves)

| Item | Priority | Notes |
|------|----------|-------|
| `plasmid.deploy` (absorb remaining `deploy_membrane.sh` ops) | P2 | Full deploy flow in Rust |
| CI workflow wiring (Forgejo Actions) | P2 | Auto-trigger on push |
| Webhook-driven pipeline (vs timer-poll) | P3 | Instant refresh on push |
| Binary taxonomy + evolution velocity tracking | P3 | Size, symbols, dep surface over time |

## VPS Deployment Validation (Wave 83 — CONFIRMED)

| Validation | Status |
|------------|--------|
| 13/13 primals ACTIVE on VPS | **CONFIRMED** |
| 12/13 health.liveness on UDS | **CONFIRMED** (petaltongue needs BTSP auth) |
| skunkBat on TCP localhost:9140 | **CONFIRMED** (--socket pending upstream) |
| UDS-only posture (zero external primal TCP) | **CONFIRMED** |
| 5-domain sovereign TLS (Caddy + Let's Encrypt) | CONFIRMED |
| `socat` bridges for UDS→private-network | OPERATIONAL |
| Federation mesh port :7700 | OPERATIONAL |
| BTSP auth enforced | SINCE 2026-06-02 |
| plasmid-pipeline.timer active (30-min cycle) | **CONFIRMED** |
| Old membrane-self-refresh.timer disabled | **CONFIRMED** |
| Songbird discovery.peers responding | CONFIRMED (0 peers — awaiting mesh enrollment) |

## Fixes Applied During Wave 83 Deployment

| Primal | Issue | Resolution |
|--------|-------|-----------|
| barracuda | May 14 binary lacked `--socket` support | Force-rebuilt from HEAD, `--unix` flag now works |
| squirrel | Ignored `--socket`, bound to biomeos discovery path | Force-rebuilt from HEAD, now binds correctly |
| coralreef | No `--socket` flag in CLI | Unit updated to `--tarpc-bind unix:///run/membrane/coralreef.sock` |

## Codebase Metrics (Wave 83)

- **231 tests** passing (up from 226)
- **Zero clippy warnings** (pedantic + nursery enforced)
- **Zero unsafe code** (`#![forbid(unsafe_code)]` on both crates)
- **Zero `unwrap()` in production** code (all in test fns)
- **Zero hardcoded non-fallback paths** in production
- **Zero mocks** in production code
- **57 Rust files**, 14,931 lines total
- **Max file**: 743L (test coverage module)
- **All external deps pure Rust** (reqwest+rustls, blake3, tokio, serde)

## Resolved Gaps (Wave 83)

| Gap | Resolution |
|-----|-----------|
| squirrel UDS socket binding | Force-rebuilt from latest HEAD — binds correctly now |
| 3 rolled-back VPS binaries | All rebuilt and redeployed |
| Cascade-to-VPS sync gap | `plasmid-pipeline.timer` (30-min zero-touch cycle) |
| No auto-build capability on VPS | `plasmid.harvest` builds from source |

## Remaining Gaps for Upstream Primal Teams

| Gap | Owner | Blocking |
|-----|-------|----------|
| petaltongue BTSP auth required for health probe | ironGate | Health probe (workaround: SocketExists) |
| skunkBat needs `--socket` flag in binary | eastGate | UDS-only audit |

---

*"The pipeline flows. The depot is sovereign. The VPS refreshes itself."*
