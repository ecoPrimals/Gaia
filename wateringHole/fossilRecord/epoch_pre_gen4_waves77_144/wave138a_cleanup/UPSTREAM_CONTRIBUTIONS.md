# Upstream Contributions — ecoPrimals to the Wider Rust Ecosystem

**Date**: March 9, 2026  
**Type**: Ecosystem Strategy  
**Status**: Active — First candidate identified, more planned  
**Authority**: WateringHole Consensus

---

## Philosophy

ecoPrimals follows a natural pattern: **evolve internally, then contribute upstream**.

The same cycle we use with springs (springs find gaps → primals solve them →
springs validate → improvements flow back) applies to the wider Rust ecosystem.
When a primal solves a deep problem, the solution often has value far beyond
ecoPrimals. Extracting it as a standalone crate lets us:

1. **Give back** to the Rust community that we build on
2. **Get wider testing** — thousands of users find bugs faster than we do alone
3. **Reduce maintenance** — if the crate gains traction, others contribute
4. **Lean upstream** — maybe one day the crate becomes so popular we depend on
   it as an external dependency, completing the circle

This is the same evolve-and-lean pattern we use with the springs, but applied to
the entire Rust world. The standards our primals evolve might end up in a popular
crate that we then pull back in as a dependency.

---

## Contribution Candidates

### 1. `proc-sysinfo` (from `toadstool-sysmon`)

**Origin**: toadStool S137 (March 9, 2026)  
**Maturity**: Production-tested in toadStool workspace  
**License for upstream**: MIT OR Apache-2.0 (dual-license for maximum adoption)

**What it does**: Pure Rust Linux system monitoring via `/proc` filesystem parsing.
CPU count/brand/usage, memory info, disk usage (via `rustix` `statvfs`), network
stats, process info, load average.

**Why it's valuable to the community**:
- `sysinfo` is the dominant crate but pulls `libc` via FFI for many operations
- Many projects just need basic Linux metrics and don't need Windows/macOS
- Zero C compilation step = cross-compilation friendly
- `#![deny(unsafe_code)]` — fully safe Rust
- No mega-object pattern — individual query functions (CPU, memory, etc.)
- Only dependency: `rustix` (for `statvfs`), everything else is `std::fs`

**Upstream work needed**:
- [ ] Rename from `toadstool-sysmon` to `proc-sysinfo` (or `linux-sysmon`)
- [ ] Remove AGPL-3.0 license header, apply MIT/Apache-2.0 dual license
- [ ] Remove workspace inheritance in Cargo.toml (standalone versioning)
- [ ] Add comprehensive README with benchmarks vs sysinfo
- [ ] Add `#![doc = include_str!("../README.md")]` for docs.rs
- [ ] Ensure API is generic (no ecoPrimals-specific concepts)
- [ ] Add CI matrix: x86_64, aarch64, armv7, riscv64
- [ ] Publish to crates.io
- [ ] Announce on r/rust, This Week in Rust

**API surface (ready today)**:
```rust
// CPU
pub fn cpu_count() -> usize;
pub fn cpu_brand() -> Result<String, SysmonError>;
pub fn cpu_usage() -> Result<f32, SysmonError>;
pub fn per_cpu_usage() -> Result<Vec<f32>, SysmonError>;

// Memory
pub fn memory_info() -> Result<MemoryInfo, SysmonError>;

// Disk
pub fn disk_usage() -> Result<Vec<DiskInfo>, SysmonError>;

// Network
pub fn network_stats() -> Result<Vec<NetworkInterface>, SysmonError>;

// Process
pub fn process_info(pid: u32) -> Result<ProcessInfo, SysmonError>;
pub fn process_count() -> Result<usize, SysmonError>;
pub fn all_processes() -> Result<Vec<ProcessInfo>, SysmonError>;

// Load
pub fn load_average() -> Result<LoadAverage, SysmonError>;
```

**Design decisions to document**:
- Linux-only by design (not a cross-platform crate — that's `sysinfo`'s domain)
- No refresh/cache model — each call reads fresh data from `/proc`
- Errors are per-call, not global state
- `rustix` for `statvfs` only — everything else is `std::fs::read_to_string`

---

### 2. Architectural Patterns (Documentation)

These aren't crates but reusable architectural patterns worth publishing as
blog posts or RFC-style documents.

#### Tower Atomic — Crypto Delegation Without Embedding

**Origin**: bearDog + songBird (January 2026)

**Pattern**: Instead of every service linking a crypto library (Ring, OpenSSL),
delegate all crypto to a single service (bearDog) over IPC. The crypto service
is a self-contained binary with no shared library linking. Result: every consumer
is Pure Rust, the crypto service is audited once.

**Relevant to**: Any distributed system where crypto is a shared concern.
Microservice architectures, edge deployments, IoT clusters.

#### /proc-first System Monitoring

**Origin**: toadStool S137 (March 2026)

