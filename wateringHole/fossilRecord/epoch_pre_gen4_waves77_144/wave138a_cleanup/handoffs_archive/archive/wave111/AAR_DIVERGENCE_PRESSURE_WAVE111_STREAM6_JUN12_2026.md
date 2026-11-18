# AAR: Stream 6 Divergence Pressure — Wave 111 Results

**Date**: 2026-06-12  
**From**: eastGate overwatch  
**Wave**: 111  
**Status**: 13/16 scenarios SHIPPED — convergence criteria emerging

---

## Strategic Context

Wave 111 intentionally applied divergence pressure across the ecosystem to force
cellMembrane, songBird, biomeOS, and primalSpring to evolve robustness primitives
that WAN (ionic) and portable (weak) bonding depend on. LAN gates are forgiving —
sub-millisecond, always-on. The hypothesis: break things NOW in controlled ways,
and the fixes become the reliability substrate for non-LAN bonds.

**Result**: The hypothesis held. 13/16 scenarios resolved, all producing auto-recovery
or actionable diagnostics. The ecosystem is converging on patterns that make old
approaches obsolete.

---

## Scenario Results (13/16)

### cellMembrane — 5/6 DONE

| ID | Scenario | Resolution | Old Pattern Deprecated |
|----|----------|-----------|----------------------|
| CASCADE-STALE-RECOVERY | Gate 5+ commits behind, dirty worktree | Auto-stash, ff-only pull, pop. Handles any drift. | Manual `git stash && git pull` scripts |
| PARTIAL-FETCH-RESUME | Kill during binary transfer | Atomic write (temp+rename), .tmp cleanup on start, retry | Partial binaries left corrupting depot |
| CANARY-STALENESS-AUDIT | Failover to 3-wave-old canary | Refuse if >168h stale (configurable). `plasmid.canary.audit --refresh` prunes. | Unconditional failover to any canary |
| CROSS-GATE-SKEW-REPORT | Version mismatch across mesh | `health.audit --mesh` reports per-primal staleness + provenance mismatch | Manual comparison of versions across gates |
| WAN-TIMEOUT-GRACEFUL | Disconnect during plasmid.refresh | Exponential backoff (2s/4s/8s), partial .new rollback, diagnostic logging | Hard timeout → corrupt state |
| SANDBOX-DEPENDENCY-CHAIN | Sandbox primal needs unstarted prereq | **PENDING** | — |

### songBird — 4/4 DONE (ALL COMPLETE)

| ID | Scenario | Resolution | Old Pattern Deprecated |
|----|----------|-----------|----------------------|
| FEDERATION-STATUS-WIRE | Status RPC doesn't read env vars | Reads SONGBIRD_FEDERATION_ENABLED/PEERS/PORT in bin_interface | Hardcoded false in status response |
| FEDERATION-RECONNECT | VPS restart → peer lost | spawn_peer_health_loop, 30s probe, exponential backoff to 300s cap | Manual mesh.init after every restart |
| MESH-PARTITION-TOLERANCE | Partial mesh split (VPS reachable from A but not B) | Cross-gate reachability gossip, PartialPartition/LocallyUnreachable states | Silent failure — mesh.status lies |
| PEER-VERSION-MISMATCH | v0.2.0 on one gate, v0.2.1 on another | Version negotiation, backward-compatible wire, version_skew array in status | Protocol break on minor version bump |

### primalSpring — 3/3 DONE (ALL COMPLETE)

| ID | Scenario | Resolution | Old Pattern Deprecated |
|----|----------|-----------|----------------------|
| S_VERSION_SKEW | Detect semver divergence across NUCLEUS | s_version_skew_detection scenario + wetSpring mesh_health endpoint | No detection — silent divergence |
| S_CASCADE_REGRESSION | Validate post-cascade matches provenance | s_cascade_provenance_match scenario | Trust cascade without verification |
| S_WAN_LATENCY_TOLERANCE | IPC over high-latency link | s_wan_ipc_tolerance with configurable threshold | Assume LAN latency everywhere |

