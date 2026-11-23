# BTSP Protocol Standard

**Version:** 1.0.0
**Date:** April 8, 2026
**Status:** Active — all primals MUST implement when `FAMILY_ID` is set
**Authority:** wateringHole (ecoPrimals Core Standards)
**Derived from:** Secure Socket Architecture plan (primalSpring Phase 26)
**Related:** `PRIMAL_IPC_PROTOCOL.md`, `PRIMAL_SELF_KNOWLEDGE_STANDARD.md`, `CAPABILITY_WIRE_STANDARD.md`, `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md`

> **Note (Wave 111):** BTSP is now signaled via riboCipher transport routing.
> A riboCipher signal byte (0xEC/0xED/0xEE) precedes the BTSP handshake on the wire.
> BTSP protocol types within riboCipher: 0x02 (binary), 0x03 (JSON-line), 0x05 (encrypted resume).
> See `RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md` for the routing layer specification.

---

## Abstract

The BearDog Secure Tunnel Protocol (BTSP) defines mandatory authentication
and optional encryption for JSON-RPC communication over Unix domain sockets.
BTSP is the local equivalent of TLS 1.3, designed for intra-machine IPC
between primals within the ecoPrimals ecosystem.

**Core invariant:** Every production connection authenticates via BTSP
handshake first. Plaintext is a negotiated privilege after secure nucleation,
never a default. Hostile until proven otherwise.

---

## Motivation

Local Unix sockets are inherently unencrypted. Any process with filesystem
access to the socket can connect and issue JSON-RPC calls. In a multi-tenant
or multi-family deployment, this means:

- A process from family A can call methods on family B's primals
- A rogue process can impersonate a primal
- No tamper detection on the wire
- No confidentiality for sensitive payloads (crypto keys, health data)

BTSP addresses all four by wrapping JSON-RPC frames in an authenticated,
optionally encrypted tunnel derived from the family seed.

---

## Security Model

### Hostile Until Proven Otherwise

```
connect() → BTSP handshake (mandatory) → authenticated ✓ → negotiate cipher → communicate
connect() → no handshake → REFUSED
```

Every socket connection starts with the BTSP handshake. There are no
exceptions in production. An unauthenticated connection is refused before
any JSON-RPC payload is processed.

### FAMILY_ID as Production Toggle

| Environment | Behavior |
|-------------|----------|
| `FAMILY_ID` set (not `"default"`) | **Production.** BTSP handshake mandatory. Cipher negotiated post-auth. |
| `BIOMEOS_INSECURE=1`, no `FAMILY_ID` | **Development.** No handshake. Raw cleartext JSON-RPC. |
| `FAMILY_ID` set + `BIOMEOS_INSECURE=1` | **Error.** Primal MUST refuse to start. |

---

## Handshake Protocol

The BTSP handshake proves family membership using a challenge-response
derived from the family seed. It runs on every new socket connection
before any JSON-RPC frames are exchanged.

### Key Derivation

```
family_seed (from .family.seed file or FAMILY_SEED env)
    │
    ▼
HKDF-SHA256(ikm=family_seed, salt="btsp-v1", info="handshake")
    │
    ▼
handshake_key (32 bytes)
```

The same derivation pattern used for Dark Forest beacon keys
(`DARK_FOREST_PROTOCOL.md` §Key Derivation).

### Handshake Sequence

```
Client                              Server
  │                                    │
  │──── ClientHello ──────────────────▶│
  │     { version: 1,                  │
  │       client_ephemeral_pub: X25519 }│
  │                                    │
  │◀──── ServerHello ─────────────────│
  │     { version: 1,                  │
  │       server_ephemeral_pub: X25519,│
  │       challenge: random(32) }      │
  │                                    │
  │──── ChallengeResponse ───────────▶│
  │     { response: HMAC-SHA256(       │
  │         key=handshake_key,         │
  │         data=challenge ‖           │
  │              client_ephemeral_pub ‖│
  │              server_ephemeral_pub),│
  │       preferred_cipher: "chacha20" }
  │                                    │
  │     [Server verifies HMAC with     │
  │      own handshake_key derivation] │
  │                                    │
  │◀──── HandshakeComplete ───────────│
  │     { cipher: "chacha20",          │
  │       session_id: random(16) }     │
  │                                    │
  │     [Both derive session keys:     │
  │      X25519(client_eph, server_eph)│
  │      → shared_secret               │
  │      → HKDF(shared_secret,         │
  │             "btsp-session-v1",     │
  │             session_id)            │
  │      → (encrypt_key, decrypt_key)] │
  │                                    │
  │◀═══ Encrypted/Authenticated ══════▶│
```

