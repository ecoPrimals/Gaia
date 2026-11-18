# cellMembrane Wave 55 Deep Debt + Docs Handoff

**From:** cellMembrane team (ironGate)
**To:** primalSpring, projectNUCLEUS, all primals teams, all springs
**Date:** 2026-05-27
**Wave:** 55
**Priority:** Pre-stadial NC-3 + ecosystem debt resolution

---

## Executive Summary

Two-phase sprint responding to the primalSpring audit from the spring river delta:

1. **NC-3 Alignment** — cellMembrane docs and types synced to Nest Atomic VPS reality
2. **Deep Debt** — architectural refactors across all 4 owned repos (cellMembrane, benchScale, agentReagents, plasmidBin)

All tests green, all repos pushed. primalSpring validation scenarios can now activate
live phases against the published `membrane.toml` and K-Derm boundary.

---

## Phase 1: NC-3 Nest Atomic Alignment

### membrane.toml (K-Derm boundary publication — NC-3.2)
- `composition = "nest"` (was "tower")
- `topology = "diderm"`
- Signal channel enabled: `knot-dns` :53, `dnssec = true`
- Unblocks primalSpring `s_kderm_boundary` live validation

### Ops docs synced to Nest Atomic reality
- `VPS_STATE.md` — 11 services, 7 primals, all ports/versions
- `GLACIAL_SHIFT_TRACKER.md` — Nest blocker RESOLVED, DNS status updated
- `README.md` — composition, escalation phase, channels, hardening counts
- `IRONGATE_VERIFICATION.md` — full rewrite for Phase 1.5 / Nest Atomic
- `RUNBOOKS.md` — §1 counts, §5 knot-dns DEPLOYED, §6 Nest ops, §9 composition

### Specs aligned
- `MEMBRANE_COMPOSITION_MODEL.md` — Nest ports corrected (9602, 53, 8443), all 4 channels
- `FIELDMOUSE_CONTRACT.md` — Dark Forest 21/21 for Nest Atomic production
- `MULTI_MEMBRANE_DEPLOYMENT.md` — signal channel `enabled = true` with DNSSEC

---

## Phase 2: Deep Debt — Architectural Evolution

### cellMembrane — Registry Unification

**Single source of truth:** `MembraneService` registry is now the only place where services,
ports, units, and tier membership are defined. `CompositionSpec` derives everything via
`from_registry()` instead of maintaining parallel hardcoded lists.

| Before | After |
|--------|-------|
| Ports in 3 places (channels, services, composition) | Derived from `MembraneService` only |
| `health_method: &'static str` ("health.liveness") | `HealthCheckMethod` enum (Liveness/TcpConnect/HttpsProbe/DnsProbe) |
| Magic `"0.0.0.0"` / `"127.0.0.1"` in service defs | `BIND_ALL` / `BIND_LOOPBACK` constants |
| Hardcoded `7` for cutover days | `MIN_CUTOVER_GATE_DAYS` constant |
| Hardcoded `22` for SSH | `SSH_PORT` constant |
| 225-line monolithic `validate()` | 8 focused sub-validators |
| `dnssec` config swallowed by `extra` map | Typed `dnssec: Option<bool>` on `ChannelConfig` |
| `min_composition` not on services | Each service declares its tier: `min_composition: MembraneComposition::Nest` |

**Impact:** Adding a new service to any composition tier requires changing exactly ONE constant
definition. All ports, units, boot order, firewall rules, and binary integrity expectations
derive automatically.

### benchScale — Type Safety + Error Handling

| Debt | Resolution |
|------|------------|
| `CloudInitProgress.status: String` | `CloudInitStatus` enum (Running/Done/Error/Disabled/Unknown) |
| `apply_network_conditions` silent no-op | Returns `Err` — callers know the operation was not performed |
| `panic!("BUG: ...")` in timeout_utils | Proper `Err` returns |
| clippy auto-fixable warnings | Duration units, redundant patterns resolved |

### agentReagents — Constants + Cleanup

| Debt | Resolution |
|------|------------|
| Magic reboot timing numbers | `DEFAULT_REBOOT_TIMEOUT_SECS`, `MAX_REBOOT_TIMEOUT_SECS`, etc. |
| Magic SSH timeout `120` | `DEFAULT_SSH_CMD_TIMEOUT_SECS` |
| Dead `discovery.rs` comment | Removed |
| `unused_async` clippy allow | Removed (no violations) |
| clippy auto-fixable warnings | `map_unwrap_or`, redundant patterns |

