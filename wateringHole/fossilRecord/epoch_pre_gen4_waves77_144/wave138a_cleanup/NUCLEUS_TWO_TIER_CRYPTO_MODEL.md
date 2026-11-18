# NUCLEUS Two-Tier Crypto Model

**Version**: 1.0.0  
**Status**: Phase 55 — Composition-level encryption operational  
**Date**: April 28, 2026  
**From**: primalSpring v0.9.20

## Overview

Every NUCLEUS deployment encrypts data at rest and in transit using a two-tier key hierarchy derived from published primal DNA (seed fingerprints). The model ensures:

1. **No plaintext by default** — even the base tier uses public DNA as encryption input material
2. **Family isolation** — deployments with different `FAMILY_SEED` values cannot read each other's data
3. **Composition-level transparency** — primals don't need to change their internal storage; the composition layer handles encrypt/decrypt through BearDog delegation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 0: Public DNA (plaintext-free by default)             │
│                                                             │
│  plasmidBin BLAKE3 fingerprints → HKDF base key            │
│  Anyone with published fingerprints derives the same key    │
│  Base encryption = "translation" (DNA encoding, not secrecy)│
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: Family Encryption (deployment-specific)            │
│                                                             │
│  base_key + FAMILY_SEED → HKDF family key                  │
│  Unique per deployment. "Nuclear envelope" — all primals    │
│  in a family share crypto, isolated from other families     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: Personal Encryption (human sovereignty)            │
│  [future — on release]                                      │
│                                                             │
│  family_key + human entropy → sovereign key                 │
│  User mixes in personal entropy, clips connection           │
│  System inherits sovereign genetics                         │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

- **BearDog is the sole auth/crypto authority** within a NUCLEUS. Individual primal auth mechanisms (NestGate JWT, etc.) are standalone fallbacks for isolated deployments and are deprecated within compositions.
- **No centralized token servers.** JWT is inherently centralized — a shared secret that must be distributed. The NUCLEUS model uses BearDog's asymmetric crypto and BTSP sessions instead. Each primal proves identity through Tower delegation, not by holding a shared secret.
- **Primals that detect `NESTGATE_AUTH_MODE=beardog` (or equivalent)** should bypass their standalone auth and delegate to Tower. This keeps standalone compatibility while enabling sovereign composition-level security.

## Key Derivation

All derivation happens through BearDog's `crypto.hmac_sha256` — key material never leaves the Tower atomic.

### Tier 0: Base Key

```
base_key = HMAC-SHA256(
    key   = published_fingerprint,       # from seed_fingerprints.toml
    msg   = hex("primal-nucleus-v1:" + primal_name)
)
```

The published fingerprints live in `primalSpring/validation/seed_fingerprints.toml` and are BLAKE3 hashes of the form: `BLAKE3("primal-seed-v1" || primal_name || version || binary_blake3_checksum)`.

### Tier 1: Family Key

```
family_key = HMAC-SHA256(
    key   = base_key + FAMILY_SEED,      # concatenated
    msg   = hex("family-v1:" + FAMILY_ID + ":" + primal_name)
)
```

### Purpose Key (per-atomic)

```
purpose_key = HMAC-SHA256(
    key   = family_key,
    msg   = hex("purpose-v1:" + purpose)
)
```

Purpose values map to atomic functions:

| Primal | Purpose | Use |
|--------|---------|-----|
| NestGate | `storage` | Encrypt-at-rest for all stored data |
| rhizoCrypt | `dag` | Sign DAG event appends |
| loamSpine | `ledger` | Sign ledger entries |
| sweetGrass | `provenance` | Sign braid records |
| ToadStool | `compute` | Encrypt compute job payloads |
| barraCuda | `tensor` | Encrypt tensor data in transit |
| coralReef | `shader` | Sign shader compilation artifacts |
| Squirrel | `inference` | Encrypt AI inference context |
| petalTongue | `visualization` | Sign scene graphs for integrity |
| biomeOS | `coordination` | Sign deployment graphs |
| BearDog | `security` | Master key self-reference |
| Songbird | `discovery` | Sign service registrations |

## Crypto Inheritance Model

BearDog (Tower atomic) is the sole key custodian. All other primals consume crypto through delegation:

```
BearDog ─── derives all keys
  │
  ├── secrets.store(purpose_key) ← composition bootstrap stores here
  │
  ├── NestGate ──── secrets.retrieve("storage") → encrypt before store
  ├── rhizoCrypt ── crypto.sign(dag_event) → delegated signing
  ├── loamSpine ─── crypto.sign(ledger_entry) → delegated signing
  ├── sweetGrass ── crypto.sign(braid_record) → delegated signing
  └── ToadStool ─── crypto.encrypt(job_payload) → delegated encryption
```

### Required Environment Variables (all primals)

Every primal in a NUCLEUS deployment MUST receive:

