# External Claim Convergence Standard

**Authority**: sporePrint team (eastGate overwatch)
**Status**: Ecosystem Standard — Wave 150x
**Date**: July 25, 2026
**Triggered by**: External credibility audit of primals.eco

---

## Purpose

Every public-facing surface — README, GitHub org profile, primals.eco page,
llms.txt — must converge to a single pipeline of truth. An external reviewer
found inconsistencies across surfaces that are individually correct but
collectively undermine credibility. This standard defines what convergence
means and what each team must do.

The canonical registry is `sporePrint/config.toml`. All external counts
must either:

1. Pull from this registry at build/render time, OR
2. State the measurement date and source explicitly

No manually entered ecosystem number should survive outside the registry.

---

## 1. Metric Pipeline

### The Problem

| Metric | Canonical (config.toml) | Found elsewhere |
|--------|------------------------|-----------------|
| Springs | 9 | "8 springs" (15+ pages, pre-fix) |
| Organizations | 4 | "Three organizations" (homepage, pre-fix) |
| WGSL shaders | 952 | 806 (architecture pages), 860 (barraCuda README), 914 (thesis) |
| Primals | 15 | "13 primals" (ECOSYSTEM_INVENTORY, pre-fix) |

### The Standard

**S1**: Every README that displays an ecosystem-wide metric (LOC, tests,
shaders, springs, primals) MUST include a `<!-- metrics: YYYY-MM-DD -->` comment
with the measurement date. Stale metrics (>30 days) should be flagged by CI.

**S2**: sporePrint pages MUST use `{{ total_stat() }}` or `{{ entity_stat() }}`
shortcodes for any number that appears in `config.toml`. Hardcoded numbers
are a bug.

**S3**: GitHub org profiles and repo descriptions SHOULD be updated when
`spore-validate refresh` detects >5% drift. The sporePrint team will
issue an impulse when this happens.

**S4**: Thesis chapters are historical snapshots. They carry the numbers
from their authoring wave and do not update. This is acceptable because
they are dated academic documents.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| barraCuda | Update README WGSL count from 860 → 952 (or pull from registry) | P1 |
| All primals | Add `<!-- metrics: YYYY-MM-DD -->` to README header | P2 |
| sporePrint | Issue impulse when `refresh` detects drift | Continuous |

---

## 2. Claim Qualification

### The Problem

Several claims on external surfaces are accurate in narrow scope but stated
absolutely. An external reviewer will interpret them at face value.

| Claim | Issue | Scoped Truth |
|-------|-------|-------------|
| `#![forbid(unsafe_code)]` everywhere | toadStool has 44 justified unsafe blocks | Forbidden by default; isolated to hardware-containment crates |
| "zero C dependencies" | `cc` crate exists in build graph (unused backend) | No C/C++/Fortran in runtime dependency chain |
| "any GPU" | Requires Vulkan drivers | Any GPU with Vulkan (tested: NVIDIA, AMD, Intel) |
| "replaces X" | Invites unfavorable feature-completeness comparison | Provides sovereign alternative for specific validated workflows |
| "production ready" | Pre-1.0 semver on some primals | Deployed and running on N gates; version M.N.P |

### The Standard

**S5**: Absolute claims (`all`, `every`, `zero`, `no`) MUST be followed by
their scope in the same sentence or paragraph. If the scope cannot fit,
the claim is too broad.

**S6**: "Replaces X" is acceptable in comparison tables where the context is
clear. It MUST NOT appear in meta descriptions, JSON-LD, or AI surface
files without qualification.

**S7**: `#![forbid(unsafe_code)]` claims MUST specify which crates. The
ecosystem-wide phrasing is:

> Unsafe code is forbidden by default (`#![forbid(unsafe_code)]` at crate roots)
> and isolated to narrowly scoped, safety-documented hardware-containment crates
> where required.

**S8**: "Zero C dependencies" MUST be stated as:

