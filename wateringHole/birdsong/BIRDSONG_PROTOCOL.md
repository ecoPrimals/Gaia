# 🎵 BirdSong Protocol Specification

**Version**: 2.0  
**Last Updated**: January 3, 2026  
**Status**: Production Ready (Songbird v3.6)

---

## 🎯 Purpose

BirdSong is the **encrypted discovery protocol** for the ecoPrimal ecosystem. It solves the "chicken-and-egg problem" of encrypted UDP discovery:

> **Problem**: How do you discover primals using encryption when you don't know who to trust yet?

> **Solution**: Plaintext family_id header + encrypted payload for dual-phase trust evaluation.

---

## 🏗️ Protocol Architecture

### Two-Phase Discovery

```
Phase 1: Family Identification (Plaintext)
  ↓
  UDP Packet Header: family_id (plaintext)
  ↓
Phase 2: Identity Verification (Encrypted)
  ↓
  UDP Packet Payload: Identity + Capabilities (encrypted)
  ↓
  Result: Auto-trust within family!
```

### Why This Works

1. **Plaintext family_id** → Receivers can quickly filter "is this my family?"
2. **Encrypted payload** → Only family members can decrypt identity details
3. **No chicken-and-egg** → Don't need to know peer before evaluating trust

---

## 📦 Packet Structure

### BirdSongPacket v2

```json
{
  "version": 2,
  "family_id": "your-family-id",
  "encrypted_payload": {
    "ciphertext": "<base64-encoded-encrypted-data>",
    "nonce": "<base64-encoded-nonce>",
    "algorithm": "ChaCha20-Poly1305"
  },
  "timestamp": 1704326400,
  "ttl": 300
}
```

### Encrypted Payload Contents (After Decryption)

```json
{
  "primal_id": "songbird-tower-1",
  "primal_type": "songbird",
  "endpoint": "http://192.0.2.10:8080",
  "capabilities": ["discovery", "auto-trust", "encrypted-birdsong"],
  "identity_attestations": {
    "family_id": "your-family-id",
    "seed_hash": "<hash-of-family-seed>",
    "public_key": "<optional-public-key>",
    "signature": "<optional-signature>"
  }
}
```

---

## 🔐 Encryption Details

### Algorithm

**ChaCha20-Poly1305** (AEAD - Authenticated Encryption with Associated Data)

**Why ChaCha20-Poly1305?**
- Fast on all platforms (including ARM)
- Widely trusted (used by TLS 1.3)
- Authenticated encryption (integrity + confidentiality)
- Modern alternative to AES-GCM

### Key Derivation

```
Family Seed (base64-encoded)
  ↓
Base64 Decode
  ↓
Use as ChaCha20-Poly1305 key (32 bytes)
```

**Note**: Production systems should use proper KDF (e.g., HKDF, Argon2)

### Nonce Generation

```
Random 12 bytes (96 bits) per packet
  ↓
Base64 encode for JSON transport
```

**Critical**: Nonce MUST be unique for each packet with same key!

---

## 🚀 Implementation (Songbird v3.6)

### Encryption Flow

```rust
// 1. Prepare plaintext payload
let payload = IdentityPayload {
    primal_id: "songbird-tower-1",
    primal_type: "songbird",
    endpoint: "http://192.0.2.10:8080",
    capabilities: vec!["discovery", "auto-trust"],
    identity_attestations: attestations,
};

// 2. Serialize to JSON
let plaintext = serde_json::to_vec(&payload)?;

// 3. Call BearDog encryption API
let response = beardog_client
    .encrypt(plaintext, family_id)
    .await?;

// 4. Build BirdSongPacket
let packet = BirdSongPacket {
    version: 2,
    family_id: family_id.clone(),
    encrypted_payload: EncryptedPayload {
        ciphertext: response.ciphertext,
        nonce: response.nonce,
        algorithm: "ChaCha20-Poly1305".to_string(),
    },
    timestamp: SystemTime::now()
        .duration_since(UNIX_EPOCH)?
        .as_secs(),
    ttl: 300,
};

// 5. Serialize packet to JSON
let packet_json = serde_json::to_vec(&packet)?;

// 6. Send via UDP multicast
send_udp_multicast(packet_json, "239.255.0.1:4200")?;
```

### Decryption Flow (Receiver)

