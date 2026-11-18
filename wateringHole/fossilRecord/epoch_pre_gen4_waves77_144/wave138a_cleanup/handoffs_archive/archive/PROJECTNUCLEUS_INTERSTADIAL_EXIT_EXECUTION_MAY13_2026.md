# projectNUCLEUS — Interstadial Exit Execution (May 13, 2026)

## Summary

Executed against the 3 remaining interstadial exit gate items. All three
now have code artifacts ready — only operational deployment remains.

## Exit Gate Items

### 1. Songbird NAT + VPS Relay (H2-14)

**Status**: OPS-READY — binary in plasmidBin, deploy script staged.

- Songbird binary confirmed in both plasmidBin and source build
- `deploy/deploy_songbird_relay.sh` ready for VPS provisioning
- Upstream systemd unit at `primals/songBird/deployment/systemd/songbird-relay.service`
- `songbird_nat_parity.sh` benchScale scenario ready
- Remaining: provision ~$5/mo VPS and run deploy script

### 2. BTSP Dual-Auth Shadow (H2-01→H2-04)

**Status**: BUILT — plugin + deploy script created. Ready for shadow run.

- `deploy/jupyterhub_btsp_auth.py` — JupyterHub BTSPAuthenticator
  - Verifies ionic tokens via BearDog `auth.verify_ionic` JSON-RPC
  - Dual-auth mode: BTSP + PAM fallback during shadow period
  - Auth logging: `AUTH_BTSP`, `AUTH_PAM`, `AUTH_FAIL` with latency
  - `pre_spawn_hook`: injects BTSP tier into notebook environment
  - Configurable via traitlets (host, port, timeout, dual_auth)
- `deploy/deploy_btsp_auth_shadow.sh` — shadow run management
  - `--enable`: installs plugin, configures JupyterHub, starts shadow
  - `--disable`: removes config, restores PAM-only
  - `--status`: shows shadow state, BearDog reachability, auth events

### 3. ABG WCM Through Provenance Trio

**Status**: Graph capabilities reconciled. Pipeline exercises canonical methods.

- `nucleus_complete.toml` loamSpine capabilities: `session.commit`/`entry.append` →
  canonical `spine.create`/`spine.get`/`spine.seal`/`entry.append`/`entry.get`/`certificate.mint`
- `nucleus_complete.toml` sweetGrass capabilities: `provenance.create_braid`/`provenance.lineage`/`provenance.graph` →
  canonical `braid.create`/`braid.commit`/`braid.get`/`anchoring.anchor`/`anchoring.verify`
- `rootpulse_commit.toml` workflow methods: `dag.dehydrate`→`dag.dehydration.trigger`,
  `commit.session`→`spine.seal`, `provenance.create_braid`→`braid.create`
- `provenance_pipeline.sh` already uses canonical names — no changes needed

## CATHEDRAL Items

### lithoSpore Module 7 (anderson)

- Created `artifact/data/anderson_predictions/` with provenance README
- Module 7 now PASS 5/5 at Tier 2 (no plateau, diminishing returns, GOE/Poisson, variance, 12 populations)
- Full suite: **6/7 PASS**, 1 SKIP (biobricks awaits B6)
- Upstream litho-core shared library (discovery, harness, stats) absorbed and builds clean

### liveSpore.json Deployment Tracking

- lithoSpore registered as artifact in plasmidBin manifest.toml
- 8 binaries tracked, ecoBin compliant, composition = nucleus

### API Absorption

- `biomeos.spring_status` updated from "Resolved" to IMPLEMENTED (v3.54)
- Registry count updated to 415 methods (was 413)
- `LIVE_SCIENCE_API.md` and `EVOLUTION_GAPS.md` aligned

## Files Modified

### projectNUCLEUS

- `deploy/jupyterhub_btsp_auth.py` — NEW: BTSP authenticator plugin
- `deploy/deploy_btsp_auth_shadow.sh` — NEW: shadow run management
- `graphs/nucleus_complete.toml` — provenance trio capabilities reconciled
- `graphs/rootpulse_commit.toml` — workflow method names reconciled
- `specs/EVOLUTION_GAPS.md` — updated for all changes + changelog
- `specs/LIVE_SCIENCE_API.md` — spring_status IMPLEMENTED, registry 415
- `README.md` — updated current state

### lithoSpore

- `artifact/data/anderson_predictions/README.md` — NEW: data provenance
- `artifact/liveSpore.json` — new validation run recorded (6/7 pass)

### infra/plasmidBin

- `manifest.toml` — lithoSpore artifact section + 415 methods
