<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Genetics Carrier Pattern — Universal Node Enrollment

**Date**: June 15, 2026
**Status**: Active (fieldGate first-ant-through)
**Owner**: cellMembrane/ironGate + bearDog (crypto)

---

## Principle

A new node needs exactly one secret to join the family: `FAMILY_SEED`.
Everything else (identity, keys, mesh enrollment, depot access) derives from it.

The **genetics carrier** is the mechanism by which `FAMILY_SEED` reaches a new
node securely. The carrier varies by deployment context; the bootstrap procedure
after delivery is identical.

---

## What FAMILY_SEED Provides

```
FAMILY_SEED (root secret, 32 bytes)
  ├── FAMILY_ID (namespace label, derived via BLAKE3)
  ├── Node identity (GATE_NAME + HKDF-derived node key)
  ├── Mesh enrollment credentials (songBird peer auth)
  ├── BTSP handshake material (bearDog inter-primal auth)
  └── riboCipher key derivation (transport signal tier)
```

With FAMILY_SEED + GATE_NAME, a node can:
1. Prove family membership to any peer
2. Derive all required cryptographic material
3. Authenticate to mesh, depot, and peer services
4. Pass health sweeps (bearDog S4 sovereignty probe)

---

## Carrier Tiers

| Tier | Carrier | Security | Attestation | Use Case |
|------|---------|----------|-------------|----------|
| 1 | **File (scp/USB)** | Medium | None | LAN first-ant-through, controlled env |
| 2 | **Encrypted file + passphrase** | Medium-High | User knowledge | Offsite NUC via courier |
| 3 | **SoloKey FIDO2 resident credential** | High | Hardware | Physical genesis ceremony |
| 4 | **grapheneGate Strongbox** | High | Hardware | Mobile carrier bootstraps nearby |
| 5 | **songBird mesh relay** | High | End-to-end | Mesh-native (future) |

---

## Tier 1: File Carrier (Current — fieldGate)

The simplest path. Used when operator has SSH access to both source and target.

```bash
# On eastGate (source of truth for FAMILY_SEED):
cat /opt/membrane/env
# Contains: FAMILY_SEED=<hex>, FAMILY_ID=<hex>, GATE_NAME=eastGate, ...

# Create env file for new gate:
cat > /tmp/fieldGate.env << 'EOF'
FAMILY_SEED=<production-family-seed>
FAMILY_ID=e8b62b6e
NODE_ID=fieldGate
GATE_NAME=fieldGate
SONGBIRD_PEERS=golgiBody@[RELAY_PUBLIC]:7700,eastGate@<lan-ip>:7700
SONGBIRD_FEDERATION_ENABLED=true
SECURITY_SOCKET=/run/membrane/beardog.sock
PRIMAL_BIND_MODE=auto
ECOPRIMALS_ROOT=[KEY_SCRUBBED]
EOF

# Deliver to target:
scp /tmp/fieldGate.env fieldGate:/opt/membrane/env
ssh fieldGate "chmod 600 /opt/membrane/env"
rm /tmp/fieldGate.env
```

**Security boundary**: Transit encrypted (SSH). File at rest protected by filesystem
permissions (600). Relies on operator trust + SSH key auth.

---

## Tier 2: Encrypted File (Offsite NUC)

For shipping a NUC to a remote site where operator isn't physically present at both ends.

```bash
# On eastGate: encrypt env file with passphrase
age -p -o fieldGate.env.age /tmp/fieldGate.env

# Transfer encrypted file via any channel (email, USB, cloud, courier)
# Recipient decrypts on target:
age -d fieldGate.env.age > /opt/membrane/env
chmod 600 /opt/membrane/env
```

**Security boundary**: Passphrase-protected. Can survive insecure transport channels.
Operator must communicate passphrase out-of-band.

---

## Tier 3: SoloKey FIDO2 (Physical Genesis Ceremony)

The sovereign path. SoloKey carries FAMILY_SEED as a resident FIDO2 credential.
Requires physical presence (button press) to release.

```
Ceremony:
1. Insert SoloKey into source gate (eastGate)
2. bearDog genesis: imprint FAMILY_SEED as resident credential
   - Requires user-presence verification (button tap)
   - FAMILY_SEED stored in hardware secure element
   - Attestation certificate proves hardware origin

3. Transport SoloKey to target (physical courier)

4. Insert SoloKey into target gate (fieldGate)
5. bearDog genesis: read FAMILY_SEED from resident credential
   - Requires user-presence (button tap)
   - Derives node identity from FAMILY_SEED + GATE_NAME
   - Writes /opt/membrane/env
   - SoloKey can optionally be wiped after genesis (one-time use)
```

