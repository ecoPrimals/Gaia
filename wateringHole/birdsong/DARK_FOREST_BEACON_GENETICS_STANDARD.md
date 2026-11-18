# Dark Forest Beacon Genetics Specification

**Version**: 2.0.0  
**Date**: February 5, 2026  
**Status**: ✅ IMPLEMENTED & VALIDATED  
**Author**: ecoPrimal + AI Collaborative Intelligence

---

## Executive Summary

This specification implements a **two-seed genetic architecture** separating discovery from identity:

| Seed | Biological Analog | Shared? | Function |
|------|-------------------|---------|----------|
| **Beacon Seed** | Mitochondrial DNA | ✅ Yes | Family encryption, address book |
| **Lineage Seed** | Nuclear DNA | ❌ No | Device identity, ancestry proof |

**Key Insight**: 
- **Mitochondrial (Beacon)**: Shared across family, enables Dark Forest encryption, can be synced/evolved
- **Nuclear (Lineage)**: Unique per device, always derived never copied, proves individual ancestry

### Validated Implementation (Feb 5, 2026)

```
Tower:  beacon.seed = 8ff3b864... (SHARED)
        lineage.seed = 5772c07f... (UNIQUE)

Pixel:  beacon.seed = 8ff3b864... (SHARED - same!)  
        lineage.seed = 3795d0ca... (UNIQUE - different!)

Cross-device beacon exchange: ✅ is_family=true both directions
```

---

## 1. Problem Statement

### Current Architecture (Single Seed)

```
Family Seed → Discovery + Trust + Permissions (all bundled)
```

**Limitations**:
- All-or-nothing visibility (see me = access me)
- No cluster hierarchy (every node individually discoverable)
- No "meeting" concept (immediate trust or no trust)
- Beacon broadcasts leak family membership

### Proposed Architecture (Two Seeds)

```
Beacon Seed (Mitochondrial) → Discovery visibility
                              ├── Who have I met?
                              ├── What clusters do I belong to?
                              └── Who can decrypt my beacons?

Lineage Seed (Nuclear)     → Permission verification
                              ├── What can they do after meeting?
                              ├── Read-only / write / admin
                              └── Temporal / capability grants
```

**Benefits**:
- Granular visibility (see me ≠ access me)
- Cluster-based discovery (entry points → internal nodes)
- Social graph of meetings (beacon exchange)
- TRUE Dark Forest (beacons encrypted, observers see noise)

---

## 2. Biological Model

### Mitochondrial vs Nuclear DNA

| Property | Mitochondrial DNA | Nuclear DNA |
|----------|-------------------|-------------|
| **Inheritance** | Maternal only (simpler) | Mixed (both parents) |
| **Function** | Energy/metabolism | Identity/traits |
| **Mutation rate** | Lower (stability) | Higher (adaptation) |
| **Size** | ~16.5kb (small) | ~3 billion bp (large) |
| **Copies per cell** | 100-1000 | 2 |

### Mapping to ecoPrimals

| Property | Beacon Seed | Lineage Seed |
|----------|-------------|--------------|
| **Inheritance** | Social (meetings) | Genetic (family) |
| **Function** | Discovery | Permissions |
| **Rotation** | Can rotate frequently | Stable (identity) |
| **Size** | 32 bytes | 32 bytes |
| **Sharing model** | Exchange on meeting | Derive from parent |

**Key Difference**: Beacon seed can be **mixed** through meetings (not strictly maternal). This enables the "who you've met" social graph.

---

## 3. Architecture

### 3.1 Seed Structure

```rust
/// Beacon seed - controls discovery visibility
struct BeaconSeed {
    /// Core seed material (32 bytes)
    seed: [u8; 32],
    
    /// Beacon family derived from seed
    beacon_family: BeaconFamily,
    
    /// Known beacon peers (social graph)
    met_beacons: HashMap<BeaconId, MeetingRecord>,
    
    /// Cluster memberships
    clusters: Vec<ClusterMembership>,
}

/// Lineage seed - controls permissions (existing)
struct LineageSeed {
    /// Core seed material (32 bytes)
    seed: [u8; 32],
    
    /// Family ID derived from seed
    family_id: String,
    
    /// Node ID for this instance
    node_id: String,
    
    /// Lineage chain
    lineage_chain: Vec<LineageProof>,
}
```

