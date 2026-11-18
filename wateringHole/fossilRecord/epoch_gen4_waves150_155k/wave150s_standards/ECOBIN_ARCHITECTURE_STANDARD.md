# ecoBin Architecture - Ecosystem Standard

**Status**: 🌟 **ECOSYSTEM STANDARD v3.0** 🌟  
**Adopted**: January 17, 2026  
**Evolved**: January 30, 2026 (Platform-Agnostic v2.0)  
**Evolved**: March 9, 2026 (Infrastructure C Elimination v3.0)  
**Authority**: WateringHole Consensus (All Primal Teams)  
**Compliance**: Mandatory for all new primals, recommended for existing  
**Reference Implementation**: BearDog (FIRST TRUE ecoBin), ToadStool (FIRST ecoBin v3.0)

---

## 🌍 **ecoBin v2.0 Evolution** (January 30, 2026)

**Catalyst**: Pixel 8a GrapheneOS deployment learning

**Philosophy Update**:
> **"If it can't run on the arch/platform, it's not a true ecoBin"**

**Evolution**:
- **v1.0 (Jan 17)**: Cross-Architecture (x86_64, ARM64, RISC-V) - ~80% coverage
- **v2.0 (Jan 30)**: Cross-Architecture + **Cross-Platform** - 100% coverage

**New Coverage**:
- ✅ Linux (all architectures)
- ✅ **Android** (ARM64, x86_64) - abstract sockets
- ✅ **Windows** (x86_64, ARM64) - named pipes
- ✅ macOS (Intel, M-series)
- ✅ **iOS** (ARM64) - XPC
- ✅ **WASM** (browser, Wasmtime) - in-process
- ✅ **Embedded** (bare metal) - shared memory

**Key Addition**: **Platform-agnostic IPC** (runtime transport discovery, zero assumptions)

See: `docs/deep-debt/PLATFORM_AGNOSTIC_IPC_EVOLUTION.md` in biomeOS for implementation details

---

## 📜 **Standard Declaration**

**ecoBin Architecture** is hereby adopted as the official ecosystem standard for **universal portable binaries** across all ecoPrimals. This standard builds upon UniBin by eliminating C dependencies, enabling **true cross-compilation** to any Rust-supported target with **zero external toolchain setup**.

**All primal teams** are expected to evolve toward this standard for maximum portability and security.

---

## 🎯 **Core Principle**

### **ecoBin = Ecological Binary = Universal Cross-Compilation**

**ecoBin** is a **UniBin** that achieves **FULL cross-compilation** to ANY platform, architecture, and era.

**The Ecological Principle**:
Just like ecoPrimals ecosystem is **agnostic**, **universal**, and **adaptive**, an ecoBin is a binary that:
- 🌍 **Universal**: Runs on ANY architecture (x86, ARM, RISC-V, PowerPC, etc.)
- 🖥️ **Cross-Platform**: Runs on ANY platform (Linux, Android, Windows, macOS, iOS, WASM, embedded)
- 🔧 **Agnostic**: Builds without platform-specific toolchains
- 🌿 **Adaptive**: Thrives in any computing environment
- ⏳ **Era-spanning**: Works on systems from past, present, and future

**Formula (v2.0)**:
```
ecoBin = UniBin (one binary, multiple modes)
       + FULL Cross-Compilation (any arch, any platform, any era)
       + Platform-Agnostic IPC (runtime transport discovery)
       
Achieved via:
       + Pure Rust (zero C compiler requirements!)
       + Minimal dependencies (no external toolchains!)
       + Universal portability (one build command for any target!)
       + Runtime discovery (zero platform assumptions!)
```

**Key Insight**: **Pure Rust is the MEANS, not the END!**

Pure Rust enables TRUE portability because:
- ✅ No C compiler needed → Simple cross-compilation
- ✅ No platform-specific code → Universal builds
- ✅ No external toolchains → Zero setup required
- ✅ Consistent behavior → Predictable everywhere

**The Goal**: A binary that runs **EVERYWHERE** with **ONE** `cargo build` command!

---

## 🆚 **UniBin vs ecoBin - The Distinction**

### **UniBin** (Architecture Standard)

**Definition**: Single binary per primal with multiple operational modes

**Focus**: Binary structure and CLI UX

**Requirements**:
- ✅ One binary per primal (no `-server`, `-client` suffixes)
- ✅ Subcommand-based modes (`primal <mode>`)
- ✅ Professional CLI (`--help`, `--version`)
- ⏳ May have C dependencies (openssl, ring, etc.)

**Goal**: Eliminate binary naming fragility, improve UX

**Example**:
```bash
# UniBin (may have C deps)
beardog server     # Single binary, multiple modes
beardog client     # But might depend on openssl (C)
beardog doctor     # Might not cross-compile easily
```

**Status**: ✅ Foundation (UniBin is prerequisite!)

---

### **ecoBin** (Universal Cross-Compilation Standard)

**Definition**: A UniBin that cross-compiles to ALL platforms without external toolchains

**Focus**: **TRUE ecological portability** - runs ANYWHERE, any arch, any era

**Requirements (v1.0 - Cross-Architecture)**:
- ✅ All UniBin requirements (prerequisite!)
- ✅ **FULL cross-compilation** to ALL major architectures:
  - Linux (x86_64, ARM64, ARM32, RISC-V, PowerPC, etc.)
  - macOS (Intel x86_64, Apple Silicon ARM64)
  - Windows (x86_64, ARM64)
  - Android (ARM64, x86_64)
  - WebAssembly (WASM32)
  - Embedded systems (as applicable)
- ✅ **ZERO external toolchains** required (no NDK, no musl-gcc, no Xcode SDK)
- ✅ **ONE build command** works for any target: `cargo build --target <any>`

