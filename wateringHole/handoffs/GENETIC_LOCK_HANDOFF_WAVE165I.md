# Handoff: Genetic Lock Deployed — Sec-Fetch Breach Closed

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — skunky-ingest / entity_classifier / bearDog integration
**Priority**: Informational — breach already closed, upstream evolution items

---

## What Happened

The Caddyfile on golgiBody had an `@human_browser` matcher:

```caddy
@human_browser {
    header Sec-Fetch-Mode navigate
    header Sec-Fetch-Dest document
}
handle @human_browser {
    reverse_proxy localhost:3000  # ← real Forgejo, bypassing scatter
}
```

The evolved fleet spoofed these two headers and read real source code directly. ~390 of 400 "human-classified" visits were fleet.

## What Was Done

1. **Removed `@human_browser` matcher** — Sec-Fetch headers alone no longer grant passthrough
2. **Generated bearDog-derived bearer token**:
   - Master key: `membrane-passthrough-v1` (AES-256-GCM, Argon2id)
   - Derived: purpose `golgi-body-web-passthrough` (Gen 1, lineage tracked)
   - Token: `bd1-*` (BLAKE3 of derived key entropy)
3. **Set token in `@agent_passthrough`** handler (already existed in Caddyfile)
4. **Caddy validated and reloaded** — zero downtime

## Current Routing

```
git.primals.eco
  │
  ├─ @wg_mesh (10.13.37.0/24) → Real Forgejo       ✅ unchanged
  ├─ @agent_passthrough (bd1-*) → Real Forgejo      ✅ NEW (genetic lock)
  ├─ @human_browser → REMOVED                       ❌ CLOSED (fleet spoofed)
  └─ fallthrough → Scatter (localhost:9753)          ✅ unchanged
```

## Verified

```bash
# Fleet with Sec-Fetch → scatter ✅
curl -H "Sec-Fetch-Mode: navigate" -H "Sec-Fetch-Dest: document" \
  https://git.primals.eco/  # → scatter content

# Agent with bearDog token → real Forgejo ✅
curl -H "Authorization: Bearer bd1-*" \
  https://git.primals.eco/  # → data-theme="forgejo-auto"

# Wrong token → scatter ✅
curl -H "Authorization: Bearer bd1-wrong" \
  https://git.primals.eco/  # → scatter content

# No headers → scatter ✅
curl https://git.primals.eco/  # → scatter content
```

## What sporeGate Needs to Do

### Immediate (optional — breach is already closed)

Nothing urgent. The Caddy-layer lock is functional and verified.

### Next wave — classifier evolution

Wire the 6 conserved epitopes into `entity_classifier`:

| Epitope | Detection Method |
|---------|-----------------|
| `sec_fetch_monotone` | Same Sec-Fetch headers on every request in session |
| `reading_deficit` | <3s between page loads (no human reading time) |
| `ua_pool_poverty` | <10 unique UAs across hundreds of visits |
| `session_absent` | No cookies, no login, no session state |
| `referer_self_loop` | Only self-referrers or empty |
| `burst_ratio` | >50% of intervals <3s |

### Future — Rust-level bearDog integration

Replace Caddy-layer bearer check with scatter_server.rs calling bearDog:

```rust
// In handle_request():
if let Some(proof) = extract_lineage_proof(&request) {
    if genetic::verify_lineage(&proof, &peer_context).await? {
        return proxy_to_forgejo(request).await;
    }
}
// Fall through to scatter
```

Requirements:
- `beardog-client` or `beardog-ipc` as skunky-ingest dependency
- bearDog running on golgiBody (or IPC over WG to eastGate)
- Session-scoped tokens replacing permanent bearer
- SoloKey Tier 3 entropy (human tap + hardware RNG)

### Key material

The bearDog receipts are on eastGate:
- Generate: `receipts/receipt-key-generate-20261007-161539-430.json`
- Derive: `receipts/receipt-key-derive-20261007-161539-433.json`

Key lineage: `membrane-passthrough-v1` (Gen 0) → derived (Gen 1) → BLAKE3 → bearer token

Token is in `/etc/membrane/Caddyfile` on golgiBody (backup: `.bak-{timestamp}`).

---

## AAR Cross-References

- `AAR_EVOLVED_FLEET_SEC_FETCH_SPOOFING.md` — fleet evolution analysis and breach evidence
- `AAR_AGENT_SCATTER_CLASSIFICATION_GAP.md` — original scatter routing gap (all web → scatter)
- `AAR_ENMESHMENT_PHASE1_3_WAVE165I.md` — VPS enmeshment for new nodes

---

*eastGate overwatch → sporeGate. Breach closed, genetic lock live. Upstream items are evolutionary, not emergency.*

*Wave 165i, Oct 7, 2026*
