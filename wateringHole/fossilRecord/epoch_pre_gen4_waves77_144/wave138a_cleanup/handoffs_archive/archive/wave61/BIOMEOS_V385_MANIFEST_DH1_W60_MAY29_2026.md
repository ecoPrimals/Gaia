# biomeOS v3.85 — Wave 60: Manifest Gate Profile + DH-1 /tmp Cleanup

**Date**: May 29, 2026
**Author**: biomeOS team
**Wave**: 60 (PostPrimordial → Glacial Shift)
**Previous**: v3.84 (Wave 58b — env var centralization)

---

## Summary

Two Wave 60 upstream evolution targets completed:

1. **`manifest.gate_profile`** — New Neural API method that resolves
   gate profiles from `ecosystem_manifest.toml` at runtime. Needed by
   all 3 ecosystem signal graphs (`ecosystem.check`, `ecosystem.pull`,
   `ecosystem.push`). HIGH priority target now live.

2. **DH-1: `/tmp` hardcoding elimination** — Changed all socket/data/log
   fallbacks from bare `/tmp` to VPS-friendly paths (`/run/biomeos`,
   `/var/lib/biomeos`). Unblocks `ProtectSystem=strict` on VPS membrane.

---

## manifest.gate_profile

### What it does

Reads `ecosystem_manifest.toml` (the WaterFall catalog maintained in
`wateringHole`) and returns the gate profile for the local gate — which
repos this gate cares about, enriched with per-repo metadata (org, path,
membrane, sync config).

### Wire contract

```json
// Request
{"jsonrpc":"2.0","method":"manifest.gate_profile","params":{"gate_id":"eastGate"},"id":1}

// Response
{
  "gate_id": "eastGate",
  "manifest_version": "2.0.0",
  "wave": 60,
  "repo_count": 37,
  "repos": [
    {
      "name": "nestGate",
      "org": "ecoPrimals",
      "local_path": "primals/nestGate",
      "membrane": "trailing-mirror",
      "sync_priority": "standard",
      "category": "primal",
      "github_repo": "ecoPrimals/nestGate",
      "forgejo_repo": "ecoPrimals/nestGate",
      "default_branch": "main",
      "sync_source": "github"
    }
    // ...
  ],
  "sync": {
    "forgejo_base_url": "https://git.primals.eco",
    "forgejo_ssh": "ssh://git@git.primals.eco:2222",
    "forgejo_host": "vps"
  }
}
```

### Resolution

- **Manifest path**: `$BIOMEOS_ECOSYSTEM_MANIFEST` → `params.manifest_path` → walk-up to `infra/wateringHole/ecosystem_manifest.toml`
- **Gate ID**: `params.gate_id` → `$BIOMEOS_GATE_ID`

### Files changed

| File | Change |
|------|--------|
| `handlers/manifest.rs` | NEW — handler + 5 tests |
| `route_table.rs` | Added `ManifestGateProfile` variant |
| `routing.rs` | Added dispatch arm |
| `handlers/mod.rs` | Registered `manifest` module |
| `env_config.rs` | Added `ECOSYSTEM_MANIFEST_PATH`, `GATE_ID` constants |
| `capability_registry.toml` | Added `[manifest]` domain |

---

## DH-1: /tmp Hardcoding Elimination

### Production Rust changes

| File | Before | After |
|------|--------|-------|
| `defaults.rs` | `DEFAULT_SOCKET_DIR = "/tmp"` | `/run/biomeos` |
| `paths.rs` (`new_lazy`) | `env::temp_dir()` fallbacks | `/run/biomeos`, `/var/lib/biomeos`, `/etc/biomeos`, `/var/cache/biomeos` |
| `ecosystem_health.rs` | Hardcoded `"/tmp/biomeos"` | `FALLBACK_RUNTIME_BASE` constant |
| `platypus/mesh.rs` | `"/tmp/biomeos/mesh-peers.json"` | `/run/biomeos/mesh-peers.json` |
| `fossil/mod.rs` | `default_value = "/tmp/primals"` | XDG `data_dir().join("primals")` |
| `logs.rs` | `default_value = "/tmp/primals"` | XDG `data_dir().join("primals")` |

### TOML/script changes

| File | Change |
|------|--------|
| `niches/tower.toml` | Socket paths → `${SOCKET_DIR:-/run/biomeos}/...` |
| `niches/compute-node.toml` | Socket paths → `${SOCKET_DIR:-/run/biomeos}/...` |
| `niches/nest.toml` | Socket path → `${SOCKET_DIR:-/run/biomeos}/...` |
| `niches/ui.toml` | Comment updated |
| 3× `tower_atomic_bootstrap.toml` | `NEURAL_API_SOCKET` → `${SOCKET_DIR:-/run/biomeos}/...` |
| `livespore_deploy.sh` | Socket/log paths → env-first resolution |
| `create_sibling_spore.sh` | Socket paths → env-first resolution |
| `capability_registry.toml` | Socket template `tmp_fallback` → `run_biomeos` |

### VPS deployment note

For `ProtectSystem=strict` compatibility, the systemd unit should include:

```ini
RuntimeDirectory=biomeos
StateDirectory=biomeos
CacheDirectory=biomeos
ConfigurationDirectory=biomeos
```

This creates `/run/biomeos/`, `/var/lib/biomeos/`, etc. with correct
ownership, matching the new fallback paths.

---

## Test fixes

3 pre-existing environment-dependent tests were fixed. They previously
panicked when live primal sockets existed in `$XDG_RUNTIME_DIR/biomeos/`:

- `test_hash_via_capability_no_socket_returns_none` — now skips assertion
  when `crypto.sock` exists (correct production behavior)
- `test_discover_capability_ai_category_empty_registry` — skips when
  `compute-nucleus01.sock` exists
- `test_discover_capability_via_prefix` — relaxed assertion to check
  `loamspine` is among providers rather than first

---

## Stats

| Metric | Value |
|--------|-------|
| Tests | 8,058 (was 8,053) |
| Failures | 0 |
| Warnings | 0 |
| Crates | 26 |
| Production files >800L | 0 |

---

## Remaining Wave 60 targets

- **Cross-gate `graph.execute` Phase B** — `relay` hints on graph nodes.
  Timeline: Wave 65. `gate` hint already works today via direct TCP.
- **`FALLBACK_RUNTIME_BASE`** (`/tmp/biomeos`) still in `constants/mod.rs`
  as tier-5 documentation. Actual production paths now resolve to
  `/run/biomeos` instead. Full removal requires gating behind
  `#[cfg(debug_assertions)]` or a feature flag.
