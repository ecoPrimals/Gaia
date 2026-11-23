# nestGate — Wave 155i Deep Debt + CAS on ZFS

**Date**: Jul 29, 2026 | **Gate**: westGate | **From**: nestGate code team
**Status**: COMPLETE — ready for overwatch audit

---

## Summary

nestGate deep debt sweep complete. CAS on ZFS verified operational. All prior P0/P1 resolved.
Codebase at production quality: zero unsafe, zero panicking patterns, modern Rust 2024,
capability-based discovery, sovereignty-first architecture.

## What Shipped

| Item | Details |
|------|---------|
| CAS on ZFS | Verified live: 3,119 objects, 25.4TB pool, 1.56x compression |
| CLI evolution | `storage scan` env-aware; probe commands bypass JWT |
| Flaky test fix | Health check ZFS availability race eliminated |
| File renames | `production_placeholders` → `native_handlers`; `stub_helpers` → `procfs_helpers` |
| P1 ghost methods | `content.repo.*`/`content.mirror.*` removed from registry |
| systemd service | `ops/nestgate.service` — hardened, ZFS-dependent, socket-only |
| `.env.westgate` | Production environment aligned with live composition |

## Codebase Health

- **Tests**: 13,095+ passing, 0 failures
- **Clippy**: 0 warnings (`--workspace --all-features -D warnings`)
- **Format**: Clean
- **Unsafe**: Forbidden on all 20 crate roots
- **Production panics**: Zero (`unwrap`/`expect`/`todo!` only in tests/docs)
- **File sizes**: All < 800L (max: 760L)
- **Dependencies**: 156 crates, all pure Rust, deny.toml enforced
- **Edition**: Rust 2024 (env-shim stays 2021 deliberately)

## Live Composition State

```
westGate NEST ATOMIC LIVE
├── nestgate-westgate-tower-155f.sock (storage.sock symlink)
├── loamspine-westgate-tower-155f.sock (ledger.sock, permanence.sock)
├── rhizocrypt-westgate-tower-155f.sock (dag.sock)
├── songbird-westgate-tower-155f.sock (network-*.sock)
├── sweetgrass-westgate-tower-155f.sock (provenance.sock)
└── beardog-default.sock (security.sock)

ZFS: nestgate 25.4TB ONLINE, 5 datasets (cas/{objects,metadata,bulk}, data, snapshots)
Tiers: warm/nvme + cold/zfs (auto-detected via NESTGATE_SUBSTRATE_BASE)
```

## Blocked On

- **biomeOS BTSP session propagation** (P0) — signal graph executor needs composition broker
  for inter-primal trust at composition boundaries. Individual IPC works; orchestrated
  pipelines break at BTSP auth boundary.

## Next Work (after BTSP broker)

1. E2E `nest.ingest_dataset` signal graph validation (small PDB)
2. AlphaFold bulk ingestion (~1TB from northGate through pipeline)
3. Tier migration profiling NVMe→ZFS

## For Overwatch

nestGate has no remaining P0/P1. Codebase is clean, modern, and production-ready.
The P1 #7 in the blurb (`nestGate ghost methods`) was already resolved — commit `3ca3e1bc`.
Next evolution depends on biomeOS BTSP broker (eastGate/biomeOS team).