**Additional Requirements (v2.0 - Cross-Platform)** ⭐ NEW January 30, 2026:
- ✅ **Platform-agnostic IPC**: No assumptions about Unix/Windows/etc.
- ✅ **Runtime transport discovery**: Detect best transport at runtime (Unix sockets, abstract sockets, TCP, named pipes, etc.)
- ✅ **Graceful fallback**: Prefer native transport, fall back to TCP localhost
- ✅ **Zero platform assumptions**: No hardcoded paths (`/run/user/`, `C:\`, etc.)

**How it's achieved**:
- Pure Rust (eliminates C compiler requirements)
- Careful dependency selection (must support ALL platforms)
- Tested cross-compilation matrix (proof, not theory!)

**Goal**: **Deploy ONE binary to ANY computing environment with ZERO setup!**

**Example**:
```bash
# ecoBin (FULL cross-compilation - TRUE ecological portability!)
beardog server     # Single binary
beardog client     # Builds for ANY target
beardog doctor     # Zero toolchain setup needed!

# The ecological test - ALL should succeed:
cargo build --target x86_64-unknown-linux-musl      # Linux x86
cargo build --target aarch64-unknown-linux-musl     # Linux ARM64
cargo build --target x86_64-apple-darwin            # macOS Intel
cargo build --target aarch64-apple-darwin           # macOS Silicon
cargo build --target x86_64-pc-windows-gnu          # Windows
cargo build --target aarch64-linux-android          # Android
cargo build --target wasm32-wasi                    # WebAssembly
cargo build --target riscv64gc-unknown-linux-gnu    # RISC-V

# If ALL succeed → TRUE ecoBin! 🌍
# The binary is "ecological" - it adapts to ANY environment!
```

**Status**: 🎯 Evolution target (4/6 primals on path!)

---

### **Quick Comparison Table**

| Feature | UniBin | ecoBin |
|---------|--------|--------|
| **Single binary per primal** | ✅ Required | ✅ Required (inherits) |
| **Subcommand modes** | ✅ Required | ✅ Required (inherits) |
| **Professional CLI** | ✅ Required | ✅ Required (inherits) |
| **Cross-compilation** | ⏳ Complex | ✅ **FULL** (any target!) |
| **External toolchains** | ⏳ May need | ❌ **NEVER** needed! |
| **Universal deployment** | ⏳ Limited | ✅ **COMPLETE!** |
| **Platform support** | ⏳ Some | ✅ **ALL!** |
| **Build command** | ⏳ Complex | ✅ **ONE** for any target! |

**TL;DR**:
- **UniBin** = Structure (how binary works) - Single binary with modes
- **ecoBin** = UniBin + **Universal Portability** (runs EVERYWHERE!)
- **Pure Rust** = The primary strategy to achieve ecoBin (enables FULL cross-compilation!)
- **All ecoBins are UniBins, but not all UniBins are ecoBins!**

---

## ✅ **ecoBin Requirements**

### **0. Understanding: Why Pure Rust?** (FUNDAMENTAL)

**Pure Rust is not a goal for purity's sake - it's the KEY to TRUE portability!**

**The Problem with C Dependencies**:
```
Your primal with openssl (C library):
    ↓
Needs C compiler for target platform
    ↓
Needs platform-specific headers/libs
    ↓
May need cross-compiler toolchain (musl-gcc, arm-gcc, etc.)
    ↓
May need SDKs (NDK for Android, Xcode for macOS)
    ↓
❌ FAILS ecoBin goal - CANNOT run everywhere with one command!
```

**The Power of Pure Rust**:
```
Your primal with RustCrypto (Pure Rust):
    ↓
Rust compiler compiles to target directly
    ↓
No C compiler needed
    ↓
No platform-specific toolchains
    ↓
No SDKs required
    ↓
✅ ACHIEVES ecoBin goal - runs EVERYWHERE with `cargo build`!
```

**Why Pure Rust is FUNDAMENTAL**:

1. **Eliminates Toolchain Requirements**
   - C deps require C compilers for each target
   - Pure Rust only needs `rustc` (which you already have!)
   - Result: Universal builds without setup

2. **Removes Platform Barriers**
   - C deps may need platform-specific code
   - Pure Rust compiles consistently everywhere
   - Result: True "write once, run anywhere"

3. **Simplifies Cross-Compilation**
   - C deps: `rustup target add` + `apt-get install gcc-cross` + configure
   - Pure Rust: `rustup target add` (done!)
   - Result: ONE command for any architecture

4. **Enables Future-Proof Portability**
   - New architectures emerge (RISC-V, ARM64, etc.)
   - C toolchains may lag or be unavailable
   - Rust supports new targets quickly
   - Result: Your binary works on future platforms automatically!

**Bottom Line**:
```
Pure Rust = Universal Portability
Universal Portability = ecoBin's Core Goal
Therefore: Pure Rust is FUNDAMENTAL for ecoBin!
```

**Not for purity, but for ECOLOGICAL adaptability!** 🌍

---

### **1. UniBin Compliance** (PREREQUISITE)

**Rule**: MUST meet all UniBin Architecture Standard requirements.

**See**: `UNIBIN_ARCHITECTURE_STANDARD.md` for complete requirements.

**Checklist**:
- [ ] Single binary named after primal
- [ ] Subcommand structure implemented
- [ ] `--help` comprehensive
- [ ] `--version` implemented
- [ ] Professional error messages

**Why**: ecoBin builds upon UniBin foundation!

---

### **2. Pure Rust Application Code** (MANDATORY)

**Rule**: MUST eliminate all APPLICATION C dependencies.

**Zero Tolerance List** ❌:
```toml
# These are NOT allowed in ecoBin:
openssl-sys        # Crypto (use RustCrypto instead!)
ring               # Crypto (use RustCrypto instead!)
aws-lc-sys         # Crypto (use RustCrypto instead!)
native-tls         # TLS (use rustls instead!)
zstd-sys           # Compression (use pure-rust or feature-gate!)
lz4-sys            # Compression (use pure-rust or feature-gate!)
libsqlite3-sys     # Database (use rusqlite with bundled!)
cryptoki-sys       # HSM (feature-gate or use pure-rust alternatives!)
```

**Why These Are Banned**:
- 🔥 Security vulnerabilities (C memory safety issues!)
- 🚫 Cross-compilation blockers (require C compiler!)
- 💥 Platform-specific bugs and complexity
- 🎯 Violate Pure Rust principle

**Acceptable Alternatives**:
```toml
# Use these instead (Pure Rust!):
sha2 = "0.10"              # Instead of openssl for SHA
blake3 = { version = "1.5", features = ["pure"] }  # Pure Rust hashing
rustls = "0.22"            # Instead of native-tls (still has C, Songbird only!)
rusqlite = { version = "0.30", features = ["bundled"] }  # Bundled SQLite
RustCrypto suite           # All crypto primitives in Pure Rust!
```

---

### **3. Infrastructure C: Acceptable → Eliminable** (EVOLVED in v3.0)

**Rule**: musl/libc syscall wrapper is acceptable (unavoidable OS interface).

**Two Types of C**:

#### **Application C** ❌ **NOT ALLOWED!**
```
Your crypto, HTTP, compression code in C
  ↓
SECURITY RISK! Must eliminate!
```

#### **Infrastructure C** ✅ **Acceptable**
```
musl → Linux syscalls (open, read, write)
  ↓
OS interface only, minimal risk
```

**Why musl is OK**:
- ✅ Minimal code (~1MB vs 20MB for glibc)
- ✅ Well-audited and stable (2 CVEs in 4 years, both low severity)
- ✅ No application logic (just syscall wrappers)
- ✅ Unavoidable for practical Linux programs
- ✅ Static linking (no runtime dependencies!)

**Mental Model**:
```
┌─────────────────────────────────────┐
│   YOUR APPLICATION CODE             │  ← 100% Pure Rust! ✅
│   (crypto, logic, algorithms)       │
├─────────────────────────────────────┤
│   Rust Standard Library (std)       │  ← Pure Rust! ✅
│   (collections, threads, async)     │
├─────────────────────────────────────┤
│   OS Interface (musl)                │  ← Infrastructure C ⏳
│   (open, read, write, mmap)         │     (acceptable)
├─────────────────────────────────────┤
│   Linux Kernel                       │  ← OS (irrelevant)
└─────────────────────────────────────┘
```

**v1.0/v2.0 Position**: ecoBin = 100% Pure Rust APPLICATION + musl infrastructure

**v3.0 Evolution** (March 9, 2026): toadStool proved that `/proc` parsing + `rustix`
direct syscalls can eliminate libc from application dependencies entirely. musl is
still acceptable for targets that need it, but v3.0 primals don't require it.
The long-term trajectory: `rustix` + `linux-raw-sys` → zero C in the entire binary.

**See**: ecoBin v3.0 section below for full details

---

### **4. FULL Cross-Compilation Matrix** (MANDATORY)

**Rule**: MUST successfully cross-compile to ALL major platforms.

**The ecoBin Test Matrix**:
```bash
# Linux targets (ALL must succeed!)
cargo build --release --target x86_64-unknown-linux-musl      # x86_64
cargo build --release --target aarch64-unknown-linux-musl     # ARM64
cargo build --release --target armv7-unknown-linux-musleabihf # ARM32

# macOS targets (ALL must succeed!)
cargo build --release --target x86_64-apple-darwin            # Intel Mac
cargo build --release --target aarch64-apple-darwin           # Apple Silicon

# Windows targets (SHOULD succeed)
cargo build --release --target x86_64-pc-windows-gnu          # Windows x64

# Mobile/Embedded (SHOULD succeed if applicable)
cargo build --release --target aarch64-linux-android          # Android
cargo build --release --target wasm32-wasi                    # WebAssembly

# Future/Alternative (NICE TO HAVE)
cargo build --release --target riscv64gc-unknown-linux-gnu    # RISC-V
```

**Success Criteria**:
- ✅ ALL Linux targets build without errors
- ✅ ALL macOS targets build without errors
- ✅ No C compiler errors (no `cc-rs` failures!)
- ✅ No missing toolchain errors (no `musl-gcc`, `arm-gcc`, etc. needed!)
- ✅ Binaries are static (no dynamic dependencies)
- ✅ **ONE `cargo build` command** is sufficient (no setup!)

**Failure Examples** (NOT ecoBin!):
```bash
# C dependency detected - breaks cross-compilation:
error: failed to run custom build command for `openssl-sys`
error: failed to find tool "musl-gcc"  
# ❌ Needs C cross-compiler!

# Platform-specific dependency - breaks cross-compilation:
error: failed to run custom build command for `ring`
error: failed to find tool "aarch64-linux-android-clang"  
# ❌ Needs Android NDK!

# Build script issue - breaks cross-compilation:
error: failed to run custom build command for `redb`
cc: error: unrecognized command-line option '-arch'
# ❌ Platform-specific code blocking cross-compilation!
```

**Why FULL Matrix**:
- ✅ Proves TRUE portability (not just theory!)
- ✅ Exposes hidden platform dependencies
- ✅ Validates ecological adaptability
- ✅ Ensures binary works on past, present, future platforms!

**The ecoBin Promise**:
```
If your primal passes FULL cross-compilation matrix:
→ It's a TRUE ecoBin
→ It runs EVERYWHERE
→ It's ecologically adaptive!
→ One binary for any platform, any architecture, any era! 🌍
```

---

### **5. Additional Platform Testing** (VALIDATION)

**Rule**: SHOULD test actual runtime on multiple platforms.

**Test Platforms**:
```bash
# Copy binary to diverse systems and run:
# - Different Linux distros (Ubuntu, Alpine, Debian, Fedora)
# - Different architectures (x86_64, ARM64, RISC-V)
# - Different macOS versions (Intel, Apple Silicon)
# - Different kernel versions (old and new)
# - Raspberry Pi (ARM)
# - Android devices (if applicable)
# - Windows (if applicable)

# Just copy and run:
./primal --version  # Should work everywhere! ✅
./primal doctor     # Should provide health status! ✅
```

**Success Criteria**:
- ✅ Binary runs without platform-specific errors
- ✅ No missing library errors
- ✅ Core functionality works across all platforms
- ✅ Performance is acceptable on all architectures

**Status**: Validates TRUE ecological adaptability across real-world environments!

---

### **6. Dependency Audit** (MANDATORY)

**Rule**: MUST verify zero C dependencies via `cargo tree`.

**Audit Commands**:
```bash
# Check for C system dependencies
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys|native-tls|zstd-sys|lz4-sys|libsqlite3-sys)"

