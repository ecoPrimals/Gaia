# Wave 102 Blurbs — Mesh Proven, Transport Near-Complete, Depot Refresh Needed

**Date**: 2026-06-09
**From**: eastGate overwatch
**Context**: Mesh is LIVE (songBird 03f23d45+aebe271f, validated overnight — 10.8h uptime, reachable_peers:1). Transport evolution at 9/11 non-exempt primals. All sourdough-core self-knowledge violations eliminated. NUCLEUS 13/13 alive. Zero P1 blockers in the ecosystem.

---

## toadStool Team — Transport Adoption Needed (Last Remaining Gap)

toadStool is the **only non-exempt primal** without `TransportEndpoint` adoption. 9/11 primals have shipped — you're the last gap before ecosystem-wide transport compliance.

**What to implement** (see sweetGrass or nestGate for reference):
1. Add a local `TransportEndpoint` enum in your types crate with `#[serde(tag = "transport")]` — variants: `uds { path }`, `tcp { host, port }`, `mesh_relay { peer_id, capability }`
2. Implement `connect_transport()` locally (~30 lines — UDS/TCP dispatch)
3. Accept `TRANSPORT_ENDPOINT` env var at startup, log it
4. Keep `--port` as Tier 5 fallback (debug/standalone only)
5. Do **NOT** import `sourdough-core` — the wire format is the contract, implement locally

**Priority call sites** (~101 TCP refs):
- GPU compute dispatch (outbound to compute nodes)
- Orchestration IPC (outbound to biomeOS/songBird)
- Health probe connections

You're at Session 299 with 9,069 tests and zero clippy — the codebase is in great shape for this.

---

## cellMembrane — Depot Refresh Cycle Needed

Multiple primals have shipped significant evolution since last depot rebuild:

| Primal | Key Change | Depot Status |
|--------|-----------|--------------|
| songBird | P1 mesh fix v2 + auth hardening | **STALE** — critical |
| bearDog | Transport Phase 2 + fail-closed PQC | **STALE** |
| barracuda | sourdough-core removal + deep debt | **STALE** |
| rhizoCrypt | 3 waves: transport local + service extract | **STALE** |
| coralReef | Transport + capabilities.list + deep debt | **STALE** |
| squirrel | Transport Phase 2 + deep debt | **STALE** |
| skunkBat | Transport + typed ServerError | **STALE** |
| petalTongue | Transport + deep debt + coverage sprint | **STALE** |
| sourDough | scaffold transport-kit + dep detection | **STALE** |

**Action**: Trigger peptidoglycan rebuild. Priority: songBird first (mesh binary is source-built on eastGate, depot should match), then bearDog (transport + PQC), then sweep remaining.

Running `coralReef` binary still lacks `capabilities.list` — depot rebuild will fix IPC compliance from 11/12 to 12/12.

---

## biomeOS Team — v4.14 Rebuild Reminder

`LocalTrusted` access level (`a459ec58`) is still in git only. Running binary is pre-v4.14, so `nucleus-deploy --graph-deploy` remains auth-gated via BTSP.

**Action**: Rebuild and harvest to depot. Once deployed, `composition.deploy` from local UDS should succeed without capability token. eastGate will revalidate `--graph-deploy` immediately after.

---

## songBird Team — Status Update: Mesh Validated

Both P1 integration gaps are **RESOLVED** and **PROVEN IN PRODUCTION**:

- `SB-SECURITY-URL-01`: Trust/lineage API calls route through adapter transport on UDS endpoints
- `SB-TLS-LAN-01`: TLS retry loop breaks on HTTP-not-TLS detection, discovery bridge degrades gracefully

eastGate mesh running 10.8+ hours, stable. strandGate (192.168.1.173:7700) reachable, healthy, direct path. Auth hardening (`aebe271f`) confirmed: reject-by-default stubs, real TOTP, `/proc/net/fib_trie` detection.

**Next for songBird**: `ipc.resolve` should return structured `TransportEndpoint` JSON (Phase 2 M1). 9/11 primals now accept it — the consumer side is ready.

---

## sourDough — scaffold transport-kit Acknowledged

`4cf83fd` shipping `sourdough scaffold transport-kit` and dep violation detection is exactly right. Two ecosystem actions completed as a result:
- barracuda (`408afaa5`): removed sourdough-core dep, implemented locally
- rhizoCrypt (`e621c6b`): removed sourdough-core dep, implemented locally

Zero sourdough-core self-knowledge violations remain in the ecosystem. `sourdough validate transport` is the compliance check — ready for full ecosystem audit once depot is refreshed.

---

## All Gates — Mesh Enrollment

The mesh protocol is **proven operational**. Any gate running songBird with `03f23d45` or later can enroll:

```bash
SECURITY_PROVIDER_SOCKET=/run/user/1000/biomeos/security.sock \
SONGBIRD_PRODUCTION_BIND_ADDRESS=0.0.0.0 \
songbird server --port 7700

# Then mesh.init with known peers:
echo '{"jsonrpc":"2.0","method":"mesh.init","params":{"node_id":"<gate>","peers":["192.168.1.173:7700","192.168.1.144:7700"]},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
```

| Gate | Status | Action |
|------|--------|--------|
| **eastGate** | LIVE — 13/13, mesh active, *:7700 | Stable |
| **strandGate** | LIVE — federation :7700 | Rebuild songBird from `03f23d45`+ for full mesh fix |
| **ironGate** | Deployed, no federation | Start songBird with `--port 7700` to enroll |

---

## Remaining Work (prioritized)

| # | Item | Owner | Priority | Status |
|---|------|-------|----------|--------|
| 1 | Depot refresh (9 stale primals) | cellMembrane | **P1** | Blocking downstream deploys |
| 2 | toadStool TransportEndpoint | toadStool | **P2** | Last non-exempt gap |
| 3 | biomeOS v4.14 rebuild (LocalTrusted) | biomeOS | **P2** | Unblocks --graph-deploy |
| 4 | coralReef depot rebuild (capabilities.list) | cellMembrane | **P2** | 11/12 → 12/12 IPC |
| 5 | songBird ipc.resolve TransportEndpoint | songBird | **P2** | Phase 2 M1 |
| 6 | loamSpine TransportEndpoint | loamSpine | LOW | Wave 103 target |
| 7 | Pixel aarch64 cross-compilation (12 primals) | cellMembrane | LOW | Only sourdough built |
| 8 | ironGate mesh enrollment | ironGate | LOW | Hardware coordination |
| 9 | WAN covalent validation (flockGate) | flockGate | LOW | Pending coordination |