```rust
// 1. Receive UDP packet
let packet_data = receive_udp()?;

// 2. Parse BirdSongPacket
let packet: BirdSongPacket = serde_json::from_slice(&packet_data)?;

// 3. Check family_id (plaintext header)
if packet.family_id != our_family_id {
    return Err("Not our family, ignoring");
}

// 4. Call BearDog decryption API
let response = beardog_client
    .decrypt(
        packet.encrypted_payload.ciphertext,
        packet.family_id,
        packet.encrypted_payload.nonce
    )
    .await?;

// 5. Parse decrypted payload
let payload: IdentityPayload = serde_json::from_slice(&response.plaintext)?;

// 6. Evaluate trust
if payload.identity_attestations.family_id == our_family_id {
    // Auto-trust! Add to trusted peers
    add_trusted_peer(payload);
}
```

---

## 🌐 Network Transport

### UDP Multicast

**Multicast Group**: `239.255.0.1:4200` (default)

**Why UDP Multicast?**
- Single packet reaches all towers on LAN
- No need to know peer IPs in advance
- Low overhead for periodic beacons
- Standard discovery pattern

### Beacon Frequency

**Recommended**: Every 30-60 seconds

**Trade-offs**:
- Too frequent: Network spam
- Too infrequent: Slow peer discovery

**Adaptive**: Increase frequency when topology changes detected

### Packet Size

**Typical**: 500-1000 bytes
- Plaintext header: ~50 bytes
- Encrypted payload: ~400-800 bytes
- Well under UDP MTU (1500 bytes)

---

## 🔄 Protocol Evolution

### Version History

#### v1.0 (Deprecated)
- Plaintext only
- No encryption
- Simple primal_id broadcast
- **Problem**: No security, anyone could spoof

#### v2.0 (Current)
- Plaintext family_id + encrypted payload
- Solves chicken-and-egg problem
- Identity attestations
- **Status**: ✅ Working (Songbird v3.6)

#### v3.0 (Future)
- Public key cryptography (optional)
- Digital signatures for attestations
- Key rotation support
- Multi-family routing

---

## 🧪 Testing & Validation

### Manual Test (Send Packet)

```bash
# Start Songbird with debug logging
RUST_LOG=songbird=debug ./songbird-orchestrator-v3.6

# Watch logs for:
# - "Calling BearDog encryption API"
# - "Encryption succeeded"
# - "Sending BirdSongPacket"
```

### Manual Test (Receive Packet)

```bash
# Listen on multicast group
socat UDP4-RECV:4200,ip-add-membership=239.255.0.1:0.0.0.0 -

# Should see JSON packets with:
# - family_id (plaintext)
# - encrypted_payload with ciphertext
```

### Integration Test

```bash
# Start BearDog
./start-beardog-server.sh

# Start Songbird (Tower 1)
./start-songbird.sh

# Start Songbird (Tower 2 - different terminal)
./start-songbird.sh

# Verify Tower 2 logs show:
# - "Received BirdSongPacket from <Tower 1>"
# - "Decryption succeeded"
# - "Added trusted peer: <Tower 1>"
```

---

## 📊 Production Status

### What's Working ✅

- ✅ BirdSongPacket v2 structure
- ✅ Encryption via BearDog API
- ✅ Decryption via BearDog API
- ✅ UDP multicast transmission
- ✅ Plaintext family_id filtering
- ✅ Identity attestations
- ✅ Base64 serialization (correct!)
- ✅ Songbird v3.6 integration

### Known Issues ⚠️

1. **No key rotation** - Same family seed forever
   - Impact: High (security)
   - Mitigation: Periodic manual rotation
   - Fix: Implement key rotation protocol

2. **No replay protection** - Old packets can be resent
   - Impact: Medium (DoS potential)
   - Mitigation: TTL check, sequence numbers
   - Fix: Add packet sequence numbers

3. **No rate limiting** - Beacon spam possible
   - Impact: Low (LAN only)
   - Mitigation: Reasonable beacon frequency
   - Fix: Implement adaptive beaconing

---

## 🎯 For Primal Developers

### Implementing BirdSong Support

**Step 1**: Add BearDog client dependency
```rust
use biomeos_core::adaptive_client::BirdSongClient;
```

**Step 2**: Initialize client
```rust
let beardog_endpoint = "http://localhost:9000";
let client = BirdSongClient::new(beardog_endpoint);
```

**Step 3**: Encrypt discovery data
```rust
let payload = your_primal_identity();
let plaintext = serde_json::to_vec(&payload)?;
let encrypted = client.encrypt(plaintext, family_id).await?;
```

**Step 4**: Build and send BirdSongPacket
```rust
let packet = BirdSongPacket::new(family_id, encrypted);
send_udp_multicast(packet)?;
```

**Step 5**: Receive and decrypt
```rust
let packet = receive_birdsong_packet()?;
if packet.family_id == our_family {
    let decrypted = client.decrypt(
        packet.encrypted_payload.ciphertext,
        packet.family_id,
        packet.encrypted_payload.nonce
    ).await?;
    handle_peer_identity(decrypted)?;
}
```

