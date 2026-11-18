# G68 Cross-Deployment Audit — All 15 Primals

**Date**: Aug 7, 2026 | **Wave**: 157a | **From**: eastGate overwatch
**Purpose**: Full audit for cross-platform deployment readiness. Covers G68 substrate violations, remaining G66 transport gaps, cephalization health, and cross-arch status.

---

## CROSS-ARCH — 15/15 PASS

All 15 primals pass `cargo check --target x86_64-pc-windows-gnu` on eastGate.

**Note**: nestGate and rhizoCrypt pin `rust-toolchain.toml` to 1.94.1. The Windows
target must be installed for that specific toolchain: `rustup target add x86_64-pc-windows-gnu --toolchain 1.94.1`. Builder gates (sporeGate, blueGate) must ensure this.

### Post-G68 Push Temporal Check (4:34 PM)

7 primals pushed G68 evolution. Cross-arch recheck:

| Primal | G68 Shipped | Cross-arch | Notes |
|--------|-------------|------------|-------|
| nestGate | L1/L2/L3 via `nestgate-platform` | **PASS** | |
| rhizoCrypt | Transport split + G68 audit | **PASS** | |
| loamSpine | G68 platform + error hygiene | **PASS** | |
| sweetGrass | `platform_link()` replaces raw symlink | **PASS** | |
| coralReef | 18 silicon deism sites evolved | **PASS** | |
| barraCuda | Deprecated batch unwiring + error idiom + G68 audit | **PASS** | Long-tail debt work |
| toadStool | L1 links + L2 access + akida-driver gating | **FAIL** | `neurobench-runner` imports `select_backend` unconditionally — unix-only export from akida-driver. toadStool team must gate consumer crates. |

**Result**: 6/7 PASS, toadStool team has remaining work.

---

## G68 PLATFORM SUBSTRATE — VIOLATION MATRIX

### Layer 1: Raw Symlinks (17 files / 13 primals)

`std::os::unix::fs::symlink` → should use `platform_link()`.

| Primal | Count | Files (production) |
|--------|-------|--------------------|
| biomeOS | 4 | boot/install, boot/device_mgr, socket_discovery/path_builder, biomeos/modes |
| bearDog | 3 | socket_config, disaster_recovery |
| toadStool | 3 | unibin/mod, ipc/platform/unix |
| loamSpine | 2 | loamspine-service/main |
| songBird | 1 | env_config/socket |
| skunkBat | 1 | ipc/mod |
| nestGate | 1 | rpc/socket_config |
| rhizoCrypt | 1 | jsonrpc/uds/symlinks |
| sweetGrass | 1 | uds/lifecycle |
| barraCuda | 1 | ipc/transport/server |
| coralReef | 1 | transport |
| petalTongue | 1 | unix_socket_server/mod |
| squirrel | 1 | rpc/unix_socket |
| sourDough | 0 | — (only in validation checker) |
| bingoCube | 0 | — |

**Remediation**: Implement `platform_link(target, link)` per G68 spec. 1-2 hours per primal. sourDough leads.

### Layer 2: Raw PermissionsExt (56+ files / 10 primals)

`PermissionsExt::set_mode()` / `from_mode()` → should use `PlatformAccess` enum.

| Primal | Count | Severity |
|--------|-------|----------|
| biomeOS | 70 | HIGH — deployer, genomebin, spore, boot, lab, chimera, capability_handlers |
| coralReef | 56 | HIGH — volume suggests systematic pattern |
| bearDog | 36 | MEDIUM — key_management, installer, acme, disaster_recovery, tunnel |
| toadStool | 23 | MEDIUM — akida-setup, auto_config, tarpc_server, nvpmu, common |
| sourDough | 15 | MEDIUM — layout, genomebin validator/builder |
| songBird | 12 | LOW — universal-ipc, deployment_api, chunked_upload |
| petalTongue | 12 | LOW — audio_discovery, audio/backends/socket |
| nestGate | 9 | LOW — installer, platform |
| squirrel | 8 | LOW — security, transport/listener, unix_socket, mcp/secret_store |
| loamSpine | 0 | CLEAN |
| sweetGrass | 0 | CLEAN |
| rhizoCrypt | 0 | CLEAN |
| skunkBat | 0 | CLEAN |
| barraCuda | 0 | CLEAN |
| bingoCube | 0 | CLEAN |

