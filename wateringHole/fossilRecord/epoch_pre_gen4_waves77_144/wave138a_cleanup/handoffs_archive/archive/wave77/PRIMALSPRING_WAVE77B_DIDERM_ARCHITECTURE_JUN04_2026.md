# primalSpring Wave 77b — Diderm Membrane Architecture

**Gate**: eastGate  
**Date**: 2026-06-04  
**Status**: DELIVERED  
**Supersedes**: `WAVE76_REMAINING_WORK_JUN03_2026.md` (deployment phase tracker)

---

## What Shipped

### 1. Diderm Membrane Architecture — Trust Barrier Model

Formalized the diderm (double-membrane) domain architecture with the
peptidoglycan VPS layer as the trust barrier / air gap between outer and
inner membranes.

**New document**: `DIDERM_DOMAIN_ARCHITECTURE.md`

| Domain | K-Derm Layer | DNS | Trust Level |
|--------|-------------|-----|-------------|
| `primals.eco` | Outer (trans) | Cloudflare (acceptable) | Untrusted — verified by cross-validation |
| `primal.eco` | Inner (cis) | Sovereign knot-dns | Full trust — zero commercial |
| `nestgate.io` | Content organelle | Sovereign knot-dns | Content trust — BLAKE3 integrity |

### 2. DNS Zones Created (Live on VPS)

Both zones operational on knot-dns (ns1 + ns2), DNSSEC active, zone
transfer confirmed:

**`primal.eco`** — Inner membrane:
- `primal.eco` A → 137.184.197.151 (golgiBody-ext)
- `mesh.primal.eco` A → [RELAY_PUBLIC] (Songbird)
- `relay.primal.eco` A → [RELAY_PUBLIC] (peptidoglycan TURN)
- `auth.primal.eco` A → [RELAY_PUBLIC] (bearDog BTSP)
- `api.primal.eco` A → [RELAY_PUBLIC] (biomeOS)
- `dns.primal.eco` A → [RELAY_PUBLIC] (knot-dns)

**`nestgate.io`** — Content layer:
- `nestgate.io` A → 137.184.197.151 (golgiBody-ext)
- `www.nestgate.io` A → 137.184.197.151

### 3. Caddy Virtual Hosts

`primal.eco` and `nestgate.io` vhosts added to golgiBody-ext Caddyfile.
HTTP→HTTPS redirect verified. TLS certs will auto-provision after NS cutover.

### 4. Documentation Updates

| Document | Change |
|----------|--------|
| `GLACIAL_SHIFT_READINESS.md` | Revised criteria for diderm model. Criterion 6 = inner membrane zero-commercial + cross-membrane validation. |
| `DEPLOYMENT_PHASE_PLAN.md` | Part C revised. B2 now inner/outer TLS distinction. |
| `SOVEREIGNTY_STANDARDS.md` | §3b layer model + sovereignty shadow membrane applicability. |
| `DARK_FOREST_GLACIAL_GATE_STANDARD.md` | §Dark Forest Membrane Classification (per-pillar per-layer). |
| `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` | Full Porkbun instructions for all 3 domains. |

### 5. Cross-Membrane Validation Scenario

New primalSpring scenario: `s_cross_membrane_integrity` (5 phases, 21+ checks).

- DNS consistency: sovereign NS serves all 3 domains
- Membrane isolation: BTSP opaque relay verification
- Content integrity: BLAKE3 dual-path verification
- Timing baseline: inner membrane response time floor
- Dark Forest classification: outer/peptidoglycan/inner/content

Registered in scenario registry: **61 scenarios, 858 tests, 0 failures**.

### 6. Peptidoglycan Formalization FRAGO

Filed `wave77b-peptidoglycan-fieldmouse-formalization.toml` (P1) to
cellMembrane: formalize `composition = "peptidoglycan"` in `membrane.toml`
schema with trust barrier contract.

### 7. Housekeeping

- 11 delivered handoffs archived to `handoffs/archive/wave77/`
- `GLACIAL_SHIFT_WAVE_PLAN.md` and `GLACIAL_CUTOVER_PLAN.md` archived
  (superseded by `DEPLOYMENT_PHASE_PLAN.md` + `DIDERM_DOMAIN_ARCHITECTURE.md`)
- `freshness.toml` bumped to Wave 77
- `README.md` updated

---

## Metrics

| Metric | Value |
|--------|-------|
| Scenarios | 61 (+1: `s_cross_membrane_integrity`) |
| Lib tests | 858 (0 failures) |
| DNS zones | 3 (primals.eco + primal.eco + nestgate.io), all DNSSEC |
| Handoffs archived | 11 (to wave77/) |
| Active impulses | 4 |
| Active handoffs | 1 (WAVE76_REMAINING_WORK) + this |

---

## Operator Action Needed

| Action | Checklist |
|--------|-----------|
| Set NS at Porkbun for `primal.eco` → `ns1/ns2.primals.eco` | `DNS_NS_CUTOVER_OPERATOR_CHECKLIST.md` |
| Set NS at Porkbun for `nestgate.io` → `ns1/ns2.primals.eco` | Same checklist |
| Review S4 probe log ~Jun 9 | — |

---

## Next Steps (Blurbed Separately)

1. **Code work** → primalSpring evolution team: live cross-gate `capability.call`,
   Songbird Phase 3.5 relay security, content federation
2. **Gate deployment** → cellMembrane + overwatch: peptidoglycan formalization,
   westGate enrollment, peptidoglycan replicability test
3. **User/operator** → Porkbun NS cutover, Cloudflare outer membrane config,
   S4 gate review

---

*"The organism now has two membranes. Between them, the trust barrier
stands. What the world sees is not what the organism trusts."*
