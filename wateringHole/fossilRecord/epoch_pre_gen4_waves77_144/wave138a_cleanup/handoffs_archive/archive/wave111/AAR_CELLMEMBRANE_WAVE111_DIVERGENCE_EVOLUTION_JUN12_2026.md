# AAR: cellMembrane — Wave 111 Divergence Evolution

**Date**: 2026-06-12  
**Team**: cellMembrane (ironGate)  
**Wave**: 111  
**Stream 6 Score**: 5/6 SHIPPED  
**Key Commits**: acab3f6, c8c2631, e80993f, e230e10

---

## Shipped (Stream 6 Divergence Scenarios)

### CASCADE-STALE-RECOVERY (acab3f6)
- **Scenario**: Gate 5+ commits behind with dirty worktree
- **Solution**: Auto-stash dirty worktree → ff-only pull → pop stash
- **Pattern**: Self-healing cascade handles any local drift without intervention
- **Deprecates**: Manual `git stash && git pull` on gates, `cascade-pull.sh`

### PARTIAL-FETCH-RESUME (acab3f6)
- **Scenario**: Kill during binary transfer (simulated via kill -9)
- **Solution**: Atomic write (temp file + rename), .tmp cleanup on startup, one-retry with 2s backoff
- **Pattern**: No partial state persists across interruptions
- **Deprecates**: Write-in-place binary fetch, partial downloads corrupting depot

### CANARY-STALENESS-AUDIT (e80993f)
- **Scenario**: Canary pool holds binaries from 3 waves ago, failover triggered
- **Solution**: Refuse failover if canary >168h stale (configurable `MEMBRANE_CANARY_MAX_AGE_HOURS`). `plasmid.canary.audit --refresh` auto-prunes stale entries.
- **Pattern**: Freshness-aware failover — never promote known-stale binaries
- **Deprecates**: Unconditional canary failover regardless of binary age

### CROSS-GATE-SKEW-REPORT (e80993f)
- **Scenario**: Newer songBird on VPS, older on eastGate
- **Solution**: `membrane health.audit --mesh` reports depot staleness per-primal and provenance commit mismatches vs VPS
- **Pattern**: Version awareness across the entire mesh from any gate
- **Deprecates**: Manual `git log` comparison across SSH sessions

### WAN-TIMEOUT-GRACEFUL (e80993f)
- **Scenario**: WAN disconnect during plasmid.refresh SCP transfer
- **Solution**: Exponential backoff (3 attempts: 2s/4s/8s), partial `.new` files cleaned on failure (rollback), diagnostic logging per attempt
- **Pattern**: Network operations always retry with backoff, never leave partial state
- **Deprecates**: Hard timeout → corrupt/partial state on network failure

---

## Additional Evolution (Non-Stream-6)

### 3-Tier Diesel Engine (e230e10)
- **gate.provision CLI**: DigitalOcean API v2 client (create/poll/destroy droplets)
- **Post-provision bootstrap**: SSH hardening, SCP binaries, systemd, mesh join, health sweep
- **canary-fieldmouse.toml**: Full NUCLEUS 13/13 warm standby profile
- **gate.provision / gate.provision.status / gate.provision.destroy** commands

### Deep Debt Evolution (c8c2631 + e230e10)
- cascade.rs: 877L → 390L (extracted `post_sync.rs`)
- All hardcoded primal names → `ServiceCapability` enum discovery
- `FALLBACK_CRYPTO_SIGNER`, `FALLBACK_MESH_RELAY`, `FALLBACK_CONTENT_SERVING` constants
- `SOVEREIGN_DOMAIN` → `resolve_sovereign_domain()` via `ENV_DEPOT_HOSTNAME`
- Pure Rust ELF validation (no external `file` command)
- Magic numbers → named constants
- Zero `unwrap`/`expect`/`todo`/`allow`/`unsafe` in production code

### Bash Fallback Removal (e230e10)
- `gate/mod.rs`: removed dead `cascade-pull.sh` fallback
- `pull()` and `check()` now directly invoke `membrane temporal.cascade` / `membrane temporal.check`
- **This is the final step in making gate operations fully deterministic**

### membrane.toml Header Update
- "Wave 63: Three-node diderm" → "Wave 111: 3-tier diesel engine" with canary fieldMouse topology

---

## Remaining (1/6)

| ID | Scenario | Notes |
|----|----------|-------|
| SANDBOX-DEPENDENCY-CHAIN | Sandbox primal requiring bearDog — bearDog not started | Design decision needed: start prereqs automatically, or skip-with-warning? |

---

## Convergence Criteria for cellMembrane

The following must be true before old patterns are fully deprecated:

1. ✅ `cascade-pull.sh` removed from code
2. ⚠️ All active gates running post-e230e10 binary (ironGate local binary is older)
3. ⚠️ One full cascade cycle post-e230e10 with zero manual intervention
4. ⚠️ NUC canary bootstrapped with canary-fieldmouse profile
5. ❌ SANDBOX-DEPENDENCY-CHAIN resolved

**Action for ironGate**: `cargo install --path crates/membrane-shadow` to activate
the full diesel engine locally. After that, `membrane temporal.cascade` will use the
pure Rust path on all subsequent invocations.

---

## Test State

- 377/377 tests green
- Zero clippy warnings
- `#![forbid(unsafe_code)]` on both crates (cellmembrane-types + membrane-shadow)
- Full rebuild from clean: 7.88s
- 1.2 GiB build artifacts reclaimed via cargo clean