**Pattern**: Instead of linking C libraries for system metrics, parse `/proc`
directly. Linux exposes everything as text files. `std::fs::read_to_string` +
string parsing is simpler, safer, and cross-compiles without toolchains.

**Relevant to**: Any Rust project monitoring Linux systems. Prometheus exporters,
health check endpoints, resource schedulers.

---

### 3. Future Candidates

These are patterns or code that may become upstream contributions as they mature:

| Candidate | Origin | Status | Notes |
|-----------|--------|--------|-------|
| `proc-sysinfo` | toadStool sysmon | Ready for extraction | First candidate |
| **`wgsl-precision`** | **barraCuda DF64 + toadStool PrecisionBrain** | **Production — priority extraction** | **DF64 + precision routing for Dimforge/wgmath and Rust GPU community. 1,145 shaders, 88K WGSL lines validate the approach. See `EXTERNAL_VALIDATION_AND_UPSTREAM_STRATEGY.md`** |
| **`wgsl-compose`** | **coralReef `prepare_wgsl`** | **Production — priority extraction** | **Preamble composition solving WGSL module system gap Dimforge documented** |
| Capability-based service discovery | biomeOS + songBird | Under development | JSON-RPC capability advertising protocol |
| Pure Rust DRM ioctl wrappers | coralReef coral-driver | In progress | `rustix`-based, no `nix`/`libc` |
| Genetic lineage trust model | bearDog | Conceptual | Family-seed auto-trust without CA |

---

## Licensing Strategy

### Internal (ecoPrimals workspace)

All primal code is **AGPL-3.0-or-later**. This protects the ecosystem's
sovereign compute mission.

### Upstream contributions

Standalone crates intended for crates.io should use **MIT OR Apache-2.0**
dual-license. This is the Rust ecosystem convention and maximizes adoption.

**Rationale**: The goal of upstream contributions is maximum community benefit.
Restrictive licensing on a utility crate limits adoption. The primal-specific
code that uses these utilities remains AGPL-3.0.

**Example**:
- `proc-sysinfo` (upstream crate) → MIT/Apache-2.0
- `toadstool-sysmon` (in-tree, uses proc-sysinfo) → AGPL-3.0
- The primal-specific monitoring integration → AGPL-3.0

Once `proc-sysinfo` gains traction, we depend on it as an external crate
and remove our in-tree copy. The circle completes.

---

## The Evolve-and-Lean Cycle

```
Springs find gaps in primals
  → Primals solve deep problems (Ring→RustCrypto, sysinfo→/proc)
    → Solutions extracted as standalone crates
      → Published to crates.io (MIT/Apache-2.0)
        → Community adopts, improves, contributes
          → Crate matures with wider testing
            → We depend on the upstream crate
              → Our in-tree copy removed
                → We lean on the community solution
                  → Springs validate the leaner stack
```

This is the same pattern the springs use with us. The springs evolved our
math layer (barraCuda), our compiler (coralReef), our hardware stack (toadStool).
Now we evolve the wider Rust ecosystem the same way.

**The springs taught us evolution. Now we teach it upstream.**

---

## Precedents in Rust Ecosystem

This pattern is well-established:

| Project | Internal Tool | Became Upstream | Impact |
|---------|--------------|-----------------|--------|
| Servo | url parser | `url` crate | Standard URL parser for Rust |
| Servo | CSS engine | `cssparser` crate | Used by hundreds of projects |
| Tokio | bytes buffer | `bytes` crate | Foundational for async Rust |
| AWS | smithy-rs codegen | `aws-sdk-rust` | Official AWS SDK |
| Cloudflare | QUIC impl | `quiche` | Production QUIC for anyone |

ecoPrimals joining this pattern with `proc-sysinfo` continues a proud tradition.

---

## Timeline

**Q1 2026 (Now)**:
- [x] `toadstool-sysmon` created and production-tested
- [ ] Extract as `proc-sysinfo` standalone crate
- [ ] Add benchmarks, comprehensive docs
- [ ] Publish v0.1.0 to crates.io

**Q2 2026**:
- [ ] Community feedback on `proc-sysinfo` incorporated
- [ ] v0.2.0 with any API improvements
- [ ] Blog post on r/rust about the /proc-first pattern
- [ ] **Extract `wgsl-precision` standalone crate (DF64 + PrecisionBrain)**
- [ ] **Extract `wgsl-compose` standalone crate (preamble composition)**
- [ ] **Peer engagement with Dimforge/wgmath — proof of work, not pitch**
- [ ] See `EXTERNAL_VALIDATION_AND_UPSTREAM_STRATEGY.md` for full scope

**Q3 2026**:
- [ ] If adoption sufficient, depend on upstream `proc-sysinfo`
- [ ] Remove in-tree `toadstool-sysmon` (lean upstream)
- [ ] Document the complete cycle

---

*The primals evolved from the springs. Now the primals evolve the ecosystem.*
*One day, the standards we built will come back to us as dependencies we trust.*
