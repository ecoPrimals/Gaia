# SOLOKEY-PHYSICAL Hardware Test — After Action Review

**Wave**: 138b | **Date**: Jul 14, 2026 | **Operator**: eastGate overwatch
**Status**: PARTIAL — Protocol handshake proven, MakeCredential response blocked at HID layer

---

## Mission

First physical hardware trust ceremony in the ecosystem. SoloKey Solo 2 plugged into
sporeGate NUC, validate bearDog FIDO2 IPC end-to-end: discover → register → entropy harvest.

## What Worked

### 1. Device Discovery (PASS)

`beardog.fido2.discover` via IPC correctly enumerated the SoloKey:

```
Solo 2 Security Key (VID:1209, PID:beee) @ /dev/hidraw4
```

- `beardog-hid` pure Rust discovery: scans `/dev/hidraw*`, reads `/sys/class/hidraw/*/device/uevent`
- ACL permissions correct: `crw-rw----+` with `user:sporegate:rw-` via udev rules
- Only 1 hidraw interface for the SoloKey (no multi-interface ambiguity)

### 2. CTAPHID_INIT Handshake (PASS)

Protocol handshake completes successfully every time. Confirmed via strace:

```
write(14, "\xff\xff\xff\xff\x86\x00\x08[nonce]...", 64) = 64   # INIT request
read(14, ...)  = -1 EAGAIN                                       # 1 retry
read(14, "\xff\xff\xff\xff\x86\x00\x11[nonce][CID]...", 64) = 64  # INIT response
```

Decoded INIT response:
- Channel ID assigned: `0x00000006`
- CTAPHID protocol version: `0x02`
- Device firmware: `2.3.196`
- Capabilities: `0x05` = `CAPABILITY_WINK | CAPABILITY_CBOR`

The SoloKey supports CTAP2 CBOR commands. Channel allocation is healthy.

### 3. MakeCredential Write (PASS — bytes delivered)

CTAP2 MakeCredential command sent correctly via CTAPHID_CBOR (0x90):

```
write(14, "\x00\x00\x00\x06\x90\x00\xd0\x01\xa5...", 64) = 64   # init packet
write(14, "\x00\x00\x00\x06\x00...", 64) = 64                    # continuation 0
write(14, "\x00\x00\x00\x06\x01...", 64) = 64                    # continuation 1
write(14, "\x00\x00\x00\x06\x02...", 64) = 64                    # continuation 2
```

4 packets, 208 bytes CBOR payload. CID matches allocated channel. Command byte is
`0x01` (CTAP2_MAKE_CREDENTIAL). CBOR structure includes rp_id, user, pubKeyCredParams,
options (rk=true, up=true).

### 4. EAGAIN Retry Infrastructure (PASS)

The EAGAIN retry loop works correctly — 150 attempts × 200ms = 30 seconds of user
presence wait. Confirmed via debug logs:

```
CTAPHID read attempt 1: EAGAIN (waiting for user touch)
...
CTAPHID read attempt 150: EAGAIN (waiting for user touch)
CTAPHID timeout waiting for response
```

### 5. Build System (PASS)

- `cargo build --features fido2` compiles cleanly
- Feature flag chain: `fido2` → `beardog-security/fido2` + `beardog-tunnel/ctap2` + `beardog-hid`
- All 30 FIDO2 unit tests pass (mocked CTAP2 transport)
- Android cross-compile: clean (graceful no-op on `aarch64-linux-android`)

---

## What Did Not Work

### MakeCredential Response: SoloKey Silent (FAIL — P0)

After receiving 4 CTAPHID_CBOR packets (208 bytes of valid CTAP2 MakeCredential CBOR),
the SoloKey sends **nothing**. No keepalive (0xBB), no error (0xBF), no CBOR response.
150 read attempts over 30 seconds — all return EAGAIN.