### Handshake Failure

If the server cannot verify the challenge response (wrong family seed),
it sends:

```json
{ "error": "handshake_failed", "reason": "family_verification" }
```

and immediately closes the connection. No JSON-RPC methods are exposed.

---

## Cipher Suites

After the handshake succeeds, both parties negotiate a cipher suite.
The negotiation is authenticated — forging a downgrade request requires
the family seed.

### BTSP_CHACHA20_POLY1305 (default)

- **Algorithm:** ChaCha20-Poly1305 AEAD
- **Key:** Session key derived from X25519 shared secret via HKDF-SHA256
- **Nonce:** 12-byte counter (incremented per frame, reset per session)
- **AAD:** Frame length (4 bytes, big-endian)
- **Properties:** Confidentiality + integrity + authentication
- **Use case:** Default for all bonds. Zero-knowledge: even biomeOS relay
  cannot read cross-family payloads.

### BTSP_HMAC_PLAIN

- **Algorithm:** HMAC-SHA256 tag appended to each frame
- **Key:** Session key (same derivation as CHACHA20)
- **Properties:** Integrity + authentication (no confidentiality)
- **Use case:** High-throughput same-machine workloads where the OS is
  trusted but tamper detection is desired. GPU tensor pipelines between
  ToadStool and rhizoCrypt in the same Covalent family.

### BTSP_NULL

- **Algorithm:** None. Raw plaintext frames.
- **Properties:** Authentication only (proven during handshake, not per-frame)
- **Constraints:** Both parties must request it AND the BondingPolicy must
  allow it. Only valid for Covalent bonds.
- **Use case:** Maximum throughput for trusted intra-family workloads.
  biomeOS still routes, discovers, and manages the socket. The eco doesn't
  lose visibility because the workload opted for plaintext.

### Cipher Selection Rules

| Bond Type | Minimum Cipher | Negotiable Down To |
|-----------|---------------|-------------------|
| Covalent (`GeneticLineage`) | `BTSP_NULL` | `BTSP_NULL` (all three allowed) |
| Metallic (`Organizational`) | `BTSP_HMAC_PLAIN` | `BTSP_HMAC_PLAIN` |
| Ionic (`Contractual`) | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| Weak (`ZeroTrust`) | `BTSP_CHACHA20_POLY1305` | None (encrypted only) |
| OrganoMetalSalt | Per-scope | Covalent core → `BTSP_NULL`, ionic edge → encrypted |

---

## Wire Framing

All BTSP frames use a uniform length-prefixed format regardless of cipher
suite. This means the same parser, tooling, and debugging infrastructure
works for encrypted and plaintext modes.

### Frame Format

```
┌──────────┬──────────────────────────────────────────┐
│ Length(4) │ Payload (Length bytes)                    │
└──────────┴──────────────────────────────────────────┘
```

- **Length:** 4 bytes, big-endian unsigned 32-bit integer.
  Maximum frame size: 16 MiB (`0x01000000`).
- **Payload:** Depends on cipher suite:
  - `BTSP_CHACHA20_POLY1305`: `nonce(12) ‖ ciphertext ‖ tag(16)`
  - `BTSP_HMAC_PLAIN`: `plaintext ‖ hmac(32)`
  - `BTSP_NULL`: `plaintext` (raw JSON-RPC)

### Relationship to Existing Framing

The `PRIMAL_IPC_PROTOCOL.md` v3.1 specifies newline-delimited JSON-RPC
as the canonical wire framing. BTSP wraps this:

- **Without BTSP** (development mode): Newline-delimited JSON-RPC as before.
- **With BTSP** (production mode): Length-prefixed frames containing the
  JSON-RPC message. Each frame holds exactly one JSON-RPC request or
  response. The newline delimiter is no longer needed (length prefix
  provides framing) but MAY be included in the plaintext for backward
  compatibility.

