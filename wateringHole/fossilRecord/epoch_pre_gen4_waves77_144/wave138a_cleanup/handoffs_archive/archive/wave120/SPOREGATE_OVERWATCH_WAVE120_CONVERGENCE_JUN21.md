# sporeGate Overwatch — Wave 120 FRAGO: Deployment Convergence

**Date**: Jun 21, 2026 | **From**: sporeGate overwatch (hardware + VPS topology)
**Wave**: 120 | **Scope**: Config generation convergence, sovereign CI, auth evolution

---

## What Shipped

### Deployment Convergence — Config Generation Now Manifest-Authoritative

cellMembrane commit `4347987`: manifest-driven config generation closes the divergence gap.

| Generator | Before | After |
|-----------|--------|-------|
| `firewall.generate` | Required 8+ CLI flags (`--plasma-membrane --wan enp1s0 --lan eno1 --trust-lan --wg-iface wg0 --subnet 192.168.4.0/22 --gate-name sporeGate nucleus`) | Zero flags: auto-derives from gate profile roles + interface fields |
| `wireguard.generate` | Listed all peers flat, no hub routing, no pubkeys | Hub topology: spoke→hub only, `AllowedIPs = subnet/24`, real pubkeys from manifest |
| `caddy.generate` | Looked for role `"caddy"` (no match) | Searches `caddy`, `caddy_tls`, `tls_terminator` |
| Composition parse | `"full"` rejected | `"full"` → `nucleus` alias |

**Convergence proof**: `diff generated-nftables.nft hand-written-nftables.nft` → cosmetic only (5 comment lines). Functionally identical output with zero operator input.

### GateProfile Extended (cellMembrane)

New manifest fields consumed by generators:

| Field | Purpose | Populated |
|-------|---------|-----------|
| `host` | IP/hostname for VPS gates | golgiBody |
| `wan_interface` | WAN NIC name | sporeGate |
| `lan_interface` | LAN NIC name | sporeGate |
| `lan_subnet` | LAN CIDR | sporeGate |
| `wg_pubkey` | WireGuard public key | all 4 mesh gates |
| `wan_endpoint` | Public endpoint for WG peers | golgiBody |

### Manifest Updated (wateringHole)

Commit `24270ba9`: All 4 active mesh gates now carry `wg_pubkey` harvested from live mesh. sporeGate carries interface fields. golgiBody carries `wan_endpoint`.

### Sovereign CI — First Full Cycle Post-Switchover

Build completed on sporeGate local hardware: 14/14 binaries (13 primals + membrane), BLAKE3 checksums, rsync to golgi depot. Membrane binary updated to include convergence work. Depot sync: 4MB delta transferred (vs 193MB total).

---

## Auth Evolution: S1 → S3 Sovereignty Progression

### Current Problem

ironGate team reports inability to SSH/push to Forgejo. Root cause: S1 auth friction.

- ironGate's key IS registered in Forgejo (key ID 1, `irongate@pop-os`, added May 28)
- Forgejo SSH listener is healthy (port 2222, built-in SSH server)
- Path works from sporeGate — problem is on ironGate's side
- Likely: wrong git remote URLs (same pattern as pepti's 37-repo fix), or host key mismatch

### ironGate Troubleshooting (for ironGate team)

```bash
# 1. Test SSH connectivity
ssh -T git@git.primals.eco -p 2222 -v 2>&1 | tail -20

# 2. If host key error:
ssh-keygen -R '[git.primals.eco]:2222'

# 3. Check remote URLs (should be ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git)
cd ~/Development/ecoPrimals/primals/<repo> && git remote -v

# 4. Fix remote URLs if wrong:
git remote set-url origin ssh://git@git.primals.eco:2222/ecoPrimals/<repo>.git
```

### Auth Evolution Path (handoff to flockGate Tower team — bearDog)

| Stage | Auth Model | Identity Bound To | Owner |
|-------|-----------|-------------------|-------|
| **S1 (now)** | ed25519 pubkeys manually copied to `authorized_keys` + Forgejo user | Specific key file on specific host | Operator |
| **S2 (bearDog BTSP)** | Trust bootstrap validates gate against genetics (composition lineage, merkle provenance) | Provenance chain, not host | flockGate Tower (BearDog) |
| **S3 (full genetics)** | Auth is composition-deterministic — right to push/join/access derived from genetic composition | Role identity, portable | cellMembrane + BearDog |

Every S1 friction point (manual key copy, host key mismatch, wrong URLs on 37 repos) is a symptom of host-coupled identity. bearDog's BTSP is the path to identity-coupled auth where credentials follow roles, not hosts.

**Tier 3 isomorphism debt** (`gate.bootstrap --absorb`, credential portability) depends on this auth evolution.

---

## For cellMembrane Team

New `GateProfile` fields are in your crate (`manifest.rs`). The generators work end-to-end. Next evolution targets:

1. **`wireguard.generate` key management** — read private keys from a local keyfile path (not manifest). Generate `PostUp` directive for keyfile-based configs.
2. **`caddy.generate` depth** — add `file_server`, `handle` blocks, K-Derm headers, `acme_email` from manifest.
3. **`firewall.generate` from manifest without binary** — currently requires the `membrane` binary on the gate. Long-term: gate.bootstrap should generate + apply nftables as part of enrollment.

### Test Commands (verify after pulling)

```bash
# Should work with zero flags on sporeGate
GATE_NAME=sporeGate membrane firewall.generate
GATE_NAME=sporeGate membrane wireguard.generate --gate sporeGate
GATE_NAME=sporeGate membrane wireguard.generate --gate golgiBody
GATE_NAME=sporeGate membrane caddy.generate --gate golgiBody
```

---

## For primalSpring Overwatch

New validation scenarios available:

1. **Config convergence** — generate nftables/wg/caddy from manifest, diff against live configs on each gate
2. **Manifest completeness** — assert all mesh gates have `wg_pubkey`, all plasma membrane gates have interface fields
3. **Sovereign CI freshness** — compare depot checksums against HEAD commit SHAs, flag stale builds

---

## Updated Metrics

| Metric | Value |
|--------|-------|
| cellMembrane | **731 tests**, zero clippy, zero warnings |
| Config generators | **3 working** (firewall, wireguard, caddy) — all manifest-aware |
| Depot | **14/14** fresh from HEAD, BLAKE3 verified, synced to golgi |
| Manifest coverage | **4/4** mesh gates with `wg_pubkey`, sporeGate with interface fields |
| Auth keys in Forgejo | **10** registered across 8 gates/services |

---

## Team Ownership Summary

| Domain | Owner | Scope |
|--------|-------|-------|
| Hardware, LAN, VPS topology, gate enrollment | **sporeGate overwatch** (this team) | Physical mesh, NAT/FW, Omada, Flint 2, WG admin |
| cellMembrane code, generators, type evolution | **cellMembrane team** (parallel IDE) | Rust crates, CLI commands, test coverage |
| primalSpring scenarios, ecosystem validation | **primalSpring overwatch** (eastGate) | Scenario coverage, cascade review, convergence monitoring |
| Auth evolution (BTSP), Tower primals | **flockGate Tower team** | BearDog trust, Songbird mesh, SkunkBat defense |
| Node compute (ToadStool, BarraCuda, CoralReef) | **ironGate Node team** | After SSH enrollment |
