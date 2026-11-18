# Capability Wire Standard

**Version:** 1.0.0
**Date:** April 8, 2026
**Status:** Active — all primals and springs MUST adopt this
**Authority:** wateringHole (ecoPrimals Core Standards)
**Derived from:** Live validation runs 1–4 (primalSpring Phase 26)
**Related:** `CAPABILITY_BASED_DISCOVERY_STANDARD.md`, `PRIMAL_SELF_KNOWLEDGE_STANDARD.md`, `SEMANTIC_METHOD_NAMING_STANDARD.md`

---

## Abstract

The Capability Wire Standard defines the JSON-RPC response format for primal self-advertisement over IPC. When biomeOS (or any orchestrator) sends `capabilities.list` or `identity.get` to a primal, the response MUST follow this specification. The standard enables automatic capability discovery, composition completeness validation, and AI-assisted routing without hardcoded knowledge of individual primals.

---

## Problem Statement

Prior to this standard, 5 independent wire formats evolved across the ecosystem:

| Format | Shape | Primals |
|--------|-------|---------|
| A | `result: ["method.name", ...]` (bare array) | Songbird |
| B | `result: {capabilities: [...], methods: [...], ...}` | sweetGrass |
| C | `result: {method_info: [{name, ...}]}` | (reference parser) |
| D | `result: {semantic_mappings: {domain: {method: {}}}}` | loamSpine (tests) |
| E | `result: {provided_capabilities: [{type, methods}]}` | BearDog, rhizoCrypt |

biomeOS maintained a 5-format parser to extract method names from each. Rich metadata (cost estimates, operation dependencies, consumed capabilities) was discarded. Method name translation tables introduced errors (GAP-MATRIX-09: `braid.create` mistranslated to `provenance.create_braid`). No primal advertised what it consumed, making composition validation impossible without hardcoded graphs.

---

## Specification

### 1. capabilities.list Response — Required Envelope

