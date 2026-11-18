<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# riboCipher — Transport Signal Standard

**Status**: Ecosystem Standard (Draft — Wave 111)  
**Version**: 0.1.0  
**Date**: June 13, 2026  
**Authority**: wateringHole (eastGate overwatch)  
**Replaces**: Ad-hoc peek-and-guess protocol detection  
**Acceleration**: sourDough (scaffold + validate)

---

## Biological Context

In molecular biology, the **ribosome** is the machine that reads the genetic
code (mRNA codons) and produces functional proteins. Codons are a **cipher** —
three nucleotides encode one amino acid. The ribosome doesn't guess what it's
reading; the code declares its intent.

Similarly, when a newly synthesized protein needs routing to a specific
organelle (ER, mitochondria, nucleus), it carries a **signal peptide** — a
short leader sequence at its N-terminus. The **Signal Recognition Particle
(SRP)** reads this signal, pauses translation, and routes the ribosome to
the correct membrane for translocation.

**riboCipher** models this process for IPC connections:

- The **connection** is the nascent protein
- The **first bytes** are the signal peptide (leader sequence)
- The **accept loop** is the SRP — it reads the signal and routes
- The **handler** is the target organelle

The old approach (peek-and-guess) is like a ribosome trying to figure out
where a protein goes by looking at a random amino acid. riboCipher is the
proper signal peptide system: intentional, deterministic, tiered.

### Naming Lineage

- **BTSP** (BearDog-to-SongBird Protocol): Legacy security handshake.
  Named for specific primals. Remains as a protocol type WITHIN riboCipher.
- **riboCipher**: The convergent routing standard. Named for the biological
  process. The ribosome reads the cipher; the connection is routed.

---

## Purpose

Define how every ecoPrimals IPC connection declares its intended protocol
via an intentional signal envelope. This replaces fragile peek-and-guess
patterns where servers read the first byte and hope to classify the
connection correctly.

**Problem**: The current approach breaks when BTSP-encrypted frames start
with arbitrary ciphertext (the peeked byte is indistinguishable from noise),
and different primals disagree on what "unknown first byte" means (bearDog
assumes BTSP binary, biomeOS assumes HTTP).

**Solution**: Clients send an intentional signal. Servers route deterministically.

---

## Design Principles

1. **Signal, don't peek** — the client declares intent, the server doesn't guess.
2. **Each primal implements independently** — no shared crate dependency. Each
   team evolves their own idiomatic implementation of this standard.
3. **Convergent, not imposed** — teams adopt at their own pace within the
   deprecation window. The standard defines the target; evolution finds the path.
4. **Three security tiers** — clear (local), mito-obfuscated (family WAN),
   nuclear-sealed (privileged). Leverages existing genetics infrastructure.
5. **Warn-then-cut** — legacy peek logic stays temporarily with loud warnings,
   then gets hard-cut in a future wave.
6. **sourDough accelerates** — new primals are born with riboCipher; existing
   primals are audited toward convergence.

---

## Wire Format

### Tier 1: Clear Signal

For local same-gate IPC where the wire is trusted (UDS on same host).

```
[0xEC][protocol_type: u8]
```

Total: 2 bytes. Any ecosystem participant can read.

### Tier 2: Mito-Obfuscated Signal

For cross-gate / WAN connections where the wire is untrusted. Only family
members (those holding the mitoBeacon seed) can decode the protocol type.

```
[0xED][hmac_tag: [u8; 4]]
```

Total: 5 bytes. Observer sees random-looking bytes.

Derivation:
```
mito_key = HKDF-SHA256(salt=b"ribocipher-v1", ikm=family_seed, info=b"mito-signal")
hmac_tag = HMAC-SHA256(key=mito_key, data=[protocol_type])[0..4]
```

Server decodes by trying each known protocol type against the tag
(max 16 HMAC comparisons for 16 protocol types).

### Tier 3: Nuclear-Sealed Signal

For privileged protocol negotiation where even other family members
shouldn't know what protocol is being used.

```
[0xEE][encrypted_payload: [u8; 6]]
```

Total: 7 bytes.

