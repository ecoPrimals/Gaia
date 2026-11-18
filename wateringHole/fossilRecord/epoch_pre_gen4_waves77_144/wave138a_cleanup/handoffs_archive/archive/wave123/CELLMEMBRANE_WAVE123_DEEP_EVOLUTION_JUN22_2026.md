# cellMembrane — Wave 123 Deep Evolution Status

**Date**: Jun 22, 2026 | **From**: cellMembrane team (sporeGate)
**Wave**: 123 | **Tests**: 769 (up from 731 at Wave 120)
**Supersedes**: CELLMEMBRANE_WAVE121_TRANSPORT_ENVELOPE_BLURB.md (transport tasks completed)

---

## Completed (Wave 121–123)

### P1: Quorum Phase 1 — Autonomous Cascade Timer
- `gate.quorum` CLI command: generates + installs systemd `.service` + `.timer` units
- `membrane-cascade.timer` runs `membrane temporal.cascade --source forgejo` on interval
- `RandomizedDelaySec=60` prevents thundering herd across gates
- Supports `--generate` (preview), `--interval N`, `--dry-run`

### P1: TransportEndpoint.mesh_relay — Graduated to Operational
- `call_via_relay()` routes JSON-RPC through songBird relay socket
- `call_endpoint()` dispatches to UDS/TCP/MeshRelay transport variants
- `resolve.rs` unified endpoint resolver: `(gate, capability)` → `TransportEndpoint`
- `topology.endpoint` CLI command for transport resolution

### P1: TCP Transport — Graduated
- `call_tcp()` implements riboCipher-framed JSON-RPC over WireGuard mesh
- All three `TransportEndpoint` variants now operational

### P1: Dual-Target Depot
- `TargetArch` enum: `X86_64Musl`, `X86_64Gnu`, `Aarch64Musl`
- GPU primals (`barracuda`, `coralreef`) build gnu alongside musl
- ELF validation adapted for dynamic gnu binaries

### P1: PAT → SSH Auth Evolution
- File-based `~/.config/forgejo/token` deprecated with runtime warning
- Environment variable or BTSP auth preferred

### P0: Wire Format Bug Fix
- `ServiceCapability::wire_name()` const method + `Display` impl
- Fixed mesh relay routing: `"cryptosigner"` (Debug) → `"crypto_signer"` (serde wire format)
- Comprehensive tests assert wire_name matches serde for all 9 capabilities

### P0: Sovereignty Ledger Coverage
- `parse_verify_response()` extracted as pure function from `sovereignty_verify()`
- 7-branch test suite: all-match, mismatch, missing-from-ledger, JSON error, invalid JSON, missing key, empty heads
- Error variant fix: `ShadowError::Ssh` → `ShadowError::Parse` for UDS failures
- Fragile `contains("error")` → structured JSON field check

### Deep Debt
- Role-to-capability mapping consolidated (`resolve::role_to_capability` canonical)
- `parse_capability_name` delegates to canonical mapping
- `is_local()` case-insensitivity verified
- Documentation updates across all root docs

---

## Remaining (cellMembrane Team)

| Task | Priority | Status |
|------|----------|--------|
| Tier 3 isomorphism (gate.migrate, gate.bootstrap --absorb) | P2 | Design ready |
| golgi-as-NUCLEUS evolution (nestGate, bearDog, biomeOS integration) | P2 | Blocked on Tier 3 |
| DNS config generation (gate.provision --dns) | P2 | Tier 2 extension |
| webhook/pipeline.rs test coverage | P1 | Zero tests, needs coverage |
| freshness publish merge / auto-commit race guard tests | P1 | Edge case coverage |
| context weave/sense/clear integration tests | P2 | Integration coverage |
| nucleus start_primals / generate_secrets_env tests | P2 | Integration coverage |
| jsonrpc JsonRpcError + policy/fallback types | P2 | String errors → typed |

---

## Codebase Health

- **769 tests**, all passing
- Zero clippy warnings (pedantic + nursery)
- Zero doc warnings
- Zero unsafe code (`#![forbid(unsafe_code)]`)
- Zero production `unwrap()`/`expect()`
- Zero hardcoded primal names or IPs
- All files < 600 lines
- AGPL-3.0 + CC-BY-SA + ORC triple license