# If ANY matches: NOT ecoBin!
# If zero matches: Potential ecoBin! ✅
```

**Common False Positives**:
```bash
# These are OK (infrastructure):
├── libc v0.2.151        # ✅ Rust wrapper for libc
├── cc v1.0.83           # ✅ Build tool (not runtime!)

# These are NOT OK (application C):
├── openssl-sys v0.9.96  # ❌ C crypto library!
├── ring v0.17.7         # ❌ C assembly crypto!
```

**Status**: Zero APPLICATION C dependencies = ecoBin candidate! 🎯

---

## 🏗️ **Implementation Guide**

### **Step 1: Achieve UniBin**

**Prerequisites**:
- ✅ Single binary per primal
- ✅ Subcommand structure
- ✅ Professional CLI

**See**: `UNIBIN_ARCHITECTURE_STANDARD.md`

**Time**: 1-2 weeks per primal

---

### **Step 2: Eliminate C Dependencies**

**Process**:

#### **2.1 Audit Current Dependencies**
```bash
cd /path/to/primal
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys|native-tls|zstd-sys)"
```

#### **2.2 Identify Sources**
```bash
# Find which crates pull in C deps
cargo tree -i openssl-sys
cargo tree -i ring
```

#### **2.3 Replace with Pure Rust**

**Common Replacements**:

| C Dependency | Pure Rust Alternative |
|--------------|----------------------|
| `openssl-sys` | `RustCrypto` suite (sha2, aes, etc.) |
| `ring` | `RustCrypto` suite |
| `aws-lc-sys` | `RustCrypto` suite |
| `native-tls` | `rustls` (still has C, Songbird only!) |
| `reqwest` (non-Songbird) | Remove! (Unix sockets only!) |
| `zstd-sys` | Feature-gate or remove |
| `libsqlite3-sys` | `rusqlite` with `bundled` feature |

**Example Migrations**:

**Before** (C dependencies):
```toml
[dependencies]
openssl = "0.10"          # ❌ Pulls openssl-sys!
ring = "0.17"             # ❌ C assembly!
reqwest = "0.11"          # ❌ Pulls native-tls or ring!
```

**After** (Pure Rust):
```toml
[dependencies]
sha2 = "0.10"             # ✅ Pure Rust SHA-256
blake3 = { version = "1.5", features = ["pure"] }  # ✅ Pure Rust hashing
ed25519-dalek = "2.1"     # ✅ Pure Rust signatures
# No HTTP! Use Unix sockets for IPC!
```

**Time**: 2-4 weeks per primal (depends on complexity)

---

### **Step 3: Test musl Cross-Compilation**

**Command**:
```bash
cargo build --release --target x86_64-unknown-linux-musl
```

**Expected**: Success with zero C compiler errors!

**If Fails**: You still have hidden C dependencies! Return to Step 2.

**Time**: Immediate validation

---

### **Step 4: Validate Static Binary**

**Check Dependencies**:
```bash
ldd target/x86_64-unknown-linux-musl/release/primal
```

**Expected**:
```
not a dynamic executable
```

**If Shows Libs**: Not static! Check musl target setup.

**Time**: 5 minutes

---

### **Step 5: Test Universal Deployment**

**Copy to Different Systems**:
```bash
# Copy binary to:
# - Different Linux distros (Ubuntu, Alpine, Debian)
# - Different kernel versions
# - Raspberry Pi (ARM)
# - Old systems

# Just copy and run:
./primal --version  # Should work everywhere! ✅
```

**Time**: 1 hour validation

---

### **Step 6: Declare ecoBin Compliance**

**Checklist**:
- [ ] UniBin compliant
- [ ] Zero application C dependencies
- [ ] musl cross-compilation succeeds
- [ ] Binary is static
- [ ] Tested on multiple platforms
- [ ] Documented in WateringHole

**Time**: 30 minutes documentation

---

## 🌟 **Reference Implementation: BearDog**

**Status**: ✅ **FIRST TRUE ecoBin** 🎉

### **Why BearDog is the Reference**

**UniBin** ✅:
- Single binary: `beardog`
- Multiple subcommands: `entropy`, `key`, `hsm`, `cross-primal`, `service`, `jwt`, `secret`, `rotate`, `hash`, `verify`, `audit`
- Professional CLI with `--help`, `--version`

**Pure Rust** ✅:
- Zero application C dependencies
- RustCrypto suite for all crypto
- `blake3` with `pure` feature
- No HTTP (Unix sockets only!)
- No C compression libraries

**Universal Deployment** ✅:
- Cross-compiles to `x86_64-unknown-linux-musl` ✅
- Cross-compiles to `aarch64-unknown-linux-musl` ✅
- Cross-compiles to `aarch64-linux-android` ✅ (with feature gates)
- Static binary (~4.9MB)
- Runs on any Linux (universal!)

**Validation**:
```bash
# Build for x86_64 musl
cargo build --release --target x86_64-unknown-linux-musl
# ✅ Success! No C compiler needed!

# Check dependencies
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys)"
# ✅ Zero matches!

# Verify static
ldd target/x86_64-unknown-linux-musl/release/beardog
# ✅ not a dynamic executable

