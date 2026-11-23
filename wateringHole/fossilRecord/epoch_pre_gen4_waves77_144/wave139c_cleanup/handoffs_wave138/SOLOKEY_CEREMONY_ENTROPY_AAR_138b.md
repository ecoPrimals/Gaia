# AAR: SoloKey Tap-Sequence Entropy Ceremony — Wave 138b

**Date**: 2026-07-14
**Gate**: eastGate / sporeGate
**Scope**: Implement `beardog.fido2.ceremony` IPC method for multi-tap entropy harvest

## Summary

Implemented the full tap-sequence entropy ceremony pipeline: transport-level timing capture,
ceremony orchestrator in `SoloV2Provider`, IPC handler with BLAKE3 multi-source mixing, and
statistical summary reporting. All code compiles clean, all tests pass (33 fido2 + provider tests).

Live hardware testing revealed a critical SoloKey firmware limitation: the device enters an
irrecoverable `ERR_CHANNEL_BUSY (0x06)` state after timed-out CTAP2 operations, requiring
physical unplug/replug to restore. Even USB reset (`USBDEVFS_RESET`) does not clear this state.
This was confirmed independently using the reference `python-fido2` library.

## What Was Built

### Layer 1: Transport-Level Timing (`hid_transport.rs`)

- **`TapTimingEntropy`** struct: captures `command_sent_ns`, `first_keepalive_ns`, `response_received_ns`, `eagain_count`, `keepalive_count`
- **`CtapResponseWithTiming`**: pairs CTAP2 payload with timing metadata
- **`read_ctaphid_ctap_response_timed()`**: refactored from the existing reader to count EAGAINs and keepalives, capture nanosecond timestamps using `std::time::Instant`
- **`hid_send_receive_timed()`**: timed variant of `hid_send_receive` exposed via `Ctap2TransportBackend::send_receive_timed()`
- **`CTAPHID_CANCEL (0x91)`** support: added to channel init to clear stale transactions from previous sessions

### Layer 2: Ceremony Orchestrator (`provider.rs`)

- **`ceremony_tap_sequence()`** on `SoloV2Provider`: loops N `GetAssertion` calls with fresh OS-RNG challenges, captures `CeremonyTap` per tap
- **`CeremonyResult`**: computes `inter_tap_intervals_ns/ms()`, `mean_reaction_ms()`, `reaction_jitter_ms()`, `timing_entropy_bits_estimate()`
- Validates tap_count 1..=20, immediately sends next GetAssertion after each response for rapid-fire UX

### Layer 3: IPC + Entropy Mixing (`fido2.rs`)

- **`beardog.fido2.ceremony`** IPC method: accepts `rp_id`, `credential_id`, `tap_count` (default 5), `purpose`
- **`ceremony_blake3_mix()`**: keyed BLAKE3 hash combining per-tap `challenge + signature + reaction_ns + eagain_count + keepalive_count` plus inter-tap interval bytes
- Returns JSON with `entropy` (base64, 32 bytes), `timing_summary`, `sources` array, `tier: 3`

### Mock Transport Support

- `MockCtap2Transport` returns deterministic timing in `send_receive_timed()` for unit tests
- All existing provider tests continue to pass

## Hardware Exploration Findings

### P0: SoloKey ERR_CHANNEL_BUSY Lock-Up

