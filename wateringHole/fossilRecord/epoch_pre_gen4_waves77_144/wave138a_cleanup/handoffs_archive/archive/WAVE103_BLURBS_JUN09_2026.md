# Wave 103 Blurbs — Unlocking WAN/LAN/Cross-Arch Deployments

**Date**: 2026-06-09
**From**: eastGate overwatch

**Where we are**: Mesh LIVE (11.6h+ stable). Transport injection at 10/11 non-exempt primals. Depot fresh (14/14 x86_64-musl). Build-carrying cascades operational (`--with-rebuild`). aarch64 pipeline active — songbird/skunkbat/sourdough confirmed. **P1 blocker**: bearDog `aws-lc` C-dep prevents aarch64 cross-compile. Zero self-knowledge violations. NUCLEUS 13/13 alive.

**What we're driving**: Every remaining item below directly unlocks a deployment topology. Transport injection makes primals deploy identically across UDS/TCP/mesh. `ipc.resolve` connects the consumer side (10 primals ready) to the producer side (songBird). Cross-arch gets us to Pixel. WAN mesh gets us to flockGate. These aren't cleanup — they're the infrastructure for the next phase.

---

## 1. toadStool — Transport Adoption (Last Gap)

You're the only non-exempt primal without `TransportEndpoint`. 10/11 have shipped. This blocks isomorphic deployment of any composition that includes toadStool (which is most of them — GPU compute is in `tower`, `agent`, `node`, and `full`).

**What to implement** (~60 lines total):

```rust
// In toadstool-types or equivalent:
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "transport")]
pub enum TransportEndpoint {
    #[serde(rename = "uds")]   Uds { path: String },
    #[serde(rename = "tcp")]   Tcp { host: String, port: u16 },
    #[serde(rename = "mesh_relay")] MeshRelay { peer_id: String, capability: String },
}

// In main.rs — accept at startup:
if let Ok(json) = std::env::var("TRANSPORT_ENDPOINT") {
    match serde_json::from_str::<TransportEndpoint>(&json) {
        Ok(ep) => info!("transport = {ep}"),
        Err(e) => warn!("TRANSPORT_ENDPOINT parse error: {e}"),
    }
}
```

**Reference**: sweetGrass `sweet_grass_core::transport` or nestGate `nestgate-types::transport`. Do NOT import `sourdough-core` — implement locally.

**Why it matters**: Without this, toadStool needs manual `--port` configuration on every deployment. With it, the launcher injects the right transport for the topology.

---

## 2. songBird — `ipc.resolve` Must Return Structured Endpoints (Phase 2 M1)

10 primals accept `TRANSPORT_ENDPOINT`. Nobody produces it yet. `ipc.resolve` is the keystone that connects the two sides.

**Current**: `ipc.resolve` returns plain strings (`/run/biomeos/beardog.sock` or `192.168.1.173:9100`).

**Target**: Return structured JSON that Tower Atomic can inject directly:
```json
{"transport":"uds","path":"/run/user/1000/biomeos/beardog.sock"}
{"transport":"tcp","host":"192.168.1.173","port":9100}
{"transport":"mesh_relay","peer_id":"strandgate","capability":"security"}
```

**Why it matters**: This is what makes topology-aware deployment automatic. When a composition deploys on LAN, `ipc.resolve` returns TCP endpoints to remote primals. On the same machine, UDS. Through the mesh, relay. The primal never knows — it just calls `connect_transport()` on whatever it gets.

---

## 3. biomeOS — Rebuild v4.14 for LocalTrusted

`a459ec58` adds `LocalTrusted` access level. The running binary is pre-v4.14, so `nucleus-deploy --graph-deploy` is still auth-gated.

**Action**: Rebuild from latest, harvest to depot. eastGate revalidates `--graph-deploy` immediately after.