**Strace confirms:**
- All writes return `= 64` (kernel accepted the data)
- All reads return `= -1 EAGAIN` (no data from device)
- The SoloKey LED did **not** blink (user was physically present and touching)

---

## Root Cause Analysis

### Bug Found and Fixed: Wrong CTAPHID Command Byte

**Original code**: Used `CTAPHID_MSG (0x83)` for CTAP2 commands.
**Correct**: CTAP2 CBOR commands must use `CTAPHID_CBOR (0x90)`.

Per FIDO CTAPHID spec:
- `0x83` = `CTAPHID_MSG` — CTAP1/U2F APDU messages
- `0x90` = `CTAPHID_CBOR` — CTAP2 CBOR commands

**Fix applied** (uncommitted): Added `Cbor = 0x90` variant, changed `send_ctaphid_message`
to use it, updated response reader to accept both `0x90` and `0x83`.

**Result after fix**: Still EAGAIN timeout. The command byte fix was necessary but
insufficient. The SoloKey still does not respond.

### Remaining Suspect: Linux hidraw Report ID Prefix

The HID report descriptor for the SoloKey confirms **no report IDs** are defined:

```
06 d0f1    Usage Page (FIDO Alliance, 0xF1D0)
09 01      Usage (CTAPHID, 0x01)
a1 01      Collection (Application)
  09 03    Usage (Input)
  75 08    Report Size (8)
  95 40    Report Count (64)
  81 08    Input (64 bytes, no report ID)
  09 04    Usage (Output)
  75 08    Report Size (8)
  95 40    Report Count (64)
  91 08    Output (64 bytes, no report ID)
c0         End Collection
```

Linux hidraw `write()` semantics (from kernel source `drivers/hid/hidraw.c`):

> "The first byte of the buffer is the report number. For devices without
> numbered reports, set the first byte to 0x00."

Our code writes 64 bytes raw (no report ID prefix). The kernel interprets `packet[0]`
(which is 0xFF for broadcast CID during INIT, or the CID first byte for CBOR) as the
report ID.

**Paradox**: CTAPHID_INIT works despite this. Possible explanation:
- INIT uses broadcast CID `0xFF FF FF FF` — kernel may pass report_id=0xFF through
  as a vendor report, and the SoloKey's USB stack is lenient with INIT
- MakeCredential uses CID `0x00 00 00 06` — kernel sees report_id=0x00 and **strips it**,
  shifting the remaining 63 bytes, garbling the packet

This remains the **primary suspect** and needs testing.

### Additional Suspects (Lower Probability)

| Suspect | Likelihood | Evidence |
|---------|-----------|----------|
| tokio async I/O + O_NONBLOCK on hidraw | Medium | epoll may not wake on hidraw data ready. Current code busy-polls (works) but the non-blocking mode could affect kernel USB transaction queuing |
| SoloKey firmware quirk with long CBOR | Low | 208 bytes spans 4 packets. Firmware might have a framing issue with multi-packet CBOR |
| clientDataHash all-zeros | Very Low | Authenticators don't validate clientDataHash content |
| USB hub/power issue | Very Low | INIT works consistently, so USB link is healthy |

---

## Ad-Hoc Fixes Applied During Session

### 1. CTAPHID EAGAIN Retry (Wave 138b — committed `ae47557c9`)

- `read_ctaphid_ctap_response`: retry on EAGAIN with 200ms sleep, 150 attempts (30s)
- `ctaphid_init`: retry on EAGAIN with 50ms sleep, 20 attempts (1s)
- `MAX_KEEPALIVE_ATTEMPTS`: 32 → 150

### 2. CTAPHID_CBOR Command Byte (This session — uncommitted)

- Added `Cbor = 0x90` to `CtapHidCommand` enum
- Changed `send_ctaphid_message` to use `Cbor` instead of `Msg`
- Response reader accepts both `0x90` and `0x83`

---

## What Needs to Be Written (Parity Gaps)

### P0: HID Report ID Prefix (`HIDRAW-REPORT-ID`)