---

## BearDog JSON-RPC Methods

BearDog implements the BTSP crypto primitives as JSON-RPC methods. These
are used by other primals and biomeOS to establish BTSP sessions.

### btsp.session.create

Create a new BTSP session (server-side). Called by a primal's socket
listener when a new connection arrives.

**Params:**
```json
{
  "family_seed_ref": "env:FAMILY_SEED",
  "client_ephemeral_pub": "<base64 X25519 public key>",
  "challenge": "<base64 random 32 bytes>"
}
```

**Result:**
```json
{
  "session_id": "<hex 16 bytes>",
  "server_ephemeral_pub": "<base64 X25519 public key>",
  "handshake_key": "<base64 32 bytes>"
}
```

### btsp.session.verify

Verify a client's challenge response.

**Params:**
```json
{
  "session_id": "<hex>",
  "client_response": "<base64 HMAC-SHA256>",
  "client_ephemeral_pub": "<base64>",
  "server_ephemeral_pub": "<base64>",
  "challenge": "<base64>"
}
```

**Result:**
```json
{
  "verified": true,
  "session_key": "<base64 derived session key>"
}
```

### btsp.negotiate

Negotiate cipher suite for an authenticated session.

**Params:**
```json
{
  "session_id": "<hex>",
  "preferred_cipher": "chacha20_poly1305",
  "bond_type": "Covalent"
}
```

**Result:**
```json
{
  "cipher": "chacha20_poly1305",
  "allowed": true
}
```

### btsp.encrypt / btsp.decrypt

Encrypt or decrypt a BTSP frame using the session key.

**Params (encrypt):**
```json
{
  "session_id": "<hex>",
  "plaintext": "<base64 JSON-RPC message>",
  "frame_counter": 42
}
```

**Result (encrypt):**
```json
{
  "ciphertext": "<base64 nonce ‖ ciphertext ‖ tag>"
}
```

---

## biomeOS Integration

### Intra-NUCLEUS (same family, same machine)

biomeOS is a family member. It holds BTSP session keys derived from the
family seed. When relaying `capability.call`:

1. biomeOS connects to target primal socket
2. BTSP handshake (biomeOS proves family membership)
3. Cipher negotiated per BondingPolicy
4. JSON-RPC forwarded inside BTSP frames
5. biomeOS CAN read method names for routing (trusted within family)

### Cross-NUCLEUS (different family or machine)

biomeOS only nucleates — returns the target socket path and bond type.
The caller connects directly via Tower Atomic:

1. Caller asks biomeOS: `capability.discover(storage)`
2. biomeOS returns: `{ socket_path, bond_type }`
3. Caller connects directly to socket via Tower
4. BTSP handshake with cross-family key exchange
5. biomeOS CANNOT read the payload (zero-knowledge)

---

## Socket Naming Convention (Phase 1)

When `FAMILY_ID` is set, primals MUST create sockets at:

```
$BIOMEOS_SOCKET_DIR/{primal}-{family_id}.sock
```

This aligns with biomeOS `path_builder.rs`:
```rust
let socket_name = format!("{primal_name}-{family_id}.sock");
```

And `list_family_scoped_unix_sockets()` which filters by `-{family_id}.sock`
suffix.

### Per-Primal Socket Naming

| Primal | Development (no FAMILY_ID) | Production (FAMILY_ID set) |
|--------|---------------------------|---------------------------|
| BearDog | `beardog.sock` | `beardog-{fid}.sock` |
| Songbird | `songbird.sock` | `songbird-{fid}.sock` |
| NestGate | `nestgate.sock` | `nestgate-{fid}.sock` |
| ToadStool | `toadstool.sock` | `toadstool-{fid}.sock` |
| rhizoCrypt | `rhizocrypt.sock` | `rhizocrypt-{fid}.sock` |
| loamSpine | `loamspine.sock` (capability: `ledger.sock`, legacy: `permanence.sock`) | `loamspine-{fid}.sock` |
| sweetGrass | `sweetgrass.sock` | `sweetgrass-{fid}.sock` |
| biomeOS | `biomeos.sock` | `biomeos-{fid}.sock` |

