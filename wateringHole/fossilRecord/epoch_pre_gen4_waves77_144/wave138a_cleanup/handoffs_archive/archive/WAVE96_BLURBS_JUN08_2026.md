# Wave 96 Blurbs — Mesh Transport Negotiation + Launcher Env Propagation

**Status**: All 3 gates deployed from plasmidBin. beardog capability.call VERIFIED.
strandGate + ironGate both ACK. Two remaining blockers for mesh.

---

## songBird Team — P1: Two Blockers

### SB-TLS-LAN-01: Plain HTTP Peer Probe Support

Songbird HTTP client sends TLS ClientHello to LAN federation peers serving plain HTTP
on `:7700`. Peer responds `HTTP/1.1 400 Bad Request` → handshake fails →
`bootstrap_peers_added: 0`. **Confirmed on ALL 3 gates independently.**

Fix options:
1. Detect plain HTTP response during TLS handshake and fall back to non-TLS
2. Add TLS termination to federation server (using beardog TLS methods)
3. Probe with plain HTTP health check first, upgrade to TLS for data

### SB-STARTUP-01: Security Provider Env Propagation

When launched via `nucleus_launcher`, songbird does NOT receive
`SECURITY_PROVIDER_SOCKET` / `BEARDOG_SOCKET` env vars. It falls back to
`/var/run/biomeos/neural-api.sock` which doesn't exist → TLS handshake crash loop.

**Confirmed on both strandGate and eastGate.**

Fix: songbird should discover beardog via:
1. Explicit env var (`SECURITY_PROVIDER_SOCKET`, `BEARDOG_SOCKET`)
2. XDG capability symlink (`$XDG_RUNTIME_DIR/biomeos/security.sock`)
3. Songbird should NOT crash if security provider is unavailable — degrade to
   non-TLS federation until provider discovered

**Priority**: P1 — both block production mesh deployment.

---

## biomeOS / nucleus_launcher Team — P2: Env Propagation

`nucleus_launcher` must propagate these env vars to child processes:
- `SECURITY_PROVIDER_SOCKET` → beardog socket path
- `BEARDOG_SOCKET` → same (legacy compat)
- `SONGBIRD_SECURITY_PROVIDER` → same (songbird-specific)

strandGate finding: `nucleus_launcher --seed-only` registers 9 primals with Songbird,
but songbird crashes without manual env vars. The launcher knows where beardog is
(it started it) — it should tell songbird.

Also: `ipc.register` returns "Invalid params" during seeding — songbird ipc.register
API may have evolved. Needs investigation.

**Priority**: P2 — launcher env propagation enables automated deployment.

---

## cellMembrane / ironGate — Status: Deployed, Env Consolidated

**Completed (thank you)**:
- Env var consolidation: 9 typed constants in `cellmembrane-types::service`
- toadStool divergence resolved (master→main rename)
- Cascade: **22/22 parity** (first clean sweep)

**Next**: VPS peptidoglycan NUCLEUS deployment. The VPS can serve as an additional
mesh node once SB-TLS-LAN-01 is resolved. This validates WAN deployment from
plasmidBin alongside LAN gates.

**Priority**: P2 (waiting on songbird fixes for mesh).

---

## hotSpring / strandGate — Status: Deployed, Validated

**Completed (thank you)**:
- Full rollback/redeploy from plasmidBin — matches ironGate pattern
- Core stack running: beardog (capability.call), songbird (:7700), skunkbat,
  barracuda, coralreef
- Cascade: 24/24 parity

**Findings documented**: SB-STARTUP-01 (env propagation), UniBin subcommand
requirement. 8 primals exit during health check — same as ironGate, expected
until env consolidation rolls out.

**Next**: Standby for SB-TLS-LAN-01 fix. eastGate currently on WiFi (.65) —
ethernet transient. Will mesh.init with all 3 peers once transport fixed.

---

## eastGate / primalSpring — Overwatch

- Songbird: LIVE on 192.168.1.65:7700 (WiFi, ethernet transient)
- beardog: LIVE with capability.call
- Depot: 13/13 current
- Cascade: 36/38 (resolved divergences, re-cascading)
- primalSpring: 52 scenarios, 887 tests, 52/52 bare cert

**Active**: monitoring SB-TLS-LAN-01 and SB-STARTUP-01 resolution. Transport
evolution (Phase 2 M1 ipc.resolve) next after mesh proven. VPS NUCLEUS deployment
planning with cellMembrane.

---

## Deployment Status — All 3 Gates

| Gate | Depot | Core Stack | Cascade | Mesh | Blocker |
|------|-------|------------|---------|------|---------|
| **eastGate** | 13/13 | beardog + songbird | 36/38 | BLOCKED | SB-TLS-LAN-01 |
| **strandGate** | 13/13 | beardog + songbird + skunkbat + compute | 24/24 | BLOCKED | SB-TLS-LAN-01 |
| **ironGate** | 13/13 | beardog + songbird | 22/22 | BLOCKED | SB-TLS-LAN-01 |