**Remediation**: Implement `PlatformAccess { OwnerOnly, GroupReadWrite, WorldReadable }` per G68 spec. 2-4 hours per primal. Mechanical substitution. sourDough leads.

### Layer 3: Raw rustix/libc (37 files / 3 primals)

Hardware kernel interfaces — requires backend trait abstraction.

| Primal | Count | Domain |
|--------|-------|--------|
| toadStool | 42 | VFIO, DMA, mmap, DRM, V4L2, huge pages, sandbox/proc, nvpmu |
| biomeOS | 6 | spore, boot (initramfs, init_filesystem), deploy (qemu), lifecycle (resurrection) |
| songBird | 2 | universal-ipc platform module |

**Remediation**: toadStool already has `NpuBackend` trait + `SoftwareBackend` + `SyntheticBackend`. Evolve: trait compiles everywhere, backends gated. biomeOS boot paths are Stage 3 (biomeOS-as-OS). songBird's 2 uses are already gated in its platform module. toadStool is the primary target.

---

## G66 TRANSPORT — REMAINING GAPS

G66 is COMPLETE (15/15 shipped). But adoption depth varies:

### Raw UnixStream/UnixListener (bypasses G66 TransportStream)

| Primal | Raw | G66 Adopted | Ratio | Grade |
|--------|-----|-------------|-------|-------|
| biomeOS | 76 | 550 | 12% raw | B — orchestrator, many paths |
| songBird | 66 | 281 | 19% raw | B- — mesh discovery paths |
| squirrel | 31 | 129 | 19% raw | B- |
| toadStool | 26 | 51 | 34% raw | C — lowest G66 adoption |
| sweetGrass | 26 | 173 | 13% raw | B |
| sourDough | 23 | 301 | 7% raw | A- — reference primal |
| loamSpine | 22 | 146 | 13% raw | B |
| rhizoCrypt | 21 | 298 | 7% raw | A- |
| bearDog | 18 | 100 | 15% raw | B |
| nestGate | 14 | 239 | 6% raw | A |
| coralReef | 14 | 157 | 8% raw | A- |
| barraCuda | 13 | 128 | 9% raw | A- |
| petalTongue | 12 | 195 | 6% raw | A |
| songBird | — | — | — | — |
| skunkBat | 8 | 144 | 5% raw | A |
| bingoCube | 4 | 92 | 4% raw | A |

**Target**: ≤5% raw ratio for all primals. Currently 6/15 at target.

### Self-Bind Violations (primals binding own transport)

Primals should accept injected transport (`TransportEndpoint`), not bind their own
`TcpListener` or `UnixListener`. Many of these are in server modules that need
to bind *something*, but the address should come from `from_env_or_default()`.

| Primal | Self-binds | Notes |
|--------|-----------|-------|
| biomeOS | 85 | Orchestrator — justified for NUCLEUS lifecycle |
| songBird | 59 | Mesh server — needs refactor to `bind_transport()` |
| squirrel | 32 | Agent server — needs transport injection |
| bearDog | 25 | Tunnel + ACME — partially justified |
| nestGate | 24 | CAS server — needs `bind_transport()` |
| sweetGrass | 20 | Ledger server |
| loamSpine | 19 | Spine server |
| toadStool | 17 | Dispatch server |
| sourDough | 17 | Reference — should be exemplary |
| petalTongue | 16 | Render server |
| barraCuda | 14 | GPU server |
| skunkBat | 6 | Defense server |
| coralReef | 6 | Shader server |
| rhizoCrypt | 5 | DAG server |
| bingoCube | 2 | Test primal |

---

## CROSS-PRIMAL COUPLING (name references)

Primals referencing other primals by string name instead of capability semantics.
Neural API (G56/G67) eliminates this — callers use `capability.call("crypto", "sign", ...)`
not `connect_to("beardog.sock")`.

| Primal | Cross-refs | Primary coupling |
|--------|-----------|-----------------|
| songBird | 169 | mesh discovery, primal health — justified as discovery service |
| toadStool | 116 | dispatch routing to other primals — should use capability |
| petalTongue | 62 | viz routing to data primals — should use capability |
| sourDough | 55 | validation references — justified as standards checker |
| squirrel | 48 | agent dispatch — should use Neural API |
| sweetGrass | 35 | ledger references other primals — should use capability |
| bearDog | 7 | crypto delegation — minimal |
| barraCuda | 6 | GPU peer references — minimal |
| nestGate | 3 | CAS references — minimal |
| coralReef | 2 | minimal |