**Owner**: bearDog team (beardog-hid crate)
**Location**: `beardog-hid/src/linux.rs` → `LinuxHidDevice::write()`

The `write()` method must prepend a `0x00` report ID byte for devices without numbered
reports. This is the standard Linux hidraw convention and is how libhidapi does it.

```rust
// Current (broken for devices without report IDs):
self.device.write_all(report).await

// Needed:
let mut buf = Vec::with_capacity(1 + report.len());
buf.push(0x00); // report ID for devices without numbered reports
buf.extend_from_slice(report);
self.device.write_all(&buf).await
```

Note: This changes the wire format. `HID_PACKET_SIZE` (64) is the CTAPHID payload size.
The actual hidraw write becomes 65 bytes (1 report ID + 64 payload). Read is unaffected
(kernel strips the report ID on input for devices without numbered reports).

This should be gated on a `has_report_id` flag read from the HID report descriptor,
but for FIDO2 devices (which never use report IDs), unconditionally prepending 0x00 is safe.

### P1: Blocking I/O for HID Operations (`HID-BLOCKING-IO`)

**Owner**: bearDog team (beardog-hid crate)
**Location**: `beardog-hid/src/linux.rs` → `LinuxHidDevice::open()`

Current: `O_NONBLOCK` + tokio async read/write. This creates two problems:
1. Read returns EAGAIN immediately, requiring busy-poll retry loops
2. epoll readiness notifications may not work correctly for hidraw devices

Recommended: Open without `O_NONBLOCK`, wrap read/write in `tokio::task::spawn_blocking`.
This lets the kernel block until data is available, which is correct for HID devices
that need user presence timeouts.

```rust
// Blocking open:
let device = OpenOptions::new().read(true).write(true).open(path).await?;

// Blocking read wrapped for async:
let n = tokio::task::spawn_blocking(move || {
    std::io::Read::read(&mut file, &mut buf)
}).await??;
```

### P2: CTAPHID_PING Diagnostic (`CTAPHID-PING-DIAG`)

**Owner**: bearDog team
**Location**: `beardog-tunnel/src/tunnel/hsm/solo_v2/hid_transport.rs`

Add a `CTAPHID_PING` (0x81) diagnostic command that sends data and expects it echoed back.
This would allow testing the raw HID transport without requiring user presence or CBOR
parsing, isolating HID I/O issues from CTAP2 protocol issues.

### P2: GetInfo Before MakeCredential (`CTAP2-GETINFO-FIRST`)

**Owner**: bearDog team
**Location**: `beardog-tunnel/src/tunnel/hsm/solo_v2/provider.rs`

Before attempting MakeCredential, issue CTAP2 GetInfo (command 0x04). This:
1. Validates the CTAPHID_CBOR round-trip works
2. Confirms the device supports the requested algorithms
3. Reads the device's max credential count, pin protocol, etc.
4. Does NOT require user presence (good for diagnostics)

---

## Hardware Interaction Trace (Full Protocol Walk)