# Test deployment
./beardog --version
# beardog 0.9.0
# ✅ Works everywhere!
```

**All primals should follow BearDog's ecoBin pattern!**

---

## 📊 **Ecosystem Compliance Status**

### **TRUE ecoBins** ✅ (100% Pure Rust + Universal Portability)

| Primal | Version | Certified | Validation Date |
|--------|---------|-----------|-----------------|
| **BearDog** | 0.9.0 | ✅ TRUE ecoBin #1 | Jan 17, 2026 |
| **NestGate** | 0.11.0+ | ✅ TRUE ecoBin #2 | Jan 17, 2026 |
| **sourDough** | 0.1.0 | ✅ TRUE ecoBin #3 | Jan 19, 2026 |
| **Songbird** | v5.24.0 | ✅ TRUE ecoBin #4 🎉 | Jan 24, 2026 |
| **biomeOS** | 0.1.0 | ✅ TRUE ecoBin #5 🌟 | Jan 24, 2026 |

**Notes**:
- BearDog: FIRST TRUE ecoBin (reference implementation)
- NestGate: Second TRUE ecoBin (close follower)
- sourDough: THIRD TRUE ecoBin (starter culture, scaffolding, genomeBin tooling)
- Songbird: FOURTH TRUE ecoBin (Pure Rust TLS 1.3 via Tower Atomic!)
- **biomeOS: FIFTH TRUE ecoBin (Orchestrator - proves workspace ecoBin viable!) 🌟**

**MILESTONE**: Universal Orchestrator Achieved! biomeOS orchestrates ecoBins because it IS an ecoBin!

---

### **ecoBin v3.0 Certified** (Infrastructure C Eliminated)

| Primal | Version | Certified | Validation Date | Notes |
|--------|---------|-----------|-----------------|-------|
| **ToadStool** | S141 | ✅ ecoBin v3.0 #1 | Mar 10, 2026 | sysinfo eliminated, `toadstool-sysmon` (pure /proc + rustix), cross-compile CI (aarch64, armv7), clippy pedantic `--all-targets`, zero-copy GPU payloads |

**Achievement**: First primal to reach ecoBin v3.0 — zero infrastructure C in application code.
Pattern: `/proc` parsing + `rustix` syscalls replaces libc-based crates entirely.

---

### **ecoBin Candidates** ⏳ (Close, HTTP cleanup needed)

| Primal | Status | Blockers | ETA |
|--------|--------|----------|-----|
| **Squirrel** | UniBin ✅ | HTTP legacy (delegate to Songbird) | ~2 hours |

**Notes**:
- Squirrel: Use Songbird for HTTP/TLS (via JSON-RPC) - follow Tower Atomic pattern

---

### **Work in Progress** 🚧 (UniBin but not Pure Rust)

**NONE!** 🎉

**Previous Entry** (RESOLVED):
| Primal | UniBin | Pure Rust | Status | Resolution Date |
|--------|--------|-----------|--------|-----------------|
| **Songbird** | ✅ | ✅ | **RESOLVED** | Jan 24, 2026 |

**Resolution**: Songbird achieved Pure Rust TLS 1.3 via Tower Atomic pattern with BearDog crypto delegation!

---

## 🎯 **The Tower Atomic Strategy** (Evolved from Concentrated Gap)

### **Architectural Innovation**

**Previous Principle**: Only **ONE** primal (Songbird) handles external HTTP/TLS.

**Evolution**: **ALL primals are Pure Rust via crypto delegation!**

**Why Tower Atomic Works**:
- ✅ Songbird: Pure Rust TLS 1.3 protocol implementation
- ✅ BearDog: Pure Rust cryptographic operations (RustCrypto)
- ✅ Communication: JSON-RPC over Unix sockets
- ✅ Result: BOTH are TRUE ecoBins!

**Implementation**:
```
External World (HTTPS)
    ↓
Songbird (Pure Rust TLS 1.3 - TRUE ecoBin!)
    ↓ JSON-RPC over Unix socket
BearDog (Pure Rust Crypto - TRUE ecoBin!)
    ↓ RustCrypto primitives
Pure Rust Operations
```

**Result**:
- 🎉 **4/4 primals are TRUE ecoBins!**
- 🚀 100% Pure Rust ecosystem achieved!
- ✅ Universal cross-compilation for all primals!
- 🏆 Tower Atomic pattern proven at scale!

**Status**: ✅ **ACHIEVED** - Architectural breakthrough! (Jan 24, 2026)

---

## 🚀 **Migration Path**

### **For Existing Primals**

**Phase 1: UniBin Compliance** (1-2 weeks)
- ✅ Achieve UniBin (see UNIBIN_ARCHITECTURE_STANDARD.md)
- ✅ Single binary, subcommands, professional CLI

**Phase 2: C Dependency Audit** (1 week)
- 🔍 Run `cargo tree` audit
- 📋 Identify all C dependencies
- 📝 Document sources and reasons

**Phase 3: Pure Rust Migration** (2-4 weeks)
- 🔄 Replace C dependencies with Pure Rust
- 🧪 Test functionality maintained
- ✅ Verify musl cross-compilation

**Phase 4: Validation & Certification** (1 week)
- 🧪 Cross-compile to musl targets
- 🧪 Test on multiple platforms
- 📝 Document compliance
- 🎉 Declare ecoBin!

**Total Timeline**: 5-8 weeks per primal

---

### **For New Primals**

**Requirement**: MUST implement ecoBin from day one (if not Songbird-role).

**Checklist**:
- [ ] Implement as UniBin (prerequisite)
- [ ] Use RustCrypto suite (no openssl/ring!)
- [ ] Use `blake3` with `pure` feature
- [ ] No HTTP dependencies (use Unix sockets!)
- [ ] Test musl cross-compilation early
- [ ] Verify zero C dependencies
- [ ] Document ecoBin compliance

**Timeline**: Same development time (if designed right from start!)

---

## 💡 **Best Practices**

### **1. Avoid C Dependencies from Day One**

**Prefer**:
- ✅ `RustCrypto` suite over openssl/ring
- ✅ `blake3` with `pure` feature
- ✅ Unix sockets over HTTP for IPC
- ✅ Pure Rust compression or feature-gate

**Avoid**:
- ❌ `reqwest` (unless you're Songbird!)
- ❌ `native-tls` (unless you're Songbird!)
- ❌ `ring`, `openssl`, `aws-lc-sys`
- ❌ `zstd-sys`, `lz4-sys` (use Pure Rust or feature-gate)

---

### **2. Test Cross-Compilation Early**

**Integrate into CI**:
```yaml
# .github/workflows/ci.yml
jobs:
  test-musl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: rustup target add x86_64-unknown-linux-musl
      - run: cargo build --release --target x86_64-unknown-linux-musl
      # If this fails, you have C deps!
```

**Benefit**: Catch C dependencies early!

---

### **3. Use Feature Gates for Optional C**

**Example**:
```toml
[dependencies]
cryptoki = { version = "0.6", optional = true }  # HSM support

[features]
hsm = ["cryptoki"]  # Optional C dependency
```

**Usage**:
```bash
# Default build: Pure Rust (ecoBin!)
cargo build --target x86_64-unknown-linux-musl

# HSM build: With C deps (not ecoBin)
cargo build --features hsm
```

**Benefit**: Core is ecoBin, advanced features optional!

---

### **4. Document Dependency Rationale**

**In Cargo.toml**:
```toml
[dependencies]
# Pure Rust crypto (ecoBin compliant!)
sha2 = "0.10"             # SHA-256 hashing
blake3 = { version = "1.5", features = ["pure"] }  # BLAKE3 (pure Rust!)
ed25519-dalek = "2.1"     # Ed25519 signatures

# Note: No openssl or ring! We're 100% Pure Rust for ecoBin!
```

**Benefit**: Team understands WHY choices were made

---

### **5. Celebrate ecoBin Achievement!**

**When you achieve ecoBin**:
- 🎉 Update WateringHole documentation
- 🎉 Announce to ecosystem
- 🎉 Add badge to README
- 🎉 Share lessons learned

**Benefit**: Motivates other teams, shares knowledge!

---

## 🎓 **Examples**

### **Example 1: Crypto Migration**

**Before** (C dependencies):
```toml
[dependencies]
ring = "0.17"  # ❌ C assembly crypto
```

```rust
use ring::digest;

let hash = digest::digest(&digest::SHA256, b"data");
```

**After** (Pure Rust):
```toml
[dependencies]
sha2 = "0.10"  # ✅ Pure Rust crypto
```

```rust
use sha2::{Sha256, Digest};

let mut hasher = Sha256::new();
hasher.update(b"data");
let hash = hasher.finalize();
```

**Result**: Same functionality, zero C dependencies! ✅

---

### **Example 2: HTTP Removal**

**Before** (C dependencies):
```toml
[dependencies]
reqwest = "0.11"  # ❌ Pulls native-tls (C!)
```

```rust
let resp = reqwest::get("https://api.example.com").await?;
```

**After** (Pure Rust - Concentrated Gap):
```rust
// For external HTTP: Route through Songbird!
// For internal IPC: Use Unix sockets!