| Variable | Value | Purpose |
|----------|-------|---------|
| `BEARDOG_SOCKET` | `beardog-{family}.sock` path | Crypto delegation endpoint |
| `BTSP_PROVIDER_SOCKET` | `beardog-{family}.sock` path | BTSP tunnel provider |
| `FAMILY_SEED` | Random hex (deployment-specific) | Tier 1 key derivation input |
| `DISCOVERY_SOCKET` | `songbird-{family}.sock` path | Capability-based resolution |
| `BIOMEOS_SOCKET_DIR` | UDS directory path | Socket directory for all primals |

## Encrypt-at-Rest Pattern

### Current State (composition-level)

NestGate stores plaintext. The composition layer wraps storage calls:

1. **Store**: plaintext → `crypto.chacha20_poly1305_encrypt(purpose_key)` → NestGate `storage.store`
2. **Retrieve**: NestGate `storage.retrieve` → `crypto.chacha20_poly1305_decrypt(purpose_key)` → plaintext

The encrypted envelope format:

```json
{
    "v": 1,
    "ct": "<base64 ciphertext>",
    "n": "<base64 nonce>",
    "alg": "chacha20-poly1305"
}
```

This envelope is base64-encoded before passing to NestGate.

### Target State (native encrypt-at-rest)

NestGate should evolve to:

1. Accept encryption key via `NESTGATE_ENCRYPTION_KEY` env var or resolve from BearDog `secrets.retrieve`
2. Auto-encrypt on `storage.store`, auto-decrypt on `storage.retrieve`
3. Store the envelope format internally
4. Support key rotation via periodic `secrets.retrieve` refresh

## BTSP (BirdSong Trust and Security Protocol)

BTSP provides authenticated encrypted channels between primals. The session flow:

1. `btsp.session.create` → server ephemeral pub + challenge
2. `btsp.session.negotiate` → client response, derive shared secret
3. `btsp.tunnel.establish` → encrypted bidirectional channel
4. `btsp.tunnel.encrypt` / `btsp.tunnel.decrypt` → per-message encryption

Current state: BearDog creates sessions but no primal actively establishes persistent BTSP tunnels. This is the next evolution frontier.

## Bootstrap Workflow

After NUCLEUS starts, run:

```bash
# Derive and store all purpose keys
./tools/nucleus_crypto_bootstrap.sh

# Verify keys are accessible
./tools/nucleus_crypto_bootstrap.sh --verify-only

# Full validation including crypto checks
./tools/desktop_nucleus.sh validate
```

The bootstrap script:
1. Reads published seed fingerprints from `validation/seed_fingerprints.toml`
2. Derives Tier 0 base keys through BearDog HMAC
3. Mixes with `FAMILY_SEED` for Tier 1 family keys
4. Derives per-atomic purpose keys
5. Stores all keys in BearDog `secrets.store`
6. Tests sign/verify, encrypt/decrypt, and BTSP session round-trips
7. Tests NestGate encrypt-at-rest flow (composition-level)

## Per-Primal Evolution Requirements

### BearDog (Tower)
- **Status**: Operational — derives keys, signs, encrypts, creates BTSP sessions
- **Gap**: `genetic.derive_lineage_key` requires `peer_family_id` — no self-derivation path for single-family NUCLEUS. Workaround: use `crypto.hmac_sha256` chain
- **Evolution**: Add `crypto.derive_purpose_key(family_key, purpose)` as first-class method

### NestGate (Nest)
- **Status**: Stores plaintext. Declares `crypto.sign`/`verify` as consumed capabilities but does not call them
- **Gap**: No encrypt-at-rest. Must evolve to consume `crypto.encrypt`/`crypto.decrypt`
- **JWT deprecation**: NestGate's `NESTGATE_JWT_SECRET` exists exclusively for standalone deployments where a user wants just NestGate with its own auth lock. Within a NUCLEUS composition, JWT is deprecated — BearDog provides all auth/crypto via BTSP and the Tower key hierarchy. The composition layer passes `NESTGATE_AUTH_MODE=beardog` to signal this. NestGate should evolve to check `NESTGATE_AUTH_MODE` and skip JWT validation when `beardog` is set, delegating all auth to the Tower atomic.
- **Evolution**: 
  1. Respect `NESTGATE_AUTH_MODE=beardog` — bypass JWT, delegate auth to BearDog
  2. On startup, resolve `crypto` capability → BearDog socket
  3. Retrieve storage purpose key via `secrets.retrieve`
  4. Wrap all `storage.store` with encrypt, all `storage.retrieve` with decrypt
  5. Accept `NESTGATE_ENCRYPTION_KEY` env var as bootstrap override

### rhizoCrypt (Nest)
- **Status**: BLAKE3 content hashing remains local (content addressing); **Ed25519 vertex signing delegated to crypto provider** (S52) — `sign_vertex_if_available` calls `crypto.sign_ed25519` via discovered signing provider. Graceful degradation when no provider is present.
- **Gap**: Vertex signature **verification on retrieval** not yet implemented (read-path optional check)
- **Evolution**: Add optional signature verification when reading vertices from DAG or computing Merkle roots