Derivation:
```
nuclear_key = HKDF-SHA256(salt=b"ribocipher-v1", ikm=nuclear_seed, info=b"nuclear-signal")
plaintext   = [protocol_type: u8][session_hint: u8][padding: [u8; 4]]
ciphertext  = ChaCha20-Poly1305(key=nuclear_key, nonce=derived_from_context, plaintext)[0..6]
```

Only decryptable by the holder of the nuclear lineage key for this peer pair.

### Legacy (deprecated)

Any connection NOT starting with `0xEC`/`0xED`/`0xEE`:
- Wave 111-112: Log warning, fall through to old peek logic
- Wave 113: Reject with JSON-RPC error `-32002: riboCipher signal required`
- Wave 114: Remove all legacy peek code

---

## Signal Prefix Bytes

| Byte   | Meaning          | Mnemonic |
|--------|------------------|----------|
| `0xEC` | Clear signal     | **eC**oPrimals (open) |
| `0xED` | Mito-obfuscated  | **eD**NA (mitochondrial) |
| `0xEE` | Nuclear-sealed   | **eE**ncrypted (nuclear) |

These bytes were chosen because they:
- Never start valid UTF-8 JSON documents
- Are not ASCII printable (no HTTP verb collision)
- Are not NUL (0x00)
- Are sequential for easy range-checking

---

## Protocol Type Table

| Byte   | Protocol           | Usage |
|--------|--------------------|-------|
| `0x00` | Probe              | Lightweight health check |
| `0x01` | NDJSON JSON-RPC    | Standard ecosystem IPC |
| `0x02` | BTSP Binary        | Length-prefixed binary handshake |
| `0x03` | BTSP JSON-line     | JSON-line ClientHello handshake |
| `0x04` | HTTP/1.1           | axum/hyper over UDS |
| `0x05` | Encrypted Resume   | Post-BTSP session resume |
| `0x06` | Dark Forest Beacon | birdsong beacon packet |
| `0x07` | Mesh Relay         | songBird relay-routed frame |
| `0x08-0x0F` | Reserved      | Future expansion |

---

## Key Derivation

Reuses existing HKDF domain-separation patterns from `btsp-v1` and
`birdsong_beacon_v1`:

```
// Mito-tier (shared by all family members with same beacon seed)
mito_key = HKDF-SHA256(
    salt = b"ribocipher-v1",
    ikm  = family_seed,    // from FAMILY_SEED env / .beacon.seed
    info = b"mito-signal"
) -> [u8; 32]

// Nuclear-tier (per-peer, from nuclear lineage)
nuclear_key = HKDF-SHA256(
    salt = b"ribocipher-v1",
    ikm  = nuclear_seed,   // from node lineage seed
    info = b"nuclear-signal"
) -> [u8; 32]
```

---

## Server-Side Detection (pseudocode)

Each primal implements this in their own accept loop:

```
read first_byte from stream

match first_byte:
    0xEC -> read protocol_type (1 byte)
            route to handler for protocol_type
    0xED -> read hmac_tag (4 bytes)
            for each known protocol_type:
                if hmac_verify(mito_key, protocol_type, tag):
                    route to handler
            else: reject (not family member)
    0xEE -> read encrypted (6 bytes)
            decrypt with nuclear_key
            if success: route to handler
            else: reject
    _    -> WARN "DEPRECATED: unsignalled connection"
            legacy_guess(first_byte) -> route with old behavior
            (prepend first_byte back to stream for handler)
```

---

## Legacy Guess Table (deprecation period only)

For the warn period, unsignalled connections fall back to existing behavior:

| First byte | Legacy guess | Notes |
|------------|-------------|-------|
| `{` or `[` | NDJSON JSON-RPC | JSON document start |
| `G`, `P`, `H`, `D`, `O`, `T`, `C` | HTTP/1.1 | HTTP verb first chars |
| Anything else | Socket default | bearDog: BTSP binary; biomeOS: HTTP |

Each primal documents their socket default. This table exists ONLY for the
deprecation period and is removed at hard-cut.

---

## sourDough Integration

sourDough is the **starter culture** — it pre-evolves standards so new
primals are born compliant, and audits the fleet toward convergence.

### Scaffold (new primals born with riboCipher)