> No C/C++/Fortran libraries in the runtime dependency chain. Pure Rust
> cryptography (RustCrypto), pure Rust compression (`miniz_oxide`).

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| ecoPrimals org | Update GitHub org bio: scope the `#![forbid(unsafe_code)]` claim | P1 |
| biomeOS | Remove "A++ LEGENDARY" from external-facing README; use dual labeling | P1 |
| toadStool | Ensure README documents unsafe block count and justification summary | P2 |
| All READMEs | Audit for unscoped absolutes (`all`, `every`, `zero`, `no`) | P2 |

---

## 3. Maturity Labeling

### The Problem

Internal evolutionary grades (stadial, wave, "A++") appear on external
surfaces. External reviewers interpret these as audit results or maturity
claims. They are neither.

### The Standard

**S9**: Every public-facing README MUST include an **External Maturity** label
from this vocabulary:

| Label | Meaning |
|-------|---------|
| `experimental` | Under active development; API unstable |
| `research-ready` | Functioning with validated results; not feature-complete |
| `deployment-ready` | Tested on multiple gates; stable API; documented |
| `production-candidate` | Deployed in production; monitoring active |
| `externally-validated` | Used or reviewed by external parties |

**S10**: Internal evolutionary labels (stadial, wave grade, debt state) are
welcome in CHANGELOG, internal docs, and wateringHole AARs. They MUST NOT
appear in the first 20 lines of a public README.

**S11**: sporePrint's products page and Evidence Snapshot are the canonical
external maturity reference. Discrepancies between a repo's README maturity
label and sporePrint's label should be resolved by the team owning the repo.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| biomeOS | Add `External Maturity: deployment-ready` to README; move "A++ LEGENDARY" to CHANGELOG | P1 |
| All primals | Add maturity badge to README top-matter | P2 |
| sporePrint | Validate maturity labels during `spore-validate refresh` | P3 |

---

## 4. Inspectable Infrastructure

### The Problem

bearDog and skunkBat source remain "available on request" rather than
publicly inspectable. The identity, crypto, transport, and defensive-security
foundation is precisely the portion skeptical reviewers most need to inspect.
This creates a philosophical gap with the project's openness claims.

### The Standard

**S12**: Any primal whose capabilities are cited on primals.eco SHOULD have
its source code publicly available. If operational security requires delayed
publication, the README MUST state the timeline and rationale.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| Tower team | Evaluate timeline for bearDog + skunkBat public source publication | P2 |
| Tower team | If not publishing: add README explaining why and when (with timeline) | P2 |

---

## 5. Externalization Roadmap

### The Problem

The project has substantial commits, tests, documentation, and internal
validation, but public participation remains close to zero. The proof chain
is technically deep but socially only one node wide.

### The Standard

**S13**: The next phase should prioritize externalization over architecture.
Five milestones, in priority order:

1. **One canonical guideStone** that a stranger can download and verify in
   under 5 minutes. No setup beyond `rustup` and `git clone`.
2. **One public reproduction ledger** showing failures alongside successes.
   (lithoSpore's pseudoSpore braid can serve this role.)
3. **One spring used by a scientist** on data the ecosystem did not select.
4. **One institutional-quality technical report** with claims narrower than
   the evidence behind them.
5. **Complete publication** of foundational Tower source.

### Team Actions

| Team | Action | Priority |
|------|--------|----------|
| sporePrint + lithoSpore | Publish one-command guideStone verification path | P1 |
| All spring teams | Identify one external dataset for validation | P2 |
| sporePrint | Draft narrow-claim technical report | P3 |
| Tower team | Evaluate source publication timeline | P2 |

---

## Adoption

This standard is effective immediately. Teams should address P1 items within
the current wave. P2 items should be planned for the next wave. P3 items are
roadmap guidance.

sporePrint team will track convergence via `spore-validate refresh` drift
detection and periodic external review cycles.

**Companion AAR**: `aars/SPOREPRINT_CREDIBILITY_AUDIT_AAR_150x.md`