---

## Compliance Checklist

```
BTSP_PROTOCOL_STANDARD v1.0 — Audit Checklist

Primal: ___________  Version: ___________  Date: ___________

Socket Naming:
  [ ] Reads FAMILY_ID (or {PRIMAL}_FAMILY_ID) from environment
  [ ] Creates {primal}-{family_id}.sock when FAMILY_ID is set
  [ ] Creates {primal}.sock when FAMILY_ID is not set (development)
  [ ] Refuses to start when both FAMILY_ID and BIOMEOS_INSECURE are set

Handshake (Phase 2+):
  [ ] BTSP handshake runs on every incoming connection when FAMILY_ID is set
  [ ] Challenge-response verifies family membership via HKDF-SHA256
  [ ] Connection refused on handshake failure (no JSON-RPC methods exposed)
  [ ] Ephemeral X25519 keys generated per connection (forward secrecy)

Cipher Negotiation (Phase 2+):
  [ ] Supports BTSP_CHACHA20_POLY1305 (default)
  [ ] Supports BTSP_HMAC_PLAIN (optional)
  [ ] Supports BTSP_NULL (optional, Covalent bonds only)
  [ ] Enforces minimum cipher per BondingPolicy
  [ ] Client preferred_cipher respected when allowed by policy

Framing (Phase 2+):
  [ ] Length-prefixed frames (4-byte big-endian length)
  [ ] Maximum frame size 16 MiB enforced
  [ ] Same frame parser for all cipher suites
```

---

## Implementation Phases

### Phase 1: Socket Naming Alignment (complete)

- All primals honor `FAMILY_ID` for socket naming
- `BIOMEOS_INSECURE` guard prevents conflicting configuration
- biomeOS routing works immediately (already expects this pattern)

### Phase 2: BTSP Handshake (BearDog complete — Wave 31)

- BearDog implements `btsp.session.create`, `btsp.session.verify`, `btsp.session.negotiate`
- BearDog socket listener enforces 4-step handshake (X25519 + HMAC-SHA256 challenge-response) when `FAMILY_ID` is set
- Handshake failure → connection refused
- Consumer primals: wrap socket listeners using BearDog's handshake-as-a-service RPC

### Phase 3: Cipher Negotiation + Encryption (BearDog complete — Wave 31)

- BearDog implements encrypted framing: ChaCha20-Poly1305, HMAC-plain, null cipher suites
- Length-prefixed (4-byte BE) frames replace NDJSON in production mode
- Session key derivation: HKDF-SHA256 from X25519 shared secret with directional keys
- biomeOS Neural API: BTSP client for encrypted relay (pending)
- `BondingPolicy` → cipher suite mapping enforced

### Phase 4: Ecosystem-Wide Secure Nucleation

- All primals implement BTSP
- Cross-NUCLEUS nucleation mode
- `BondingPolicy` enforcement at both handshake and runtime layers

---

## Relationship to Other Standards

| Standard | Relationship |
|----------|-------------|
| `PRIMAL_IPC_PROTOCOL.md` v3.1 | Extended: BTSP wraps the existing JSON-RPC framing with authentication and optional encryption. Newline-delimited framing is preserved in development mode. |
| `PRIMAL_SELF_KNOWLEDGE_STANDARD.md` | Extended: Socket naming convention updated with `FAMILY_ID` → BTSP production mode. |
| `CAPABILITY_WIRE_STANDARD.md` | Complementary: `capabilities.list` and `identity.get` work identically over BTSP — the wire format is unchanged, only the transport is secured. |
| `DARK_FOREST_PROTOCOL.md` | Foundation: BTSP reuses the same key derivation (HKDF-SHA256), cipher (ChaCha20-Poly1305), and challenge-response patterns designed for Dark Forest beacons. |
| `NUCLEUS_ARCHITECTURE.md` | Aligned: BTSP implements the "AES-256-GCM at rest, BTSP on IPC" encryption architecture described in the NUCLEUS spec (ChaCha20-Poly1305 replaces AES for IPC). |

---

**License:** AGPL-3.0-or-later