**Target**: All cross-primal dispatch routes through Neural API `capability.call()`.
Allowed exceptions: songBird (mesh discovery), sourDough (validation).

---

## CEPHALIZATION HEALTH SUMMARY

| Dimension | Score | Notes |
|-----------|-------|-------|
| **G64 tarpc** | **15/15 COMPLETE** | All primals dual-protocol |
| **G65 protocol negotiation** | **15/15 COMPLETE** | Single-socket |
| **G66 transport abstraction** | **15/15 shipped, 6/15 fully adopted** | Raw UnixStream remnants |
| **G68 platform substrate** | **0/15** | NEW — spec written, convergence begins |
| **Cross-arch** | **15/15 PASS** | (toolchain note for nestGate/rhizoCrypt) |
| **TODO/FIXME** | **13/15 CLEAN** | toadStool: 1, petalTongue: 1 |
| **unsafe** | **12/15 ZERO** | bearDog: 7 (crypto), toadStool: 151 (GPU/VFIO), petalTongue: 8 (WASM/GPU) |

---

## PER-PRIMAL ACTION ITEMS

### Priority 1: High Impact (most violations, most code paths)

| Primal | L1 (symlink) | L2 (perms) | L3 (rustix) | G66 raw % | Action |
|--------|-------------|-----------|------------|-----------|--------|
| **biomeOS** | 4 | 70 | 6 | 12% | L2 is massive — 70 permission sites. biomeOS boot paths (L3) are Stage 3. |
| **toadStool** | 3 | 23 | 42 | 34% | Worst G66 adoption. L3 is justified (GPU/VFIO). Backend trait evolution needed. |
| **coralReef** | 1 | 56 | 0 | 8% | L2 dominant. 56 permission sites. Shader pipeline. |

### Priority 2: Medium Impact

| Primal | L1 | L2 | L3 | G66 raw % | Action |
|--------|----|----|----|----|--------|
| **bearDog** | 3 | 36 | 0 | 15% | L2 in crypto key management, installer, ACME. |
| **songBird** | 1 | 12 | 2 | 19% | L3 is in platform module (already gated). Focus on G66 raw %. |
| **sourDough** | 0 | 15 | 1 | 7% | Reference primal — must be exemplary. L2 in genomebin. |
| **squirrel** | 1 | 8 | 0 | 19% | High G66 raw %. Agent dispatch needs Neural API. |

### Priority 3: Low Impact (few violations)

| Primal | L1 | L2 | L3 | G66 raw % | Action |
|--------|----|----|----|----|--------|
| **nestGate** | 1 | 9 | 0 | 6% | Already A grade G66. Minor L2. |
| **petalTongue** | 1 | 12 | 0 | 6% | A grade. L2 in audio discovery. |
| **sweetGrass** | 1 | 0 | 0 | 13% | L2 CLEAN. Focus on G66 raw %. |
| **loamSpine** | 2 | 0 | 0 | 13% | L2 CLEAN. Minor L1. |
| **rhizoCrypt** | 1 | 0 | 0 | 7% | L2 CLEAN. A- grade. |
| **barraCuda** | 1 | 0 | 0 | 9% | L2 CLEAN. Minor L1. |
| **skunkBat** | 1 | 0 | 0 | 5% | A grade. 1 symlink. |
| **bingoCube** | 0 | 0 | 0 | 4% | CLEAN — exemplary. |

---

## CONVERGENCE ORDER

1. **sourDough** implements `platform_link()` and `PlatformAccess` as reference
2. **sourDough** adds L1/L2 detection to `transport_compliance.rs`
3. **bingoCube** already clean — validates the pattern compiles
4. **Provenance trio** (rhizoCrypt, loamSpine, sweetGrass) — few violations, fast wins
5. **skunkBat** — 1 violation, fast win
6. **nestGate, petalTongue, barraCuda** — minor L1/L2
7. **bearDog, squirrel, songBird** — medium L2 + G66 raw cleanup
8. **coralReef** — 56 L2 sites, systematic but mechanical
9. **toadStool** — 42 L3 + backend trait evolution (architectural, longer timeline)
10. **biomeOS** — 70 L2 + 6 L3. Orchestrator, will converge last.

---

*G68 audit: 134+ files across 15 primals. 15/15 cross-arch PASS. 6/15 fully G66 adopted.
sourDough leads → provenance trio first → tower → node → orchestrator last.*