### plasmidBin — Unsafe Elimination + Shared Utils

| Debt | Resolution |
|------|------------|
| `unsafe { std::env::set_var(...) }` for Barracuda | `Command::env()` — no process-wide mutation |
| Duplicated `unsafe { libc::getuid() }` in 2 files | Shared `current_uid()` helper — single unsafe site |
| `stdin.take().unwrap()` in seed.rs | `anyhow` error propagation |
| `parent().unwrap()` in update.rs | `anyhow` error propagation |
| clippy match→if-let | Auto-fixed to zero warnings |

---

## Validation State

| Repo | Tests | Clippy | Push |
|------|-------|--------|------|
| cellMembrane | 80/80 PASS | 0 warnings | `a48a4da` |
| benchScale | 284 PASS | pre-existing only | `6308b48` |
| agentReagents | 113 PASS | pre-existing only | `26444f8` |
| plasmidBin | 24 PASS | 0 warnings | `7b21f62` |

---

## For Primals Teams: Composition Patterns

### Registry-Driven Composition (cellMembrane pattern)

The `MembraneService` registry pattern can be adopted by any primal managing a service
inventory. Key properties:

1. **Each service declares its minimum composition tier** — `min_composition` field
2. **`CompositionSpec::from_registry(tier)`** collects all services at or below the tier
3. **Firewall rules derive from the registry** — `is_externally_reachable()` filters
4. **Binary integrity expectations derive from the registry** — BLAKE3 vs SHA-256 by `is_primal`
5. **Boot order derived from registry insertion order** — primals first, symbiotic second

### NUCLEUS Deployment via Neural API

The composition ladder (relay → rustdesk → tower → nest) maps to biomeOS deployment:
- `biomeos nucleus deploy --composition nest` fetches from plasmidBin, deploys systemd units
- Signal graph: `nest_ingest_spore.toml` defines the spore flow through NestGate
- Provenance: DAG session → rhizoCrypt → loamSpine spine → sweetGrass braid → BearDog sign

### Atomic Composition Instantiation

deploy_membrane.sh (1199 lines) handles atomic composition transitions. Key pattern:
- Stop all services in reverse boot order
- Fetch binaries from plasmidBin releases
- Install systemd units from templates
- Start services in boot order
- Validate composition (UFW, health checks, provenance trio)

---

## NC-3 Remaining Items for Coordination

| ID | Item | Owner | Status |
|----|------|-------|--------|
| NC-3.3 | knot-dns NS cutover to primary | cellMembrane + registrar | knot-dns RUNNING, registrar action needed |
| NC-3.4 | Forgejo Releases alongside GitHub | cellMembrane + plasmidBin | `auto-harvest.yml` ready, coordination pending |
| NC-3.5 | sporePrint living content | cellMembrane + petalTongue | BLOCKED on BearDog `auth.issue_session` scope |

---

## For primalSpring Reconciliation

1. Run `s_membrane_composition` against updated `membrane.toml` (composition=nest, 3 channels)
2. Run `s_kderm_boundary` live validation — K-Derm boundary now published
3. Update `docs/PRIMAL_GAPS.md` NC-3 section: NC-3.1 and NC-3.2 now RESOLVED
4. Update `NICHE_CLIMATE_EVOLUTION.md` NC-3 status
5. Update upstream method count reference from 445 → 460 in `DOWNSTREAM_PATTERN_GUIDE`

---

## Ecosystem Learnings

### Deep debt patterns that worked
- **Registry as single source of truth** — eliminated 3-way sync drift
- **Typed enums replacing strings** — compile-time guarantees on health methods, composition tiers, cloud-init status
- **Named constants replacing magic numbers** — discoverable, greppable, testable
- **`Command::env()` over `set_var`** — eliminates process-wide unsafe mutation
- **Focused validators over monolithic** — 8 sub-validators easier to test and extend than 225-line function
- **`min_composition` on service definitions** — tier membership declared at source, not re-hardcoded in composition builders

### What to watch for in other repos
- Any `println!` in library code (should be `tracing`)
- Any `panic!`/`unwrap` in non-test code (should be `?` / `Err`)
- Stringly-typed fields compared with `== "done"` patterns (should be enums)
- Duplicate path/port/name constants across modules (should be single registry)
- `unsafe { set_var }` before spawning children (should be `Command::env`)
