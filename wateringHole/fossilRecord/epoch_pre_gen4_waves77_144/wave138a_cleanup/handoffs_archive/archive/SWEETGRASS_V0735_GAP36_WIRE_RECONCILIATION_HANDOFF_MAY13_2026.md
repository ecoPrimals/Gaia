# sweetGrass v0.7.35 — GAP-36 Wire-Name Reconciliation Handoff

**Date**: May 13, 2026
**From**: sweetGrass team
**To**: primalSpring, healthSpring, ludoSpring, ecosystem teams
**Ref**: primalSpring Glacial Debt Escalation — GAP-36 Provenance Trio

---

## Summary

sweetGrass v0.7.35 resolves the GAP-36 composition gap: downstream
springs calling `braid.attribution.create` (and 9 other variant names)
were receiving `-32601 Method not found`, reported as "empty socket
responses." The fix is a static wire-name alias table that transparently
resolves downstream method names to canonical handlers.

Additionally, `lifecycle.status` now has a handler (was classified public
in the JH-0 method gate but returned "Method not found" on all paths).

---

## Root Cause

The "empty socket" report was a **method name mismatch**, not a transport
issue. UDS handlers have always returned well-formed JSON-RPC responses
(including error responses). The issue was that downstream callers sent
method names documented in outdated integration guides:

- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` references `attribution.create_braid`
- `CAPABILITY_DOMAIN_REGISTRY.md` references `provenance.create_braid`
- ludoSpring trio graph references `attribution.create_braid`
- primalSpring handoffs reference `attribution.braid`, `attribution.anchor`
- biomeOS GAP-MATRIX-09: `braid.create` mistranslated to `provenance.create_braid`

None of these matched sweetGrass's canonical `braid.create`.

---

## What Changed

### Wire-Name Alias Table (10 aliases)

| Downstream Name | Canonical Handler |
|----------------|-------------------|
| `braid.attribution.create` | `braid.create` |
| `attribution.create_braid` | `braid.create` |
| `provenance.create_braid` | `braid.create` |
| `attribution.braid` | `braid.create` |
| `attribution.add_contribution` | `contribution.record` |
| `attribution.calculate` | `attribution.calculate_rewards` |
| `attribution.seal` | `braid.commit` |
| `attribution.export_prov` | `provenance.export_provo` |
| `provenance.lineage` | `attribution.chain` |
| `attribution.anchor` | `anchoring.anchor` |

Aliases are resolved in both the handler lookup and the method gate
(so the canonical name's access classification applies correctly).

### `lifecycle.status` Handler

Returns:
```json
{
  "status": "running",
  "primal": "sweetgrass",
  "version": "0.7.35",
  "gate_mode": "permissive"
}
```

### Method Surface

- 37 canonical methods (36 + `lifecycle.status`)
- 10 wire-name aliases
- **47 total accessible wire names**

---

## Downstream Action Required

**Update integration guides** — the following docs reference non-existent
method names and should be updated to use canonical wire names:

1. `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — sweetGrass method table uses
   `attribution.create_braid`, `attribution.add_contribution`, etc.
2. `CAPABILITY_DOMAIN_REGISTRY.md` — sweetGrass examples use
   `provenance.create_braid`, `provenance.lineage`
3. primalSpring `config/capability_registry.toml` — lists `braid.sync`,
   `attribution.claim`, `attribution.resolve` which don't exist

The aliases ensure backward compatibility, but canonical names should be
used going forward.

---

## UDS Response Verification

Confirmed: all UDS transport paths (`handle_uds_connection_raw`,
`handle_uds_connection_btsp`, `handle_uds_with_autodetect`) return
well-formed JSON-RPC 2.0 responses for every request, including:

- Unknown methods → `{"error":{"code":-32601,"message":"Method not found: ..."}}`
- Parse errors → `{"error":{"code":-32700,"message":"Parse error: ..."}}`
- Unrecognized protocols → `{"error":{"code":-32600,"message":"Unrecognized protocol: ..."}}`
- EOF / disconnect → connection closed cleanly (no response required)

---

## Metrics

| Metric | v0.7.34 | v0.7.35 |
|--------|---------|---------|
| Tests | 1,544 | 1,549 |
| LOC | 54,879 | 55,062 |
| Methods | 36 | 37 + 10 aliases |
| Clippy | 0 | 0 |

---

## Verification

```bash
cargo test --all-features    # 1,549 pass, 0 fail
cargo clippy --workspace --all-features --all-targets  # 0 warnings
```