use tokio::net::UnixStream;
let stream = UnixStream::connect("/tmp/songbird.sock").await?;
// Send JSON-RPC request to Songbird to make HTTP call
```

**Result**: No HTTP dependencies, Pure Rust! ✅

---

### **Example 3: blake3 Fix**

**Before** (C assembly):
```toml
[dependencies]
blake3 = "1.5"  # ❌ Uses C assembly by default!
```

**After** (Pure Rust):
```toml
[dependencies]
blake3 = { version = "1.5", features = ["pure"] }  # ✅ Pure Rust!
```

**Result**: Same API, Pure Rust implementation! ✅

---

## 🏆 **Benefits**

### **For Security**

- ✅ Eliminate C memory safety vulnerabilities
- ✅ Reduce attack surface (no openssl CVEs!)
- ✅ Easier security auditing (Pure Rust!)
- ✅ Leverage Rust's safety guarantees

**Example**: openssl 53 CVEs (4 years) vs musl 2 CVEs (4 years)

---

### **For Portability**

- ✅ Cross-compile to ANY Rust target
- ✅ No C compiler/linker needed
- ✅ No external toolchains (NDK, musl-gcc, etc.)
- ✅ Deploy anywhere (x86, ARM, RISC-V, Android, etc.)

**Example**: Single `cargo build` command for any target!

---

### **For Development**

- ✅ Simpler build process (no C toolchain setup!)
- ✅ Faster CI (no C compiler overhead!)
- ✅ Easier debugging (Pure Rust stack traces!)
- ✅ Better IDE support (no FFI boundaries!)

---

### **For Maintenance**

- ✅ Fewer dependencies to track
- ✅ Fewer CVEs to monitor (no C libs!)
- ✅ Easier updates (Pure Rust ecosystem!)
- ✅ Better long-term stability

---

### **For Ecosystem**

- ✅ Consistent dependency strategy
- ✅ Universal deployment story
- ✅ Professional, modern architecture
- ✅ Showcase Rust's capabilities!

---

## 🔬 **ecoBin v3.0: Infrastructure C Elimination** (March 9, 2026)

### **The Evolution: From "Acceptable C" to Zero C**

**v1.0** (Jan 17, 2026): Cross-Architecture — Pure Rust application code, musl infrastructure acceptable  
**v2.0** (Jan 30, 2026): Cross-Platform — Platform-agnostic IPC, runtime transport discovery  
**v3.0** (Mar 9, 2026): **Zero Infrastructure C** — Eliminate libc/musl from application dependencies entirely

**Catalyst**: toadStool S137 proved that the largest C surface in a mature primal
(sysinfo → 15 transitive crates → libc FFI) can be replaced with pure Rust
`/proc` parsing + `rustix` direct syscalls. Zero C compilation step. Cross-compile
with just `rustup target add`.

**The v2.0 position was**: "musl infrastructure C is acceptable — it's just syscall wrappers."

**The v3.0 evolution**: "We proved we can eliminate even that. `/proc` + `rustix` =
raw Linux syscalls from pure Rust. No C compiler, no musl-tools, no NDK."

### **The Pattern: Proven Across Primals**

| Primal | C Eliminated | Pure Rust Replacement | Pattern |
|--------|-------------|----------------------|---------|
| **BearDog + Songbird** | Ring (C asm crypto) | RustCrypto suite | Tower Atomic delegation |
| **barraCuda + coralReef** | Vulkan FFI, SPIR-V tools | naga WGSL roundtrip, sovereign compiler | Node Atomic delegation (in progress) |
| **toadStool** | sysinfo (15 crates → libc) | `toadstool-sysmon` (/proc + rustix) | `/proc` parsing |
| **akida-driver** | libc VFIO ioctls | rustix ioctl wrappers | Direct syscall |

**Each primal that eliminates C teaches the ecosystem a reusable pattern.**

> **Node Atomic Delegation (April 11, 2026)**: The barraCuda + coralReef row is
> the same class of problem as BearDog + Songbird. wgpu's transitive chain
> (`wgpu` → `wgpu-hal` → `ash` → `libloading` → `dlopen(libvulkan.so.1)`)
> prevents musl-static binaries from accessing GPU hardware. The resolution
> mirrors Tower Atomic: barraCuda delegates GPU dispatch to toadStool (hardware)
> + coralReef (compiler) via IPC, with pure-Rust CPU fallback (`cpu-shader` /
> `naga-exec` + scalar Rust) when no peers are available. See
> `PORTABILITY_DEBT_AND_NODE_DELEGATION.md` for the full pattern and gap registry.

### **The DNA Analogy**

Rust as unified language = DNA.
`/proc` filesystem as kernel interface = cellular environment.
No C translation layer = no mRNA intermediate.

This gives:
- **Cross-arch**: `cargo build --target aarch64-unknown-linux-gnu` without musl-tools/NDK
- **Reproducible**: Same binary semantics on any Linux kernel (including Android)
- **Auditable**: One language, one compilation model, one type system
- **Sovereign**: No vendor toolchains, no C compilers in the build graph

### **ecoBin v3.0 Additional Requirements**

In addition to v2.0 requirements:

- **Zero `sysinfo`/`psutil` crates**: Replace with `/proc` parsing (see `toadstool-sysmon` pattern)
- **`rustix` over `libc`**: For any direct syscall needs (ioctl, mmap, statvfs)
- **Feature-gate remaining ecosystem C**: Track mio/tokio/wgpu evolution upstream
- **Cross-compile CI**: `cargo check --target aarch64-unknown-linux-gnu` in CI (no musl-tools installed)

### **Upstream Contribution Path**

ecoPrimals doesn't just eliminate C for ourselves — we evolve patterns into
standalone crates the wider Rust community can use:

- `toadstool-sysmon` → candidate for `proc-sysinfo` on crates.io
- `rustix` ioctl patterns → documented for ecosystem adoption
- Tower Atomic (crypto delegation) → architectural pattern for any Rust project
- Node Atomic (compute delegation) → IPC-first GPU dispatch without dlopen coupling

**See**: `UPSTREAM_CONTRIBUTIONS.md` for the full upstream strategy.

### **Remaining Infrastructure C (Ecosystem Phase 2)**

These remain as transitive dependencies through ecosystem crates we don't own:

| Crate | Uses libc For | Upstream Status | Our Action |
|-------|--------------|-----------------|------------|
| mio | epoll | tokio-rs/mio#1735 (rustix migration) | Track, adopt when ready |
| tokio | Via mio + signal-hook | Follows mio | Automatic |
| drm | DRM ioctls | Partial rustix adoption | Track |
| evdev | Via nix | No rustix alt yet | Consider contributing |
| wgpu-hal | GPU platform libs (`libloading` → `dlopen`) | Replaced by coralReef sovereign compiler (long-term) | Node Atomic delegation (BC-07) |
| ash | Vulkan FFI (`libloading` → `dlopen`) | Transitive via wgpu-hal | Same — eliminated by sovereign path |
| ~~ring~~ | ~~C/ASM crypto (via rustls default crypto provider)~~ | ~~NestGate NG-08~~ | **RESOLVED** (April 11) — `reqwest` → `ureq` + `rustls-rustcrypto` |

When mio adopts rustix and Rust std adopts `linux-raw-sys`, the remaining
libc paths vanish automatically. Our code is already ready.

> **NestGate ring leak — RESOLVED (April 11, 2026)**: `ring` v0.17.14 was present
> via `rustls` → `reqwest` → `nestgate-rpc`. Fix applied: `reqwest` replaced with
> `ureq` 3.3 + `rustls-rustcrypto` (pure Rust). `cargo tree -i ring` now returns
> "did not match any packages". `cargo deny check bans` PASS. NestGate ecoBin
> certification reconfirmed — zero C/ASM crypto in production binary.
> See `PORTABILITY_DEBT_AND_NODE_DELEGATION.md` for full resolution details.

### **The v3.0 Mental Model**

```
┌─────────────────────────────────────┐
│   YOUR APPLICATION CODE             │  ← 100% Pure Rust ✅
│   (crypto, logic, algorithms)       │
├─────────────────────────────────────┤
│   System Monitoring                 │  ← Pure Rust (/proc) ✅  [NEW in v3.0]
│   (CPU, memory, disk, network)      │
├─────────────────────────────────────┤
│   Syscalls                          │  ← Pure Rust (rustix) ✅  [NEW in v3.0]
│   (ioctl, mmap, statvfs)           │
├─────────────────────────────────────┤
│   Rust Standard Library (std)       │  ← Pure Rust ✅
│   (collections, threads, async)     │
├─────────────────────────────────────┤
│   Ecosystem (mio, tokio)            │  ← Transitioning to rustix ⏳
│   (event loop, async runtime)       │
├─────────────────────────────────────┤
│   Linux Kernel                      │  ← OS (irrelevant)
└─────────────────────────────────────┘
```

**v2.0 had C in layers 2-3. v3.0 eliminated it. Layer 4 is ecosystem evolution.**

### **Validation**

```bash
# Verify zero sysinfo (C surface eliminated):
cargo tree --workspace | grep sysinfo
# Expected: nothing