### Using Adaptive Client

**Why**: Handles both BearDog v1 and v2 APIs automatically

```rust
use biomeos_core::adaptive_client::BirdSongClient;

// Client auto-detects API version
let mut client = BirdSongClient::new("http://localhost:9000");

// Works with both v1 and v2!
let encrypted = client.encrypt(data, family_id).await?;
```

See: `biomeOS/crates/biomeos-core/src/adaptive_client.rs`

---

## 🔗 Ecosystem Integration

### Songbird → BearDog

```
Songbird (Discovery Orchestrator)
  ↓ HTTP POST /api/v2/birdsong/encrypt
BearDog (Genetic Keeper)
  ↓ Encrypted payload
Songbird
  ↓ UDP multicast
Network (239.255.0.1:4200)
```

### Receiving Tower

```
Network (UDP multicast)
  ↓ BirdSongPacket (JSON)
Songbird (Receiver)
  ↓ Parse, check family_id
BearDog (Decryption)
  ↓ Decrypted identity
Songbird
  ↓ Trust evaluation
biomeOS (Orchestration)
  ↓ Add to topology
PetalTongue (Visualization)
```

---

## 📋 Technical Specifications

### Packet Format (JSON)

```typescript
interface BirdSongPacket {
  version: number;                    // Protocol version (2)
  family_id: string;                  // Plaintext family identifier
  encrypted_payload: {
    ciphertext: string;               // Base64-encoded encrypted data
    nonce: string;                    // Base64-encoded 12-byte nonce
    algorithm: string;                // "ChaCha20-Poly1305"
  };
  timestamp: number;                  // Unix timestamp (seconds)
  ttl: number;                        // Time-to-live (seconds)
}

interface IdentityPayload {           // Decrypted payload contents
  primal_id: string;                  // Unique primal identifier
  primal_type: string;                // "songbird", "beardog", etc.
  endpoint: string;                   // HTTP endpoint URL
  capabilities: string[];             // Supported capabilities
  identity_attestations: {
    family_id: string;                // Family membership proof
    seed_hash: string;                // Hash of family seed
    public_key?: string;              // Optional public key
    signature?: string;               // Optional signature
  };
}
```

### Network Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Multicast IP | 239.255.0.1 | Site-local range |
| UDP Port | 4200 | Configurable |
| Beacon Interval | 30-60s | Adaptive |
| TTL | 300s (5 min) | Packet lifetime |
| Max Packet Size | 1500 bytes | Standard MTU |

---

## 💡 Best Practices

### For Implementers

1. **Always check family_id** before attempting decryption
2. **Validate timestamp and TTL** before processing
3. **Use adaptive client** for BearDog API compatibility
4. **Never log family seeds** or plaintext payloads
5. **Implement exponential backoff** for API failures

### For Operators

1. **Use same family_id** across all towers in family
2. **Secure family seed** with proper permissions
3. **Monitor beacon frequency** to prevent spam
4. **Check network multicast** support (some cloud providers block)
5. **Test cross-tower discovery** before production

---

## 🚦 Roadmap

### Short-term (1-2 months)

- [ ] Packet sequence numbers (replay protection)
- [ ] Adaptive beacon frequency
- [ ] Rate limiting
- [ ] Enhanced attestations

### Medium-term (3-6 months)

- [ ] Public key cryptography (optional)
- [ ] Digital signatures
- [ ] Key rotation protocol
- [ ] Multi-family routing

### Long-term (6-12 months)

- [ ] BirdSong v3.0 protocol
- [ ] Federation support
- [ ] Advanced trust models
- [ ] Performance optimizations

---

## 📚 References

### Implementation Examples

- **Songbird v3.6**: `ecoPrimals/phase1/songbird/songbird-orchestrator-v3.6-api-wrapper`
- **Adaptive Client**: `biomeOS/crates/biomeos-core/src/adaptive_client.rs`
- **BearDog API**: `wateringHole/btsp/BEARDOG_TECHNICAL_STACK.md`

### Related Documentation

- **BearDog Technical Stack**: `wateringHole/btsp/`
- **biomeOS Architecture**: `biomeOS/README.md`
- **Integration Guides**: `biomeOS/docs/jan3-session/`

---

**Status**: ✅ **PRODUCTION READY**  
**Verified**: Songbird v3.6 + BearDog v0.15.0  
**Next**: Enhanced attestations + replay protection

🎵 **BirdSong: Encrypted Discovery for Secure Auto-Trust** 🔐

