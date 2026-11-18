# cellMembrane — Wave 119+ Native Evolution Handoff

**Date:** 2026-06-20
**Wave:** 119+
**Gate:** sporeGate
**Supersedes:** CELLMEMBRANE_WAVE118_DEEP_DEBT_JUN19_2026.md

---

## Summary

Two commits shipped since Wave 118: test coverage expansion + error normalization
(`3a9828a`), and native detection + error normalization + hardcode elimination
(`6e5956d`). Combined: 29 files touched, +351/-243 lines, 711 tests, zero clippy.

---

## Shell-out → Rust-native evolution

| Before | After | Module |
|--------|-------|--------|
| `ss -tlnp` (port 53 check) | `/proc/net/{tcp,udp}` hex port + state parsing | `gate/preflight.rs` |
| `ip -j link show` + `ip -j addr show` | `/sys/class/net/` sysfs enumeration | `gate/interface.rs` |
| `ip -j route show default` | `/proc/net/route` destination `00000000` | `gate/interface.rs` |
| `systemctl is-active NM` | `/sys/fs/cgroup/system.slice/{unit}/cgroup.procs` | `gate/preflight.rs` |

Fallback: `ip -j addr show` retained for IPv4 address resolution when `/proc/net/fib_trie`
parsing is insufficient. All other `ip`/`ss`/`systemctl` shell-outs replaced.

---

## Error semantic normalization

`ShadowError::Parse` reduced from ~60+ production uses to 22 genuine parsing operations.

| Category | Variant | Files affected |
|----------|---------|----------------|
| Missing CLI args/flags | `Config` | cli.rs, caddy/mod.rs, cloudflare/mod.rs |
| Missing env vars/tokens | `Config` | cloudflare, digitalocean, dispatch/mod.rs |
| Invalid enum values | `Config` | cli.rs (impulse type, status) |
| Missing config files | `Config` | manifest.rs, depot.rs, lib.rs |
| SSH failures | `Ssh` | provision/bootstrap.rs |
| File I/O errors | `Io` (via From) | depot.rs, integrity.rs |
| DO API non-2xx | `Config` | provision/digitalocean.rs |
| reqwest transport | `Http` (via ?) | provision/digitalocean.rs |

---

## Safety evolution

| Pattern | Before | After |
|---------|--------|-------|
| `HmacSha256::new_from_slice().expect()` | 3 sites in ribocipher.rs | `let Ok(..) = .. else { unreachable!() }` |
| reqwest error wrapping | `map_err(\|e\| Parse(format!(...)))` | `?` via `From<reqwest::Error>` |
| depot sources.toml read | `map_err(\|e\| Parse(format!(...)))` | `map_err(ShadowError::Io)` |

Zero `.unwrap()` in production, zero `unsafe`, zero `panic!`.

---

## Hardcode elimination

- Added `PLASMID_BIN_DIR` constant (`"plasmidBin"`) to cellmembrane-types
- Replaced 8 hardcoded `"plasmidBin"` literals across 6 files
- `gate/verify.rs` now uses `INFRA_PLASMID_BIN` constant for checksums path

---

## Test coverage: 707 → 711

| Module | New tests |
|--------|-----------|
| `gate/preflight.rs` | 4: hex port formatting, TCP LISTEN state parsing, route parsing |
| `gate/interface.rs` | 1: proc/net/route default gateway parsing (replaced `build_addr_map` test) |

Total: 711 tests across workspace, all passing.

---

## Remaining debt inventory

| Item | Priority | Status |
|------|----------|--------|
| git2 crate for read-only git ops | P2 | Pending — currently shell-outs via `git_ops.rs` |
| webhook.receive HTTP/UDS listener | P2 | Pending — Caddy integration |
| systemctl restart/enable → zbus D-Bus | P3 | Pending — only is-active replaced |
| gate/bootstrap.rs 655L | P3 | Borderline — mostly tests |
| temporal/post_sync.rs 637L | P3 | Borderline — mostly tests |
| coverage.rs 817L | P3 | Test-only file |
| provision-golgi.sh | P4 | Deprecated — fossil record |

---

## Upstream dependency table

| Crate | Role | Rust-native? |
|-------|------|-------------|
| tokio | Async runtime | Yes |
| reqwest | HTTP client (DO, Cloudflare, WAN fetch) | Yes |
| serde/serde_json/toml | Serialization | Yes |
| blake3 | Binary checksums | Yes |
| hmac/sha2 | Webhook HMAC, riboCipher | Yes |
| tracing | Structured logging | Yes |
| chrono | Timestamps | Yes |
| git2 | Not yet adopted | Planned |
| nix | Process signals | Yes |
| dirs | Home directory | Yes |

---

## Docs updated

- README.md: 711 tests, Wave 119+ block, sysfs tree reference
- VPS_STATE.md: Wave 119+, test count 711
- RUNBOOKS.md: Wave 119+, fixed duplicate §12, daily health → membrane CLI
- IRONGATE_VERIFICATION.md: Wave 119+, native detection noted
- GLACIAL_SHIFT_TRACKER.md: Wave 119+, reconciled test counts
- membrane.toml: Wave 119+
- capability_registry.toml: Added 20+ missing capabilities
- CI: Added musl target install step
- provision-golgi.sh: Marked deprecated