### biomeOS — 2/2 DONE (ALL COMPLETE)

| ID | Scenario | Resolution | Old Pattern Deprecated |
|----|----------|-----------|----------------------|
| DISCOVERY-STALE-PRUNE | Primal dies, registration lingers | unregister_primal() + prune_stale_registrations() + 60s background sweep | Ghost registrations accumulate |
| ROUTING-PARTITION-AWARE | Unreachable segment | all_circuits_open detection, mesh fallback before hard error | Routing blocks indefinitely on dead peer |

### ops — 0/2 PENDING (Require Hardware)

| ID | Scenario | Blocked By |
|----|----------|-----------|
| DEPLOY-THEN-STALE | Deploy westGate, skip cascades 2 waves | westGate hardware setup |
| WINDOWS-ECOBIN-DIVERGENCE | ecoBin on blueGate (Windows/WSL2) | blueGate access |

---

## Patterns Now Proven (Convergence Gate)

These patterns are now validated and tested. They represent the NEW standard that
replaces legacy approaches. Once all gates run binaries built from these commits,
the old patterns can be **permanently deprecated**.

### 1. Atomic Operations (Replace Partial-State)

**Pattern**: Every mutation (fetch, cascade, provision) uses temp-file + atomic-rename.
Interruption at any point leaves the system in the previous good state.

**Proven by**: PARTIAL-FETCH-RESUME, WAN-TIMEOUT-GRACEFUL  
**Commits**: acab3f6, e80993f  
**Deprecates**: Write-in-place, partial downloads left as-is

### 2. Exponential Backoff with Rollback (Replace Hard Timeouts)

**Pattern**: All network operations retry with exponential backoff. Failure at any
attempt rolls back partial state and logs diagnostics per-attempt.

**Proven by**: WAN-TIMEOUT-GRACEFUL, FEDERATION-RECONNECT  
**Commits**: e80993f (cellMembrane), f18aeb6b (songBird)  
**Deprecates**: Single-attempt with hard timeout, silent failures

### 3. Capability-Based Discovery (Replace Hardcoded Names)

**Pattern**: Primals are discovered by capability (ServiceCapability enum), not by
hardcoded name strings. Fallback constants exist but are resolved via capability first.

**Proven by**: e230e10 deep debt evolution  
**Deprecates**: Hardcoded `"beardog"`, `"songbird"` strings in dispatch paths

### 4. Freshness-Aware Failover (Replace Unconditional Canary)

**Pattern**: Canary failover checks staleness before promotion. Stale canaries (>168h)
are refused. `plasmid.canary.audit --refresh` maintains canary freshness.

**Proven by**: CANARY-STALENESS-AUDIT  
**Commit**: e80993f  
**Deprecates**: Blind failover to any available canary regardless of age

### 5. Cross-Gate Version Awareness (Replace Blind Mesh)

**Pattern**: Every gate knows the versions of its peers. Skew is reported in status.
Partitions are detected via reachability gossip. Degradation is graceful.

**Proven by**: CROSS-GATE-SKEW-REPORT, MESH-PARTITION-TOLERANCE, PEER-VERSION-MISMATCH  
**Commits**: e80993f (cellMembrane), 9903cf50 (songBird)  
**Deprecates**: Mesh assumes all peers run same version, partitions are invisible

### 6. Self-Healing Cascade (Replace Manual Git Operations)

**Pattern**: `temporal.cascade` handles dirty worktrees (auto-stash), diverged branches
(ff-only with clear error), and multi-commit drift. No manual intervention.

**Proven by**: CASCADE-STALE-RECOVERY  
**Commit**: acab3f6  
**Deprecates**: `cascade-pull.sh` bash scripts, manual `git stash && git pull`

### 7. Pure Rust Gate Operations (Replace Bash Fallbacks)

**Pattern**: All gate operations (pull, check, cascade, provision) are pure Rust
invocations of `membrane temporal.*` and `membrane plasmid.*`. No subprocess bash.

