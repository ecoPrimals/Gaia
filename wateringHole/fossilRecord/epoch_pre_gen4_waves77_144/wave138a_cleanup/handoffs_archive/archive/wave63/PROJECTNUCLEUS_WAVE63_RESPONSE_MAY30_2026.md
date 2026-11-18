# projectNUCLEUS Wave 63 Response

**Date:** 2026-05-30
**From:** irongate (projectNUCLEUS)
**To:** primalSpring, projectFOUNDATION, sporePrint, lithoSpore teams

---

## Completed

### 1. pseudoSpore Hosting Caddy Config — DONE

Added `primals.eco` domain block to the SSOT Caddyfile
(`infra/plasmidBin/membrane/Caddyfile`):

- `/lab/spores/*` → `file_server browse` from `/opt/ecoPrimals/sporePrint/spores/`
- Root → sporePrint Zola output from `/opt/ecoPrimals/sporePrint/public/`
- `www.primals.eco` → permanent redirect to apex
- VPS directories created, Caddy validated and reloaded

**Awaiting:** S3 DNS cutover (`primals.eco` A record → VPS [RELAY_PUBLIC]).
Currently serves from GitHub Pages via Cloudflare.

### 2. Forgejo Mirror → Bidirectional — DONE

Converted all 31 pull-mirror repos to regular bidirectional repos via SQLite
`is_mirror` flag + mirror config cleanup. Forgejo restarted and verified.

**Result:** 39 total repos, 0 mirrors. All gates can push and pull freely.

### 3. ABG Workload Definitions — DONE

6 new workload TOMLs across 3 springs:

| Spring | Workload | Tier | Domain |
|--------|----------|------|--------|
| wetSpring | 16s-pipeline | CPU | metagenomics |
| wetSpring | breseq-variant | CPU | evolutionary biology |
| healthSpring | pkpd-validation | CPU | clinical pharmacology |
| healthSpring | population-pk-gpu | GPU | population PK |
| neuralSpring | inference-validation | CPU | neural inference |
| neuralSpring | gpu-inference | GPU | transformer attention |

Total workloads: 12 (6 hotSpring + 6 new). All follow toadstool-validate-v1
schema and reference spring domain_profiles.

### 4. Deploy Script Audit — DONE

31 bash scripts in `deploy/` (not 46 — other files are .py, .toml, etc.).

| Category | Count | Scripts |
|----------|-------|---------|
| Core infra | 10 | nucleus_config, deploy, deploy_graph, gate_provision, membrane_telemetry, provenance_pipeline, security_validation, forgejo_mirror, deploy_health_check, gate_watchdog |
| ABG ops | 4 | abg_accounts, abg_data, tier_test_all, tier_enforcement_test |
| sporePrint | 4 | publish_sporeprint, sporeprint_dns, sporeprint_verify, sporeprint_local |
| Membrane | 4 | membrane_provenance, membrane_summary, external_validation, vps_resize |
| Shadow/transition | 3 | deploy_beardog_tls_shadow, deploy_btsp_auth_shadow, switch_to_static_observer |
| Other active | 6 | deploy_primal_start, deploy_knot_dns, gate_switch, signal_executor, rotate_cookie_secret, wheelhouse_sync |

**Verdict:** Zero stale scripts. All have 2+ cross-references. Shadow scripts are
correctly scoped to transition period. The May 11 scripts are older but still active.

**Rust evolution candidates** (critical-path, would benefit most):
1. `deploy.sh` (398L, 31 refs) — main deploy orchestrator
2. `security_validation.sh` (597L, 8 refs) — already has Rust companion (darkforest)
3. `provenance_pipeline.sh` (454L, 11 refs) — data pipeline

---

## For primalSpring

- All HIGH items resolved. pseudoSpore infrastructure is staged, mirrors are
  bidirectional, workloads are defined.
- `primals.eco` VPS hosting ready but blocked on S3 DNS cutover (registrar action).
- Deploy scripts are clean — Rust evolution is incremental, not urgent.

## For projectFOUNDATION

- Forgejo repo is now bidirectional — you can push directly to
  `git.primals.eco/sporeGarden/projectFOUNDATION`.
- pseudoSpore gallery path is wired: `/lab/spores/{name}/` on VPS.
  Foundation needs to generate gallery pages → place in
  `/opt/ecoPrimals/sporePrint/spores/{name}/index.html`.

## For sporePrint

- VPS hosting infrastructure ready. Zola build output goes to
  `/opt/ecoPrimals/sporePrint/public/`.
- pseudoSpore gallery template needed at `content/lab/spores/` in Zola config.
- Caddy will serve both static site and spore gallery once DNS cuts over.

## For lithoSpore

- healthSpring domain_profile.toml is ready for `litho emit-pseudospore` testing.
- groundSpring also shipped domain_profile.toml this wave.
- wetSpring domain_profile.toml exists — 3 springs ready for multi-spring emission.

---

*Wave 63. Infrastructure staged. Mirrors bidirectional. Workloads defined. Deploy ready.*
