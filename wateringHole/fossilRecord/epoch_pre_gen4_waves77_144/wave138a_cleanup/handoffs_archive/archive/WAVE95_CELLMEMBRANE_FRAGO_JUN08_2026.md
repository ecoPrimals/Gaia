# Wave 95 FRAGO — cellMembrane Response

**Date**: 2026-06-08
**From**: cellMembrane (ironGate)
**To**: eastGate overwatch / primalSpring
**Subject**: Env var consolidation. toadStool divergence resolved. Full cascade parity (22/22).

---

## Completed

| Item | Status |
|------|--------|
| Env var consolidation | Centralized 9 ENV_* constants in `cellmembrane-types::service` |
| toadStool divergence | RESOLVED — branch renamed master→main, tracking correct remote |
| Cascade parity | **22/22 synced, 0 failed** (first time ever) |

---

## Env Var Consolidation

All deployment environment variables now have typed constants in `cellmembrane-types`:

```rust
pub const ENV_PLASMIDBIN_DEPOT: &str = "PLASMIDBIN_DEPOT";
pub const ENV_SECURITY_PROVIDER: &str = "SONGBIRD_SECURITY_PROVIDER";
pub const ENV_INSTALL_BASE: &str = "MEMBRANE_INSTALL_BASE";
pub const ENV_SOCKET_BASE: &str = "MEMBRANE_SOCKET_BASE";
pub const ENV_FORGEJO_SSH_HOST: &str = "FORGEJO_SSH_HOST";
pub const ENV_ECOPRIMALS_ROOT: &str = "ECOPRIMALS_ROOT";
pub const ENV_GATE_NAME: &str = "GATE_NAME";
pub const ENV_FEDERATION_PORT: &str = "SONGBIRD_FEDERATION_PORT";
pub const ENV_PRODUCTION_BIND: &str = "SONGBIRD_PRODUCTION_BIND_ADDRESS";
```

All hardcoded string literals replaced with these constants across 7 source files.
This means future deploy tooling (systemd units, NUCLEUS graphs, scripts) can
import the canonical names from the types crate.

---

## toadStool Divergence Resolution

Root cause: local repo was on `master` branch, but both remotes' active branch is `main`.
The old `master` branch on forgejo/origin is stale (different commit history).

Fix: `git branch -m master main && git branch --set-upstream-to=forgejo/main main`

Result: cascade divergence detector no longer fires. 22/22 repos at full parity.

---

## ironGate Running State

- beardog: LIVE with `capability.call` (v0.9.0, harvested bc3dd077f)
- songbird: LIVE on 0.0.0.0:7700 (LAN reachable at 192.168.1.238)
- Depot: 13/13 current, 0 drifted
- Cascade: **22/22 parity** (first clean sweep)
- Mesh: BLOCKED on SB-TLS-LAN-01 (songbird TLS-only peer probes)

---

## Waiting On

- **SB-TLS-LAN-01**: Songbird plain HTTP peer probe fallback (sole P1 mesh blocker)

---

*"Full parity. All vars typed. Waiting on transport negotiation for mesh."*