**Security boundary**: Hardware attestation. FAMILY_SEED never exists in plaintext
outside the secure element until delivery. Tamper-evident (SoloKey reports if
accessed). Physical possession required.

**bearDog implementation**: `crates/beardog-tunnel/src/tunnel/hsm/solo_v2/mod.rs`
and `[KEY_SCRUBBED]_GENETIC_SPORE_SPECIFICATION.md`.

---

## Tier 4: grapheneGate Strongbox (Mobile Carrier)

The Pixel phone acts as a portable genesis device. Android Strongbox (hardware-backed
keystore) holds FAMILY_SEED. When brought to a new node's network:

```
1. grapheneGate on local network (WiFi/Bluetooth)
2. bearDog on grapheneGate: advertise genesis capability via mDNS
3. New node discovers grapheneGate, requests genesis
4. User confirms on Pixel (biometric/PIN)
5. Strongbox releases FAMILY_SEED over authenticated channel
6. New node derives identity, writes env, proceeds with bootstrap
```

**Security boundary**: Hardware-backed keystore + biometric. FAMILY_SEED in Strongbox
is non-extractable without user confirmation. Bluetooth/WiFi channel encrypted via
bearDog BTSP.

**bearDog implementation**: `crates/beardog-security/src/hsm/android_strongbox/`

---

## Tier 5: Mesh-Native (Future — songBird)

The fully sovereign path. No physical carrier needed. A node with network access
requests enrollment from the mesh itself:

```
1. New node connects to any mesh peer (WAN relay or LAN direct)
2. Enrollment request: "I am <proposed-name>, requesting family membership"
3. Mesh routes request to an authorized enrolling gate (requires quorum or operator approval)
4. Enrolling gate seals FAMILY_SEED + node identity via bearDog nuclear envelope
5. Sealed payload delivered over songBird mesh relay
6. New node unseal requires: operator confirmation OR hardware attestation
```

**Security boundary**: End-to-end encrypted (bearDog nuclear tier). Requires explicit
authorization from existing mesh member. Zero trust in transport layer.

---

## Environment File Standard

All carriers ultimately produce the same artifact: `/opt/membrane/env`

```ini
# Gate identity (required)
GATE_NAME=<gate-name>
NODE_ID=<gate-name>

# Family genetics (required — the secret)
FAMILY_SEED=<64-char-hex>
FAMILY_ID=<8-char-hex>

# Mesh configuration (required for enrollment)
SONGBIRD_PEERS=<peer1>@<host1>:7700,<peer2>@<host2>:7700
SONGBIRD_FEDERATION_ENABLED=true

# Security (required for BTSP)
SECURITY_SOCKET=/run/membrane/beardog.sock

# Runtime (required for primals)
PRIMAL_BIND_MODE=auto
ECOPRIMALS_ROOT=/home/<user>/Development/ecoPrimals
```

Permissions: `chmod 600` (owner-only read). Sourced by all systemd units via
`EnvironmentFile=/opt/membrane/env` per GATE_NUCLEUS_SYSTEMD_STANDARD.

---

## Connection to Universal Onboarding

The genetics carrier is step 1 of the universal pattern:

```
Genetics delivered → Identity resolved → Bootstrap runs → Node enrolled
     (this doc)        (cellMembrane)      (gate.bootstrap)  (songBird mesh)
```

Regardless of carrier tier, the downstream pipeline is identical:
- `membrane gate.bootstrap <gate-name>` orchestrates fetch → verify → install → start → sweep → enroll
- Same systemd units, same health sweep, same mesh enrollment
- Only the **source of FAMILY_SEED** varies

---

## References

- [GATE_NUCLEUS_SYSTEMD_STANDARD.md](../GATE_NUCLEUS_SYSTEMD_STANDARD.md) — env file consumed by units
- [SOLOKEY_GENETIC_SPORE_SPECIFICATION.md](../..[KEY_SCRUBBED]_GENETIC_SPORE_SPECIFICATION.md) — Tier 3 detail
- [PHYSICAL_GENESIS_BOOTSTRAP_PLAN.md](../..[KEY_SCRUBBED]_GENESIS_BOOTSTRAP_PLAN.md) — ceremony design
- [TIERED_ACCESS_ARCHITECTURE.md](../..[KEY_SCRUBBED]_ACCESS_ARCHITECTURE.md) — access tiers that rely on identity
