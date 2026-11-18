# sporeGate Subteam Dispatch — Wave 121

**Date**: Jun 21, 2026 18:45 EDT | **From**: eastGate overwatch
**To**: sporeGate overwatch (hardware/topology) + cellMembrane team (code/VPS)

---

## Subteam 1: sporeGate Overwatch (Hardware + Topology + Infra)

### P1: Dual-Target Depot (ironGate impulse)

ironGate has a working RTX 5070 but musl depot binaries can't access GPU (no dlopen).
Build barracuda + coralReef as `x86_64-unknown-linux-gnu` alongside existing musl.

**Immediate**: `/opt/depot/build-local.sh` gains `--target gnu` mode for GPU primals.
**Depot layout**: `primals/x86_64-unknown-linux-gnu/` alongside existing musl path.
**Long-term**: sovereign-dispatch IPC (musl binary delegates GPU work to glibc coralReef peer).

### P1: PAT Token Deprecation

All gates now have SSH key auth to Forgejo (port 2222). Legacy PAT tokens should be revoked:

```bash
# On golgi — check for lingering tokens:
ssh root@[RELAY_PUBLIC]
sqlite3 /opt/forgejo/data/forgejo.db "SELECT id, name, token_last_eight FROM access_token;"

# Revoke any found (keep ONLY tokens actively used by CI hooks):
# sqlite3 /opt/forgejo/data/forgejo.db "DELETE FROM access_token WHERE name = 'tmp-fossil-create';"
# Then: sudo systemctl restart forgejo
```

**Known stale token**: `tmp-fossil-create` (from Wave 62, never revoked).
**Policy going forward**: SSH keys for all git operations. Forgejo API access only via bearDog `auth.token.*` when BTSP is ready.
**Update**: Remove `token_path = "~/.config/forgejo/token"` from `DEPLOYMENT_INSTANCE.toml` (deprecated).

### P2: HPC VLAN Implementation

VLAN 10 (192.168.10.0/24) designed in `compute-sharing/HPC_VLAN_DESIGN.toml`.
Blocked on MikroTik CRS310 credentials (operator: 5s reset button when convenient).

### P2: Omada Management

Access confirmed at https://192.168.4.111, admin/admin. Ready for VLAN tagging when MikroTik is configured.

### P2: strandGate + southGate Relay Push

Both on sovereign relay. RustDesk in and push sovereign config. Low urgency — no active team on those gates.

---

## Subteam 2: cellMembrane Team (Code + VPS Evolution)

### P1: Dual-Target Depot Support (code changes)

Per ironGate impulse `2026-06-21T14-20_ironGate__wave120-dual-target-depot.toml`:

| Change | Where | Notes |
|--------|-------|-------|
| Add `X86_64Gnu` to arch enum | `plasmidbin-types/src/arch.rs` | `.triple() = "x86_64-unknown-linux-gnu"` |
| `gpu_primals = ["barracuda", "coralreef"]` | `sources.toml` or manifest | Drive build matrix |
| Fetch logic: gates with `node_atomic` role fetch gnu | `membrane-shadow/src/plasmid.rs` | Use manifest roles |
| `is_static_elf()` accepts dynamic for gnu dir | `depot/validation.rs` | Don't reject glibc binaries |
| Depot layout: new gnu directory | Build scripts | Parallel to existing musl |

### P1: Auth Evolution — PAT → BTSP

Current auth is S1 (manual SSH keys). Path to S2:

| Stage | Model | Owner | Status |
|-------|-------|-------|--------|
| S1 | Manual ed25519 + Forgejo SSH | — | ✅ Current (all gates enrolled) |
| S1.5 | **PAT revocation** + SSH-only policy | sporeGate overwatch | THIS WAVE |
| S2 | bearDog BTSP trust bootstrap | flockGate Tower team | P1 (BearDog primal work) |
| S3 | Composition-deterministic auth | cellMembrane | Tier 3 target |

### P2: Tier 3 Isomorphism

| Primitive | What It Does | Depends On |
|-----------|-------------|------------|
| `gate.migrate <role> <from> <to>` | Move a service between gates | Credential portability |
| `gate.bootstrap --absorb <role>` | Node assumes role + creds | bearDog vault |
| DNS config generation | `gate.provision --dns` | Caddy/DNS integration |

### P2: golgi as NUCLEUS

golgi is still a manually configured VPS. The goal (from Wave 62 AAR) is:
- nestGate `content.repo.create/list` → proxies Forgejo API
- bearDog `auth.token.create/revoke` → manages Forgejo tokens via BTSP
- biomeOS `gate.service.status/restart` → manages systemd units

This eliminates SSH-and-sqlite token management forever.

---

## Current Metrics

| Repo | Tests | Gate |
|------|-------|------|
| cellMembrane | 731 | sporeGate |
| primalSpring | 998 | eastGate |
| sporePrint | 183+ | flockGate |
| toadStool | 9,074 | ironGate |
| biomeOS | 8,351 | eastGate |
| songBird | 8,929 | flockGate |
