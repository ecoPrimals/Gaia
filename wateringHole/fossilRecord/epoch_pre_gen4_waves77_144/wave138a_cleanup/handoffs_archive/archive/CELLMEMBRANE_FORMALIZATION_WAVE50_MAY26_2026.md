# cellMembrane — Formalization as Deployable Infrastructure

**From**: cellMembrane team (ironGate)
**To**: primalSpring (upstream audit), all primal teams
**Date**: May 26, 2026
**Wave**: 50
**Priority**: Medium — formalizes membrane architecture for open-source deployability
**Status**: Complete — requesting upstream review

---

## Summary

cellMembrane has been formalized from 8 files (docs + bash scripts) into a typed
Rust system with 5 spec documents, a `cellmembrane-types` crate (**80 tests** across
6 domain modules, zero clippy warnings), and a reference `membrane.toml`
configuration. The K-Derm cell envelope topology models inner/outer membrane sync
as monoderm/diderm topologies with absolute layer naming, bonding per layer, and
channel protein specificity. The architecture is encoded in types that can be
validated programmatically, and the config file is the open-source interface for
third-party membrane operators.

## What Changed

### New: `specs/` (5 documents)

| Spec | Purpose |
|------|---------|
| `CELLMEMBRANE_ARCHITECTURE.md` | Canonical 3-channel model (Signal/Relay/Surface), crypto layers, process isolation, firewall policy, K-Derm topology section |
| `MEMBRANE_COMPOSITION_MODEL.md` | Composition ladder: relay → rustdesk → tower → nest, with per-tier requirements |
| `FIELDMOUSE_CONTRACT.md` | What a fieldMouse deployment must satisfy — hardening, credentials, lifecycle |
| `MULTI_MEMBRANE_DEPLOYMENT.md` | `membrane.toml` schema, provider abstraction, multi-region topology |
| `K_DERM_TOPOLOGY.md` | Cell envelope model — monoderm/diderm, absolute layer naming, bonding per layer, channel proteins, vesicle transport (braid), endosymbiosis |

### New: `crates/cellmembrane-types/` (Rust)

Pure types crate — `#![forbid(unsafe_code)]`, zero async, serde + toml only.

| Module | Types | Source |
|--------|-------|--------|
| `channels.rs` | `MembraneChannel`, `ChannelConfig`, `TrustLevel`, `CryptoLayer` | MEMBRANE_CHANNEL_ARCHITECTURE.md |
| `composition.rs` | `MembraneComposition`, `CompositionSpec` | `deploy_membrane.sh` case statements + `ports.env` |
| `config.rs` | `MembraneConfig`, `HardeningConfig`, `TelemetryConfig`, `ShadowMode` | New — `membrane.toml` parser, typed shadow mode |
| `credentials.rs` | `CredentialModel`, `CredentialFile`, `credential_files_for()` | `share_credentials.sh` + MEM-08/MEM-12 |
| `envelope.rs` | `EnvelopeTopology`, `EnvelopeLayer`, `BondType`, `ChannelProtein`, `BraidPolicy`, `BoundaryPolicy` | K_DERM_TOPOLOGY.md |
| `firewall.rs` | `FirewallRuleset`, `FirewallRule` | UFW logic in `deploy_membrane.sh` |
| `identity.rs` | `MembraneIdentity` | `VPS_STATE.md` + `tower.env` |
| `provider.rs` | `ProviderConfig`, `SubstrateProfile` | Hardcoded DO config in `deploy_membrane.sh` |
| `service.rs` | `MembraneService` (static `&'static str` registry), `BinaryIntegrity`, `binary_integrity_for()` | `membrane/*.service` units + MEM-09 |
| `validation.rs` | `Report`, `ReportEntry`, `Severity` | `plasmidbin-types` pattern |

### New: `membrane.toml`

Reference configuration for the live `membrane-relay` VPS (Tower composition,
DigitalOcean nyc1). This is the file a third party writes to deploy their own
membrane.

### Gap Closure: Dark Forest Audit Alignment

Compared `cellmembrane-types` against `darkforest_membrane.sh` (MEM-01..17),
`s_membrane_composition.rs` (4 pillars), and `ports.env`. Closed 5 gaps:

