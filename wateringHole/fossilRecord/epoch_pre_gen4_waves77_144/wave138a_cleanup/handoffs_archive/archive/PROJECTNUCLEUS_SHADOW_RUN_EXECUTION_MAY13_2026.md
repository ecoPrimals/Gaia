# projectNUCLEUS — Shadow Run Execution & Baseline Fixes (May 13, 2026)

**Scope**: Execute shadow runs, fix DoT/tunnel baselines, start BearDog H2-12, resolve proposed APIs
**Canonical tracker**: `sporeGarden/projectNUCLEUS/specs/EVOLUTION_GAPS.md`

---

## Changes

### 1. DoT Baseline Fixed

**Problem**: `dot_sovereign_parity.sh` captured 0/10 success on all domains. `dig` not installed; DoT detection regex didn't match `+DNSOverTLS` format from `resolvectl status`.

**Fix**:
- Replaced `dig` with `resolvectl query` → `dig @127.0.0.53` → `getent hosts` fallback chain
- Fixed DoT detection: `grep -q "+DNSOverTLS"` instead of regex pattern matching
- **Result**: 10/10 success, 3-8ms latency, DoT ACTIVE via Cloudflare 1.0.0.1

### 2. Tunnel Baseline Uptime Fix

**Problem**: `tunnel_baseline_*.toml` showed `uptime_pct = 0` but had valid latency numbers (109ms TTFB). HTTP 502 responses were counted as failures.

**Fix**:
- Added `tunnel_reachable_pct` metric: counts any non-timeout HTTP response (TLS connected)
- `uptime_pct` remains HTTP 200 only (service availability)
- **Result**: tunnel_reachable_pct = 100%, uptime_pct = 0% (expected — no hub running)

### 3. BearDog TLS Shadow LIVE (H2-12)

**Problem**: `deploy_beardog_tls_shadow.sh` used `--tls-cert`/`--tls-key` flags that don't exist in BearDog v0.9.0.

**Fix**:
- Updated to use `--listen`/`--family-id`/`--audit-dir` (actual v0.9.0 CLI)
- BearDog v0.9.0 running on :8443 with 200+ methods, BTSP v2.0, Ed25519 signed announcement
- **Baseline**: 10ms RPC latency vs 120ms Cloudflare tunnel
- `btsp_tls_parity.sh` ready for 7-day comparison

### 4. Proposed API Methods Resolved

| Proposed | Resolution |
|----------|-----------|
| `biomeos.spring_status` | Use `capabilities.list` on each primal via Songbird discovery |
| `nestgate.artifact_query` | Use `content.get`/`content.resolve` (SHIPPED Session 60) |
| `rhizocrypt.dag_summary` | Use `dag.session.get`/`dag.session.list` (SHIPPED) |

### 5. Infrastructure Fixes

- Fixed `nucleus_config.sh` source path in 6 benchScale scenario scripts (`../../` → `../../../`)
- Extended `parse_graph_nodes` to handle `fragment.nodes` in addition to `graph.nodes`
- Fixed `nucleus_complete.toml` TOML key conflict (`bonding_policy` string vs table)
- Cleaned superseded baseline/report files (pre-fix DoT, pre-fix tunnel)

### 6. lithoSpore Execution

- Fixed `gen` reserved keyword in `ltee-citrate` (renamed to `pot_gen`/`cit_gen`)
- Fixed allele fitness check: validate >= 1.0 (positive adaptation) not ≈ 1.0
- Added `--max-tier` CLI flag to `ltee-alleles` and `ltee-citrate` for CLI dispatch
- **Result**: 5/7 modules PASS Tier 2, 46/46 checks

---

## Files Modified

**projectNUCLEUS**:
- `deploy/deploy_beardog_tls_shadow.sh` — rewritten for BearDog v0.9.0 CLI
- `deploy/deploy_graph.sh` — `parse_graph_nodes` extended for `fragment.nodes`
- `graphs/nucleus_complete.toml` — TOML key conflict fixed
- `infra/benchScale/scenarios/dot_sovereign_parity.sh` — DNS fallback chain + DoT detection
- `infra/benchScale/scenarios/cloudflare_tunnel_baseline.sh` — `tunnel_reachable_pct` metric
- `infra/benchScale/scenarios/{btsp_tls,cloudflare_tunnel,full_stack_load,nestgate_content,shadow_run_orchestrator,songbird_nat}_parity.sh` — source path fix
- `specs/EVOLUTION_GAPS.md` — H2-12 RUNNING, DoT BASELINE CAPTURED, changelog
- `specs/LIVE_SCIENCE_API.md` — proposed methods resolved, status table updated

**lithoSpore**:
- `crates/ltee-alleles/src/main.rs` — fitness check fix, `--max-tier` flag
- `crates/ltee-citrate/src/main.rs` — reserved keyword fix, `--max-tier` flag
