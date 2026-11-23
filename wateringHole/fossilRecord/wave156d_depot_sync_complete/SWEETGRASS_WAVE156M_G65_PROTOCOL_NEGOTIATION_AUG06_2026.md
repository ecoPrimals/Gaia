# sweetGrass — G65 Protocol Negotiation — Wave 156m AAR

**Date**: Aug 6, 2026 | **Gate**: eastGate | **Commit**: `f1efb27`
**Status**: SHIPPED — G65 protocol negotiation live on main

---

## What Was Done

Implemented G65 Protocol Negotiation Standard (Phase 3 of cephalization) for
sweetGrass. Single-socket protocol selection replaces C2 dual-socket as the
canonical tarpc entry point.

### Wire Protocol

```text
Client → Server: "PROTOCOLS: tarpc,jsonrpc\n"
Server → Client: "PROTOCOL: tarpc\n"
[Connection proceeds in selected protocol]
```

### Implementation

| File | Lines | Purpose |
|------|-------|---------|
| `protocol_negotiation.rs` | 344 | `IpcProtocol` enum, wire parsing, client/server negotiation |
| `peek.rs` | +8 | `DetectedProtocol::ProtocolNegotiation` variant (first byte `P`) |
| `uds.rs` | +30 | `handle_g65_negotiation` — UDS handler routing to tarpc or JSON-RPC |
| `tcp_jsonrpc.rs` | +45 | `handle_g65_negotiation_tcp` — TCP handler |

### Design Decisions

1. **First-byte detection**: `P` (0x50, start of `PROTOCOLS:`) triggers G65.
   Does not conflict with riboCipher signals (0xEC/0xED/0xEE) or ASCII JSON (`{`).
2. **Tarpc framing**: After negotiation selects tarpc, the stream uses
   `tokio_util::codec::length_delimited` + bincode — same framing as C2.
3. **Backward compatible**: riboCipher, BTSP, and raw JSON-RPC unchanged.
4. **C2 remains**: `.tarpc.sock` stays operational for existing clients.
5. **Reference pattern**: Convergent evolution from squirrel/sourDough G65.

### Test Results

- 1,676 tests passing (+14 new protocol negotiation tests)
- 0 clippy warnings
- All files ≤752L

---

## Relationship to C2 Dual-Socket

C2 (Phase 2) proved tarpc works at scale and gave cellMembrane discovery
concrete socket targets. G65 (Phase 3) unifies back to single socket with
protocol intelligence at connection time. C2 remains for backward compat
until all ecosystem clients migrate to negotiation.

---

## Next Steps

- **cellMembrane discovery evolution**: Drop `has_tarpc` field in favor of
  `protocols_supported` from G65 negotiation probes
- **songBird cross-gate negotiation**: Mesh relay gains protocol transparency
- **C2 sunset**: Remove `.tarpc.sock` after all clients adopt G65 (Wave 157+)

---

*sweetGrass G65 — single socket, best protocol, auto-negotiation.*
