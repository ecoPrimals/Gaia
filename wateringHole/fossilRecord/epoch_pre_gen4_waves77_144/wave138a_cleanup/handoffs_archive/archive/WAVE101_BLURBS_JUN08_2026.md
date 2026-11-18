# Wave 101 Blurbs — Mesh Fix v2 Landed, Transport Adoption Accelerating

**Date**: 2026-06-08
**From**: eastGate overwatch
**Context**: songBird shipped fixes for both P1 integration gaps (03f23d45). coralReef and squirrel adopted TransportEndpoint correctly (local impl, no sourdough-core dep). 6/14 primals now have transport injection. Mesh revalidation ready once songBird is rebuilt on eastGate.

---

## songBird Team — P1 Fix v2 Landed, Rebuild Needed

`03f23d45` addresses both integration gaps identified in Wave 100:

- **Gap 1 (security_client UDS routing)**: Trust/lineage API calls now route through adapter transport when endpoint is a UDS socket path. `transport_get`/`transport_post` exposed on `SecurityAdapter`. Lineage method mappings added to `JsonRpcTransport` and `TarpcTransport`.
- **Gap 2 (TLS retry abort)**: `Error::is_http_not_tls()` detection added. TLS retry loop breaks immediately when HTTP-not-TLS is detected instead of exhausting 3 retries against plain-HTTP peers.
- **Bonus**: Discovery bridge no longer blocks on crypto provider failure. `mesh.init` accepts both `bootstrap_peers` and `peers` param keys.

**Status**: Fix is in git. eastGate will rebuild from source and revalidate with:
```bash
SECURITY_PROVIDER_SOCKET=/tmp/biomeos/biomeos/security.sock \
SONGBIRD_PRODUCTION_BIND_ADDRESS=0.0.0.0 \
songbird server --port 7700

echo '{"jsonrpc":"2.0","method":"mesh.init","params":{"node_id":"eastgate","peers":["192.168.1.173:7700"]},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
# Target: bootstrap_peers_added:1
```

If this passes, **3-gate mesh is live**. We'll report back immediately.

---

## Transport Evolution Scorecard — 6/14 Adopted

Wave 100 trigger got fast response. Updated adoption status:

| Primal | Status | Pattern | Notes |
|--------|--------|---------|-------|
| sweetGrass | **DONE** | LOCAL | v0.7.53 — wire-compatible, 0 new deps |
| nestGate | **DONE** | LOCAL | Session 97 — 13,116 tests |
| coralReef | **DONE** | LOCAL | `0a2f2f6` — `ipc::transport` module, 19 new tests |
| squirrel | **DONE** | LOCAL | `f1c06822` — 7,098 tests, Phase 2 (outbound) pending |
| barracuda | **DONE** | **FIX NEEDED** | `47a17b62` — imported `sourdough-core` path dep, must remove |
| rhizoCrypt | **DONE** | **FIX NEEDED** | `1caf0f9` — imported `sourdough-core` path dep, must remove |
| loamSpine | ACK | — | Ready, LOW priority (Wave 103) |
| bearDog | PENDING | — | HIGH priority — crypto spine |
| toadStool | PENDING | — | HIGH priority — orchestrator |
| skunkBat | PENDING | — | |
| petalTongue | PENDING | — | |
| songBird | EXEMPT | — | Transport provider |
| biomeOS | EXEMPT | — | Orchestrator |

**Correct pattern** (coralReef, squirrel, sweetGrass, nestGate): Local `TransportEndpoint` type with identical `#[serde(tag = "transport")]` wire format. No cross-primal dependency. The wire format is the contract.

### barracuda + rhizoCrypt — Action Required

You both shipped transport injection (good!) but imported `sourdough-core` as a path dependency. This violates primal self-knowledge — a primal only knows itself. Please:
1. Remove `sourdough-core` from `Cargo.toml` workspace deps
2. Implement `TransportEndpoint` locally in your types crate (~40 lines)
3. Implement `connect_transport()` locally (~30 lines)
4. Reference `sourDough/crates/sourdough-core/src/transport.rs` as spec only

See sweetGrass `sweet_grass_core::transport` or nestGate `nestgate-types::transport` for correct examples.

---

## bearDog Team — Transport Adoption Needed

bearDog is HIGH priority for transport injection (90 TCP refs, crypto spine). With 6/14 primals adopted, bearDog is the critical gap — it's the security provider that every other primal connects to.

**Action**: Implement `TransportEndpoint` locally in beardog types. Accept `TRANSPORT_ENDPOINT` env var. The launcher/Tower Atomic should inject the endpoint — bearDog should not self-bind in production paths.

---

## biomeOS Team — Rebuild Reminder

v4.14 (`a459ec58` — `LocalTrusted` access level) is still in git only. The running binary is pre-v4.14, so `composition.deploy` via `nucleus-deploy --graph-deploy` remains auth-gated.

**Action**: Rebuild and harvest to depot. Once deployed, we revalidate orchestrated graph deployment immediately.

---

## cellMembrane — Depot Staleness

7/14 depot binaries are stale after recent cascade evolution. With 6 primals shipping transport injection code, the depot needs a peptidoglycan rebuild cycle to pick up the new binaries.

**Action**: Trigger peptidoglycan rebuild for stale primals. Priority order: songBird (mesh fix), biomeOS (LocalTrusted), coralReef (capabilities.list + transport), then remaining transport adopters.

---

## Deployment Status

| Gate | NUCLEUS | Federation | Mesh | Next Action |
|------|---------|------------|------|-------------|
| **eastGate** | 13/13 FULL | *:7700 LIVE | Pending songBird rebuild | Rebuild songBird 03f23d45, revalidate mesh |
| **strandGate** | Core + compute | :7700 LIVE | Peer alive | Cascade picks up songBird fix |
| **ironGate** | Deployed (23 UDS) | — | — | Cascade 22/22 parity |
