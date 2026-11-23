# cellMembrane — Wave 82c plasmidBin Ownership Sprint

**Date**: 2026-06-06  
**Gate**: ironGate  
**Context**: plasmidBin ownership transfer from primalSpring → cellMembrane

---

## Completed

### 1. `plasmid.refresh` Command (P1)

New `membrane plasmid.refresh` command added to the membrane CLI:

```
membrane plasmid.refresh [--primal NAME] [--source-dir DIR] [--dry-run]
```

Flow: locate local binary → SCP to VPS as `{name}.new` → `chmod+mv` atomic
replace → `systemctl restart {unit}` → report.

- Derives primal list from service registry (no hand-maintained list)
- Resolves source from `--source-dir`, `PLASMIDBIN_STAGING`, or default staging
- Uses `ServicePaths` for install paths
- Supports `--dry-run` for safe preview

### 2. `plasmid.harvest` Command (P1 — Wave 83)

New `membrane plasmid.harvest` command for zero-touch binary building:

```
membrane plasmid.harvest [--primal NAME] [--depot DIR] [--force] [--dry-run]
```

Flow: read sources.toml → compare HEAD vs provenance.toml → clone changed →
cargo build musl static → strip → BLAKE3 checksum → stage to depot →
update checksums.toml + provenance.toml.

### 3. `plasmid.pipeline` Command (P1 — Wave 83)

End-to-end zero-touch: `harvest → refresh → alive` in one command:

```
membrane plasmid.pipeline [--primal NAME] [--dry-run]
```

### 4. SCP Transport (`ssh.rs`)

Added `scp_to()` function for file transfer to VPS, matching the existing
`exec()` pattern (respects `ShadowConfig` timeout and host).

### 5. `sources.toml` Review

All 13 primals + sourDough + esotericWebb are registered. Tag pattern is
consistent (`v{version}`). Private repos (bearDog, skunkBat) properly marked.
`build_args` correct for workspace crates (biomeos → `-p biomeos-unibin`,
skunkbat → `-p skunk-bat-server`).

### 6. UDS Health Probe Diagnosis (squirrel + petaltongue)

**Finding**: Both primals accept UDS connections and listen on STREAM sockets
(`ss -lxp` confirms PID binding). However, they never respond to any JSON-RPC
message (newline-delimited, length-prefixed, HTTP-wrapped — all tested).

**Root cause**: The upstream primal code has separate TCP and UDS server loops.
The UDS loop accepts connections but doesn't dispatch received data through
the JSON-RPC handler. The TCP handler works fine.

**Status**: Wave 83 confirms this is RESOLVED upstream by primal teams.

---

## Remaining (P2 — next waves)

- `plasmid.deploy` — Absorb full `deploy_membrane.sh deploy` flow into Rust CLI
- CI workflow wiring (check-updates.yml, harvest.yml) for Forgejo Actions
- Peptidoglycan self-refresh timer (VPS-side poll of depot freshness)

---

## Gate Status

- **13/13 primals ALIVE on VPS** (all UDS health confirmed Wave 83)
- **mesh.primal.eco** operational, TLS + proxy
- **All 5 domains** serving with sovereign TLS
- **plasmid.pipeline** ready for zero-touch binary refresh cycles
- **226 tests**, zero clippy, zero debt markers
