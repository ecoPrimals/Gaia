# AAR: KNOWN_DEBT Gate Divergence — Wave 150t

**Date**: Jul 21, 2026
**Filed by**: ironGate hardware + deployment team
**For**: primalSpring code team (eastGate overwatch)
**Priority**: P1 — recurring cascade friction, blocks clean deployment validation

---

## Problem

`registry_all_rust_tier_pass` in `mod.rs` uses a single `KNOWN_DEBT` table
hardcoded for eastGate's deployment context. Every other gate that runs
`cargo test` hits assertion failures because scenarios pass/fail differently
depending on what's locally installed.

ironGate has manually recalibrated this table on **every cascade since Wave 137b**:
- Wave 137b (Jul 13)
- Wave 138b (Jul 14)
- Wave 139a (Jul 14)
- Wave 140a (Jul 15)
- Wave 142b (Jul 16)
- Wave 150o (Jul 20)
- Wave 150t (Jul 21)

**Seven times.** Each time upstream overwrites the fix on the next push.

---

## Root Cause

The debt table is gate-specific but stored as a universal constant:

```rust
const KNOWN_DEBT: &[(&str, u32)] = &[
    ("graphenegate-readiness", 14),    // eastGate: no aarch64 depot
    ("composition-access-control", 15), // both: composition wiring absent
];
```

On ironGate:
- `graphenegate-readiness` **passes clean** (0 failures) — deploy_pixel.sh is present locally
- `cascade-provenance-match` **fails** (2) — golgi checksums.toml format mismatch
- `bootstrap-readiness` **fails** (1) — depot path not configured

These are the inverse of eastGate's profile. Neither is wrong — they're
different deployment contexts.

---

## Proposed Fix

Branch on gate identity. The machinery already exists — `detect_local_gate()`
in `s_provenance_cross_gate.rs`, `GATE_NAME` env var, `.gate` file resolution.

```rust
fn gate_known_debt() -> &'static [(&'static str, u32)] {
    let gate = std::env::var("GATE_NAME")
        .ok()
        .or_else(|| resolve_gate_file())
        .unwrap_or_else(|| "unknown".to_owned());

    match gate.as_str() {
        "eastGate" => &[
            ("graphenegate-readiness", 14),
            ("composition-access-control", 15),
        ],
        "ironGate" => &[
            ("cascade-provenance-match", 2),
            ("bootstrap-readiness", 1),
            ("composition-access-control", 15),
        ],
        _ => &[
            ("composition-access-control", 15),
        ],
    }
}
```

Or: skip the assertion entirely for scenarios with non-zero actual failures
on unknown gates, and log instead of panic. The test should validate that
no *new* debt appears, not enforce a specific gate's exact failure profile.

---

## Impact of Not Fixing

- Every gate team that runs `cargo test` after a cascade must manually edit
  `KNOWN_DEBT` before they get green
- Those edits conflict with upstream on the next push
- Hardware/deployment teams waste cycles competing with the code team on the
  same 5 lines of Rust
- Gate teams stop running the full suite, reducing validation coverage

---

## Workaround (current)

ironGate overwrites the table each cascade, commits with a comment referencing
this AAR, and pushes. Upstream overwrites it back. Cycle repeats.
