<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 113b: Root Doc Cleanup & Orphan Purge

**Date**: May 25, 2026
**Scope**: Post-Wave 49 tightening — doc alignment, method count drift, showcase reference cleanup, orphan code purge.

---

## Deliverables

### Root Doc Date Alignment
All 7 root docs (README, CONTEXT, ROADMAP, START_HERE, ARCHITECTURE, SECURITY, STATUS) now at May 25, 2026.

### Method Count Drift Fix
- README.md badge line was correct (127) but line 34 said 126 — fixed.
- ROADMAP.md: 126 → 127.
- `docs/PRIMAL_CONTRACTS.md`: Both instances fixed (line 40, line 1500). Handler breakdown corrected: 103 CryptoHandler + 12 IonicBondHandler.

### Stale Showcase Reference Cleanup
Post-fossilization (Wave 113), 8 files still referenced the old `showcase/` tree:
- `Cargo.toml` exclude list: 8 showcase paths removed.
- `ARCHITECTURE.md`: Showcase section updated to "Fossilized".
- `.gitignore`: Showcase un-ignore rules simplified to just README pointer.
- `SCYBORG_EXCEPTION_PROTOCOL.md`, `BEARDOG_ECOSYSTEM_SECURITY_INTEGRATION.md`, `PHYSICAL_GENESIS_BOOTSTRAP_PLAN.md`, `CAPABILITY_BASED_PRIMAL_INTERACTION.md`: References updated.

### ACME Spec Status Update
`specs/ACME_TLS_INTEGRATION_PATH.md` status changed from "Design — not yet built" to "Implemented — crates/beardog-acme/ ships full RFC 8555 client" (shipped Wave 107–112).

### Orphan Code Purge
- `crates/beardog-tunnel/src/universal_hsm_discovery/` — 48 files, 616K — deleted. Never wired into any module tree (`mod universal_hsm_discovery` never declared in `lib.rs`). Active equivalent: `crates/beardog-tunnel/src/tunnel/hsm/universal_discovery/`.

## Quality Gates

- `cargo fmt --check`: PASS
- `cargo clippy --workspace -- -D warnings`: PASS (0 warnings)
- `cargo test --workspace`: PASS (14,940+ tests)
