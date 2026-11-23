# bearDog — Wave 138b: HIDRAW-REPORT-ID (P0) + HID-BLOCKING-IO (P1)

**Date**: Jul 14, 2026
**Commit**: `45fb3d1329a42ef8f4737e79f2192d134adaad0f`
**Status**: RESOLVED — both blockers fixed, SoloKey FIDO2 ceremony unblocked

---

## P0: HIDRAW-REPORT-ID — RESOLVED

**Root cause**: Linux hidraw `write()` requires the first byte to be the HID
report number. For FIDO2 devices (unnumbered reports), this must be `0x00`.
`beardog-hid` was sending the CTAPHID frame directly without this prefix,
causing the kernel to misinterpret the first data byte as a report ID.
The SoloKey never received valid CTAPHID frames.

**Fix**: Prepend `0x00` to every write in `LinuxHidDevice::write()`.
One-line semantic change in `crates/beardog-hid/src/linux.rs`.

## P1: HID-BLOCKING-IO — RESOLVED

**Root cause**: `beardog-hid` used `tokio::fs::File` with `O_NONBLOCK` for
hidraw device I/O. `tokio::fs::File` is designed for regular files, not
character devices — it doesn't properly handle non-blocking semantics for
device fds. The polling loop with `EAGAIN` retry was fragile.

**Fix**: Replaced with `std::fs::File` (blocking mode) behind explicit
`tokio::task::spawn_blocking` calls. This is the correct async pattern for
character device files that don't support `epoll`/`io_uring`. Also removed
the `libc` dependency from `beardog-hid` (now zero C dependencies).

## Also fixed

- Upstream example compile error (`test_ctap2_getinfo.rs`): unconditional
  `use beardog_hid::HidDevice` when `beardog-hid` is an optional dep
- `doc_markdown` clippy warnings in `fido2.rs` and `linux.rs`

## Verification

- `cargo check --all-targets`: PASS
- `cargo clippy --workspace --all-targets`: 0 warnings
- `cargo test --workspace`: 13,880 passed, 0 failed
- Pre-push hook (`cargo check --all-targets`): PASS

## Next steps (bearDog team)

1. Physical SoloKey test: MakeCredential → authenticate → entropy harvest
2. Loam Certificate from hardware credential
3. Pixel StrongBox ceremony (ADB, Titan M2)
