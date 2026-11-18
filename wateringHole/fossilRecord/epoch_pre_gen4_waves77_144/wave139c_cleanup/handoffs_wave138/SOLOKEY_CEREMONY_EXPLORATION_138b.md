# SoloKey Ceremony Exploration — Upstream Handoff

**Wave**: 138b | **Date**: Jul 14, 2026 | **From**: eastGate overwatch
**For**: bearDog team, primalSpring team
**Status**: First credential minted. Authenticate/entropy pending second physical session.

---

## What Happened

First hardware-attested FIDO2 credential created on the ecosystem:

```
rp_id:         primals.eco
credential_id: owBYXg2N4Dzf7bQRS5wtH6TGZiJs3J9olwS0mT7PPAmI4LF//xv/nwyH3GIt
               +LipJSjaS2cF80j+LGjggh89xRsfakx2toyAwVBMhY/1VkMxPDzJ1TveNDsU
               DH5vZkDHL9UBTFAIG7W48OAO+9BvRQJQdnedjPZ/xu/QcmKc1E7OIw==
public_key:    pAEBAycgBiFYIEYRxwGUvwyjHb4I3G9vo44tPSGmJj00qXs7WzHctKA5
algorithm:     ES256 (P-256 / ECDSA)
```

Credential lives inside the SoloKey Solo 2 secure element. Private key never leaves the chip.

---

## Bugs Fixed to Get Here

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| **HIDRAW-REPORT-ID** (P0) | Linux hidraw requires 0x00 report ID prefix on writes for devices without numbered reports. Without it, kernel misinterprets first CID byte as report ID, garbling the packet. | Prepend `0x00` in `LinuxHidDevice::write()` |
| **CTAPHID_MSG vs CTAPHID_CBOR** | Used `0x83` (CTAP1/U2F MSG) instead of `0x90` (CTAP2 CBOR) for MakeCredential | Added `Cbor = 0x90` variant, use for all CTAP2 commands |
| **CTAP2 InvalidOption** (0x2c) | Sent `up: true` in MakeCredential options. `up` is only valid for GetAssertion — MakeCredential only accepts `rk` and `uv` | Removed `up: true` from MakeCredential options |
| **EAGAIN busy-poll** | HID device opened with O_NONBLOCK, reads return EAGAIN immediately during user-presence wait | Retry loop with 200ms sleep, 300 attempts (~60s window) |

---

## FIDO2 Touch Model

Every CTAP2 operation that requires User Presence (UP) follows the same physical pattern:

```
1. Client sends CTAP2 command (MakeCredential, GetAssertion)
2. SoloKey LED starts blinking (~30s window)
3. SoloKey sends CTAPHID_KEEPALIVE (0xBB) packets every ~200ms
4. Human physically touches the capacitive sensor
5. SoloKey performs the cryptographic operation
6. SoloKey sends CTAPHID_CBOR response with result
```

If no touch within ~30 seconds: SoloKey returns `CTAP2_ERR_USER_ACTION_TIMEOUT (0x2f)`.

One touch = one authorization. Each operation (register, authenticate, entropy) is a
separate CTAP2 command requiring its own touch.

---

## Exploration: Human Tap Timing as Tier 3 Entropy

### Current Entropy Sources

```
Tier 1: OS RNG (getrandom / /dev/urandom) — always available
Tier 2: Hardware RNG (SoloKey signature nonce) — requires FIDO2 device + touch
```

### Proposed: Tier 3 — Human Presence Entropy

The human touch event contains unreproducible temporal information:

| Signal | Source | Entropy Estimate |
|--------|--------|-----------------|
| **Reaction latency** | Time from LED blink to touch (microseconds) | 4-6 bits per tap (human motor jitter ~10-50ms) |
| **EAGAIN count** | Number of read retries before response arrives | 2-3 bits (varies with USB scheduling) |
| **Inter-operation interval** | Time between successive ceremony steps | 8+ bits (human decision timing) |
| **Keepalive count** | How many keepalives before touch | 2-3 bits (USB + human variance) |

### Implementation Sketch

