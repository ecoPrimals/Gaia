# cellMembrane Wave 155i — P0 Glibc Depot Target + P1 WireGuard DNS

**Date**: 2026-07-29 | **Author**: cellMembrane team (sporeGate)
**Wave**: 155i | **Priority**: P0 + P1 closed

---

## P0 CLOSED: Glibc Depot Target for GPU Primals

**Problem**: musl-static genomeBins cannot `dlopen` glibc Vulkan ICD.
Compute primals (barraCuda, coralReef) deployed on strandGate's RTX 3090
need `x86_64-unknown-linux-gnu` depot binaries alongside musl.

**Root cause**: `targets_for_primal()` only auto-appended gnu when manifest
`targets` was empty (default path). When `[build.<primal>].targets` was
explicitly set (e.g. `["x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"]`),
the gpu auto-add was bypassed.

**Fix**: `targets_for_primal()` now applies the GPU auto-add unconditionally
— if `source.gpu` is true and we're on an x86_64 builder, gnu is appended
regardless of whether targets came from manifest or default.

**To produce gnu binaries**:

```bash
# Option A: manifest already lists targets — gpu=true auto-adds gnu
plasmid.harvest --primal barracuda

# Option B: one-off CLI
plasmid.harvest --target x86_64-unknown-linux-gnu --primal barracuda
```

**Depot layout**: `plasmidBin/primals/x86_64-unknown-linux-gnu/barracuda`

## P1 CLOSED: WireGuard DNS in wg0 Template

**Problem**: wg-quick configs had no `DNS =` directive. Mesh hostname
resolution (e.g. `golgi.primals.eco`) required separate `/etc/hosts`
or external DNS configuration.

**Fix**: `WgConfig` struct gains an optional `dns` field.
`to_wg_quick()` emits `DNS = <ip>` in `[Interface]` when set.
`manifest_to_wg_config()` resolves the hub gate's mesh IP (golgiBody,
running knot-dns) as the DNS server. `wireguard.generate` dispatch
uses `DEFAULT_HUB_MESH_IP` as fallback.

Generated config now includes:
```ini
[Interface]
Address = 10.13.37.X/24
ListenPort = 51820
PrivateKey = <PRIVATE_KEY>
DNS = 10.13.37.1
```

## Health Metrics

- **Tests**: 1,223 (was 1,219 → +4 new)
- **Clippy**: 0 warnings
- **Fmt**: 0 drift
- **Files >800L**: 0

## Files Changed

| File | Change |
|------|--------|
| `plasmid/harvest.rs` | `targets_for_primal()` — gpu auto-add unconditional |
| `plasmid/harvest_tests.rs` | +2 tests for manifest+gpu and dedup |
| `cellmembrane-types/wireguard.rs` | `dns` field + render + 2 tests |
| `gate/wg.rs` | `manifest_to_wg_config()` resolves hub DNS |
| `dispatch/gate.rs` | `wireguard.generate` populates dns |
