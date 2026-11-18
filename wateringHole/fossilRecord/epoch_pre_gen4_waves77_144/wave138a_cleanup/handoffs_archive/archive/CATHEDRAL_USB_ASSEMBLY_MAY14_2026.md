# CATHEDRAL USB Assembly — Hypogeal Cotyledon Pipeline

**Date**: May 14, 2026
**From**: CATHEDRAL (lithoSpore)
**For**: primalSpring, projectNUCLEUS, infrastructure
**Implements**: `LITHOSPORE_USB_DEPLOYMENT.md`

---

## Summary

lithoSpore now has a complete USB assembly pipeline. Running
`scripts/assemble-usb.sh` on ironGate produces a self-sufficient
~16GB USB directory matching the `LITHOSPORE_USB_DEPLOYMENT.md` spec.

The first complete chunk of Foundation — all data, primals integration
points, and validation tooling packaged for offline deployment.

---

## What Was Built

### `scripts/assemble-usb.sh` — 9-step orchestrator

```bash
./scripts/assemble-usb.sh                           # Full assembly
./scripts/assemble-usb.sh --target /media/lithoSpore # To USB mount
./scripts/assemble-usb.sh --dry-run                  # Preview
```

Steps: directory tree → root files → biomeOS → binaries → data fetch →
Python embedding → notebooks → Foundation targets → BLAKE3 manifest.

### USB Root Entry Points (`artifact/usb-root/`)

| File | Purpose |
|------|---------|
| `validate` | Tier 2 → Tier 1 → HTML dispatch with `--tier` override |
| `refresh` | Data re-fetch via `litho refresh` (requires network) |
| `spore.sh` | biomeOS ColdSpore entry — detects orchestrator or falls back to `./validate` |
| `.biomeos-spore` | JSON marker: `hypogeal-cotyledon` class, version, entry points |

### biomeOS Integration

| File | Purpose |
|------|---------|
| `biomeOS/tower.toml` | Spore composition: Tier 1/2/3 capabilities, optional primal requirements |
| `biomeOS/graphs/lithoSpore_validation.toml` | 4-phase validation flow: data-integrity → validate → provenance → artifact-register |

### `build-artifact.sh` Evolution

Added `--flat DIR` mode: copies binaries to flat `bin/` directory (USB
layout) instead of `bin/{arch}/static/` (dev layout).

---

## USB Layout Produced

```
/media/lithoSpore/
├── .biomeos-spore          ← biomeOS detection marker
├── .family.seed            ← genetics lineage
├── spore.sh                ← biomeOS entry
├── validate                ← main entry: Tier 1/2 dispatch
├── refresh                 ← data freshness
├── liveSpore.json          ← append-only provenance
├── data_manifest.toml      ← BLAKE3 inventory
├── biomeOS/                ← tower + validation graph
├── bin/                    ← 8 ecoBin binaries (flat)
├── artifact/data/          ← 7 LTEE datasets
├── projectFOUNDATION/targets/ ← projectFOUNDATION validation targets
└── notebooks/              ← Python baselines + HTML
```

---

## Upstream Dependencies for Full Deployment

| Item | Status | Owner |
|------|--------|-------|
| musl cross-compilation targets | Ready (install via `rustup target add`) | Local |
| Data fetching (NCBI/Dryad) | Ready (5 fetch scripts wired) | Local |
| python-build-standalone | Assembly downloads automatically | External |
| genomeBin primal packaging for Tier 3 | Not yet available | projectNUCLEUS + plasmidBin |
| sporePrint publishing pipeline | `notify-sporeprint.yml` dispatch exists | sporePrint + Channel 3 |

---

## Verification

```
cargo check      — PASS
cargo test       — all PASS
cargo clippy     — zero warnings
assemble-usb.sh --dry-run — correct tree output
assemble-usb.sh --skip-python --skip-fetch --skip-build — structural staging verified
```
