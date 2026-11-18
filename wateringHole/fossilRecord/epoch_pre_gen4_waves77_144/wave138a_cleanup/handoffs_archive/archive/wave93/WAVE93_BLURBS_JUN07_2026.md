# Wave 93 Blurbs — Copy/Paste by Team

**Date**: 2026-06-07
**From**: eastGate overwatch
**Cascade**: 38/38 parity | Depot: 12/13 (barracuda broken build) | Pipeline: validated

---

## barraCuda Team

Your latest commit `4d4aacff` ("resolve stash conflict — accept upstream simple_mlp") broke the build. Two missing methods on `SimpleMlp`:

```
error[E0599]: no method named `to_binary` found for struct `SimpleMlp`
  --> crates/barracuda-core/src/ipc/methods/ml/persistence.rs:55

error[E0599]: no function or associated item named `from_auto` found for struct `SimpleMlp`
  --> crates/barracuda-core/src/ipc/methods/ml/persistence.rs:149
```

The stash conflict resolution accepted the upstream `simple_mlp` module but `persistence.rs` still calls `to_binary()` and `from_auto()` which no longer exist. Available methods are `from_json`, `new`, `from_dims`.

Fix: add `to_binary()` and `from_auto()` back to `SimpleMlp`, or update `persistence.rs` to use the available serialization methods.

This is the only broken primal in the depot (12/13 current). Please fix and push.

---

## songBird Team

TransportEndpoint types shipped — thank you. Next gate:

Wire `ipc.resolve` to return `TransportEndpoint` instead of raw path/host:port strings. This unblocks transport injection for all 13 remaining primals. Once `ipc.resolve` returns structured endpoints, composition validation can query Songbird directly instead of probing sockets.

No rush — P2. barraCuda fix and mesh proof are higher priority right now.

---

## cellMembrane Team

All Wave 92 P1 items RESOLVED same-day — outstanding work.

Remaining P2 items (no urgency, next evolution wave):
1. Peptidoglycan as canonical depot host — wiring gate→pepti binary push (SCP/rsync)
2. `plasmid.watch` daemon mode (design only)
3. toadStool divergence resolution (flagged for human review)

The `--with-harvest` flag and refresh-only pipeline are working. 12/13 depot current (barracuda is a team-side code break, not pipeline).

---

## eastGate Operators (self)

Mesh proof is BLOCKED because Songbird :7700 runs on the VPS only, not on the LAN machine (192.168.1.144). strandGate confirmed — port scan shows only :8080 (Forgejo) open on 192.168.1.144.

To unblock mesh proof:
1. Start NUCLEUS + Songbird on eastGate LAN machine (192.168.1.144)
2. Ensure `SONGBIRD_FEDERATION_PORT=7700` and `SONGBIRD_PRODUCTION_BIND_ADDRESS=0.0.0.0`
3. Verify :7700 is reachable from strandGate (192.168.1.132)

This is the sole remaining P1 coordination item.

---

## All Other Teams — NO ACTION

Mountain clear. 38/38 cascade parity. All P1/P2 code items resolved except barraCuda build fix above. S4 auth gate review ends ~Jun 9 (automated).
