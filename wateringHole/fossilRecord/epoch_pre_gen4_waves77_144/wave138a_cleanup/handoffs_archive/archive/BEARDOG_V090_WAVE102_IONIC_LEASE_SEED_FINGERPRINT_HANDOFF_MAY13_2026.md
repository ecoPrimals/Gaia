<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 102: Ionic Lease + Seed Fingerprint

**Date**: May 13, 2026
**Primal**: bearDog
**Audit ref**: primalSpring Glacial Debt Escalation (May 13, 2026) — GAP-16 Tower atomic
**Status**: RESOLVED (H2 niche tasks: ionic lease + seed fingerprint)

---

## Summary

Resolves two bearDog niche tasks from the glacial debt escalation audit:
1. **Ionic lease on `crypto.sign_contract`** — time-bounded contract signatures with
   lease expiry checking in `crypto.verify_contract`
2. **`crypto.seed_fingerprint`** — Tower atomic identity verification for ludoSpring
   GAP-16

---

## 1. Ionic Lease (`crypto.sign_contract`)

### API Changes

**`crypto.sign_contract` request** — new optional field:

```json
{
  "signer": "tower_a",
  "terms": {"type": "gpu_lease", "hours": 4},
  "context": "gpu_lease",
  "ttl_seconds": 3600
}
```

**`crypto.sign_contract` response** — new optional field:

```json
{
  "terms_hash": "...",
  "signature": "...",
  "public_key": "...",
  "signed_at": "2026-05-13T16:00:00Z",
  "expires_at": "2026-05-13T17:00:00Z"
}
```

**`crypto.verify_contract` request** — new optional field:

```json
{
  "terms_hash": "...",
  "signature": "...",
  "public_key": "...",
  "expires_at": "2026-05-13T17:00:00Z"
}
```

**`crypto.verify_contract` response** — enhanced:

```json
{
  "valid": false,
  "expired": true,
  "error": "ionic lease expired"
}
```

### Behavior

- Without `ttl_seconds`: behavior unchanged, no `expires_at` in response
- With `ttl_seconds`: lease expiry computed as `signed_at + ttl_seconds`
- `crypto.verify_contract` with `expires_at`: checks both signature AND lease
- `crypto.verify_contract` without `expires_at`: pure signature check (backward compat)

---

## 2. Seed Fingerprint (`crypto.seed_fingerprint`)

### API

```json
{ "method": "crypto.seed_fingerprint" }
→ {
    "fingerprint": "a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8",
    "algorithm": "BLAKE3-over-HMAC-SHA256",
    "version": "seed-fingerprint-v1"
  }
```

### Construction

```text
fingerprint = hex(BLAKE3(HMAC-SHA256(FAMILY_SEED, "seed-fingerprint-v1"))[0..16])
```

- Non-reversible: HMAC + BLAKE3 double-hash
- Stable: deterministic from seed, same fingerprint across restarts
- Compact: 32 hex chars (16 bytes)
- Requires: `BEARDOG_FAMILY_SEED` or `FAMILY_SEED` env var

### Tower Atomic Use

ludoSpring's Tower atomic validation (GAP-16) calls `crypto.seed_fingerprint` to
verify that bearDog's identity seed is consistent. This replaces the need for
full key exchange during validation — the fingerprint proves identity without
exposing secret material.

---

## H2 Niche Task Status

| Task | Status | Notes |
|------|--------|-------|
| `crypto.sign_contract` ionic lease | RESOLVED | `ttl_seconds` + `expires_at` + lease-aware verify |
| Purpose-key derivation | ALREADY COMPLETE | `crypto.derive_purpose_key` + `crypto.derive_public_key` shipped pre-Wave 102 |
| Federation | ALREADY COMPLETE | `auth.public_key` shipped Wave 99 (H3 horizon) |
| `crypto.seed_fingerprint` | RESOLVED | New method for Tower atomic (GAP-16) |

---

## Metrics

| Metric | Value |
|--------|-------|
| Crypto IPC methods | 106 (was 105) |
| New tests | 10 (5 ionic lease + 5 seed fingerprint) |
| Total tests | 14,940+ |
| Failures | 0 |
| Quality gates | 4/4 (fmt, clippy, doc, test) |

---

## GAP-16 Remaining

BearDog's IPC surface is ready for Tower atomic validation. The remaining
GAP-16 blocker is **deployment**: bearDog, songbird, and skunkBat must be
running on local UDS for ludoSpring to execute live Tower atomic validation.
This is an ops/deployment concern, not a code gap.