```bash
sourdough scaffold new-primal myPrimal "Description"
```

Generated code includes:
- riboCipher signal detection in the accept loop
- Clear signal sending in client IPC helpers
- No legacy peek patterns (new primals never learn old habits)

### Validate (audit existing primals)

```bash
sourdough validate ribocipher <primal-path>
```

Checks:
- Accept loop reads first byte BEFORE any protocol-specific parsing
- Signal bytes 0xEC/0xED/0xEE are handled before legacy fallback
- Legacy fallback logs at WARN level (or ERROR/REJECT per wave)
- Client connections send signal prefix before payload

### Reference Implementation

sourDough's own JSON-RPC server (`sourdough doctor`, `sourdough validate`)
implements riboCipher. Teams can study this as the canonical example of
correct signal detection in a production binary.

---

## Per-Team Evolution Tasks

Each primal team independently evolves to riboCipher convergence:

### bearDog
- Implement riboCipher detection in `unix_socket_ipc/server.rs` `handle_connection()`
- Implement riboCipher detection in `tcp_ipc/server/connection.rs`
- Update `protocol_router.rs` `ProtocolDetector::detect()` to check for riboCipher first
- Send clear signal from BTSP client connections

### songBird
- Implement riboCipher detection in `pure_rust_server/server/connection.rs`
- Implement riboCipher detection in `bin_interface/ipc_session.rs`
- Send mito-obfuscated signal for federation connections (cross-gate)
- Send clear signal for local IPC

### biomeOS
- Implement riboCipher detection in `biomeos-api/src/unix_server.rs`
- Implement riboCipher detection in `neural_api_server/connection.rs`
- Send clear signal from capability resolution client code

### sweetGrass
- Update canonical `peek.rs` to implement riboCipher detection first, legacy fallback second
- This becomes the reference pattern other primals can study

### primalSpring
- Update `nucleus_launcher` to send clear signal when probing primal health
- Update harness IPC connections to send clear signal
- Update BTSP handshake client to send appropriate signal before ClientHello

### cellMembrane
- Update `gate/health.rs` `uds_jsonrpc_call()` to prepend `[0xEC, 0x01]`
- Add `[transport.ribocipher]` section to `membrane.toml` and gate profiles
- Update `plasmid.sandbox` / `plasmid.canary` IPC to send clear signal

### sourDough
- Implement riboCipher in own IPC server (reference implementation)
- Add `validate ribocipher` subcommand
- Update scaffold templates to emit riboCipher-compliant accept loops

---

## Configuration (cellMembrane gate profiles)

```toml
[transport.ribocipher]
signal_tier = "clear"              # default tier for outbound connections
unsignalled_policy = "warn"        # "warn" | "error" | "reject"
mito_key_source = "family_seed"    # derive from FAMILY_SEED
```

---

## Deprecation Timeline

| Wave | Behavior |
|------|----------|
| 111 (now) | Standard published. Teams begin implementation. WARN on legacy. |
| 112 | All clients send riboCipher signals. Legacy paths log at ERROR. |
| 113 | Hard-cut: unsignalled connections rejected (`-32002`). |
| 114 | Legacy peek code removed from all primals. |

---

## Validation

A primal is riboCipher-compliant when:

1. Its server accept loop checks for `0xEC`/`0xED`/`0xEE` BEFORE any peek logic
2. Its client connections send the appropriate signal prefix
3. Unsignalled connections produce a WARN-level log
4. Tests demonstrate correct routing for all three tiers
5. `sourdough validate ribocipher` passes

---

## Relationship to Existing Standards

| Standard | Relationship |
|----------|-------------|
| BTSP (bearDog Transport Security Protocol) | riboCipher signals WHICH protocol to use; BTSP is one of those protocols (types 0x02, 0x03, 0x05) |
| Dark Forest Beacon Genetics | Mito-tier riboCipher uses the same seed and similar HKDF derivation |
| GATE_NUCLEUS_SYSTEMD_STANDARD | Deployed primals use riboCipher for all socket connections |
| Three-tier genetics (mito/nuclear/tag) | riboCipher tiers map directly to genetics tiers |
| sourDough scaffold | New primals generated with riboCipher compliance from birth |
