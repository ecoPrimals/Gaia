# Wave 54: Provenance-Elevated Checksums + Braid Integration

**Date**: 2026-05-27
**Author**: primalSpring / eastGate
**Scope**: plasmidBin (infra), primalSpring (consumer), all downstream springs

---

## Summary

plasmidBin checksums have been elevated from raw `blake3(stripped_binary_bytes)` to a
provenance-aware composite fingerprint. Two identical binaries from different commits or
different timestamps now produce different provenance hashes. sweetGrass braids are emitted
post-harvest when the provenance trio is available.

This lays the groundwork for cellMembrane Forgejo sovereignty — provenance records will
track which forge produced each binary.

## What Changed

### Layer 1: Content Hash (unchanged)

`checksums.toml` — raw `blake3(stripped_binary_bytes)`. This is what `fetch.sh` and
`b3sum` verify. **No changes.** Backward compatible.

### Layer 2: Provenance Fingerprint (new)

`provenance.toml` — composite fingerprint per primal × target triple:

```toml
[primals.toadstool."x86_64-unknown-linux-musl"]
content_hash = "6685834c..."
source_commit = "3e851517c..."
source_repo = "ecoPrimals/toadStool"
build_timestamp = "2026-05-27T11:45:46Z"
rustc_version = "1.87.0"
target = "x86_64-unknown-linux-musl"
provenance_hash = "a1b2c3d4..."
braid_id = "urn:braid:uuid:..."   # when sweetGrass was available
```

`provenance_hash = blake3("plasmidbin-provenance-v1" || content_hash || source_commit || build_timestamp || rustc_version || target)`

Same code + different timestamp → different fingerprint.
Same bytes + different commit → different fingerprint.
Same everything + different compiler → different fingerprint.

### Layer 3: sweetGrass Braid (provenance record)

After each harvest, `braid.create` is called via sweetGrass UDS. If sweetGrass is
unavailable (CI hosts without NUCLEUS), a `.braid-pending.json` sidecar is written
for later weaving. Braid IDs are stored in `provenance.toml`.

## Files Changed (plasmidBin)

| File | Change |
|------|--------|
| `crates/plasmidbin-types/src/provenance.rs` | **NEW** — `ProvenanceFile`, `ProvenanceEntry`, `BuildSidecar`, `compute_provenance_hash()`, validation |
| `crates/plasmidbin-types/src/lib.rs` | Registered `provenance` module |
| `crates/plasmidbin-types/Cargo.toml` | Added `serde_json`, `blake3` deps |
| `crates/plasmidbin/src/cmd/build.rs` | Writes `.provenance.json` sidecar next to staged binary |
| `crates/plasmidbin/src/cmd/harvest.rs` | Reads sidecars, computes provenance_hash, writes `provenance.toml`, emits braid.create |
| `crates/plasmidbin/src/cmd/verify_provenance.rs` | **NEW** — `verify-provenance` subcommand |
| `crates/plasmidbin/src/cmd/validate.rs` | Includes provenance.toml in routine validation |
| `crates/plasmidbin/src/cmd/mod.rs` | Registered `VerifyProvenance` subcommand |
| `.github/workflows/auto-harvest.yml` | `provenance.toml` committed + uploaded as release asset |

## Files Changed (primalSpring)

| File | Change |
|------|--------|
| `tools/fetch_primals.sh` | Downloads `provenance.toml`, `--verify-provenance` flag |
| `ecoPrimal/src/validation/scenarios/s_deployment_pipeline.rs` | Stage 2.5: Provenance structural validation |
| `scripts/validate_release.sh` | Layer 2 provenance in plasmidBin health gate |
| `scripts/build_ecosystem_genomeBin.sh` | Prefers provenance-aware Rust CLI, runs verify-provenance |
| `tools/desktop_nucleus.sh` | Validate mode checks Layer 1+2 |
| `tools/gen_seed_fingerprints.sh` | Enriches output with source_commit from provenance.toml |

## Impact on Downstream Springs

**No action required** for Wave 54. `checksums.toml` is unchanged. `fetch.sh` and
`b3sum` verification work exactly as before.

**Optional upgrade**: Springs that use `fetch_primals.sh` (copied from primalSpring)
can adopt the updated version to get Layer 2 provenance download + verification.

**Future (cellMembrane Forgejo)**: `provenance.toml` will gain a `forge` field.
braids from GitHub and Forgejo can be cross-referenced via sweetGrass.

## Verification

```bash
# Layer 1 (unchanged): byte integrity
b3sum primals/x86_64-unknown-linux-musl/beardog

# Layer 2 (new): provenance chain
plasmidbin verify-provenance --root .

# Layer 2 + commit check (network):
plasmidbin verify-provenance --root . --check-commits

# Layer 2 + braid check (sweetGrass UDS):
plasmidbin verify-provenance --root . --check-braids
```

## Test Results

- plasmidBin: 24/24 tests pass (4 new provenance tests), 0 warnings, `validate` 101/101
- primalSpring: `s_deployment_pipeline` 3/3 pass (Stage 2.5 gracefully skips when provenance.toml absent)
- All shell scripts pass `bash -n` syntax check
