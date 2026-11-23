# primalSpring Wave 75b — Live Validation Prep

**Date**: 2026-06-04  
**Author**: eastGate — primalSpring evolution  
**Status**: Delivered  
**Tests**: 884 (852 unit + 4 integration + 10 ecosystem + 18 doc), zero clippy

---

## Delivered

### 1. BTSP Trust Chain as Pass Criterion (P0)

The `s_covalent_mesh` security phase now treats `verification_source="remote"` as a
**hard pass/fail** criterion for bearDog w137+:

| Check | Criterion |
|-------|-----------|
| `security:verify_source_remote` | Token accepted with `verification_source="remote"` |
| `security:btsp_gate_binding` | Response includes `gate_origin` proving provenance |
| `security:btsp_trust_chain` | Full chain valid: issued by local gate, verified for remote requestor |

When bearDog is pre-w137 (doesn't support `verification_source`), checks gracefully skip.
When w137+ is detected via successful `verification_source="local"` call, they become
strict requirements.

### 2. Live Cross-Gate capability.call (Phase 4)

`s_cross_gate_capability_call` gains Phase 4: **Live BTSP — cross-gate capability.call
via Songbird**:

1. Check `LiveMeshConfig` for reachable Songbird federation endpoints
2. Attempt `capability.call` targeting strandGate's `security.health.liveness`
3. If call succeeds, issue local BTSP token with `gate_origin`
4. Send authenticated `auth.verify_ionic` cross-gate with `verification_source="remote"`
5. Validate trust chain: token issued on eastGate, verified on strandGate

Gracefully handles capability propagation gaps (Songbird not yet advertising remote caps).

### 3. benchScale Topology

Created `benchScale/topologies/cross_gate_trust.toml`:

- Defines 2-gate mesh (eastGate ↔ strandGate) with addresses, ports, capabilities
- Specifies `pass_criteria` — which checks must PASS for validation
- Documents Dark Forest network constraints
- `LiveMeshConfig::from_topology_file()` loads when `BENCHSCALE_TOPOLOGY=cross_gate_trust`

### 4. Deep Debt Confirmed Clean

| Target | Result |
|--------|--------|
| Files >800L | CLEAN (max 775L) |
| External deps | Pure Rust (blake3 `features=["pure"]`) |
| Unsafe code | `#![forbid(unsafe_code)]` all crate roots, zero blocks |
| Production unwraps | Zero |
| Mocks in production | Zero |
| Hardcoding | Self-knowledge only, capability-first everywhere |
| Copyright headers | ADDED to 154 files |
| `warn(missing_docs)` | ADDED (zero new warnings) |

---

## Upstream Gaps (for primal teams)

### P0: Songbird Capability Propagation

Songbird's federation relay dispatches calls correctly (HTTP/TCP), but does NOT
yet **advertise remote capabilities** to local callers. This means `capability.call`
with `gate=strand-gate` works structurally but `capability.discover` on eastGate
doesn't show strandGate's capabilities.

**Owner**: Songbird team (southGate)  
**Impact**: Phase 4 checks skip rather than pass when propagation gap is detected  
**Fix path**: Songbird federation advertises remote peer capabilities in `discovery.peers` response

### P1: bearDog w137 — `verification_source` and `gate_origin`

bearDog w135 has the trust model but needs w137 for:
- `verification_source` parameter in `auth.verify_ionic`
- `gate_origin` field in verification response

**Owner**: bearDog team (southGate)  
**Impact**: `security:btsp_gate_binding` and `security:btsp_trust_chain` skip on pre-w137  
**Fix path**: bearDog adds these fields to `auth.verify_ionic` response when param is present

### P2: NestGate Content Federation Trust

`content.replicate.pull` needs to return BLAKE3 hash for end-to-end verification.
Currently skipped in `s_covalent_mesh` Phase 5.

**Owner**: NestGate team (ironGate)

---

## Next Steps

1. **Await Songbird capability propagation** → Phase 4 checks transition from skip→pass
2. **Await bearDog w137** → BTSP trust chain checks transition from skip→pass
3. **Live cross-gate test execution** — when both above are delivered, run:
   ```bash
   BENCHSCALE_TOPOLOGY=cross_gate_trust cargo run --bin primalspring -- validate --scenario cross-gate-capability-call
   ```
4. **DNS NS registrar cutover** — operator (pending)
5. **westGate enrollment** — hardware pending

---

*"The test infrastructure is ready. When upstream delivers, we validate."*
