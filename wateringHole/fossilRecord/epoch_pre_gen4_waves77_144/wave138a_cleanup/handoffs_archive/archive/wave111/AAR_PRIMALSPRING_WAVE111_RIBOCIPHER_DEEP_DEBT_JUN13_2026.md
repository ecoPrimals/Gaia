# AAR: primalSpring Wave 111 — riboCipher + Deep Debt Evolution

**Date**: 2026-06-13
**Team**: primalSpring
**Gate**: eastGate
**Commits**: `93207ac` (riboCipher), `6e16bfb` (port registry + deep debt), `d98c2b1` (LAUNCHER-01 + proto-nucleate)

---

## Summary

primalSpring is **code-complete for Wave 111**. All evolution targets shipped, all divergence scenarios implemented, riboCipher transport signal adopted, and remaining structural deep debt (port registry duplication, env-key constants, neural routing coupling) eliminated.

---

## Shipped (Wave 111)

### Stream 7: riboCipher Transport Signal (`93207ac`)

All outbound IPC connections from primalSpring now prepend `[0xEC, 0x01]` (clear tier, v1) before any JSON-RPC or BTSP handshake bytes.

| Layer | Coverage |
|-------|----------|
| Shared IPC stack (`ipc/transport.rs`) | `Transport::unix`, `unix_btsp`, `tcp` — covers PrimalClient, NeuralBridge, CompositionContext, harness, all 60 validation scenarios |
| Standalone TCP (`ipc/tcp.rs`) | `tcp_rpc_with_timeout`, `http_json_rpc` — cross-gate TCP probing |
| Launcher inline (`registry.rs`) | `health_check_tcp`, `send_uds_rpc`, `seed_songbird_peers`, `register_with_songbird` |

Constants: `tolerances::RIBOCIPHER_CLEAR_SIGNAL`, `RIBOCIPHER_CLEAR` (0xEC), `RIBOCIPHER_VERSION` (0x01).

### Deep Debt: Port Registry Consolidation (`6e16bfb`)

- **Removed**: 13 `TCP_FALLBACK_*` constants, `DEFAULT_SQUIRREL_PORT` alias, 13 per-primal `*_PORT` env-key constants
- **Result**: `config/ports.toml` is the single source of truth. `default_port_for("slug")` and `port_env_key("slug")` are the sole public APIs for port resolution.
- **Net**: -217 lines of port duplication eliminated across 18 files
- **Neural routing**: Removed `"biomeos"` from `CompositionTier::from_domain` — routing is pure capability domains

### LAUNCHER-01: aarch64 Cross-Compile (`d98c2b1`)

- `.cargo/config.toml`: `[target.aarch64-unknown-linux-musl]` with linker + static CRT
- `rust-toolchain.toml`: declares both musl targets
- `cargo cross-aarch64` alias
- **Verified**: 1.8MB statically-linked stripped ELF for ARM aarch64

### Proto-Nucleate Manifest (`d98c2b1`)

- `config/proto_nucleate.toml`: structured TOML template for gate deployments
- `nucleus_launcher --manifest <path>`: loads family_id, composition, federation_port, peers from manifest
- Examples for westGate (nest/7), northGate (full/13), grapheneGate (aarch64/edge)

### Stream 6: Divergence Pressure (3/3 COMPLETE)

- `s_version_skew_detection` — detect version skew across mesh health responses
- `s_cascade_provenance_match` — validate post-cascade state matches depot provenance
- `s_wan_ipc_tolerance` — validate IPC within tolerance over high-latency links

---

## Codebase Health

| Metric | Value |
|--------|-------|
| Tests | 1005 |
| Validation scenarios | 60 (11 tracks) |
| Clippy | 0 warnings (`-D warnings` clean) |
| Unsafe | Zero (workspace `deny` + `#![forbid(unsafe_code)]`) |
| Production mocks | Zero |
| TODO/FIXME/HACK | Zero |
| External C deps | Zero (pure Rust, `nix` for POSIX signals only) |
| Files > 800L | Zero (largest: 673L) |
| Port source of truth | Single (`config/ports.toml`) |
| Transport signal | riboCipher v1 clear tier on all connections |

---

## Upstream Gaps (for primal teams)

| Gap | Team | Description |
|-----|------|-------------|
| riboCipher server-side adoption | ALL primals | Accept loops need to read+verify the 2-byte signal prefix. primalSpring sends it; primals need to expect it. |
| `primal.list` not implemented | biomeOS | `s_schema_standard` scenario skips — biomeOS doesn't expose full roster RPC |
| `compute.dispatch.submit` not wired | toadStool | `s_compute_triangle` scenario skips |
| `crypto.ionic_bond.verify_proposal` | bearDog | `s_ionic_bond` scenario skips |
| `bonding.status` not routed | biomeOS | `s_domain_contract_sweep` scenario skips |
| `session.state` not exposed | loamSpine | `s_domain_contract_sweep` scenario skips |

---

## Next Actions

primalSpring is in **STANDBY** for Wave 111. All code evolution complete. Remaining work in the ecosystem is operational (VPS rebuild, gate cascades, hardware enrollment) and upstream primal team adoption (riboCipher server-side, gap resolution).

---

*Filed by primalSpring evolution team, eastGate.*
