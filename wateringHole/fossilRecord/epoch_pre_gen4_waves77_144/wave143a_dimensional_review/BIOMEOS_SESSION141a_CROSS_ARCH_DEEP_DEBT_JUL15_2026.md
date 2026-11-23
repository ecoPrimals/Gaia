# biomeOS — Wave 141a Handoff (Jul 15, 2026)

**Session**: Cross-Architecture Adoption + Deep Debt Evolution
**Version**: v4.34
**Gate**: Tower (eastGate)

---

## Completed Work

### 1. Cross-Architecture: `x86_64-pc-windows-gnu` (P2 from Wave 141a)

All UDS/tarpc/rustix references gated behind `#[cfg(unix)]` with `#[cfg(windows)]` stubs:

| Crate | Files Modified |
|-------|---------------|
| `biomeos-primal-sdk` | communication, capabilities, provider, discovery, tarpc_transport |
| `neural-api-client` | connection |
| `biomeos-nucleus` | client/transport |
| `biomeos-system` | disk, network, lib |
| `biomeos-graph` | ai_advisor_discovery |
| `biomeos-federation` | discovery/mod, unix_socket_client |
| `biomeos-spore` | verify, incubation/local_entropy |
| `biomeos-api` | unix_server, handlers/live_discovery |
| `biomeos-atomic-deploy` | 13+ files (executor, handlers, neural_api_server, protocol_escalation, tarpc_client, primal_launcher) |
| `biomeos` (binary) | modes/continuous, nucleus/remote, nucleus_ingest, nucleus_procs, rootpulse, proc_metrics |

**Result**: `cargo check --target x86_64-pc-windows-gnu` passes clean.

### 2. Stub Evolution (6 placeholders → real implementations)

| Stub | Before | After |
|------|--------|-------|
| `diagnose_degradation()` | Always `TransportLatency` | Checks packet_loss, latency_ms, connection/encryption status, key rotation |
| `optimize_transport_path()` | Log + `Ok(())` | TCP fallback discovery via env, mark path degraded, update routing preference |
| `execution_order()` | Declaration order | Kahn's algorithm with cycle detection + unknown-dep errors |
| `fetch_binary()` | String body | Base64/byte-array decoding + Content-Length verification |
| `collect_edge_metrics()` | Synthetic 1.5–5ms | Live socket probe (500ms timeout), `None` on failure |
| `with_feature()` | No-op warn | Typed `FeatureFlags` application (12+ named features + custom map) |
| `lineage_deriver` (raw seed) | All "unknown" | SHA-256 device_id, first-8-bytes family_id, "raw_seed" provenance |

### 3. Capability-First Discovery Architecture

- `CAPABILITY_DOMAINS` renamed to `BOOTSTRAP_CAPABILITY_HINTS` (last-resort fallback)
- Runtime registry: `LazyLock<DashMap<String, String>>` populated by live `capability.register` events
- Two-tier lookup: runtime registry → bootstrap hints
- Same pattern in `biomeos-primal-sdk` discovery (runtime cache from socket probes)

### 4. Error Propagation (5 swallowed errors → structured)

- Topology capability probes: `CapabilityQueryResult { capabilities, error }`
- Discovery socket probes: `DiscoveredPrimal.error: Option<String>`
- Federation queries: error stored on result + `warn!` logging
- Nucleus insecure discovery: `UNRESOLVED_NODE_ID` sentinel

### 5. Clone Reduction (hot-path audit)

8 production hot paths optimized: `JsonRpcRequest::serialize_line()`, iterator-by-value discovery, single-lock health snapshots, topo sort move, MCP key move, PathBuf filter-before-clone, startup timeout borrow.

### 6. Test File Refactoring (30+ monoliths split)

All test files previously >450 LOC split into domain-focused submodules. Largest remaining: 650L. Down from 1028L peak at session start.

---

## Metrics

| Metric | Value |
|--------|-------|
| Rust files | 1,217 |
| Total LOC | 294,898 (213K prod + 64K test + 18K integration) |
| Tests | 8,446+ (421 pass, 1 pre-existing unrelated failure) |
| Production files >800L | 0 |
| Test files >650L | 0 |
| `unsafe` blocks | 0 |
| `cargo check` | PASS (Unix + Windows-gnu) |

---

## Known Issues / Upstream Gaps

### Pre-existing Test Failure
- `handlers::capability::tests::test_get_standalone_providers_filter_contract` — assertion failure in capability handler. Predates this session. Needs investigation by API team.

### Remaining Hardcoding (bootstrap-tier, documented)
- `NucleusMode::primals()` returns fixed primal lists per mode (startup ordering)
- `CORE_PRIMALS` / `PROVENANCE_PRIMALS` constants used in health polling
- ~12 files with `.unwrap_or_else(|| BEARDOG/SONGBIRD)` as last-resort in 3-tier resolution
- All documented as `BOOTSTRAP_CAPABILITY_HINTS` pattern; runtime registry takes precedence when live

### Boot/Init Stubs (P3 — hardware-specific)
- `detect_biomeos_usb()`: scans hardcoded `/dev/sda1-sdc1` (needs udev/sysfs enumeration)
- Recovery path: sleeps 300s instead of spawning shell (init context)
- Chimera builder: shell script launcher (compiled binary deferred)

### Windows Stubs (P3 — deferred to Named Pipes implementation)
- All Windows paths currently bail with "unavailable on Windows; use TCP"
- TCP transport wiring is the next evolution step for Windows support

---

## For Upstream Primal Teams

### biomeOS provides to downstream:
- Cross-arch `cargo check --target x86_64-pc-windows-gnu` passes
- Runtime capability registry API: `register_capability_provider(capability, provider)`
- `BOOTSTRAP_CAPABILITY_HINTS` as documented fallback table
- Error context on discovery/topology probes (new `error` field on `DiscoveredPrimal`)

### biomeOS needs from upstream:
- **primalSpring**: FIDO2 ClientPIN scenario definitions (6 scenarios per Wave 138b)
- **eastGate**: Named Pipes transport implementation for full Windows support
- **overwatch**: Audit of pre-existing `test_get_standalone_providers_filter_contract` failure

---

## Next Evolution Targets

1. Split remaining 39 test files in 450-650L range (diminishing returns, low priority)
2. Named Pipes transport for Windows (currently TCP fallback)
3. USB detection via sysfs/udev instead of hardcoded device paths
4. Evolve `NucleusMode::primals()` to capability-discovered startup ordering
