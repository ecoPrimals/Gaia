# rhizoCrypt Wave 156e — G63 BTSP Local-Trust via SO_PEERCRED

**Date**: Aug 4, 2026 | **Wave**: 156f | **Head**: `c0abe75`

## Summary

Wire kernel-verified peer credential extraction (`SO_PEERCRED`) on every UDS
connection. `CallerContext` now carries UID/GID/PID from the kernel, enabling
same-machine trust without BTSP key exchange. Unblocks footPrint/tideGlass CAS
write on same gate (G63).

## What Shipped

| Component | Change |
|-----------|--------|
| `PeerCredentials` | New struct: `uid: u32`, `gid: u32`, `pid: Option<i32>` |
| `CallerContext` | New field `peer_cred: Option<PeerCredentials>` |
| `unix_with_peer()` | Constructor with peer credentials for UDS connections |
| `btsp_authenticated_with_peer()` | Constructor for BTSP + peer cred paths |
| `handle_uds_connection` | Extracts `UnixStream::peer_cred()` at accept time |
| `auth.peer_info` | Response now includes `peer_uid`, `peer_gid`, `peer_pid` |
| `process_single_request` | Preserves `peer_cred` through per-request context rebuild |
| `btsp_caller_with_peer()` | `const fn` helper for BTSP handshake paths |
| Tests | 6 new (4 unit + 1 socket pair + 1 E2E UDS), 1,791 total |

## Prior Waves (155n → 156d)

| Wave | Change |
|------|--------|
| 155n | BTSP test isolation: fix 12 leaked `FAMILY_ID` env failures |
| 156b | Wire `notify_dehydration_batch` (N→1 RPC). Purge 11 dead vendor HTTP files (4,100 lines) |
| 156c | RPC integration port collision fix (195xx → 197xx). `BTSP_CLEAR_ENV` isolation |
| 156d | Root doc cleanup. Debris audit (zero orphans). `cargo clean` (14.9 GiB) |

## Quality Gates

- 1,791 tests, 0 failures (`--all-features`)
- 214 `.rs` files, ~59,700 lines
- 0 clippy warnings (pedantic + nursery)
- `cargo deny`: advisories ok, bans ok, licenses ok, sources ok
- Cross-compile clean: `x86_64-pc-windows-gnu`, `aarch64-unknown-linux-musl`
- `cargo doc`: 0 warnings
- 0 unsafe blocks, 0 debt markers, 0 hardcoded values

## Ecosystem Impact

**G63 enables**: footPrint CAS write on ironGate without BTSP key exchange.
When a primal connects to rhizoCrypt via UDS on the same machine, the kernel
proves the connecting process's identity via `SO_PEERCRED`. The method gate can
use `peer_uid` to grant write access to same-user processes — filesystem
authentication plus kernel-verified identity.

**Upstream consumers**: Any primal calling `auth.peer_info` over UDS will now
see `peer_uid`/`peer_gid`/`peer_pid` in the response. Method gate policy
evolution can use these for access control decisions.

## Wave 156f — Root Doc Cleanup + Dep Update (Aug 4, 2026)
- Scrub line counts: ~59,500 → ~59,700 in CONTEXT.md + validation-summary
- Update deployment checklist date (Aug 3 → Aug 4)
- `cargo update`: regex-automata 0.4.17 → 0.4.18
- Debris audit: zero backup/temp/log/empty/orphan files, zero scripts
- TODO/marker scan: zero in .rs, zero in docs (excl CHANGELOG fossil)
- `cargo clean`: reclaimed 13.7 GiB
- `specs/archive/` properly labeled (2 docs, both with status headers)

## Remaining (not rhizoCrypt scope)

- Method gate **policy** to use peer_uid for access decisions (G63 phase 2)
- footPrint/tideGlass need to read `peer_uid` from `auth.peer_info` response
- biomeOS Neural API routing should propagate peer credentials