| Gap | MEM Check | Resolution |
|-----|-----------|------------|
| Journald persistence | MEM-07 | `HardeningConfig.journald_persistent` |
| Credential file permissions | MEM-08, MEM-12 | `credential_files_for()` returns paths + expected mode/owner |
| Binary integrity | MEM-09 | `binary_integrity_for()` with BLAKE3/SHA-256 per binary |
| RustDesk key path | MEM-12 | Included in credential file inventory |
| Telemetry/shadow config | Pillar 4 | `TelemetryConfig` with `shadow_mode`, `cutover_gate_days`, `skunkbat_correlation` |

## Port Registry Note

`cellmembrane-types` models membrane-deployed ports (e.g. rhizoCrypt :9601,
sweetGrass :9850) which differ from `ports.env` gate-standard ports (rhizoCrypt
:9700, sweetGrass :9720). This is intentional — membrane and gate deployments
use different port ranges. The discrepancy is now documented in the types.

### Debt Resolution (Quality Evolution)

| Debt | Resolution |
|------|-----------|
| `MembraneService` allocated 8 `String` fields per lookup | Static `&'static str` registry — zero allocation, `const` service definitions |
| `binary_integrity_for()` used `Box::leak` for static strings | Install paths derived from service registry — no duplication, no leak |
| `shadow_mode: String` (stringly-typed) | `ShadowMode` enum (`Permanent`, `Cutover`, `Disabled`) |
| `boundary_count()` / `periplasm_count()` hardcoded per variant | Derived from `layers()` — capability-based |
| `BoundaryPolicy` named constructors hardcoded bonds | `BoundaryPolicy::for_layer()` derives from `EnvelopeLayer::permitted_inbound_bonds()` |
| 5 clippy warnings (collapsible_if, derivable_impls, iter_cloned_collect) | All resolved |
| `default_true()` duplicated in channels.rs and config.rs | Consolidated to `pub(crate)` in lib.rs |
| `integration.rs` 832L monolith | Smart-refactored into 6 domain test modules (channels, composition, envelope, firewall, service, integration) |

### Test Coverage

80 tests across 6 modules:

| Module | Tests | Domain |
|--------|-------|--------|
| `channels.rs` | 4 | Trust ordering, ports, crypto, serde |
| `composition.rs` | 6 | Ladder, BTSP, specs, serde |
| `envelope.rs` | 27 | K-Derm topology, layers, bonding, policies, serde |
| `firewall.rs` | 5 | UFW derivation, sorting, script format |
| `service.rs` | 15 | Registry, binary integrity, credentials |
| `integration.rs` | 23 | Config parsing, validation, topology inference |

## What Did NOT Change

- `deploy_membrane.sh` — stays operational, Rust types describe the same domain
- biomeOS integration — no compile-time dep on `biomeos-graph` yet
- No CLI binary — types only, CLI follows in a later cycle

## Upstream Review Requested

### For primalSpring
- [ ] Audit `specs/` against existing wateringHole standards for consistency
- [ ] Verify `CompositionSpec` primal lists match `ports.env` compositions
- [ ] Validate `TelemetryConfig` fields against `s_membrane_composition.rs` Pillar 4
- [ ] Review `membrane.toml` schema for open-source consumer readiness

### For primal teams
- [ ] Confirm service port/protocol/bind in static `MembraneService` registry matches your primal
- [ ] Confirm health check method name (`health.liveness`, `tcp_connect`, `https_probe`)
- [ ] Flag any missing credential files in `credential_files_for()`
- [ ] Review K-Derm envelope bonding: is your primal correctly placed in the layer model?

### For projectNUCLEUS
- [ ] Review `HardeningConfig.prohibited_services()` against `darkforest_membrane.sh` MEM-06
- [ ] Validate `BinaryIntegrity` expectations against `checksums.toml`

## Next Cycle

- K-Derm evolution — recursive nesting, endosymbiosis (sovereignty escalation), vesicle transport (braid-as-membrane-coat)
- `cellmembrane` CLI binary (parse + validate + generate UFW script)
- Replace `deploy_membrane.sh` composition logic with Rust
- biomeOS `biomeos-graph` integration (typed `CompositionModel::Membrane`)
- Gate-local membrane layer (inner membrane leading outer)
- benchScale integration — experimentation layer across local/eth/VPS/GitHub
- agentReagents integration — automated testing of K-Derm boundary policies
