# Wave 92: Peptidoglycan Depot Architecture

**Date**: 2026-06-07
**From**: eastGate overwatch
**To**: cellMembrane team

## Problem

golgiBody (inner + outer membrane) is a 2GB/10GB droplet with no Rust toolchain.
The `plasmid-pipeline.service` attempts `cargo build` and fails for every primal.
Currently, builds happen on dev stations (gates) and are pushed via
`membrane plasmid.refresh` — this works but is manual and gate-dependent.

## Architecture: Peptidoglycan as Shared Depot

```
                    ┌─────────────────────┐
                    │    peptidoglycan     │
                    │  (structural layer)  │
                    │                      │
                    │  Rust 1.96 + musl    │
                    │  79GB disk, 4GB RAM  │
                    │  /opt/plasmidBin/    │  ← canonical depot
                    │    primals/          │
                    │    checksums.toml    │
                    │    provenance.toml   │
                    └──────┬───────┬───────┘
                    VPC 10.116.0.4 │
                           │       │
              ┌────────────┘       └────────────┐
              │                                 │
    ┌─────────▼──────────┐           ┌──────────▼─────────┐
    │ golgiBody-inner    │           │ golgiBody-ext      │
    │ (inner membrane)   │           │ (outer membrane)   │
    │ LAN ← cascade      │           │ → GitHub mirrors   │
    │ serves primals     │           │ → Forgejo repos    │
    │ 10.116.0.3         │           │ [RELAY_PUBLIC]      │
    └────────────────────┘           └────────────────────┘

    Both read from peptidoglycan depot over VPC (sub-1ms)
```

## Two Build Paths

### Path A: Peptidoglycan Builds (VPS-local)

When the cascade detects drift (new commits in primal repos), peptidoglycan
builds the updated binaries locally. It has Rust 1.96 and 4GB RAM.

```
cascade detects drift → peptidoglycan cargo build --release --target x86_64-unknown-linux-musl
                       → binary staged in /opt/plasmidBin/primals/
                       → checksums.toml + provenance.toml updated
                       → golgiBody inner/outer membrane serve new binary
```

**Prerequisite**: `rustup target add x86_64-unknown-linux-musl` on peptidoglycan
(one-time setup — currently only has `gnu` target).

**Tradeoff**: 4GB RAM may be tight for large primals (songBird, biomeOS).
Monitor OOM. Can set `CARGO_BUILD_JOBS=1` to reduce peak memory.

### Path B: Gate-Pushed Builds (cascade-back)

When a gate (dev station) pushes code, the cascade should carry the fresh
ecobin with it. The gate builds locally (full toolchain, 32-128GB RAM),
and the binary is pushed upstream as part of the cascade flow.

```
gate: cargo build --release --target x86_64-unknown-linux-musl
gate: membrane plasmid.harvest  (builds + checksums + provenance)
gate: git push plasmidBin       (checksums + provenance to repo)
gate: membrane plasmid.refresh  (binaries to /opt/membrane/ on golgiBody)
     ─ OR ─
gate: cascade pushes binary to peptidoglycan depot directly
```

**This is the preferred path for large primals** (songBird 17MB, biomeOS 16MB)
where gate hardware is 10-30x more capable than pepti.

## Cascade Integration

The temporal cascade should evolve to support **build-carrying cascades**:

1. **Drift detection in cascade**: When `temporal.cascade` syncs a primal repo
   and detects the HEAD has moved, it checks if the depot binary is stale.

2. **Build signal**: If stale, the cascade emits a build signal:
   - On peptidoglycan: build locally (Path A)
   - On gates: signal back that a `plasmid.harvest` + `plasmid.refresh` is needed

3. **Binary push on cascade**: Gates that build should push the binary as part
   of their cascade cycle. The `membrane temporal.cascade` command could accept
   a `--with-harvest` flag that runs `plasmid.harvest` after sync, then
   `plasmid.refresh` to push binaries upstream.

4. **Depot freshness in cascade output**: The cascade report should include
   depot status (current/drifted count) alongside repo parity.

## Storage Model

Peptidoglycan owns the canonical depot at `/opt/plasmidBin/`:

```
/opt/plasmidBin/
├── checksums.toml        # BLAKE3 per-target checksums
├── provenance.toml       # commit + version + builder metadata
├── primals/
│   └── x86_64-unknown-linux-musl/
│       ├── beardog
│       ├── songbird
│       ├── biomeos
│       └── ...
└── sources.toml          # upstream repo manifest
```

golgiBody inner and outer membranes read from pepti over VPC. Two options:

- **NFS/SSHFS mount**: peptidoglycan exports `/opt/plasmidBin` → golgiBody mounts it
- **rsync on trigger**: golgiBody pulls from pepti after build completes

NFS is simpler (zero-copy reads) but adds a dependency. rsync is more resilient.

## Immediate Actions (cellMembrane)

1. **SSH trust**: golgiBody → peptidoglycan SSH host key trust (currently fails)
2. **musl target**: `rustup target add x86_64-unknown-linux-musl` on peptidoglycan
3. **Fix pipeline**: `plasmid-pipeline.service` on golgiBody should NOT `cargo build`.
   Replace with: fetch from pepti depot OR accept gate-pushed binaries.
4. **Depot symlink on pepti**: ensure `/opt/ecoPrimals/infra/plasmidBin` → `/opt/plasmidBin`
   (same pattern we fixed on golgiBody)

## Long-term Evolution

- Gates push ecobins on cascade → peptidoglycan stores → both membranes serve
- `temporal.cascade --with-harvest` becomes the standard workflow
- Peptidoglycan can do fallback builds for primals that drift without a gate push
- Binary provenance enables genetic sequence analysis of ecobin evolution
- DigitalOcean Spaces or similar could serve as off-VPC backup depot