### 3.2 Beacon Discovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: BEACON DISCOVERY                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Node A broadcasts: encrypt(beacon_seed, presence_info)                    │
│                                                                             │
│  Observers without beacon genetics: [noise] [noise] [noise]                │
│  Observers with beacon genetics: "Node A at 192.0.2.100:9200"           │
│                                                                             │
│  ✅ TRUE Dark Forest - outsiders can't even detect communication          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Beacon decrypted (meeting established)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: LINEAGE VERIFICATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  After beacon handshake, verify lineage for permissions:                   │
│                                                                             │
│  Node A ──── lineage challenge ────► Node B                                │
│  Node A ◄─── lineage response ────── Node B                                │
│                                                                             │
│  Result: Permission level determined                                        │
│    ├── Close lineage → Full access                                         │
│    ├── Distant lineage → Read-only                                         │
│    ├── Temporal grant → Time-limited                                       │
│    └── No lineage match → Beacon visible, no access                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Cluster Architecture

```
External Network
       │
       ▼
┌─────────────────────────────────────────┐
│  Entry Point (cluster beacon)           │
│  - External peers find this first       │
│  - Gateway to internal discovery        │
│  - Shares internal beacon genetics      │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│ gate-01 │  │ gate-02 │  │ gate-03  │
│ tower   │  │ tower   │  │ tower    │
│ beacon  │  │ beacon  │  │ beacon   │
└────────┘  └────────┘  └────────┘
    │            │            │
    └────────────┴────────────┘
         Internal mesh
      (all see each other)
```