**Proven by**: e230e10 (bash fallback removal from gate/mod.rs)  
**Deprecates**: `cascade-pull.sh`, shell script fallback paths

### 8. Health-Aware Orchestration (Replace Ghost Registrations)

**Pattern**: biomeOS prunes stale registrations (60s sweep), routes around dead peers
(all_circuits_open detection), and falls back to mesh before hard errors.

**Proven by**: DISCOVERY-STALE-PRUNE, ROUTING-PARTITION-AWARE  
**Commit**: 249bce28 (biomeOS v4.24)  
**Deprecates**: Registrations that persist after primal death, routing that blocks on dead peers

---

## Convergence Criteria — When to Deprecate Old Patterns

The system is converging toward stability. The following criteria determine when
old patterns can be permanently removed (dead code excision):

| Criterion | Condition | Current State |
|-----------|-----------|---------------|
| **All gates run post-e230e10 membrane** | `membrane --version` shows ≥ Wave 111 build on all 5 active gates | ⚠️ ironGate local binary is older. VPS has it. |
| **Depot songBird includes partition tolerance** | provenance.toml shows songBird ≥ 9903cf50 | ❌ Depot has 32a8d700 — needs harvest |
| **flockGate federation handshake validated** | active_connections > 0, latency_ms measured | ❌ Blocked on depot rebuild |
| **No gate uses cascade-pull.sh** | No subprocess bash calls in any gate.pull/check | ✅ Code removed in e230e10 |
| **canary.audit passes on all canary nodes** | `plasmid.canary.audit` returns 0 stale on all canaries | ⚠️ NUC canary not yet bootstrapped |
| **2 full cascade cycles with zero manual intervention** | temporal.cascade runs twice across all gates with no human fix-up | ⚠️ Not yet tested post-e230e10 |

**Gate clearance**: When ALL criteria above are GREEN, the following can be permanently excised:
1. Any remaining bash script references in documentation
2. Legacy `cascade-pull.sh` mentions in RUNBOOKS
3. Hardcoded primal name strings (replaced by ServiceCapability)
4. Unconditional canary failover logic (replaced by freshness-aware)
5. Single-attempt fetch without backoff (replaced by exponential retry)

---

## Remaining Work (3/16)

| ID | Owner | Blocked By | Expected Wave |
|----|-------|-----------|---------------|
| SANDBOX-DEPENDENCY-CHAIN | cellMembrane | Design decision (skip-with-warning vs start-prereqs) | 112 |
| DEPLOY-THEN-STALE | ops | westGate hardware setup | 112+ |
| WINDOWS-ECOBIN-DIVERGENCE | ops | blueGate access | 112+ |

---

## Lessons Learned

1. **Divergence pressure works.** 13/16 scenarios resolved within 1 wave. The pressure
   revealed real gaps (canary staleness, WAN timeouts, partition blindness) that would
   have been invisible under LAN-only testing.

2. **Team velocity correlates with divergence exposure.** songBird (WAN-exposed) shipped
   4/4 fastest. cellMembrane (infrastructure-exposed) shipped 5/6. ops items (hardware-blocked)
   are the only laggards — divergence pressure can't substitute for physical access.

3. **The bash fallback was load-bearing longer than expected.** Removing it (e230e10) was
   the final step in making gate operations fully deterministic. Until that commit, any
   cascade could silently fall through to shell semantics.

4. **Capability-based discovery is the architectural multiplier.** Once primals are
   discovered by what they DO (ServiceCapability) rather than what they're NAMED,
   the system becomes topology-agnostic — a prerequisite for ionic/weak bonding.

---

## Recommendation

**Hold on deprecating old patterns until the convergence criteria are all GREEN.**
The code is ready (patterns proven, implementations shipped). The operational state
needs 2 more steps:
1. `plasmid.harvest --targets songbird` on VPS (depot rebuild)
2. One full cascade cycle across all 5 active gates post-e230e10

After that: excise dead patterns, close Wave 111, and enter Wave 112 with the
remaining 3 ops-blocked scenarios as the only carry items.
