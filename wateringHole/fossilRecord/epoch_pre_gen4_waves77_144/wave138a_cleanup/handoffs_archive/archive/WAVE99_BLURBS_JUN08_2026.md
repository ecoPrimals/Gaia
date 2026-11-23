# Wave 99 Blurbs — Mesh Blockers + Orchestration + Cross-Standardization

**Date**: 2026-06-08
**From**: eastGate overwatch
**Context**: Full NUCLEUS 13/13 live on eastGate (all IPC-verified). biomeOS orchestration wired. 3-gate mesh BLOCKED on 2 upstream issues. GLACIAL_SHIFT_READINESS updated.

---

## songBird Team — P1: Two Mesh Blockers

Wave 99 revalidation: we confirmed a LAN peer at 192.168.1.173:7700 is ALIVE — direct HTTP POST to `/jsonrpc` returns `{"status":"alive"}`. The federation layer works. But `mesh.init` returns `bootstrap_peers_added:0` because songbird's internal peer probe pipeline fails at two points:

### SB-TLS-LAN-01 (STILL ACTIVE)

songbird's TLS handshake fails because beardog rejects `crypto.x25519_generate_ephemeral` — it requires a capability token that songbird doesn't have during mesh bootstrap. The peer probe attempts TLS ClientHello, beardog denies the crypto call, probe fails silently.

**Action**: Either acquire a BTSP capability token from beardog during Tower Atomic startup (before mesh.init), or fall back to plain HTTP for LAN peers when TLS setup fails. The peer is serving plain HTTP on :7700 and responding correctly.

### SB-SECURITY-URL-01 (NEW)

songbird formats the beardog trust/evaluate URL as a relative path: `beardog/api/v1/trust/evaluate` — this produces `Invalid URL: invalid format`. It should resolve to the UDS socket path (e.g. `unix:///run/user/1000/biomeos/beardog-*.sock`) or use the `ipc.resolve` pattern.

Logs show this repeating every 10 seconds for every peer:
```
Security provider rejects peer <uuid> — HTTP POST failed for beardog/api/v1/trust/evaluate: Invalid URL: invalid format
```

**Action**: Fix security provider URL resolution to use the UDS socket path from `SECURITY_PROVIDER_SOCKET` / `BEARDOG_SOCKET` env var, or discover via XDG runtime dir.

Both blockers prevent 3-gate mesh. Everything else is proven — federation HTTP works, mesh.init initializes, peer discovery layer is functional.

---

## bearDog Team — P1: Capability Token for Mesh

songbird needs `crypto.x25519_generate_ephemeral` during mesh bootstrap for TLS peer handshake. beardog currently rejects this with "permission denied: requires a capability token". This is the correct security posture for general calls, but songbird as a Tower Atomic peer should be a trusted caller.

**Action**: Either:
1. Grant songbird an automatic capability token during Tower Atomic startup (beardog knows songbird is a co-resident tower primal)
2. Add songbird to a trusted-caller allowlist for crypto operations
3. Expose a token acquisition flow that songbird can call before mesh.init

Secondary: `nucleus-deploy --graph-deploy` now calls `composition.deploy` on biomeOS, which also returns "requires capability token". The BTSP auth flow for orchestration calls needs wiring — biomeOS should be able to acquire a deploy token from beardog.

---

## cellMembrane Team — P2: Depot Staleness + Rebuild

7/14 depot binaries are stale (newer commits exist than what's in the depot). `provenance.toml` now tracks `stale = true` per primal. The stale primals are: barracuda, beardog, loamspine, rhizocrypt, songbird, sweetgrass, coralreef.

**Action**:
1. Trigger peptidoglycan rebuild for the 7 stale primals
2. The depot.rs module (194 lines) is the right direction — evolve it to detect staleness from provenance.toml and trigger rebuilds
3. Consider adding a `cascade --with-rebuild` mode that rebuilds stale primals after cascade completes

Also: strandGate reports sourDough musl binary from depot still segfaults on their gate. Our eastGate depot has the FIXED static-pie binary (2026-06-08 rebuild). strandGate needs to pull the updated binary — they may be caching the May 28 version.

---

## coralReef Team — LOW: capabilities.list

IPC compliance sweep across full NUCLEUS: 12/12 liveness PASS, 12/12 readiness PASS, **11/12 capabilities PASS**. coralReef is the only primal missing `capabilities.list`.

**Action**: Implement `capabilities.list` JSON-RPC method returning the primal's capability set. All other 11 primals have this. Standard response format:
```json
{"jsonrpc":"2.0","result":{"capabilities":["..."],"methods":["..."],"transport":["uds"]},"id":1}
```

---

## biomeOS Team — P2: Orchestration Auth

`nucleus-deploy --graph-deploy` is now wired and working. It successfully probes biomeOS health (alive), calls `composition.deploy`, and verifies via `graph.status`. But both methods return "Permission denied: requires capability token".

**Action**: Wire the BTSP capability token acquisition flow so nucleus-deploy (or a deploy agent) can authenticate with beardog and pass the token to biomeOS orchestration calls. This is the path from flat COMP_* process spawning to graph-driven orchestration.

---

## benchScale Team — LOW: Docker Image Tags

All ecoprimals topology YAMLs use bare `image: ubuntu` which fails on current Docker (manifest media type error). Local images `ubuntu:24.04` and `nucleus-lab-node:latest` are available.

**Action**: Update all topology YAMLs to use `ubuntu:24.04` instead of bare `ubuntu`. Alternatively, add a default image tag resolution in the Docker backend's `get_image()` method.

---

## Deployment Status

| Gate | NUCLEUS | IPC | Mesh | Blocker |
|------|---------|-----|------|---------|
| **eastGate** | 13/13 FULL | 12/12 liveness, 11/12 caps | BLOCKED | SB-TLS-LAN-01 + SB-SECURITY-URL-01 |
| **strandGate** | Core stack + compute | Cascade 24/24 | BLOCKED | Same |
| **ironGate** | Deployed (23 UDS) | Operational | BLOCKED | Same |
| **flockGate** | WAN relay | Operational | Informal | WAN validation pending |
| **Pixel 8** | Handlers wired | — | — | 12/13 aarch64 binaries pending |