**External Discovery Path**:
1. Remote peer discovers Entry Point beacon (if they've met)
2. Beacon handshake establishes meeting
3. Entry Point shares internal beacon genetics
4. Remote peer can now discover individual towers
5. Lineage verification per tower determines permissions

**Internal Discovery**:
- All towers share internal beacon genetics
- Direct mesh, no entry point needed
- Lineage still required for permissions

---

## 4. Seed Generation and Derivation

### 4.1 Genesis Seeds

```rust
/// Generate both seeds from a master secret
fn generate_genesis_seeds(master_secret: &[u8; 64]) -> (BeaconSeed, LineageSeed) {
    // Beacon seed - first 32 bytes domain-separated
    let beacon_seed = hkdf_sha256(
        &master_secret[..32],
        b"ecoPrimals-beacon-genesis-v1",
        32
    );
    
    // Lineage seed - second 32 bytes domain-separated  
    let lineage_seed = hkdf_sha256(
        &master_secret[32..],
        b"ecoPrimals-lineage-genesis-v1",
        32
    );
    
    (BeaconSeed::from(beacon_seed), LineageSeed::from(lineage_seed))
}
```

### 4.2 Beacon Mixing (Meeting Exchange)

```rust
/// Exchange beacon genetics during a meeting
fn beacon_meeting(
    my_beacon: &BeaconSeed,
    their_beacon: &BeaconSeed,
    meeting_type: MeetingType,
) -> MeetingRecord {
    // Generate shared meeting key
    let meeting_key = hkdf_sha256(
        &[my_beacon.seed, their_beacon.seed].concat(),
        b"ecoPrimals-beacon-meeting-v1",
        32
    );
    
    MeetingRecord {
        their_beacon_id: their_beacon.id(),
        meeting_key,
        meeting_type,
        timestamp: unix_timestamp(),
        // After meeting, we can decrypt their beacons
        can_see_them: true,
        // They can decrypt ours (if mutual)
        they_can_see_us: meeting_type.is_mutual(),
    }
}
```

### 4.3 Cluster Beacon Derivation

```rust
/// Derive cluster beacon from member beacons
fn derive_cluster_beacon(
    members: &[BeaconSeed],
    cluster_id: &str,
) -> ClusterBeacon {
    // Combine all member beacon seeds
    let combined: Vec<u8> = members
        .iter()
        .flat_map(|m| m.seed.iter())
        .copied()
        .collect();
    
    // Derive cluster seed
    let cluster_seed = hkdf_sha256(
        &combined,
        format!("ecoPrimals-cluster-{}-v1", cluster_id).as_bytes(),
        32
    );
    
    ClusterBeacon {
        cluster_id: cluster_id.to_string(),
        cluster_seed,
        members: members.iter().map(|m| m.id()).collect(),
    }
}
```

---

## 5. Permission Model

### 5.1 After Beacon Handshake

```rust
/// Permission levels determined by lineage verification
enum LineagePermission {
    /// Same lineage seed - full family access
    FullFamily,
    
    /// Related lineage - read + limited write
    ExtendedFamily {
        can_read: bool,
        can_write: Vec<Capability>,
    },
    
    /// Federated partner - specific capabilities
    FederatedPartner {
        capabilities: Vec<Capability>,
        expires: Option<Timestamp>,
    },
    
    /// Temporal grant - time-limited access
    TemporalGrant {
        permissions: Vec<Capability>,
        not_before: Timestamp,
        not_after: Timestamp,
    },
    
    /// Beacon only - can see, cannot access
    BeaconOnly,
}
```

### 5.2 Permission Flow

```
Beacon handshake complete
         │
         ▼
┌─────────────────────────────────────┐
│ Request lineage verification        │
│ from BearDog                        │
└─────────────────┬───────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
   Same lineage?     Different lineage?
         │                 │
         ▼                 ▼
   Full access      Check federation
         │                 │
         │          ┌──────┴──────┐
         │          ▼             ▼
         │    Federated?    Not federated?
         │          │             │
         │          ▼             ▼
         │    Limited        Beacon only
         │    access         (no access)
         │          │             │
         └──────────┴─────────────┘
                    │
                    ▼
            Permissions set
```

---

## 6. Primal Evolution Requirements

### 6.1 BearDog Evolution

**New Responsibilities**:
- Generate and manage beacon seed (separate from lineage seed)
- Beacon encryption/decryption
- Meeting record storage
- Cluster beacon derivation

**New RPC Methods**:

```rust
// Beacon seed management
"beacon.generate"              // Generate new beacon seed
"beacon.get_id"                // Get beacon ID (public)
"beacon.encrypt"               // Encrypt data with beacon seed
"beacon.decrypt"               // Decrypt data with beacon seed

// Meeting management
"beacon.initiate_meeting"      // Start meeting exchange
"beacon.complete_meeting"      // Complete meeting exchange
"beacon.list_meetings"         // List known meetings
"beacon.revoke_meeting"        // Revoke a meeting (they can no longer see us)

// Cluster management  
"beacon.create_cluster"        // Create cluster beacon
"beacon.join_cluster"          // Join existing cluster
"beacon.get_cluster_beacon"    // Get cluster's beacon for sharing

// Lineage (existing, unchanged)
"lineage.verify"               // Verify lineage for permissions
"lineage.get_permissions"      // Get permissions after verification
```

**New Environment Variables**:

```bash
# Separate seeds
BEARDOG_BEACON_SEED=<hex>      # Beacon seed (discovery)
BEARDOG_LINEAGE_SEED=<hex>     # Lineage seed (permissions) - was BEARDOG_FAMILY_SEED

# Backward compatibility
BEARDOG_FAMILY_SEED=<hex>      # If set alone, derives both seeds from it
```

### 6.2 Songbird Evolution

**New Responsibilities**:
- BirdSong beacons encrypted with beacon seed
- Meeting exchange protocol
- Cluster discovery hierarchy

**Changes to BirdSong**:

```rust
// Before: Plaintext beacon
struct BirdSongBeacon {
    family_id: String,
    node_id: String,
    capabilities: Vec<String>,
    endpoint: String,
}

// After: Encrypted beacon
struct DarkForestBeacon {
    // Encrypted with beacon seed
    encrypted_payload: Vec<u8>,
    // Nonce for decryption
    nonce: [u8; 24],
    // Timestamp to prevent replay
    timestamp: u64,
}

struct BeaconPayload {
    beacon_id: BeaconId,
    node_id: String,
    capabilities_hash: [u8; 32],
    endpoint: String,
    cluster_id: Option<String>,
}
```

**Discovery Protocol Change**:

```
Current:
  Multicast → Everyone sees → Connect → Verify lineage

Proposed:
  Multicast → Only those with beacon genetics see → Connect → Verify lineage
```

### 6.3 biomeOS Evolution

**New Responsibilities**:
- Cluster management
- Entry point configuration
- Beacon genetics exchange protocol
- Cross-cluster federation

**New Components**:

```rust
// Cluster manager
struct ClusterManager {
    // This cluster's beacon
    cluster_beacon: ClusterBeacon,
    
    // Entry point configuration
    entry_point: Option<EntryPointConfig>,
    
    // Member management
    members: Vec<NodeId>,
    
    // External peers who have met us
    external_meetings: HashMap<BeaconId, MeetingRecord>,
}

// Entry point configuration
struct EntryPointConfig {
    // Public endpoint for external discovery
    public_endpoint: String,
    
    // Which internal beacons to share after meeting
    share_internal: bool,
    
    // Rate limiting for external meetings
    meeting_rate_limit: Option<RateLimit>,
}
```

---

## 7. Implementation Plan

### Phase 1: BearDog Beacon Seed (Priority: High)

**Tasks**:
- [ ] Add `BeaconSeed` struct to `beardog-genetics`
- [ ] Add beacon seed generation/derivation
- [ ] Add beacon encryption/decryption
- [ ] Add `beacon.*` RPC methods
- [ ] Support both `BEARDOG_BEACON_SEED` and backward-compatible `BEARDOG_FAMILY_SEED`
- [ ] Unit tests for beacon operations

**Estimated Effort**: 2-3 sessions

### Phase 2: BirdSong Dark Forest (Priority: High)

**Tasks**:
- [ ] Change BirdSong beacon format to encrypted
- [ ] Add beacon decryption on receive (try all known beacon genetics)
- [ ] Filter discovered peers by beacon visibility
- [ ] Update discovery protocol to handle encrypted beacons
- [ ] Integration tests with BearDog beacon seed

**Estimated Effort**: 2-3 sessions

### Phase 3: Meeting Exchange Protocol (Priority: Medium)

**Tasks**:
- [ ] Design meeting exchange handshake
- [ ] Implement `beacon.initiate_meeting` / `beacon.complete_meeting`
- [ ] Store meeting records in BearDog
- [ ] Add meeting management UI concepts

**Estimated Effort**: 2 sessions

### Phase 4: Cluster Architecture (Priority: Medium)

**Tasks**:
- [ ] Implement cluster beacon derivation
- [ ] Add entry point configuration
- [ ] Implement internal beacon sharing after cluster meeting
- [ ] Add cluster management to biomeOS

**Estimated Effort**: 3 sessions

### Phase 5: Permission Granularity (Priority: Low)

**Tasks**:
- [ ] Implement `LineagePermission` variants
- [ ] Add temporal grants
- [ ] Add capability-based permissions
- [ ] Federation permission negotiation

**Estimated Effort**: 2 sessions

---

## 8. Scaling Analysis

### 8.1 Beacon Load

| Network Size | Beacon Broadcasts | Visible to Each Node |
|--------------|-------------------|---------------------|
| 10 nodes | 10 beacons | 10 (small family) |
| 100 nodes, 5 families | 100 beacons | ~20 (own family) |
| 1,000 nodes, 50 families | 1,000 beacons | ~20 (own family) |
| 10,000 nodes, hierarchical | 10,000 beacons | 100-1,000 (cluster) |

**Key Insight**: Network load is O(n), but cognitive load is O(family_size). TRUE Dark Forest.

### 8.2 Meeting Scalability

| Model | Meetings Stored | Discovery Complexity |
|-------|-----------------|---------------------|
| Direct only | O(friends) | O(friends) |
| With clusters | O(friends + clusters) | O(friends) + O(1) per cluster |
| Hierarchical | O(log n) clusters | O(log n) |

### 8.3 Dark Forest Property

| Metric | Without Beacon Genetics | With Beacon Genetics |
|--------|------------------------|---------------------|
| Visible to attackers | All beacons | 0 (encrypted noise) |
| Family identifiable | Yes (family_id in plaintext) | No |
| Traffic analysis | Possible | Impossible |
| Metadata leakage | Endpoints, capabilities | Nothing |

---

## 9. Security Analysis

### 9.1 Threat Model

| Threat | Mitigation |
|--------|------------|
| Beacon eavesdropping | Encrypted with beacon seed |
| Family enumeration | Beacons indistinguishable from noise |
| Replay attacks | Timestamps in beacon payload |
| Meeting impersonation | Challenge-response in meeting exchange |
| Permission escalation | Lineage verification separate from beacon |

### 9.2 Trust Levels

```
Level 0: Unknown
    └── No beacon genetics match
    └── Cannot decrypt beacons
    └── Invisible to each other (TRUE Dark Forest)

Level 1: Met (Beacon visible)
    └── Beacon genetics exchanged
    └── Can see beacons, can attempt connection
    └── No permissions yet

Level 2: Lineage Verified
    └── Beacon visible + lineage checked
    └── Permissions determined by lineage relationship
    └── Full family / federated / temporal / capability

Level 3: Cluster Member
    └── Part of same cluster
    └── Internal beacon genetics shared
    └── Cluster-level permissions
```

---

## 10. Backward Compatibility

### 10.1 Migration Path

```
Phase 1: Dual mode
    BEARDOG_FAMILY_SEED set alone → Derives both seeds (backward compatible)
    BEARDOG_BEACON_SEED + BEARDOG_LINEAGE_SEED → New two-seed mode

Phase 2: Gradual migration
    Existing deployments continue working
    New deployments use two-seed mode
    
Phase 3: Full migration
    BEARDOG_FAMILY_SEED deprecated
    All deployments use two-seed mode
```

### 10.2 BirdSong Compatibility

```
Phase 1: Beacon format detection
    If beacon decrypts → New encrypted format
    If beacon parses as JSON → Legacy plaintext format
    Support both during transition

Phase 2: Deprecation warning
    Plaintext beacons trigger warning
    Still accepted but logged

Phase 3: Plaintext rejection
    Only encrypted beacons accepted
```

---

## 11. Summary

### What This Enables

1. **TRUE Dark Forest**: Beacons encrypted, observers see only noise
2. **Social Graph Discovery**: "Who you've met" determines visibility
3. **Cluster Hierarchy**: Entry points → internal nodes
4. **Granular Permissions**: Beacon ≠ access, lineage determines capabilities
5. **Scalable Discovery**: O(family) cognitive load, not O(network)

### The Biological Elegance

| Layer | Analog | Function |
|-------|--------|----------|
| Beacon Seed | Mitochondrial DNA | Discovery/energy |
| Lineage Seed | Nuclear DNA | Identity/permissions |
| Meeting | Social encounter | Beacon genetics exchange |
| Cluster | Colony | Hierarchical discovery |
| Entry Point | Colony entrance | External gateway |

### Design Principles

1. **Beacon = who you've met** (social graph)
2. **Lineage = what you can do** (permissions)
3. **Cluster = network topology** (hierarchy)
4. **Entry point = external interface** (gateway)
5. **TRUE Dark Forest** (observers see nothing)

---

**Status**: ARCHITECTURAL SPECIFICATION - Ready for implementation

*"Beacon genetics is who you've met. Lineage is security. Together, they create a social graph overlaid on cryptographic trust."*

---

## Appendix A: Code Examples

### A.1 Complete Beacon Discovery Flow

```rust
// Node A broadcasts encrypted beacon
async fn broadcast_beacon(beacon_seed: &BeaconSeed) {
    let payload = BeaconPayload {
        beacon_id: beacon_seed.id(),
        node_id: get_node_id(),
        capabilities_hash: hash_capabilities(&my_capabilities),
        endpoint: get_endpoint(),
        cluster_id: get_cluster_id(),
    };
    
    let encrypted = beacon_seed.encrypt(&serialize(payload));
    
    multicast_send(DarkForestBeacon {
        encrypted_payload: encrypted.ciphertext,
        nonce: encrypted.nonce,
        timestamp: unix_timestamp(),
    });
}

// Node B receives and tries to decrypt
async fn receive_beacon(
    beacon: DarkForestBeacon,
    known_beacons: &[BeaconSeed],
) -> Option<DiscoveredPeer> {
    // Try decrypting with each known beacon seed
    for known in known_beacons {
        if let Ok(payload) = known.decrypt(&beacon.encrypted_payload, &beacon.nonce) {
            let payload: BeaconPayload = deserialize(&payload)?;
            
            return Some(DiscoveredPeer {
                beacon_id: payload.beacon_id,
                node_id: payload.node_id,
                endpoint: payload.endpoint,
                met_via: known.id(),
            });
        }
    }
    
    // Can't decrypt - not someone we've met
    None
}
```

### A.2 Meeting Exchange

```rust
// Initiator
async fn initiate_meeting(peer_endpoint: &str) -> Result<MeetingRecord> {
    // Generate meeting request
    let request = MeetingRequest {
        my_beacon_id: my_beacon.id(),
        my_public_beacon: my_beacon.public_portion(),
        nonce: random_32_bytes(),
    };
    
    // Send to peer
    let response: MeetingResponse = send_request(peer_endpoint, request).await?;
    
    // Verify and complete meeting
    let meeting = beacon_meeting(
        &my_beacon,
        &response.their_beacon,
        MeetingType::Direct,
    );
    
    // Store meeting
    store_meeting(meeting.clone());
    
    Ok(meeting)
}

// Responder
async fn respond_to_meeting(request: MeetingRequest) -> Result<MeetingResponse> {
    // Verify request
    verify_meeting_request(&request)?;
    
    // Complete meeting on our side
    let meeting = beacon_meeting(
        &my_beacon,
        &request.their_beacon,
        MeetingType::Direct,
    );
    
    // Store meeting
    store_meeting(meeting);
    
    // Return our beacon info
    Ok(MeetingResponse {
        their_beacon: my_beacon.public_portion(),
        nonce_response: sign_nonce(&request.nonce),
    })
}
```

---

**Document Version**: 1.0.0  
**Last Updated**: February 4, 2026  
**Next Review**: After Phase 1 implementation
