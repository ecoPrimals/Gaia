# Songbird Wave 207 — Stadial Readiness

**Date**: May 17, 2026  
**Wave**: 207  
**Audit Reference**: primalSpring Wave 22 — Stadial Gate (May 17, 2026)  
**Category**: Stadial readiness, capability registration, deny.toml hardening, composition documentation

---

## Summary

Wave 207 closes all Songbird items from the primalSpring Wave 22 stadial gate audit. Songbird is now stadial-ready: universal standards checklist fully green, `btsp.capabilities` wired as a dispatchable method, `deny.toml` updated, and composition readiness documented.

---

## Universal Standards Checklist — Songbird Status

### Runtime ✅
- Health triad: `health.liveness`, `health.readiness`, `health.check` — all wired
- UDS socket: `$XDG_RUNTIME_DIR/biomeos/network.sock` (symlink from `songbird.sock`)
- TCP fallback: `SONGBIRD_HTTP_PORT` respected
- `server` subcommand with `--port` for JSON-RPC
- Standalone startup without `FAMILY_ID`/`NODE_ID`

### Discovery ✅
- `capabilities.list` returns `{ capabilities, count, primal, version, methods, provided_capabilities, consumed_capabilities, protocol, transport }`
- `identity.get` returns canonical L3 identity
- `primal.announce` implements self-registration (Wave 205)
- All 48 methods follow `{domain}.{operation}` naming

### Security ✅
- BTSP handshake mandatory when `FAMILY_ID` set (non-"default")
- ChaCha20-Poly1305 + HKDF-SHA256 with `btsp-v1`
- `FAMILY_ID` + `BIOMEOS_INSECURE=1` = hard error (refuse to start)
- `btsp.capabilities` registered in capability response (NEW — Wave 207)
- Zero metadata leakage (stripped binary)
- UDS-first default (TCP off unless explicitly enabled)
- `deny.toml` bans `ring`, `openssl`, `aws-lc-sys` (aws-lc-sys NEW — Wave 207)

### Build / plasmidBin ✅
- `manifest.toml` version `0.2.1` matches released tag
- `checksums.toml` entry with BLAKE3 hashes for 4 Tier 1 targets
- `seed_fingerprint` BLAKE3 hash present and correct
- `notify-plasmidbin.yml` workflow fires on release/tag push
- CI green on all targets
- musl-static clean
- `edition = "2024"` in workspace Cargo.toml

### Documentation ✅
- README.md version matches manifest (0.2.1)
- CHANGELOG.md documents Wave 207
- CONTEXT.md current: 15 capabilities, 31 crates, 0 files >800L

### Composition Readiness (stadial-specific) ✅ NEW
- Stability tiers annotated for all 48 methods (Stable/Operational/Introspection/Passthrough)
- Degradation behavior documented (5 consumer categories)
- Downstream pairing documented (cellMembrane, lithoSpore, springs, gardens)

---

## Changes Made

### Code
- `deny.toml`: Added `aws-lc-sys` to banned crates
- `songbird-types`: New `BtspMethod` enum (`Negotiate`, `Capabilities`) + `JsonRpcMethod::Btsp` variant
- `songbird-types`: `as_wire_str` / `from_wire_str` / `normalize_json_rpc_method_name` updated
- `songbird-universal-ipc`: `btsp_capabilities()` response (protocol, version, ciphers, KDF, features)
- `songbird-universal-ipc`: `btsp.capabilities` wired through `IpcServiceHandler` dispatch
- `songbird-universal-ipc`: `SONGBIRD_CAPABILITY_STRINGS` 14→15 (`network.btsp`)
- `songbird-universal-ipc`: `CALLABLE_METHODS` +2 (`btsp.negotiate`, `btsp.capabilities`)
- `songbird-universal-ipc`: `capabilities_list()` envelope adds `capabilities` + `count` fields
- `songbird-universal-ipc`: `CAPABILITY_METHOD_MAP` adds `("network.btsp", &["btsp.negotiate", "btsp.capabilities"])`

### Documentation
- `REMAINING_WORK.md`: Added "Stadial Readiness — Composition Documentation" section
- `CHANGELOG.md`: Wave 207 entry
- `CONTEXT.md`: 14→15 capabilities, `network.btsp` added
- `README.md`: 33→34 domain sub-enums

---

## Verification

```
cargo check --workspace          ✅ zero errors
cargo fmt --check                ✅ clean
cargo clippy --workspace -D warnings  ✅ zero warnings
cargo test -p songbird-universal-ipc -p songbird-types --lib  ✅ 506 pass
cargo deny check                 ✅ advisories ok, bans ok, licenses ok, sources ok
```

---

## Remaining (per audit — non-blocking)

- **Cross-gate dispatch via songBird** (Phase 2, LOW priority) — multi-gate composition routing
- **sources.toml cosmetic** — `ecoPrimals/songBird` GitHub repo matches; primal ID is lowercase `songbird` — no action needed

---

## Songbird Stadial Readiness: CONFIRMED

All items from primalSpring Wave 22 audit are green. Songbird enters the stadial clean.
