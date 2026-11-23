<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog — Wave 49 "Primals on the Mountain" Audit Acknowledgment

**Date**: May 25, 2026
**Audit**: Wave 49 — Primals on the Mountain (primalSpring eastGate)
**bearDog item**: BearDog Vault (encrypted creds at rest) — Phase 2, not blocking shift

---

## Status: Acknowledged — No action required for glacial shift

### What exists today

1. **`secrets.*` JSON-RPC IPC** (4 methods: store, retrieve, list, delete) — In-memory encrypted store using family-scoped HKDF-SHA256 → ChaCha20-Poly1305. Lazy NUCLEUS purpose-key derivation from `FAMILY_SEED` (Wave 74). Secrets survive restart via deterministic re-derivation.

2. **`FileVaultBackend`** (beardog-production) — AES-256-GCM encrypted files on disk at `$BEARDOG_DATA_DIR/vault/`. Used for BearDog's own production config secrets. Not exposed via IPC.

3. **Consent gating** — `security.verify_consent` / `security.issue_consent_token` for wetSpring vault data access (HMAC-SHA256 tokens). Shipped.

### Phase 2 gap (enhancement, not blocker)

The two vault implementations (IPC in-memory + production file-backed) are not connected. Arbitrary peer secrets stored via `secrets.store` are lost on restart unless re-derivable from `FAMILY_SEED`. Phase 2 would unify these paths or wire `SecretsHandler` to capability-discovered `storage.store`/`storage.retrieve` providers (pattern exists in `ionic_bond/persistence.rs`).

Per ROADMAP: "enhancements — nothing is blocking production use."

### Shift readiness

- S4 auth shadow: consuming through us (no primal action needed)
- S1 TLS shadow: `beardog-acme` operational (ACME renewal daemon wired, Wave 112)
- All 3 Wave 49 tightening vectors: complete (Wave 113/113b)
- Quality gates: fmt, clippy (0 warnings), test (14,940+) all pass