# Verify remaining libc is ecosystem-only:
cargo tree --workspace --invert libc | head -30
# Expected: mio, tokio, wgpu — not our code

# Cross-compile without musl-tools:
cargo check --target aarch64-unknown-linux-gnu
# Expected: success (no C toolchain needed)
```

**Status**: ✅ toadStool certified ecoBin v3.0 (March 9, 2026)  
**Next**: Track ecosystem evolution (mio/tokio rustix adoption)

---

## 📚 **Resources**

### **Documentation**

- **UniBin Standard**: `wateringHole/UNIBIN_ARCHITECTURE_STANDARD.md`
- **musl Explanation**: `biomeOS/MUSL_EXPLAINED_FOR_ECOPRIMAL.md`
- **musl vs Pure Rust**: `biomeOS/MUSL_VS_PURE_RUST_NUANCE_JAN_17_2026.md`
- **BearDog ecoBin Validation**: `biomeOS/BEARDOG_ECOBIN_VALIDATION_JAN_17_2026.md`
- **Pure Rust Status**: `biomeOS/PURE_RUST_TRUE_UNIBIN_STATUS_JAN_17_2026.md`

### **Reference Implementations**

- **BearDog**: First TRUE ecoBin (reference)
- **NestGate**: Second TRUE ecoBin

### **External Resources**

- **RustCrypto**: https://github.com/RustCrypto
- **rustls**: https://github.com/rustls/rustls
- **blake3**: https://github.com/BLAKE3-team/BLAKE3
- **rustix**: https://github.com/bytecodealliance/rustix (future)

---

## 🎯 **Compliance & Review**

### **ecoBin Compliance Checklist**

Before declaring a primal ecoBin-compliant:

**UniBin Prerequisites**:
- [ ] Single binary named after primal
- [ ] Subcommand structure implemented
- [ ] `--help` and `--version` work
- [ ] Professional CLI and error messages

**Pure Rust Requirements**:
- [ ] Zero application C dependencies
- [ ] No `openssl-sys`, `ring`, `aws-lc-sys`
- [ ] No `reqwest` (unless Songbird!)
- [ ] No `zstd-sys`, `lz4-sys` (or feature-gated)
- [ ] RustCrypto suite used for crypto
- [ ] `blake3` with `pure` feature

**Cross-Compilation Validation**:
- [ ] Builds successfully: `cargo build --target x86_64-unknown-linux-musl`
- [ ] No C compiler errors
- [ ] Binary is static (`ldd` shows "not a dynamic executable")
- [ ] Tested on multiple Linux distros
- [ ] ARM build tested (stretch goal)

**Documentation**:
- [ ] Documented in WateringHole
- [ ] Dependency rationale explained
- [ ] Migration path documented (if applicable)
- [ ] Lessons learned shared

### **Certification Process**

1. **Self-Assessment**: Use checklist above
2. **Peer Review**: Request review from ecoBin team (BearDog/NestGate)
3. **Cross-Compilation Test**: Validate musl builds
4. **Platform Testing**: Test on diverse systems
5. **WateringHole Documentation**: Update this file
6. **Announcement**: Celebrate with ecosystem! 🎉

---

## 🔄 **Version History**

### **v3.0.0** (March 9, 2026)

**Infrastructure C Elimination**

**Author**: toadStool S137 (ecoPrimals ecosystem)  
**Consensus**: WateringHole Evolution (Proven via toadStool migration)

**Changes**:
- Established ecoBin v3.0: eliminate infrastructure C (musl/libc), not just application C
- Documented `/proc` parsing + `rustix` pattern as reusable C elimination strategy
- Promoted ToadStool to first ecoBin v3.0 certified primal
- Created upstream contribution pathway for standalone crates from ecoPrimals
- Added ecosystem Phase 2 tracking (mio/tokio/wgpu rustix migration)
- Updated mental model: layers 2-3 (monitoring, syscalls) now pure Rust

**Key Achievements**:
- `sysinfo` (15 transitive crates → libc) → `toadstool-sysmon` (pure Rust, 0 C deps)
- 22+ call sites migrated across 18 files
- Cross-compilation CI: aarch64-unknown-linux-gnu, armv7-unknown-linux-gnueabihf
- Pattern mirrors Ring → RustCrypto (Tower Atomic) but for system monitoring

**The Pattern**:
```
Ring C (crypto)     → RustCrypto  (Tower Atomic)    — bearDog/songBird solved it
sysinfo C (system)  → /proc+rustix (direct parsing) — toadStool solved it
mio C (event loop)  → rustix      (upstream tracking) — ecosystem evolving
Rust std (libc)     → linux-raw-sys (language evolution) — Rust project evolving
```

**Rationale**: The v2.0 "infrastructure C is acceptable" position was pragmatic for
January 2026. By March 2026, we proved it's eliminable. The goal is a unified
language system analogous to DNA — one language (Rust), one compilation model,
compiling for any Linux-based architecture with just `rustup target add`.

---

### **v1.0.0** (January 17, 2026)

**Initial ecoBin Standard Adoption**

**Author**: biomeOS Team  
**Consensus**: WateringHole (All Primal Teams)

**Changes**:
- Established ecoBin as ecosystem standard
- Defined distinction between UniBin and ecoBin
- Documented Pure Rust requirements
- Identified reference implementations (BearDog, NestGate)
- Defined Concentrated Gap Strategy
- Created migration path for existing primals
- Explained musl infrastructure C nuance

**Rationale**:
- Enable universal cross-compilation
- Eliminate C security vulnerabilities
- Simplify deployment (no external toolchains!)
- Showcase Rust's Pure Rust capabilities
- Establish ecoPrimals as cutting-edge architecture

**Milestone**: BearDog certified as FIRST TRUE ecoBin! 🎉

---

## 📞 **Support & Questions**

### **Where to Ask**

- **WateringHole**: Inter-primal discussions
- **BearDog Team**: ecoBin implementation questions
- **NestGate Team**: ecoBin migration questions
- **biomeOS Team**: Cross-compilation and tooling

### **Common Questions**

**Q: Do I have to become an ecoBin?**  
A: Not immediately, but strongly recommended! UniBin is mandatory, ecoBin is evolution target.

**Q: What if I need C dependencies for specific features?**  
A: Use feature gates! Core should be Pure Rust (ecoBin), advanced features optional.

**Q: Is musl considered a C dependency?**  
A: Technically yes, but it's INFRASTRUCTURE C (syscall wrapper), not APPLICATION C (security risk). See `MUSL_VS_PURE_RUST_NUANCE_JAN_17_2026.md`.

**Q: Can I be an ecoBin with rustls?**  
A: Only if you're Songbird (TLS primal)! All others should use Unix sockets, not HTTP/TLS.

**Q: How long does ecoBin migration take?**  
A: 2-4 weeks for Pure Rust migration (after UniBin achieved). Depends on complexity.

**Q: What if my primal needs HTTP?**  
A: Route through Songbird! Concentrated Gap Strategy: only Songbird handles external HTTP/TLS.

**Q: What's the difference between UniBin and ecoBin?**  
A: UniBin = structure (single binary, modes). ecoBin = UniBin + Pure Rust (zero C deps).

---

## 🎊 **Conclusion**

**ecoBin Architecture** is now the **official ecosystem standard** for **universal portable binaries** across all ecoPrimals.

**This standard**:
- ✅ Builds upon UniBin foundation
- ✅ Eliminates C security vulnerabilities
- ✅ Enables universal cross-compilation
- ✅ Simplifies deployment (no toolchains!)
- ✅ Showcases Pure Rust capabilities

**Compliance pathway**:
1. ✅ UniBin (structure)
2. ✅ Pure Rust (zero C deps)
3. ✅ musl cross-compilation
4. ✅ Universal deployment
5. 🎉 ecoBin certified!

**Together, we build a Pure Rust, universally portable, secure ecosystem!**

---

**Standard**: ecoBin Architecture v1.0.0  
**Adopted**: January 17, 2026  
**Authority**: WateringHole Consensus  
**Status**: 🌟 **ACTIVE ECOSYSTEM STANDARD** 🌟

---

🦀🧬✨ **ecoBin Architecture - Pure Rust, Universal Portability!** ✨🧬🦀

**UniBin Foundation | Pure Rust Security | Universal Deployment | Zero Toolchain Setup**

---

## 🎯 **Quick Reference Card**

### **The Golden Rules**

1. **UniBin First**: Achieve UniBin before ecoBin
2. **Zero Application C**: No openssl, ring, reqwest (except Songbird!)
3. **musl Test**: Must cross-compile to musl targets
4. **Unix Sockets Only**: No HTTP except Songbird
5. **RustCrypto Suite**: Use Pure Rust crypto
6. **Feature Gate C**: Optional advanced features can have C
7. **Static Binaries**: Universal deployment
8. **Celebrate Success**: Share lessons with ecosystem!

### **Quick Validation**

```bash
# Test ecoBin compliance:
cargo build --target x86_64-unknown-linux-musl
cargo tree | grep -E "(openssl-sys|ring|aws-lc-sys)"
ldd target/x86_64-unknown-linux-musl/release/primal

