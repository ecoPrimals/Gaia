# Handoff: songBird G65 Protocol Negotiation — Wave 156p

**Date**: August 6, 2026  
**Wave**: 156p  
**Author**: overwatch  
**Primal**: songBird  
**HEAD**: (post-commit, see `git log -1`)  
**Status**: G65 SHIPPED

---

## Summary

songBird now implements G65 protocol negotiation on its primary UDS (`songbird.sock`). This completes Phase 3 cephalization for songBird — the primal supports all three phases:

1. **Phase 1**: JSON-RPC (backward-compatible default)
2. **Phase 2**: Dual-socket (`.sock` + `.tarpc.sock`)
3. **Phase 3 (G65)**: Single-socket protocol negotiation

## What Was Done

### Server-side (songbird-orchestrator)

- `bin_interface/ipc_session.rs`: Added G65 detection in the connection handler. After reading the first line, if it starts with `PROTOCOLS: `, the negotiation handler selects the best protocol and responds with `PROTOCOL: <selected>\n`.
- Detection order: riboCipher signal → G65 negotiation → BTSP handshake → plain JSON-RPC. Fully backward-compatible.

### Protocol Negotiation Module (songbird-universal)

- New module: `protocol_negotiation.rs` (~320 lines)
- Types: `IpcProtocol` (JsonRpc, Tarpc), `NegotiationRequest`, `NegotiationResponse`, `NegotiationError`
- Functions: `select_protocol()`, `negotiate_client()`, `negotiate_server_from_line()`
- Wire format: `PROTOCOLS: tarpc,jsonrpc\n` → `PROTOCOL: tarpc\n` (sourDough `d3d125f` pattern)
- Re-exported at crate root for ergonomic use by other primals

### Tests

- 18 unit tests in `protocol_negotiation::tests` (wire roundtrips, parsing, selection logic, duplex negotiation)
- 5 integration tests in `g65_protocol_negotiation_e2e.rs` (live UDS negotiation, backward compat, full duplex)
- Total: 23 new G65-specific tests

## Wire Protocol

```text
Client → Server: "PROTOCOLS: tarpc,jsonrpc\n"
Server → Client: "PROTOCOL: tarpc\n"
[Connection proceeds with selected protocol]
```

If no `PROTOCOLS:` line is sent, the server assumes JSON-RPC (Phase 1/2 backward compatibility).

## Verification

```bash
cargo clippy --workspace --all-targets -- -D warnings  # ZERO warnings
cargo test -p songbird-universal protocol_negotiation   # 18/18 pass
cargo test --test g65_protocol_negotiation_e2e          # 5/5 pass (live UDS)
```

## What This Unblocks

- songBird removed from G65 REMAINING list (was 7/15, now 6/15 remaining)
- cellMembrane can now negotiate with songBird to discover tarpc capability
- Protocol-transparent cross-gate routing can use `negotiate_client()` to auto-select best transport

## Reference

- sourDough `d3d125f` — G65 reference implementation
- `specs/PROTOCOL_NEGOTIATION_SPEC.md` — standard

## Downstream Impact

- cellMembrane: can discover songBird's tarpc capability via G65 negotiation (no longer needs `has_tarpc: bool`)
- Other primals: can use `songbird_universal::negotiate_protocol()` as a client to negotiate with songBird
- Depot rebuild: songBird binary advanced, rebuild needed

---

*Wave 156p — songBird G65 SHIPPED. 9/15 G65 complete (squirrel, sourDough, bearDog, biomeOS, petalTongue, nestGate, rhizoCrypt, sweetGrass, songBird). 6 remaining.*