**Why it matters**: Automated graph deployment via `nucleus-deploy` is how we scale from "manually start 13 primals" to "deploy a composition with one command." LocalTrusted means UDS callers (the local operator) can deploy without BTSP token ceremony.

---

## 4. bearDog — Eliminate C Dependencies (P1 Cross-Arch Blocker)

**The central dogma**: Rust compiler is our DNA synthase. All primals must flow through `rustc` alone — no C linkage, no external toolchains, no platform-specific fortification symbols.

bearDog currently depends on `aws-lc-rs` which contains C code. Cross-compiling for `aarch64-unknown-linux-musl` fails with:

```
dsa.c: undefined reference to `__memcpy_chk`
```

`__memcpy_chk` is glibc fortification — unavailable in musl. The C code assumes glibc.

**Action**: Replace `aws-lc-rs` with pure-Rust crypto. See frago `CELLMEMBRANE_WAVE103_AARCH64_BLOCKER_JUN09_2026.md` for the full replacement table.

**Priority order**:
1. beardog eliminates C deps → cross-compiles for aarch64
2. cellMembrane harvests beardog for aarch64-unknown-linux-musl
3. Remaining primals follow (songbird already confirmed, biomeos next)

**Why it matters**: bearDog is the security provider. Every primal depends on it. Until bearDog compiles through pure rustc, no aarch64 NUCLEUS can run. This blocks Pixel 8 / GrapheneOS deployment entirely.

---

## 5. cellMembrane — aarch64 Cross-Compile Pipeline (Progressing)

Pipeline is operational. Results so far:

| Primal | aarch64 | Notes |
|--------|---------|-------|
| songbird | BUILT | 20,231KB static musl |
| skunkbat | BUILT | Previously validated |
| sourdough | BUILT | Previously validated |
| beardog | BLOCKED | aws-lc C-dep (see §4) |
| remaining 9 | Queued | After beardog unblocks |

**Action**: Continue sweep once bearDog ships C-dep elimination. Pipeline, depot staging, and harvest infrastructure are ready.

---

## 6. cellMembrane — Build-Carrying Cascades (DELIVERED)

**Status**: Shipped. `temporal.cascade --with-rebuild` now:
1. Syncs all gardens (existing behavior)
2. Detects stale depot binaries via `plasmid.staleness`
3. Auto-harvests (builds) drifted primals
4. Auto-refreshes (pushes to VPS) rebuilt binaries

Even without `--with-rebuild`, cascade now reports stale primals and suggests the flag. `plasmid.staleness` is also available standalone for depot freshness auditing.

No further action needed — this is operational.

---

## 7. All Gates — Mesh Enrollment

The mesh protocol is proven. Any gate with songBird `03f23d45`+ can enroll:

```bash
SECURITY_PROVIDER_SOCKET=/run/user/1000/biomeos/security.sock \
SONGBIRD_PRODUCTION_BIND_ADDRESS=0.0.0.0 \
songbird server --port 7700

echo '{"jsonrpc":"2.0","method":"mesh.init","params":{"node_id":"<gate>","peers":["192.168.1.173:7700","192.168.1.144:7700"]},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
```

**ironGate**: Start federation port to become 3rd LAN gate.
**flockGate**: WAN mesh validation — proves transport works across network boundaries.

---

## How This Unlocks Deployment Topologies

| Topology | Blocked On | When Ready |
|----------|-----------|------------|
| **LAN multi-gate** | ironGate federation port | Now (protocol proven) |
| **WAN covalent** | flockGate coordination | When flockGate enrolls |
| **Pixel mobile NUCLEUS** | bearDog C-dep elimination (P1) | After bearDog ships pure-Rust crypto |
| **Automated graph deploy** | biomeOS v4.14 rebuild | After rebuild |
| **Topology-aware routing** | songBird ipc.resolve + toadStool transport | After both ship |
| **Zero-touch gate enrollment** | ipc.resolve (build-carrying cascades DONE) | After songBird ships |