# Expected:
# ✅ Build succeeds (no C compiler!)
# ✅ Zero C dependencies found
# ✅ not a dynamic executable

# Result: TRUE ecoBin! 🎉
```

---

**Your primal can be the next TRUE ecoBin!** 🚀🦀✨


---

## 🌍 **ecoBin v2.0: Platform-Agnostic Evolution** (January 30, 2026)

### **The Learning: Pixel 8a Catalyst**

**What Happened:**
- Deployed BearDog to Pixel 8a (GrapheneOS, Android 16, ARM64)
- Binary worked perfectly (cross-architecture success!)
- Socket binding failed (platform assumption discovered!)

**The Discovery:**
```
❌ Unix sockets assumed: /run/user/1000/biomeos/beardog.sock
❌ SELinux blocked user-space Unix sockets on Android
✅ Learning: "Works on Linux" ≠ "Works everywhere"
✅ Insight: Platform assumptions are technical debt!
```

**The Philosophy:**
> **"If it can't run on the arch/platform, it's not a true ecoBin"**

---

### **v1.0 vs v2.0: The Evolution**

**ecoBin v1.0 (January 17, 2026):**
```
ecoBin = UniBin + Pure Rust + Cross-Architecture
Coverage: ~80% (Linux, macOS, BSD variants)
Limitation: Unix-centric (assumes Unix sockets, /run/user/, etc.)
```

**ecoBin v2.0 (January 30, 2026):**
```
ecoBin = UniBin + Pure Rust + Cross-Architecture + Cross-Platform
Coverage: 100% (anywhere Rust compiles)
Achievement: Platform-agnostic (runtime transport discovery)
```

---

### **Platform Coverage Matrix**

| Platform | Primary IPC | Fallback | v1.0 | v2.0 |
|----------|-------------|----------|------|------|
| **Linux (Desktop/Server)** | Unix sockets | TCP localhost | ✅ | ✅ |
| **Android (Mobile)** | Abstract sockets | TCP localhost | ❌ | ✅ |
| **Windows (Desktop)** | Named pipes | TCP localhost | ⚠️ | ✅ |
| **macOS (Desktop)** | Unix sockets | TCP localhost | ✅ | ✅ |
| **iOS (Mobile)** | XPC | TCP (sandboxed) | ❌ | ✅ |
| **WASM (Browser)** | In-process | N/A | ❌ | ✅ |
| **Embedded (Bare Metal)** | Shared memory | Custom | ⚠️ | ✅ |

**Key Insight**: v2.0 adds **7 full platforms** vs v1.0's **~3 platforms**

---

### **Platform-Agnostic IPC Architecture**

**The Problem (v1.0):**
```rust
// Unix-centric code (platform assumption!)
let socket = "/run/user/1000/biomeos/beardog.sock";
let listener = UnixListener::bind(socket)?;  // ❌ Fails on Android!
```

**The Solution (v2.0):**
```rust
// Platform-agnostic code (runtime discovery!)
use biomeos_ipc::PrimalServer;

let server = PrimalServer::start_multi_transport("beardog").await?;
// ✅ Automatically selects:
//    - Unix sockets on Linux/macOS
//    - Abstract sockets on Android (@biomeos_beardog)
//    - Named pipes on Windows (\\.\pipe\biomeos_beardog)
//    - XPC on iOS (org.biomeos.beardog)
//    - In-process channels on WASM
//    - Falls back to TCP localhost if native fails
```

---

### **Transport Selection Strategy**

**Priority Order:**
1. **Try:** Platform-native transport (fastest, most secure)
   - Unix sockets (Linux, macOS, BSD)
   - Abstract sockets (Android, Linux)
   - Named pipes (Windows)
   - XPC (iOS)
   - Shared memory (embedded)
2. **Fall back:** TCP localhost (universal, always works)
3. **Report:** Log selected transport for observability

**Performance Characteristics:**

| Transport | Latency | Throughput | Security | Availability |
|-----------|---------|------------|----------|--------------|
| Unix Sockets | ~5μs | 10GB/s | Excellent | Linux, macOS, BSD |
| Abstract Sockets | ~5μs | 10GB/s | Excellent | Android, Linux |
| Shared Memory | ~1μs | 50GB/s | Good | All (requires setup) |
| Named Pipes | ~10μs | 5GB/s | Excellent | Windows |
| TCP Localhost | ~50μs | 1GB/s | Good | **Universal** |
| In-Process | ~0.1μs | N/A | Excellent | WASM, embedded |

---

### **Implementation: biomeos-ipc Crate**

**Reference Implementation:**
See `biomeOS/docs/deep-debt/PLATFORM_AGNOSTIC_IPC_EVOLUTION.md`

**Core API:**
```rust
/// Platform-agnostic transport abstraction
pub enum Transport {
    UnixSocket { path: PathBuf },        // Linux, macOS, BSD
    AbstractSocket { name: String },     // Android, Linux
    NamedPipe { name: String },          // Windows
    SharedMemory { name: String },       // All platforms
    Tcp { host: String, port: u16 },    // Universal fallback
    InProcess { channel_id: Uuid },      // WASM, embedded
    PlatformSpecific(Box<dyn Platform>), // iOS XPC, Android Binder
}

/// Server: Automatic multi-transport binding
pub struct PrimalServer {
    pub async fn start_multi_transport(primal: &str) -> Result<Self>;
    pub async fn accept(&self) -> Result<PrimalConnection>;
    pub fn transports(&self) -> Vec<Transport>;
}

/// Client: Automatic transport discovery
pub struct PrimalClient {
    pub async fn connect(primal: &str) -> Result<Self>;
    pub async fn send(&mut self, request: JsonRpcRequest) -> Result<JsonRpcResponse>;
}

/// Runtime discovery
impl Transport {
    pub async fn discover_best(primal: &str) -> Result<Self> {
        // Automatic platform detection and selection
    }
}
```

---

### **Migration Guide for Primals**

**Step 1: Add Dependency**
```toml
[dependencies]
biomeos-ipc = "1.0"  # Platform-agnostic IPC layer
```

**Step 2: Replace Socket Code**
```rust
// Old (Unix-only - v1.0)
use tokio::net::UnixListener;
let socket = format!("{}/biomeos/{}.sock", xdg_runtime, primal);
let listener = UnixListener::bind(&socket)?;

