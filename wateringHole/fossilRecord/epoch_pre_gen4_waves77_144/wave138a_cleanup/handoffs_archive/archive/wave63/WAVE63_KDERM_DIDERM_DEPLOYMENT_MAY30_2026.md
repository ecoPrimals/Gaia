# Wave 63 — K-Derm Diderm Envelope Deployed

**Date**: May 30, 2026
**From**: primalSpring coordination (eastGate)
**To**: All gates, all teams
**Phase**: Infrastructure evolution — diderm VPS architecture live

---

## What Happened

The single overloaded golgiBody VPS (1-vCPU, 2GB, 10GB, 80% full) has been
split into a proper K-Derm diderm envelope with three purpose-built nodes.
This physically implements the K-Derm topology standard that was previously
only a conceptual model.

## Architecture

```
Extracellular (GitHub, public internet)
    ↕ weak / ionic
Outer Membrane — golgiBody-ext (137.184.197.151)
  Caddy TLS, sporePrint hosting (HTTP 200), TURN relay, RustDesk
    ↕ ionic
Peptidoglycan — peptidoglycan ([RELAY_PUBLIC])
  Full 39-repo workspace, Rust 1.96, Zola 0.22.1, membrane binary
    ↕ metallic
Inner Membrane — golgiBody ([RELAY_PUBLIC])
  Forgejo (sovereign git), 13 NUCLEUS primals, knot-dns, BTSP auth
    ↕ covalent
Cytoplasm — LAN gates (eastGate, ironGate, southGate, biomeGate)
```

### Node Details

| Node | Role | Specs | Disk | Bond Types |
|------|------|-------|------|------------|
| golgiBody | Inner: sovereign periplasm | 1-vCPU, 2GB, 10GB | 66% (cleaned) | Covalent, Metallic |
| peptidoglycan | Structural: build/sync hub | 2-vCPU, 4GB, 80GB | 9% | Metallic |
| golgiBody-ext | Outer: public-facing | 1-vCPU, 2GB, 50GB | 6% | Ionic, Weak |

### Security Properties

Compromising the outer membrane (golgiBody-ext) does NOT grant access to:
- Forgejo data on golgiBody (inner)
- NUCLEUS primal services on golgiBody
- Build infrastructure on peptidoglycan

Each node has its own SSH key, firewall rules, and gate identity.

## What Changed

### New VPS Nodes
- **peptidoglycan** created via `doctl` — Debian 12, nyc1
- **golgiBody-ext** created via `doctl` — Debian 12, nyc1

### peptidoglycan Bootstrap
- Rust 1.96.0 (stable), Zola 0.22.1
- 39 repos cloned (--depth 1 for bloated: bearDog, songBird, toadStool, hotSpring, sporePrint)
- All repos have `origin` (GitHub) + `forgejo` (golgiBody) remotes
- membrane binary built from cellMembrane and installed to /usr/local/bin/
- UFW: SSH only (structural layer, no public services)
- Gate identity: `/opt/ecoPrimals/.gate = peptidoglycan`

### golgiBody-ext Bootstrap
- Caddy 2.11.3, Zola 0.22.1
- sporePrint cloned, built (143 pages), served via Caddy on port 80
- UFW: SSH + HTTP + HTTPS (outer membrane, public-facing)
- Gate identity: `/opt/ecoPrimals/.gate = golgiBody-ext`

### golgiBody Cleanup
- Workspace repos removed (primals/, springs/, gardens/ — 1.2GB freed)
- Rust toolchain removed (peptidoglycan builds now)
- Disk: 80% → 66%, focused on Forgejo + primal services
- Gate identity set: `/opt/ecoPrimals/.gate = golgiBody`

### SSH Keys Registered
- peptidoglycan@vps → GitHub + golgiBody Forgejo
- golgiBody-ext@vps → GitHub + golgiBody Forgejo
- Cross-node SSH mesh: all 3 nodes can SSH to each other

### Configuration Updates
- `ecosystem_manifest.toml` → v2.2.0, wave 63, `[topology]` section, gate profiles
- `membrane.toml` → three-layer `[membrane.layers.*]` config with IPs and services
- sporePrint handoff → updated with diderm architecture and deploy pipeline

## Gate Impact

### No changes needed for LAN gates
Gates continue to push to golgiBody Forgejo (inner membrane) via SSH at
`git.primals.eco:2222`. The inner membrane's covalent boundary is unchanged.

### New deployment source
Gates can now optionally clone from peptidoglycan (metallic bond) for
build-fresh repos. peptidoglycan is the canonical convergence point for
temporal sync.

### flockGate path
flockGate (WAN) connects through golgiBody-ext (outer membrane) for TURN relay,
and through golgiBody (inner) for covalent git access.

## Cost

| Node | Monthly |
|------|---------|
| golgiBody (inner) | $12 |
| peptidoglycan | $24 |
| golgiBody-ext (outer) | $12 |
| **Total** | **$48/mo** |

## Next Steps

- [ ] DNS cutover: `primals.eco` A record → golgiBody-ext (137.184.197.151)
- [ ] HTTPS: Caddy automatic TLS via Let's Encrypt on golgiBody-ext
- [ ] Move Songbird TURN relay from golgiBody → golgiBody-ext
- [ ] Move RustDesk relay from golgiBody → golgiBody-ext
- [ ] flockGate bootstrap using the diderm deploy path
- [ ] Multi-vendor VPS: evaluate Hetzner/Vultr for peptidoglycan redundancy