### loamSpine (Nest)
- **Status**: **Tower-signed ledger entries** (v0.9.16) — `entry.append` and `session.commit` sign via `crypto.sign_ed25519` when crypto provider is available. Signature stored in entry metadata (`tower_signature`, `tower_signature_alg`). BLAKE3 chain hashing remains local.
- **Gap**: BTSP **encrypted tunnels** not yet active (no primal in the ecosystem pioneers persistent tunnels yet)
- **Evolution**: Establish BTSP tunnel at startup for encrypted ledger replication when a pioneer emerges

### sweetGrass (Nest)
- **Status**: **Tower-delegated braid signing** (v0.7.28) — `braid.create` delegates to `crypto.sign` Ed25519 via `CryptoDelegate` when crypto provider is available. Tower-tier witnesses (`tier: "tower"`) with `did:key:` agent DID. SHA-256 signing hash remains local.
- **Gap**: `anchoring.anchor` still uses local signing (incremental — `CryptoDelegate` already exists)
- **Evolution**: Delegate anchor signing to Tower for ecosystem-wide trust

### ToadStool (Node)
- **Status**: Was missing `BEARDOG_SOCKET` and `BTSP_PROVIDER_SOCKET` entirely — **FIXED** in composition_nucleus.sh
- **Gap**: Compute jobs dispatched in plaintext
- **Evolution**: Encrypt job payloads using `compute` purpose key before dispatch

### Songbird (Tower)
- **Status**: Fully wired with BTSP and BearDog
- **Gap**: Service registrations are not signed
- **Evolution**: Sign `ipc.register` payloads so consumers can verify authentic registrations

### barraCuda (Node)
- **Status**: Has `BEARDOG_SOCKET` — wiring complete
- **Gap**: Tensor data transmitted in plaintext over IPC
- **Evolution**: Optional encryption for sensitive tensor data using `tensor` purpose key

### coralReef (Node)
- **Status**: Has `BTSP_PROVIDER_SOCKET` — wiring complete
- **Gap**: Shader artifacts not signed
- **Evolution**: Sign compiled shaders for integrity verification

### Squirrel (Meta)
- **Status**: Has `BEARDOG_SOCKET` — can sign/verify
- **Gap**: Inference context (prompts, responses) not encrypted in transit
- **Evolution**: Encrypt inference payloads using `inference` purpose key

### petalTongue (Meta)
- **Status**: Wiring complete (BEARDOG_SOCKET + BTSP_PROVIDER_SOCKET added)
- **Gap**: Scene graphs not integrity-verified
- **Evolution**: Sign scene pushes so the composition can verify authentic UI updates

### biomeOS (Coordinator)
- **Status**: Manages NUCLEUS deployment
- **Gap**: Deployment graphs not signed
- **Evolution**: Sign cell graphs before deployment, verify signatures on load

## Composition-Level Helpers

The composition library (`tools/nucleus_composition_lib.sh`) provides:

| Function | Purpose |
|----------|---------|
| `tower_encrypt(key, plaintext_b64)` | Encrypt via BearDog ChaCha20-Poly1305 |
| `tower_decrypt(key, ciphertext, nonce)` | Decrypt via BearDog |
| `tower_derive_key(parent_key, purpose)` | Derive purpose key via HMAC chain |
| `tower_retrieve_purpose_key(purpose)` | Retrieve stored purpose key from secrets |
| `storage_init_encryption()` | Load storage purpose key for encrypted_store/retrieve |
| `encrypted_store(key_name, value)` | Encrypt-then-store to NestGate |
| `encrypted_retrieve(key_name)` | Retrieve-then-decrypt from NestGate |
| `sign_payload(message)` | Sign via Tower Ed25519 |

## Key References

| Document | Location |
|----------|----------|
| Crypto bootstrap script | `primalSpring/tools/nucleus_crypto_bootstrap.sh` |
| Composition library | `primalSpring/tools/nucleus_composition_lib.sh` |
| NUCLEUS launcher + validate | `primalSpring/tools/desktop_nucleus.sh` |
| Primal startup wiring | `primalSpring/tools/composition_nucleus.sh` |
| Seed fingerprints | `primalSpring/validation/seed_fingerprints.toml` |
| IPC method map | `primalSpring/docs/NUCLEUS_IPC_METHOD_MAP.md` |
| BTSP protocol standard | `wateringHole/BTSP_PROTOCOL_STANDARD.md` |
| Desktop deployment guide | `wateringHole/DESKTOP_NUCLEUS_DEPLOYMENT.md` |

## Verification

After deploying a NUCLEUS and running `nucleus_crypto_bootstrap.sh`:

```bash
# Full validation including crypto tiers
./tools/desktop_nucleus.sh validate
```

Expected crypto checks:
- Tier 0: 12/12 seed fingerprints present
- Tier 1: HMAC-SHA256 derivation works through BearDog
- BTSP session create succeeds
- Sign/verify round-trip passes
- Secrets store/retrieve round-trip passes
- NestGate encrypt-at-rest flow works (composition-level)
