# Inner Membrane Deployment — Team Blurbs

**Date**: 2026-06-04 | **Source**: primalSpring Wave 77d evolution review
**Purpose**: Copy-paste context for handing off remaining work to primal teams.

---

## Songbird Team — P0 TLS Fix

**Gap**: SB-TLS-01 — Songbird's TLS crypto client calls `capability.call` on BearDog's UDS socket when `BEARDOG_MODE=direct`. BearDog returns `-32601 Method not found` because `capability.call` is a biomeOS orchestration method, not a BearDog semantic method.

**Impact**: eastGate Songbird cannot originate TLS connections. Cross-gate mesh works asymmetrically (strandGate → eastGate only). Blocks symmetric 2-gate mesh and 3-gate Plasmodium collective.

**Fix**: In Songbird's `BeardogCryptoClient` (or equivalent direct-mode crypto provider), replace:
```
rpc.call("capability.call", {"capability": "crypto", "operation": "sign_ed25519", ...})
```
With direct semantic methods:
```
rpc.call("crypto.sign_ed25519", {"message": "...", "algorithm": "ed25519"})
rpc.call("tls.derive_secrets", {...})
rpc.call("tls.sign_handshake", {...})
```

**Reference**: Wave 169 fixed `SecurityRpcClient::new_direct()` for BTSP security — same pattern needed for TLS crypto. `nucleus_crypto_bootstrap.sh` already uses direct `crypto.hmac_sha256` / `crypto.sign` calls successfully. `capability_registry.toml` has `[tls]` owner = beardog with 3 methods.

**Also**: SB-TLS-02 — Phase 3.5 `NoopSignatureVerifier` needs bearDog `crypto.verify.ed25519` integration.

---

## bearDog Team — P1 Trust Seeding

**Gap**: BD-TRUST-01 — `auth.trust_issuer` was manually called during Wave 77d live cross-gate proof. For mesh to scale, the mesh join handshake must auto-register trust issuers.

**Current**: eastGate manually called `auth.trust_issuer` on strandGate to enable cross-gate `auth.verify_ionic`. The full chain works (PROVEN in handoff), but requires operator intervention per gate.

**Ask**: When a gate joins via Songbird mesh.init + BTSP handshake, bearDog should auto-register the issuer if the BTSP trust chain validates the remote gate's mito-beacon membership.

**Also**: S4 auth graduation review ~Jun 9 (ironGate probes). 7-day gate active since Jun 2.

**bearDog auth.events.poll**: Delivered (Wave 139). rhizoCrypt needs to wire `MeshEventListener` to start polling (RC-POLL-01).

---

## cellMembrane Team — P1 Caddy Reverse Proxy Wiring

**DNS/TLS Status** (Jun 4, RESOLVED):
- `primal.eco` → LIVE, sovereign TLS via Let's Encrypt (HTTP 200)
- `nestgate.io` → LIVE, sovereign TLS via Let's Encrypt (HTTP 200)
- `primals.eco` → LIVE, Cloudflare (HTTP 200, sporePrint served)
- DNS glue (ns1/ns2.primals.eco) → LIVE in Cloudflare, resolves publicly

**Action 1**: Wire `nestgate.io` reverse proxy to Forgejo content:
```caddy
nestgate.io {
    reverse_proxy /content/* localhost:3000
}
```

**Action 2**: Wire subdomain reverse proxies on golgiBody-ext → golgiBody backends:
- `mesh.primal.eco` → Songbird ([RELAY_PUBLIC]:7700)
- `auth.primal.eco` → BearDog  
- `api.primal.eco` → biomeOS neural-api

**Also**: Peptidoglycan teardown/reprovision field test (criterion 3 for stadial).

---

## rhizoCrypt Team — P2 Event Polling

**Gap**: RC-POLL-01 — bearDog delivered `auth.events.poll` (Wave 139). rhizoCrypt's `MeshEventListener` needs to start polling for `TrustIssuerRegistered` events to close the provenance chain.

**sweetGrass**: Holding per strandGate directive until provenance chain is live.

---

## Operator — Overwatch

**DNS/TLS**: ALL RESOLVED. Three-layer diderm membrane is live with sovereign TLS:
- Outer: `primals.eco` (Cloudflare) — sporePrint public surface
- Inner: `primal.eco` (Let's Encrypt on golgiBody-ext) — sovereign inner membrane
- Content: `nestgate.io` (Let's Encrypt on golgiBody-ext) — content layer

**Resolution**: ns1/ns2.primals.eco A records were missing in Cloudflare. Added Jun 4, immediate propagation. Caddy auto-provisioned both LE certs.

**CLOUDFLARE_API_TOKEN**: cellMembrane's `membrane cloudflare.*` module delivered but needs token in `tower.env` on golgiBody-ext for future agentic DNS management.

---

## primalSpring — What We Fixed This Wave

1. **UDS-only registry fix** — Phase 5/5b now uses Songbird UDS socket when `--uds-only` is set. Previously silently failed with TCP port 0 on VPS posture.
2. **NUCLEUS Deep Debt** (Wave 77c) — TOML-driven routing, zero C deps, profile-driven launcher, 33 certification tests, hardcoded cleanup.
3. **Gap documentation** — 4 upstream gaps documented in `PRIMAL_GAPS.md` with fix paths.
4. **Root docs updated** — README/CHANGELOG/CONTEXT at 889 tests, 61 scenarios.
5. **889 tests, zero clippy, zero errors**.

## Minimum for Gate Mesh Join

A gate needs:
1. Shared `FAMILY_ID` + `FAMILY_SEED` (same mito beacon as VPS/other gates)
2. `SONGBIRD_PEERS=vps-gate=<vps-ip>:7700` or `--peers`
3. Songbird + BearDog running (minimum Tower composition)
4. TCP reachability to at least one peer's federation port
5. `nucleus_launcher start --family-id <id> --federation-port 7700 --peers <vps-ip>:7700`