```rust
struct TapTimingEntropy {
    command_sent_us: u64,      // Instant command was sent
    first_keepalive_us: u64,   // First keepalive received (device processing time)
    touch_detected_us: u64,    // First non-EAGAIN/non-keepalive response
    eagain_count: u32,         // Total EAGAIN retries
    keepalive_count: u32,      // Total keepalive packets received
}

impl TapTimingEntropy {
    fn mix_into(&self, hasher: &mut blake3::Hasher) {
        // Human reaction latency (high entropy — motor jitter)
        let reaction_us = self.touch_detected_us - self.first_keepalive_us;
        hasher.update(&reaction_us.to_le_bytes());

        // Processing latency (hardware + USB scheduling jitter)
        let processing_us = self.first_keepalive_us - self.command_sent_us;
        hasher.update(&processing_us.to_le_bytes());

        // Retry counts (USB bus timing jitter)
        hasher.update(&self.eagain_count.to_le_bytes());
        hasher.update(&self.keepalive_count.to_le_bytes());
    }
}
```

### Entropy Mixing for Loam Certificate Seed

```
loam_seed = BLAKE3_keyed(
    key: "beardog_loam_entropy_v1",
    data: [
        os_entropy[32]           // Tier 1: getrandom
        solokey_sig_nonce[64]    // Tier 2: hardware RNG in signature
        tap_timing.reaction_us   // Tier 3: human motor latency
        tap_timing.eagain_count  // Tier 3: USB scheduling jitter
        tap_timing.keepalive_ct  // Tier 3: device processing variance
    ]
)
```

### Why This Matters for Genetics

In the biological model, genetic diversity comes from **multiple independent sources of
randomness**: DNA replication errors, crossing-over, environmental mutagens. The Loam
Certificate seeding mirrors this:

- **Tier 1 (OS)** = environmental noise (thermal, interrupt timing)
- **Tier 2 (Hardware)** = internal mutation (hardware RNG in secure element)
- **Tier 3 (Human)** = selection pressure (human temporal signature)

No single compromised source can predict the seed. Even if an attacker controls the OS RNG
AND the hardware RNG, the human temporal component remains unobservable.

---

## primalSpring Scenarios to Evolve

### Existing (registered, compilation ready)

- `s_fido2_entropy_ceremony` — validate entropy IPC shape
- `s_hardware_trust_pipeline` — end-to-end trust chain
- `s_keygen_interaction_surface` — key generation coverage

### New scenarios to write

| Scenario | What it validates |
|----------|-------------------|
| `s_fido2_register_e2e` | MakeCredential returns valid credential_id + COSE public key |
| `s_fido2_authenticate_e2e` | GetAssertion signature verifies against registered public key |
| `s_fido2_entropy_mixing` | Tier 1 + Tier 2 + Tier 3 entropy mixed, output passes NIST SP 800-22 basic tests |
| `s_fido2_tap_timing_entropy` | TapTimingEntropy captures microsecond-precise timing, non-zero values |
| `s_fido2_ceremony_chain` | Full ceremony: register → authenticate → entropy → Loam cert seed |
| `s_fido2_timeout_tolerance` | UserActionTimeout (0x2f) handled gracefully, retryable |
| `s_fido2_invalid_option_guard` | No invalid CTAP2 options in MakeCredential/GetAssertion |

### Mock vs Live

primalSpring scenarios should work in TWO modes:

1. **Mock** (CI, gates without SoloKey): Use `MockCtap2Transport` with deterministic responses
2. **Live** (eastGate with SoloKey): Use real HID transport, require physical touch

Gate presence detection: `if Path::new("/dev/hidraw4").exists() && is_fido2_device(...)` → live mode.

---

## Remaining Ceremony Steps

The register succeeded. Two steps remain for the full ceremony:

```
DONE    Register:     MakeCredential → credential_id + public_key
NEXT    Authenticate: GetAssertion → signature (proves credential works)
NEXT    Entropy:      GetAssertion → mix signature nonce → Tier 2 entropy
THEN    Loam Cert:    Mix all entropy tiers → seed Loam Certificate
```

Each step requires one physical touch (~30s window).

---

## Files Changed

| File | Change |
|------|--------|
| `beardog-hid/src/linux.rs` | Prepend 0x00 report ID in write() |
| `beardog-tunnel/.../hid_transport.rs` | CTAPHID_CBOR (0x90), 300 max attempts |
| `beardog-tunnel/.../ctap2_protocol.rs` | Remove `up:true` from MakeCredential options |
| `wateringHole/handoffs/SOLOKEY_CEREMONY_EXPLORATION_138b.md` | This document |