```
1. USB enumeration
   SoloKey Solo 2 on Bus 007 Device 002 (VID:1209, PID:BEEE)
   Kernel creates /dev/hidraw4 (hid-generic driver)
   udev rule sets ACL for user:sporegate:rw-

2. Discovery (beardog.fido2.discover)
   Scan /dev/hidraw* → /sys/class/hidraw/*/device/uevent
   Parse HID_ID=0003:00001209:0000BEEE
   Report: Solo 2 at /dev/hidraw4 ✓

3. Device open
   open("/dev/hidraw4", O_RDWR|O_NONBLOCK|O_CLOEXEC) = fd 14

4. CTAPHID_INIT (channel allocation)
   WRITE fd14: [FF FF FF FF] [86] [00 08] [nonce×8] [pad×49]  = 64 bytes
   READ  fd14: EAGAIN ×1, then:
         [FF FF FF FF] [86] [00 11] [nonce×8] [00 00 00 06] [02 02 03 C4] [05]
   → Channel ID: 0x00000006
   → Capabilities: WINK | CBOR

5. CTAP2 MakeCredential (CTAPHID_CBOR)
   WRITE fd14: [00 00 00 06] [90] [00 D0] [CBOR×57]  = 64 bytes (init)
   WRITE fd14: [00 00 00 06] [00] [CBOR×59]           = 64 bytes (cont 0)
   WRITE fd14: [00 00 00 06] [01] [CBOR×59]           = 64 bytes (cont 1)
   WRITE fd14: [00 00 00 06] [02] [CBOR×33 + pad×26]  = 64 bytes (cont 2)
   Total payload: 208 bytes CBOR

   CBOR structure:
   0x01 (MakeCredential) {
     1: clientDataHash (32 bytes, zeros — ceremony placeholder),
     2: {id: "primals.eco", name: "primals.eco"},
     3: {id: "primals.eco:ceremony-test", name: ..., displayName: ...},
     4: [{type: "public-key", alg: -7 (ES256)}],
     7: {rk: true, up: true}
   }

   READ  fd14: EAGAIN ×150 (30 seconds) → TIMEOUT
   SoloKey LED: did NOT blink
   User presence: available but not solicited by device

6. Conclusion: MakeCredential never reached the authenticator logic.
   CTAPHID framing or HID report ID prefix is garbling the payload.
```

---

## Future Vision: SoloKey in NUCLEUS Deployments

The SoloKey represents a **hardware root of trust** that can anchor any NUCLEUS composition:

```
USB Hub (per NUCLEUS node)
├── SoloKey Solo 2 — FIDO2 root credential + entropy source
├── Akida NPU — neuromorphic inference
└── Compute (NUC/SBC/embedded)
    └── NUCLEUS composition
        ├── bearDog (HSM + FIDO2 IPC)
        ├── songBird (gateway routing)
        ├── cellMembrane (cascade + signing)
        └── ...primals
```

Once `HIDRAW-REPORT-ID` is fixed and MakeCredential succeeds:

1. **Loam Certificate**: bearDog mints a certificate anchored to the SoloKey credential.
   The credential_id proves the node was physically present at ceremony time.

2. **Hardware Entropy**: `beardog.fido2.entropy` mixes SoloKey signature nonce with OS RNG
   for Tier 2 hardware entropy, seeding all downstream key material.

3. **Attestation Chain**: SoloKey → bearDog credential → Loam cert → node identity → mesh trust.
   Every NUCLEUS node gets a hardware-attested identity.

4. **USB Topology as Deployment Primitive**: A standard NUCLEUS USB kit (SoloKey + NPU + compute)
   can be provisioned by plugging in and running the ceremony. No manual key exchange.

---

## Files Changed

| File | Status | Change |
|------|--------|--------|
| `beardog-tunnel/.../hid_transport.rs` | Uncommitted | `Cbor = 0x90` variant, use CTAPHID_CBOR for sends, accept both in reads |
| `wateringHole/handoffs/SOLOKEY_PHYSICAL_TEST_AAR_138b.md` | New | This document |

## Carried Items

| ID | Priority | Owner | Description |
|----|----------|-------|-------------|
| HIDRAW-REPORT-ID | P0 | bearDog | Prepend 0x00 report ID in `LinuxHidDevice::write()` |
| HID-BLOCKING-IO | P1 | bearDog | Replace O_NONBLOCK + busy-poll with blocking I/O + spawn_blocking |
| CTAPHID-PING-DIAG | P2 | bearDog | Add CTAPHID_PING diagnostic for transport-level testing |
| CTAP2-GETINFO-FIRST | P2 | bearDog | Issue GetInfo before MakeCredential for capability validation |
| SOLOKEY-CEREMONY-E2E | P0 (blocked) | bearDog | Complete register → authenticate → entropy → Loam cert ceremony |
