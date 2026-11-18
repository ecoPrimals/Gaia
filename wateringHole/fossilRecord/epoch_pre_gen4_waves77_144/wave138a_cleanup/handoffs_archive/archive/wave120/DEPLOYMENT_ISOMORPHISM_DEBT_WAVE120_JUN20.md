# Deployment Isomorphism Debt — cellMembrane P1 Handoff

**From**: sporeGate overwatch  
**To**: cellMembrane team  
**Date**: 2026-06-20  
**Wave**: 120  
**Priority**: P1  
**Classification**: Architecture debt — deployment fragility

---

## Discovery

While evaluating VPS consolidation (golgi + golgiBody-ext → single node), we found that **migrating services between nodes is prohibitively difficult**. This difficulty exposes a fundamental violation of the K-Derm fractal/isomorphic/agnostic principles.

The system is **host-coupled, not identity-coupled**. Services are nailed to specific IPs and hosts with hand-wired configs. Moving any service requires coordinated multi-node changes with downtime risk.

---

## Fragility Symptoms

| Symptom | Root Cause | Affected Files |
|---------|-----------|----------------|
| Moving golgi requires editing every gate's `wg0.conf` | WG peers reference static IPs, not resolvable identities | `/etc/wireguard/wg0.conf` on 4 nodes |
| Cross-node bridges (UDS→TCP) exist on golgi | Services can't natively route through the mesh overlay | `membrane-bridge-*.service` (3 units) |
| Caddy on ext references private IPs (`10.116.0.x`) | No service discovery — hard-wired topology | `/etc/caddy/Caddyfile` on golgiBody-ext |
| DNS zones hand-configured on each node | No declarative zone management from manifest | `/etc/knot/knot.conf` on both VPS |
| GitHub push key lives on ONE specific node | Identity not portable — credentials bound to hosts | `~/.ssh/id_ed25519` on golgiBody-ext only |
| Forgejo address hardcoded in all gates' git remotes | No service resolution for `git.primals.eco:2222` | `~/.gitconfig` / remote URLs on all gates |

---

## What "Fractal + Isomorphic + Agnostic" Deployment Means

A properly abstracted deployment allows:

1. **Any node can absorb any role** — declare intent in manifest, membrane provisions automatically
2. **WG peers resolve by identity** — `golgiBody` not `[RELAY_PUBLIC]`, mesh self-heals on IP change
3. **Services register into mesh** — Songbird discovery advertises endpoints, consumers resolve dynamically
4. **Credentials follow roles, not hosts** — GitHub push key travels with "external_publisher" role
5. **VPS migration becomes trivial** — spin new VPS, assign roles, old node drains gracefully
6. **Caddy/nftables/WG configs are generated** — from `ecosystem_manifest.toml`, not hand-written

---

## Proposed Evolution Targets

### Tier 1 — Service Discovery (enables everything else)

| Target | Module | What It Fixes |
|--------|--------|--------------|
| `topology.resolve --service forgejo` | `membrane-shadow/src/topology/` | Find any service by role, returns current IP:port |
| Songbird service registry | `songbird` | Dynamic endpoint advertisement + mesh-native routing |
| DNS-based resolution as fallback | `membrane-shadow/src/topology/` | SRV records generated from manifest |

### Tier 2 — Declarative Config Generation

| Target | Module | What It Fixes |
|--------|--------|--------------|
| `gate.provision --caddy` | `membrane-shadow/src/gate/` | Generate Caddyfile from manifest roles (like `firewall.generate`) |
| `gate.provision --wireguard` | `membrane-shadow/src/gate/` | Generate wg0.conf from manifest peers |
| `gate.provision --dns` | `membrane-shadow/src/gate/` | Generate knot.conf from manifest zones |

### Tier 3 — Role Migration

| Target | Module | What It Fixes |
|--------|--------|--------------|
| `gate.migrate <role> <from> <to>` | `membrane-shadow/src/gate/` | Orchestrated service migration between nodes |
| `gate.bootstrap --absorb <role>` | `membrane-shadow/src/gate/bootstrap.rs` | Node assumes role including credentials + state |
| Credential portability (bearDog vault) | `beardog` | Keys stored by role-identity, fetchable by any authorized node |

---

## Current Workaround

**Option B accepted** — keep both VPS nodes as-is. The topology works, it's just not resilient to change:

```
golgiBody-ext (137.184.197.151)     golgi ([RELAY_PUBLIC])          sporeGate (LAN)
├── Caddy (primals.eco TLS)    ←→   ├── Forgejo                    ├── Sovereign CI
├── Caddy (primal.eco proxy)   ←→   ├── WG Hub (10.13.37.1)        ├── Local Depot
├── Knot DNS (secondary)       ←    ├── Knot DNS (primary)         ├── 13/13 NUCLEUS
├── GitHub push key                  ├── Sovereign Relay            ├── Cascade Hub
└── Songbird TURN                    ├── WAN Depot (/depot/)        └── nftables (plasma membrane)
                                     └── 13/13 NUCLEUS
   [DO private net 10.116.0.x]
```

This is stable but **not self-healing**. Any node replacement requires manual coordination.

---

## Success Criteria

When this debt is resolved:
- [ ] `membrane gate.migrate forgejo golgi new-vps` moves Forgejo without manual config edits
- [ ] WG mesh self-heals when a peer's IP changes (identity-based, not IP-based)
- [ ] Caddy configs are generated from manifest on each deploy
- [ ] Adding a new VPS is: `membrane gate.bootstrap --roles "relay,depot,dns-secondary"`
- [ ] No `10.116.0.x` or `157.230.x.x` hardcoded in any config template

---

## Context

- pepti decommissioned (Wave 120) — build role absorbed by sporeGate sovereign CI
- 4-node mesh stable: golgi, sporeGate, eastGate, flockGate
- Sovereign CI pipeline: Forgejo push → sporeGate build → rsync to golgi → WAN depot live
- cellMembrane at 680 tests, SSH/git_ops consolidated, deep debt swept
- This is the next logical evolution after the infrastructure consolidation
