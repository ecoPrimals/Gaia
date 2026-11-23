# NestGate Session 64 — Wave 22 Stadial Gate Readiness

**Date**: May 17, 2026  
**Version**: 4.7.0-dev (internal iteration; workspace `0.1.0`, binary `2.1.0`)  
**Trigger**: primalSpring Wave 22 audit — stadial exit gate

---

## Audit Items Resolved

### CRITICAL: Version Drift

README uses `4.7.0-dev` (internal iteration tracking 64 development sessions),
workspace `Cargo.toml` uses `0.1.0` (pre-1.0 API surface), binary crate uses
`2.1.0`. plasmidBin `manifest.toml` tracks `0.1.0` (workspace root).

**Resolution**: Documented the dual versioning scheme explicitly in README,
STATUS.md, and CONTEXT.md. All versions will unify on the first tagged public
release.

### `capabilities.list` Wire Standard Alignment

All four transport paths now return the standard `{capabilities, count, primal}`
envelope per `CAPABILITY_WIRE_STANDARD.md`:

| Transport | Before | After |
|-----------|--------|-------|
| SemanticRouter | `methods` key, no `count` | `capabilities` + `count` |
| UDS dispatch | `methods` key, no `count` | `capabilities` + `count` |
| JSON-RPC server | `methods` key, no `count` | `capabilities` + `count` |
| Isomorphic IPC | `methods` key, no `count` | `capabilities` + `count` |

### Transport Parity: `identity.get`, `auth.*`, `btsp.capabilities`

Added to SemanticRouter dispatch (was only on UDS + HTTP + JSON-RPC):
- `identity.get` — primal identity
- `auth.check`, `auth.mode`, `auth.peer_info` — MethodGate introspection
- `btsp.capabilities` — **new method**: protocol version, cipher suite, KDF,
  handshake type, and whether BTSP is required

Also wired `auth.*` and `btsp.capabilities` on isomorphic IPC path.

### Stability Tier Annotations

All 16 capability domains in `capability_registry.toml` now carry
`stability = "stable" | "provisional"`:

| Tier | Domains |
|------|---------|
| stable | storage, content, session, nat, beacon, bonding, health, identity, discovery, lifecycle, auth, btsp |
| provisional | model, templates, audit, zfs |

### Vendored Crate Documentation

README now documents the rationale for vendoring `rustls-rustcrypto` and
`rustls-webpki` under `vendor/`: pure-Rust crypto, `ring` elimination from
lockfile, RUSTSEC-2023-0071 mitigation.

---

## Universal Stadial Checklist — NestGate Status

| # | Item | Status |
|---|------|--------|
| 1 | Health triad | PASS |
| 2 | UDS at `$XDG_RUNTIME_DIR/biomeos/nestgate.sock` | PASS |
| 3 | TCP fallback | PASS (env/CLI, not `ports.env`) |
| 4 | `server` subcommand + `--port` | PASS |
| 5 | Standalone startup without FAMILY_ID | PASS |
| 6 | `capabilities.list` standard shape | PASS (fixed this session) |
| 7 | `identity.get` | PASS |
| 8 | `discovery.announce` (NestGate's `primal.announce`) | PASS |
| 9 | Semantic method naming | PASS |
| 10 | `deny.toml` bans ring/openssl/aws-lc-sys | PASS |
| 11 | UDS-first, TCP opt-in | PASS |
| 12 | `strip = true` in release | PASS |
| 13 | `btsp.capabilities` registered | PASS (added this session) |
| 14 | `edition = "2024"` | PASS |
| 15 | `seed_fingerprint` in plasmidBin manifest | PASS (external) |
| 16 | `notify-plasmidbin.yml` | PASS |

---

## Remaining Items (not NestGate code scope)

- **`ports.env`**: NestGate uses `NESTGATE_*` env vars + CLI `--port`, not the
  `ports.env` file pattern. Ecosystem-level decision on whether to converge.
- **musl-static CI**: No musl target in `.github/workflows/ci.yml`. Binary
  builds succeed via `cargo build --target x86_64-unknown-linux-musl` locally;
  CI addition is infra scope.

---

## Verification

- `cargo clippy --workspace --all-features -- -D warnings`: zero warnings
- `cargo fmt --check`: clean
- `cargo test -p nestgate-rpc --lib`: 669 passed, 0 failed
- `cargo test --test capability_registry_crosscheck`: 11 passed, 0 failed