After a timed-out CTAP2 command (e.g., MakeCredential where the user didn't touch in time),
the SoloKey Solo 2 enters a permanent `ERR_CHANNEL_BUSY (0x06)` state:

- **CTAPHID_INIT succeeds** — device allocates new CIDs normally
- **ALL commands on new CIDs return 0x06** — GetInfo, GetAssertion, MakeCredential
- **USB reset (`USBDEVFS_RESET`) does NOT clear** — device re-enumerates but stays busy
- **`python-fido2` reference library confirms** — same `CTAP channel busy` loop
- **Only fix: physical unplug/replug** of the SoloKey

**Impact**: Any automation that opens a CTAP2 channel and times out (no user touch) will brick
the device until physical intervention. This must be considered in ceremony design.

**Mitigation added**: `CTAPHID_CANCEL (0x91)` sent during `ctaphid_init` to clear *some*
stale states. Effective for channel-level stale data but not for the firmware-level busy lock.

### Protocol Details Confirmed

| Property | Value |
|----------|-------|
| HID Report ID | None (no numbered reports in HID descriptor) |
| Write prefix | `0x00` required — kernel strips it per `hid_hw_output_report` |
| CTAPHID version | 2 |
| Firmware | 2.3.196 |
| Capabilities | 0x05 (WINK + CBOR) |
| NMSG flag | Not set — device supports both MSG and CBOR |
| CID allocation | Sequential from 0x00000001+ |

### Rapid-Tap Cycle Time

**Not yet measured** due to the busy-lock issue. The ceremony code is ready — once the
device is physically re-plugged, a 3-5 tap test can determine:
- Minimum inter-tap latency (expected: 200-500ms based on CTAP2 keepalive timing)
- Whether the SoloKey re-arms for user presence immediately after response
- USB bus scheduling jitter (EAGAIN count variance)

## What This Unlocks for primalSpring

### New Scenarios to Write

| Scenario | Description |
|----------|-------------|
| `s_fido2_ceremony_tap_sequence` | Validate N-tap ceremony completes, timing captured correctly |
| `s_fido2_timing_entropy_quality` | Validate inter-tap jitter exceeds minimum entropy threshold |
| `s_fido2_ceremony_to_loam` | Full ceremony → Loam Certificate seed generation |
| `s_fido2_channel_recovery` | Validate graceful handling of ERR_CHANNEL_BUSY (cancel + retry) |
| `s_fido2_device_replug_detection` | Detect and handle device re-enumeration after replug |

### Entropy Source Tiers

| Tier | Source | Bytes/Tap | Origin |
|------|--------|-----------|--------|
| 1 | OS-RNG challenge | 32 | `rand::random()` |
| 2 | ES256 signature nonce | ~64 | SoloKey hardware RNG |
| 3 | Reaction latency | 8 | Human motor jitter |
| 3 | Inter-tap interval | 8 | Human rhythm variance |
| 3 | EAGAIN count | 4 | OS scheduler jitter |
| 3 | Keepalive count | 4 | USB bus scheduling |

5 taps = ~600 bytes of multi-source entropy → 32 bytes via BLAKE3 keyed hash.

### ES256 vs Ed25519

The existing credential uses ES256 (P-256), where each signature includes a random `k` nonce
from the SoloKey's hardware RNG. Ed25519 signatures are deterministic (no per-signature randomness).
**ES256 is actually better for entropy harvest** — document this for future credential creation guidance.

## Carried Items

| Item | Priority | Team | Description |
|------|----------|------|-------------|
| SOLOKEY-BUSY-LOCK | P0 | bearDog | Document and handle device busy-lock after timeout; add `beardog.fido2.usb_reset` IPC? |
| CEREMONY-LIVE-TEST | P1 | bearDog/operator | Physical replug needed, then run 3-5 tap ceremony to measure rapid-tap latency |
| LOAM-SEED-INTEGRATION | P2 | lithoSpore | Wire `ceremony.entropy` output into Loam Certificate generation |
| TAP-BIOMETRIC-PROFILE | P3 | skunkBat | Build per-operator timing profile from ceremony rhythm data |

## Files Changed

| File | Change |
|------|--------|
| `beardog-tunnel/.../hid_transport.rs` | `TapTimingEntropy`, `CtapResponseWithTiming`, `read_ctaphid_ctap_response_timed()`, `CTAPHID_CANCEL`, `send_receive_timed()` |
| `beardog-tunnel/.../provider.rs` | `CeremonyTap`, `CeremonyResult` (with statistics methods), `ceremony_tap_sequence()` |
| `beardog-tunnel/.../fido2.rs` | `beardog.fido2.ceremony` handler, `ceremony_blake3_mix()`, 3 new tests |
| `beardog-tunnel/.../mod.rs` | Re-export `CeremonyResult`, `CeremonyTap`, `TapTimingEntropy`, `CtapResponseWithTiming` |

## Test Results

```
beardog-tunnel fido2 tests:  18 passed, 0 failed
beardog-tunnel solo_v2 tests: 15 passed, 0 failed
beardog workspace check:      0 warnings (release + fido2)
```