// New (Universal - v2.0)
use biomeos_ipc::PrimalServer;
let server = PrimalServer::start_multi_transport(primal).await?;
// Automatically handles all platforms!
```

**Step 3: Test on All Platforms**
```bash
# Should work on ALL without code changes:
cargo build --target x86_64-unknown-linux-musl      # Linux → Unix
cargo build --target aarch64-linux-android          # Android → Abstract
cargo build --target x86_64-pc-windows-msvc         # Windows → Pipes
cargo build --target aarch64-apple-darwin           # macOS → Unix
cargo build --target aarch64-apple-ios              # iOS → XPC
cargo build --target wasm32-unknown-unknown         # WASM → In-process
```

**Step 4: Validate**
- ✅ Runs on all platforms without code changes
- ✅ Automatic transport selection
- ✅ Graceful fallback to TCP
- ✅ Zero platform assumptions

---

### **Adoption Timeline**

**Q1 2026 (Implementation Phase):**
- Week 1-2: Create `biomeos-ipc` crate (core abstractions)
- Week 3-4: Integrate into BearDog (pilot)
- Week 5-8: Roll out to all primals
- Week 9-12: Production deployment, documentation

**Expected Outcome:**
- 100% platform coverage (Linux, Android, Windows, macOS, iOS, WASM, embedded)
- Zero platform assumptions (no hardcoded paths)
- Automatic transport selection (prefer native, fall back to TCP)
- TRUE ecoBin achieved (works everywhere Rust compiles)

---

### **The Transformation**

**Before (v1.0):**
```
"Does it run on Linux?" → Yes
"Does it run on Android?" → Sorry, not supported
"Does it run on Windows?" → Theoretically, but...
"Does it run on iOS?" → No
```

**After (v2.0):**
```
"Does it run on Linux?" → Yes (Unix sockets)
"Does it run on Android?" → Yes (abstract sockets)
"Does it run on Windows?" → Yes (named pipes)
"Does it run on iOS?" → Yes (XPC)
"Does it run on WASM?" → Yes (in-process)
"Does it run everywhere?" → YES! (TCP fallback)
```

---

### **The Deep Debt Lesson**

**What We Learned:**
1. **Platform assumptions are technical debt** (even subtle ones like Unix sockets)
2. **Runtime discovery > compile-time hardcoding** (let the binary adapt)
3. **Abstraction enables universality** (one interface, many transports)
4. **Failures are teachers** (Pixel 8a issue → architectural evolution)

**The Philosophy:**
> "TRUE PRIMAL thinking: Turn limitations into innovations,  
> failures into learning, assumptions into abstractions,  
> and good into LEGENDARY!"

---

### **For Other Primals: The Call to Evolution**

**If your primal:**
- ✅ Uses Unix sockets directly → Migrate to `biomeos-ipc`
- ✅ Hardcodes socket paths → Use runtime discovery
- ✅ Assumes `/run/user/` → Remove assumption
- ✅ Has `#[cfg(unix)]` → Replace with universal API

**Result:**
Your primal becomes a TRUE ecoBin v2.0:
- Works on any architecture
- Works on any platform
- Zero assumptions
- 100% coverage

**Resources:**
- `biomeOS/ECOBIN_TRUE_PRIMAL_STANDARD.md` - Complete specification
- `biomeOS/docs/deep-debt/PLATFORM_AGNOSTIC_IPC_EVOLUTION.md` - Implementation guide
- `wateringHole/PRIMAL_IPC_PROTOCOL.md` - Updated IPC protocol (see v2.0 section)

---

**Status**: ✅ Standard Evolved (v2.0)  
**Date**: January 30, 2026  
**Impact**: From 80% to 100% platform coverage  
**Achievement**: TRUE ecoBin - works EVERYWHERE!

---

## Current Compliance (Wave 103, Jun 9 2026)

**Zero C-dep violations across the ecosystem.** (Wave 104, Jun 9 2026)

bearDog Wave 145 resolved the last C-crypto dependency: `aws-lc-rs` → `rustls-rustcrypto`
(pure Rust), `rcgen` → `p256` + `x509-cert`. `PURE_RUST_CRYPTO_PURITY_STANDARD.md`
published as ecosystem standard. `deny.toml` bans 19 C-crypto crates. sweetGrass `ring`
elimination resolved Wave 98. All primals are now pure Rust application code.

| Target Triple | Status | Blocker |
|---------------|--------|---------|
| `x86_64-unknown-linux-musl` | **14/14 depot, operational** (VPS authority) | — |
| `aarch64-unknown-linux-musl` | **14/14 BUILT** (Wave 105 sweep complete) | NDK android next |
| `aarch64-linux-android` | 6/13 running on grapheneGate (Pixel 8) | UDS adaptation for 7 primals |
| `x86_64-pc-windows-msvc` | 0/14 | Not yet attempted |
| `wasm32-wasi` | 0/14 | Design phase |

All non-x86 targets UNBLOCKED. aarch64-musl sweep COMPLETE. **All gates fetch from VPS depot.**

---

## plasmidBin Submission (ecoBin v3.0 Gate)

Every primal that passes ecoBin must submit its binary to `ecoPrimals/infra/plasmidBin/`.
This is the ecosystem's shared binary distribution surface.

**POST-PRIMORDIAL DEPLOYMENT STANDARD (Wave 105c)**:
- **peptidoglycan/VPS is the sole build authority** — all production binaries are built on peptidoglycan
- **All gates FETCH from VPS** (`membrane.primals.eco/depot/`) — no local rebuilds for deployment
- `checksums.toml` always reflects VPS/peptidoglycan output
- Local `cargo build --release` is for **development/testing ONLY** — never deployed to `plasmidBin/primals/`
- Violating this breaks the post-primordial deployment model

### Deployment (all gates)

```bash
# Fetch from VPS (the sole authority):
membrane plasmid.fetch --source vps

# Or direct fetch:
curl -o plasmidBin/primals/x86_64-unknown-linux-musl/YOUR_PRIMAL \
  https://membrane.primals.eco/depot/x86_64-unknown-linux-musl/YOUR_PRIMAL
chmod +x plasmidBin/primals/x86_64-unknown-linux-musl/YOUR_PRIMAL
```

### Build submission (peptidoglycan only)

```bash
# ON PEPTIDOGLYCAN (VPS build authority) ONLY:
cd /path/to/your-primal

# 1. Build musl-static for x86_64
cargo build --release --target x86_64-unknown-linux-musl

# 2. Verify ecoBin compliance
file target/x86_64-unknown-linux-musl/release/YOUR_PRIMAL
# Must say: "statically linked" and NOT "not stripped"

# 3. Cross-compile for aarch64 (if .cargo/config.toml is set up)
cargo build --release --target aarch64-unknown-linux-musl

# 4. Harvest into plasmidBin (peptidoglycan deploys to VPS depot)
membrane plasmid.harvest YOUR_PRIMAL
```

**DEPRECATED**: Direct local `cargo build` → `plasmidBin/primals/` on any gate.
If you are building locally and copying to depot, you broke post-primordial deployment.

### Compliance checklist

- [ ] `file` output says "statically linked" (musl, no glibc)
- [ ] `file` output does NOT say "not stripped"
- [ ] `ldd` says "statically linked" or "not a dynamic executable"
- [ ] Binary runs on Pixel/GrapheneOS via ADB (aarch64)
- [ ] Binary starts with TCP listener (`--listen` or `--port`)
- [ ] `health.liveness` responds over TCP JSON-RPC
- [ ] `b3sum` checksum recorded in `checksums.toml`

### Current inventory (March 31, 2026)

| Primal | x86_64 | aarch64 | ecoBin |
|--------|--------|---------|--------|
| beardog | A++ | A++ | Full |
| songbird | A++ | A++ | Full |
| nestgate | A++ | pending | x86 only |
| squirrel | A++ | A++ | Full |
| toadstool | A++ | A++ | Full |
| petaltongue | A++ | pending | x86 only |
| biomeos | A++ | A+ | Full (aarch64 unstripped) |
| coralreef | A++ | pending | x86 only (coralreef-core, coralctl; aarch64 build pending GPU driver evolution) |

See `plasmidBin/README.md` for the complete inventory and workflow.

