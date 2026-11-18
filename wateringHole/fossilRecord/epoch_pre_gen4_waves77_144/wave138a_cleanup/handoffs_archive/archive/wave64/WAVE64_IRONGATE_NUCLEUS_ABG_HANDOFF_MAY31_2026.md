# Wave 64 Handoff: ironGate — projectNUCLEUS / ABG Evolution

**From**: eastGate (overwatch)
**To**: ironGate / projectNUCLEUS team
**Date**: May 31, 2026
**Context**: K-Derm diderm relay validated (flockGate WAN + biomeGate air-gap). eastGate driving sovereignty cutovers (S1-S4). ironGate is the LAN mesh validation partner and ABG compute host.

---

## Wave 64 Assignments

### 1. Deploy scripts bash-to-Rust (independent)

Your Wave 64 handoff identified three remaining bash scripts for Rust evolution:
- `deploy.sh`
- `security_validation.sh`
- `provenance_pipeline.sh`

All other scripts already use `nucleus_config.sh` SSOT. These three are ironGate-local work — no eastGate code dependency. Target: idiomatic Rust with `clap` CLI, proper error handling, zero `unwrap()` in production.

### 2. Forgejo Actions shadow CI (independent)

Set up a Forgejo Actions runner on ironGate as shadow alongside GitHub Actions:
- Install Forgejo runner (docs at git.primals.eco admin panel)
- Configure for cellMembrane and projectNUCLEUS repos initially
- Run in parallel with GitHub Actions — compare results
- Target: validates CI on inner membrane before full inversion

This eliminates the CI SPOF (currently 1 GitHub Actions runner). Once validated, Wave 66 promotes Forgejo Actions to primary.

### 3. S4 auth shadow testbed (with eastGate)

ironGate's JupyterHub is the S4 shadow testbed:
- BearDog BTSP dual-auth code is built (S4 READY status)
- eastGate will configure the shadow period
- ironGate validates: BTSP auth works for ABG tiered access (`abg-admin/compute/observer/reviewer`)
- 7-day shadow period, then formal cutover gate

Your existing ABG tier groups map directly to BTSP capability scopes.

### 4. LAN mesh validation partner (with eastGate)

eastGate will initiate `discovery.peers` smoke test:
- Verify `SONGBIRD_FEDERATION_PORT=7700` is set on ironGate
- Verify `SONGBIRD_PEERS` includes eastGate's address
- eastGate runs `s_covalent_mesh` scenario from primalSpring
- Then: first live cross-gate `capability.call` via Songbird braid relay

Ensure Songbird is running and federated before eastGate initiates the test.

---

## Sync First

```bash
cd infra/wateringHole && git pull forgejo main
cd gardens/cellMembrane && git pull forgejo main
cd gardens/cellMembrane/crates/membrane-shadow && cargo build --release --bin membrane
cp target/release/membrane ~/.local/bin/
membrane manifest.info  # verify topology: diderm with roles
```

Push to `forgejo` only — K-Derm relay handles GitHub automatically.

---

## Wave 65 Preview

- NUC intake pattern prototype (edge node → LAN → ironGate compute)
- Workload TOMLs for wetSpring, neuralSpring, healthSpring
- Full mesh participation via `capability.call`
- ABG workload routing via biomeOS deploy graphs

## Wave 66 Target

- Outer membrane workload submission: ABG users submit via golgiBody-ext
- pseudoSpore interaction via trans face
- Forgejo Actions promoted from shadow to primary CI

---

*ironGate at Wave 64. 184 Rust tests, zero debt, LAN mesh partner. Focus: Rust evolution + CI sovereignty + S4 testbed.*