Every primal MUST return a JSON-RPC 2.0 response to `capabilities.list` (or the alias `capability.list`) containing AT MINIMUM:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "primal": "<canonical_name>",
    "version": "<semver_or_dev>",
    "methods": [
      "<domain>.<operation>",
      ...
    ]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primal` | String | **MUST** | Canonical primal name, lowercase, no spaces (e.g., `rhizocrypt`, `beardog`, `songbird`) |
| `version` | String | **MUST** | SemVer or dev version string (e.g., `0.14.0`, `0.9.0-dev`) |
| `methods` | String[] | **MUST** | Every callable JSON-RPC method, fully qualified with dotted notation (`domain.operation`). This is the primary routing signal for biomeOS. |

The `methods` array MUST contain every method the primal will accept as a JSON-RPC `method` field. If a method name appears in `methods`, the primal MUST NOT return "method not found" when that method is called (parameter validation errors are acceptable).

### 2. Structured Capabilities — Recommended

Primals SHOULD include capability grouping for structured routing and observability:

```json
{
  "result": {
    "primal": "rhizocrypt",
    "version": "0.14.0",
    "methods": ["dag.session.create", "dag.session.list", ...],
    "provided_capabilities": [
      {
        "type": "dag",
        "methods": ["session.create", "session.list", "event.append"],
        "version": "0.14.0",
        "description": "Ephemeral content-addressed DAG engine"
      }
    ]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provided_capabilities` | Object[] | SHOULD | Capability groups |
| `provided_capabilities[].type` | String | MUST (if group present) | Domain name (e.g., `dag`, `crypto`, `braid`) |
| `provided_capabilities[].methods` | String[] | MUST (if group present) | Short method names within this domain |
| `provided_capabilities[].version` | String | MAY | Group-level version |
| `provided_capabilities[].description` | String | MAY | Human-readable group description |

When `provided_capabilities` is present, biomeOS registers both the group type name (e.g., `dag`) and qualified names (e.g., `dag.session.create`) in its routing table.

### 3. Dependency & Cost Metadata — Optional

Primals MAY include metadata for AI advisors, composition planners, and billing:

```json
{
  "result": {
    "primal": "sweetgrass",
    "version": "0.7.27",
    "methods": [...],
    "provided_capabilities": [...],
    "consumed_capabilities": ["crypto.sign", "storage.artifact.store", "dag.session.create"],
    "cost_estimates": {
      "braid.create": { "cpu": "low", "latency_ms": 2 },
      "attribution.chain": { "cpu": "high", "latency_ms": 50 }
    },
    "operation_dependencies": {
      "anchoring.anchor": ["braid.create"],
      "attribution.chain": ["braid.create"]
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `consumed_capabilities` | String[] | Methods this primal needs FROM other primals. Enables composition completeness validation. |
| `cost_estimates` | Object | Per-method or per-domain cost hints (`cpu`: low/medium/high, `latency_ms`, `memory_bytes`, `gpu_eligible`). |
| `operation_dependencies` | Object | Method DAG — `{method: [prerequisite_methods]}`. Enables execution planners to sequence operations. |
| `protocol` | String | IPC protocol (e.g., `jsonrpc-2.0`) |
| `transport` | String[] | Available transports (e.g., `["uds", "tcp", "http"]`) |

### 4. identity.get — Recommended

Primals SHOULD implement the `identity.get` JSON-RPC method:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "primal": "rhizocrypt",
    "version": "0.14.0",
    "domain": "dag",
    "license": "AGPL-3.0-or-later"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `primal` | String | MUST | Same as `capabilities.list` `primal` field |
| `version` | String | MUST | Same as `capabilities.list` `version` field |
| `domain` | String | SHOULD | Primary capability domain |
| `license` | String | MAY | SPDX license identifier |

biomeOS probes `identity.get` alongside `capabilities.list` for observability. If absent, biomeOS falls back to socket-name inference.

---

## Method Naming Convention

All method names in the `methods` array MUST follow the **Semantic Method Naming Standard**:

```
<domain>.<operation>
```

- `domain`: lowercase, no dots (e.g., `dag`, `crypto`, `braid`, `health`)
- `operation`: lowercase, underscores for multi-word (e.g., `session.create`, `blake3_hash`)
- Health triad: every primal SHOULD implement `health.liveness`, `health.check`, `health.readiness`
- Meta methods: `capabilities.list`, `identity.get`

---

## biomeOS Parser Behavior

biomeOS v2.93+ reads `capabilities.list` responses with the following priority:

1. `result.methods` (this standard) → use directly, no format detection
2. `result.provided_capabilities` (Format E) → expand `type.method`
3. `result.capabilities` (Format A/B) → use directly if string array
4. `result.method_info` (Format C) → extract `name` fields
5. `result.semantic_mappings` (Format D) → traverse nested keys
6. `result` is bare array (Format A) → use directly

When `result.methods` is present, biomeOS skips format detection entirely. Legacy formats remain supported for backward compatibility but SHOULD be deprecated.

---

## Compliance Levels

### Level 1: Routable (minimum for biomeOS discovery)

- [ ] `capabilities.list` returns a response biomeOS can parse (any format A-E)
- [ ] At least one callable method is advertised
- [ ] `health.liveness` implemented

### Level 2: Standard (target for all primals)

- [ ] All Level 1 requirements
- [ ] `capabilities.list` returns `{primal, version, methods}` envelope
- [ ] `identity.get` implemented
- [ ] All methods in `methods` array are callable (no "method not found" for advertised methods)
- [ ] Method names follow Semantic Method Naming Standard

### Level 3: Composable (target for NUCLEUS-participating primals)

- [ ] All Level 2 requirements
- [ ] `provided_capabilities` grouping included
- [ ] `consumed_capabilities` declared
- [ ] `cost_estimates` for at least high-cost methods
- [ ] `operation_dependencies` for methods with prerequisites

### Current Primal Compliance (April 8, 2026)

| Primal | Level 1 | Level 2 | Level 3 | Gap |
|--------|---------|---------|---------|-----|
| BearDog | ✓ | ✓ | — | L2 complete + signed announcements (SA-01, Wave 45): unified Ed25519 identity, `signed_announcement` in `capabilities.list` and `discover_capabilities`, neural registration attestation |
| Songbird | ✓ | Partial | — | Has `capabilities.methods` token→method map (Wave 123); needs `{primal, version, methods}` envelope, `identity.get` |
| rhizoCrypt | ✓ | ✓ | ✓ | Full L3: `methods`, `consumed_capabilities`, `cost_estimates`, `operation_dependencies` |
| loamSpine | ✓ | ✓ | ✓ | Full L3: `methods` (flat, 37), `identity.get`, `provided_capabilities` (10 groups incl. bond-ledger), `consumed_capabilities`, `cost_estimates`, `operation_dependencies`. Domain symlink `ledger.sock`. Self-knowledge compliant (zero hardcoded primal names, zero biomeOS doc refs in prod). **178** source files, **1,442** tests, **stadial-gate compliant**, `rmp-serde` (bincode advisory eliminated). (April 16, 2026) |
| sweetGrass | ✓ | ✓ | ✓ | Full L3 compliance (April 8, 2026) |
| NestGate | ✓ | ✓ | ✓ | Full L3: `{primal, version, methods}` envelope, `identity.get` with domain/license, `provided_capabilities` (9 groups), `consumed_capabilities`, `protocol`, `transport`. 57 methods advertised. (April 8, 2026) |

---

## Audit Checklist

This checklist is used during primalSpring deep-debt audits and cross-spring evolution reviews:

```
CAPABILITY_WIRE_STANDARD v1.0 — Audit Checklist

Primal: ___________  Version: ___________  Date: ___________

Level 1 (Routable):
  [ ] capabilities.list responds to JSON-RPC probe over UDS
  [ ] Response parseable by biomeOS (any format)
  [ ] health.liveness responds with {status: "alive"} or {alive: true}

Level 2 (Standard):
  [ ] result contains "primal" field (canonical name)
  [ ] result contains "version" field (SemVer)
  [ ] result contains "methods" flat string array
  [ ] Every entry in "methods" is callable (returns result or param error, not method-not-found)
  [ ] Method names follow domain.operation dotted convention
  [ ] identity.get implemented and returns {primal, version}
  [ ] health.liveness, health.check, health.readiness all implemented

Level 3 (Composable):
  [ ] provided_capabilities grouping present with type + methods per group
  [ ] consumed_capabilities lists all cross-primal dependencies
  [ ] cost_estimates present for high-cost methods
  [ ] operation_dependencies present for methods with prerequisites
```

---

## What This Unlocks

### Composition Completeness Validation

With `consumed_capabilities`, biomeOS validates that a deploy graph satisfies all dependencies without hardcoded knowledge:

```
sweetGrass consumes: [crypto.sign, storage.artifact.store, dag.session.create]
BearDog provides:   [crypto.sign, ...]        ✓
NestGate provides:  [storage.artifact.store]   ✓
rhizoCrypt provides:[dag.session.create, ...]  ✓
→ Composition complete
```

### AI-Assisted Routing (Squirrel)

With `cost_estimates` and `operation_dependencies`, Squirrel can plan optimal execution:

```
Goal: anchor a provenance braid
Path: braid.create (low) → anchoring.anchor (high) → proof.generate (medium)
Total: high
```

### Self-Describing Deploy Graphs

A composition's capability surface = union of all `methods` minus all `consumed_capabilities`. No hardcoded `CapabilityTaxonomy` tables needed. biomeOS's translation layer becomes a compatibility shim, not the source of truth.

---

## Parameter Encoding (LD-01)

Binary data in JSON-RPC parameters uses **standard Base64** (RFC 4648 §4,
`+/=` alphabet) unless an explicit per-field encoding hint is provided.

### BearDog Crypto Methods

| Method | `data` / input param | Output | Notes |
|--------|---------------------|--------|-------|
| `crypto.hash` | Base64 | Base64 | BLAKE3; raw UTF-8/hex yields incorrect hashes |
| `crypto.hash_for_cipher` | Base64 | Base64 | Algorithm varies by cipher suite |
| `crypto.hmac` | Base64 (`data` + `key`) | Base64 | HMAC-SHA256 / HMAC-BLAKE3 |
| `crypto.sign_ed25519` | Per-field encoding hints | Per-field | `message_encoding`, `signature_encoding`, `public_key_encoding` (BD-01) |
| `crypto.verify_ed25519` | Per-field encoding hints | — | Same per-field hints as sign |
| `crypto.sign_contract` | JSON (`terms` object) | Hex (hash), Hex (sig, pk) | Canonical JSON → SHA-256 → Ed25519 |
| `crypto.verify_contract` | Hex (all fields) | — | Validates Ed25519 over terms hash |

### Encoding Hints (BD-01, Wave 33)

Ed25519 sign/verify methods accept per-field encoding overrides:
- `"base64"` (default), `"hex"`, `"base64url"`, `"utf8"`, `"none"`

When no hint is present, Base64 is assumed.

**Primals calling `crypto.hash`**: Encode your raw bytes as standard Base64
before sending. The response `hash` field is also Base64.

---

## Signed Capability Announcements (SA-01, Wave 45)

For cross-family federations where socket-level access control (owner-only 0600 permissions) is insufficient, primals MAY include a cryptographic attestation in their capability responses so that Songbird discovery and Neural API can verify advertisement authenticity.

### Wire Format

The `signed_announcement` field appears in `capabilities.list` and `discover_capabilities` responses:

```json
{
  "result": {
    "primal": "beardog",
    "version": "0.9.0",
    "methods": ["crypto.sign_ed25519", ...],
    "signed_announcement": {
      "schema_version": 2,
      "algorithm": "ed25519",
      "public_key": "<hex-encoded Ed25519 verifying key>",
      "signature": "<hex-encoded Ed25519 signature>",
      "signed_fields": ["primal", "version", "methods"]
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | Integer | Canonical message format version (currently `2`) |
| `algorithm` | String | Always `"ed25519"` |
| `public_key` | String | Hex-encoded 32-byte Ed25519 verifying key |
| `signature` | String | Hex-encoded 64-byte Ed25519 signature |
| `signed_fields` | String[] | Which response fields are covered by the signature |

### Canonical Signed Message (schema_version 2)

The signed payload is `SHA-256(primal ":" version ":" sorted_methods)`:

```
message = SHA-256(
    primal_name_bytes
    || b":"
    || version_bytes
    || b":"
    || for each method in sorted(methods):
        method_bytes || b","
)
```

The signature is `Ed25519.sign(signing_key, message)` where `message` is the 32-byte SHA-256 digest. Methods MUST be lexicographically sorted before hashing to ensure determinism regardless of registry enumeration order.

### Identity Key Derivation

Each primal instance derives a single Ed25519 keypair from its runtime identity:

```
seed = SHA-256("primal-identity-key:" || primal_name || ":" || node_id)
signing_key = Ed25519.from_seed(seed)
```

The same key MUST be used for capability announcements, ionic bond signing, contract signing, and neural registration attestation. This gives each primal instance one verifiable public identity.

### Neural API Registration Attestation

When registering via `capability.register`, primals MAY include a `signed_attestation` field in the registration payload. Neural API stores the public key for downstream verification by Songbird and other discovery consumers.

### Verification

Verifiers reconstruct the canonical message from the response's `primal`, `version`, and `methods` fields, compute SHA-256, and verify the Ed25519 signature against the announced `public_key`. If the primal's public key is already known (e.g., from a prior ionic bond or BTSP session), the verifier can confirm identity continuity.

### Implementation Status (April 13, 2026)

| Primal | `signed_announcement` in `capabilities.list` | `signed_announcement` in `discover_capabilities` | Neural Registration Attestation |
|--------|----------------------------------------------|--------------------------------------------------|-------------------------------|
| BearDog | ✓ (schema_version 2, unified key) | ✓ | ✓ |

---

## Transport Security Advertisement (TS-01, Wave 48)

Primals that use BTSP SHOULD include a `transport_security` object in their
`capabilities.list` and `discover_capabilities` responses. This lets consumers
(biomeOS, primalSpring, Songbird) determine whether a BTSP handshake is required
**before** attempting a connection, preventing silent rejection on family-scoped
sockets.

### Wire Format

```json
{
  "transport_security": {
    "btsp_required": true,
    "btsp_version": "2.0",
    "btsp_server_available": true,
    "cleartext_available": false,
    "note": "Family-scoped socket: BTSP handshake required before JSON-RPC."
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `btsp_required` | Boolean | Whether a BTSP handshake is mandatory before JSON-RPC traffic is accepted. `true` on family-scoped sockets, `false` on dev/standalone. |
| `btsp_version` | String | BTSP protocol version supported (e.g., `"2.0"`). |
| `btsp_server_available` | Boolean | Whether this primal exposes `btsp.server.*` methods for handshake-as-a-service. |
| `cleartext_available` | Boolean | Whether plaintext JSON-RPC is accepted. Inverse of `btsp_required` in most cases. |
| `note` | String | Human-readable guidance for debugging. Optional. |

### Rejection Behavior (TS-01 Companion)

When a non-BTSP connection arrives on a family-scoped socket, the primal SHOULD
send a JSON-RPC error response before dropping:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "BTSP handshake required",
    "data": {
      "reason": "This socket is family-scoped and requires a BTSP handshake before JSON-RPC traffic.",
      "btsp_version": "2.0"
    }
  },
  "id": null
}
```

This replaces silent connection drops, giving forwarding proxies (biomeOS) and
test harnesses (primalSpring AtomicHarness) a clear signal to initiate BTSP.

### Implementation Status (April 14, 2026)

| Primal | `transport_security` in response | Rejection JSON-RPC |
|--------|----------------------------------|-------------------|
| BearDog | ✓ (Wave 48) | ✓ (Wave 48) |

---

## Relationship to Other Standards

| Standard | Scope | Relationship |
|----------|-------|-------------|
| **UniBin** | Binary structure (subcommands, `--help`, `--version`) | Prerequisite — primal must be a UniBin |
| **ecoBin** | Build portability (pure Rust, no C deps, musl-static) | Prerequisite — primal must be an ecoBin |
| **genomeBin** | Deployment attestation (checksums, lineage) | Extends — genomeBin MAY embed capability manifest |
| **Capability Wire Standard** (this) | IPC self-advertisement | Complements — defines what the binary says about itself at runtime |
| **Semantic Method Naming** | Method name convention | Referenced — `methods` array follows this convention |

The binary ladder: **UniBin → ecoBin → genomeBin**
The runtime ladder: **health.liveness → capabilities.list (Level 1) → Standard (Level 2) → Composable (Level 3)**

---

## Socket Permissions Convention (SP-01, Wave 259)

All primals SHOULD support a `{PRIMAL}_SOCKET_MODE` environment variable
that sets Unix socket file permissions as an octal string.

### Convention

| Env Var | Default | Description |
|---------|---------|-------------|
| `{PRIMAL}_SOCKET_MODE` | `0600` | Octal permission mode for the primal's UDS |

Where `{PRIMAL}` is the uppercase canonical primal name: `TOADSTOOL_SOCKET_MODE`,
`BARRACUDA_SOCKET_MODE`, `CORALREEF_SOCKET_MODE`, etc.

### Recommended Values

| Deployment | Mode | Rationale |
|------------|------|-----------|
| User-mode (dev) | `0600` | Owner-only, default umask behavior |
| Group-accessible (systemd) | `0660` | biomeOS/primalSpring in same group |
| World-accessible (testing) | `0666` | Never in production |

### Implementation Status

| Primal | `{PRIMAL}_SOCKET_MODE` | Notes |
|--------|------------------------|-------|
| toadStool | **Done** (S259) | First adopter, reads `TOADSTOOL_SOCKET_MODE` |
| barraCuda | Pending | Creates at user umask |
| coralReef | Pending | Creates at user umask |
| Others | Pending | Adopt as socket-based IPC is enabled |

### Implementation Pattern

```rust
fn socket_mode() -> u32 {
    std::env::var("{PRIMAL}_SOCKET_MODE")
        .ok()
        .and_then(|s| u32::from_str_radix(&s, 8).ok())
        .unwrap_or(0o600)
}
```

---

## Graceful Drain Convention (GD-01, Wave 259)

All primals that accept long-running work SHOULD implement `health.drain`
and `health.version` for zero-downtime upgrades.

### health.drain

Stops accepting new work, waits for in-flight dispatches to complete
(with configurable timeout), and returns when the primal is safe to stop.

**Request:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "health.drain", "params": {"timeout_ms": 30000}}
```

**Response (drained):**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "drained", "in_flight": 0, "drained_at": "2026-05-14T11:15:00Z"}}
```

**Response (timeout, still draining):**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "draining", "in_flight": 3, "timeout_ms": 30000}}
```

After returning `"drained"`, the primal rejects all new work with error code
`-32000` ("Service draining") until restarted. This allows upgrade scripts to:
1. `health.drain` → wait for clean stop
2. Replace binary
3. Start new process
4. `health.version` → verify new binary is running

### health.version

Returns build metadata so upgrade scripts can verify the correct binary is
running after restart.

**Request:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "health.version"}
```

**Response:**
```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "version": "0.2.1",
    "build_hash": "abc123def",
    "session": "S259",
    "compiled_at": "2026-05-12T19:21:00Z",
    "rust_version": "1.87.0"
  }
}
```

### Upgrade Sequence (reference)

```bash
# 1. Drain
echo '{"jsonrpc":"2.0","id":1,"method":"health.drain","params":{"timeout_ms":30000}}' \
  | socat - UNIX-CONNECT:/primal/toadstool

# 2. Stop + swap binary
systemctl stop toadstool
cp /opt/plasmidBin/primals/x86_64-unknown-linux-musl/toadstool /primal/bin/toadstool

# 3. Start + verify
systemctl start toadstool
echo '{"jsonrpc":"2.0","id":1,"method":"health.version"}' \
  | socat - UNIX-CONNECT:/primal/toadstool
```

### Implementation Status

| Primal | health.drain | health.version | Notes |
|--------|-------------|----------------|-------|
| toadStool | Proposed | Proposed | Primary target (long-running compute) |
| barraCuda | Proposed | Proposed | GPU dispatches need drain |
| coralReef | Proposed | Proposed | Shader compilation has in-flight work |
| All others | Optional | Recommended | Short-lived RPC primals can implement trivially |

---

**License**: AGPL-3.0-or-later
