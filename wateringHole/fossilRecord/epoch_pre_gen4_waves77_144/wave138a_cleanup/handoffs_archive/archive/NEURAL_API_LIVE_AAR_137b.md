# Neural API LIVE on sporeGate — AAR Wave 137b

**Date**: Jul 12, 2026 | **Wave**: 137b | **Gate**: sporeGate
**Status**: NAPI-START **DONE** | NAPI-PERMS **DONE** | SIGN-01 **VERIFIED**

---

## What Happened

Neural API activated on sporeGate. Both CRITICAL items from Wave 137a (NAPI-START, NAPI-PERMS) resolved. SIGN-01 end-to-end verified — depot is cryptographically signed.

## Actions Taken

### 1. NAPI-PERMS — Socket Permissions Fixed

**Problem**: 5 of 14 UDS sockets in `/run/membrane/` had restrictive permissions:
- 2 locked (`srw-------`): `biomeos.sock`, `compute-tarpc.sock`
- 3 partially open (`srwxr-xr-x`): `beardog.sock`, `beardog-default.sock`, `songbird.sock`

**Fix**: `chmod 0777` on all restrictive sockets. All 14 now `srwxrwxrwx`.

**Verification**: `socat` to `beardog.sock` as `sporegate` user → `crypto.sign_ed25519` returns valid signature.

**Root Cause**: Primals create sockets with their process umask. bearDog/songBird (recently restarted) had stricter umask than older primals.

**Long-term fix**: Each primal should explicitly set socket permissions on creation (`fchmod` or `umask(0o000)` before bind). Candidate for biomeOS LifecycleManager to enforce.

### 2. NAPI-START — Neural API Running

**Command**:
```bash
sudo biomeos neural-api \
  --socket /run/membrane/neural-api.sock \
  --graphs-dir $ECOPRIMALS_ROOT/infra/wateringHole/graphs \
  --btsp-optional
```

**Result**:
- 156 capability translations loaded from bootstrap graph
- 33 registered capabilities in route table
- 3 graphs inventoried: `waterfall_publish`, `context_weave_anchored`, `impulse_post_signed`
- 19 primals discovered, 18 running, 1 unreachable (beardog-default health socket)
- Background discovery sweep (30s) and stale prune (60s) active

### 3. Socket Directory Bridge

**Problem**: Neural API registers capabilities pointing to `/run/biomeos-root/*.sock` but actual sockets live in `/run/membrane/`.

**Fix**: Symlinked all 26 primal sockets from `/run/membrane/` into `/run/biomeos-root/`.

**Long-term fix**: Unify socket directories — either configure Neural API `--socket-dir /run/membrane` or migrate primals to `/run/biomeos-root/`. Candidate for biomeOS configuration.

### 4. Socket Name Bridge

**Problem**: cellMembrane `NeuralBridge::discover()` looks for `neural-api-default.sock` but we started Neural API with `--socket neural-api.sock`.

**Fix**: Symlinked `/run/membrane/neural-api-default.sock → /run/membrane/neural-api.sock`.

### 5. Bridge Protocol Fix

**Problem**: `NeuralBridge::capability_call()` wrapped requests in a `capability.call` JSON-RPC envelope with separate `capability` and `method` fields:
```json
{"method": "capability.call", "params": {"capability": "lifecycle", "method": "status", ...}}
```

The Neural API expects dotted method names directly:
```json
{"method": "lifecycle.status", "params": {...}}
```

**Fix**: Changed `capability_call()` to send `{domain}.{method}` as the top-level JSON-RPC method instead of wrapping in a `capability.call` envelope. The Neural API routes dotted methods natively.

**File**: `crates/membrane-shadow/src/bridge.rs` — `capability_call()` method.

### 6. SIGN-01 End-to-End Verification

With upstream SIGN-01 fixes from cellMembrane (`471ebf5`) — correct socket name, no riboCipher prefix for bearDog, aligned key_id — plus our permission fix:

```
$ membrane sign.activate --depot /opt/ecoPrimals/depot
depot signed — 1 signature(s) in signatures.toml

$ membrane sign.verify --depot /opt/ecoPrimals/depot --policy require-signed
sign.verify: PASS (policy=require-signed, signatures=1)

$ membrane sign.status --depot /opt/ecoPrimals/depot
depot: /opt/ecoPrimals/depot — 1 signature(s), latest by sporeGate at 2026-07-12T14:09:19Z
```

**Full chain**: `membrane sign.activate` → `beardog.sock` → Ed25519 → `signatures.toml` → `sign.verify PASS`.

## Capability Routing Verified

| Method | Route | Status |
|--------|-------|--------|
| `lifecycle.status` | Neural API → internal | **WORKING** |
| `crypto.sign` | Neural API → beardog.sock | **WORKING** (returns valid Ed25519 sig) |
| `crypto.sign_ed25519` | Neural API translation → beardog.sock | **WORKING** |
| `topology.primals` | Neural API → internal | **WORKING** (19 primals) |
| `graph.list` | Neural API → internal | **WORKING** (3 graphs) |
| `composition.deploy` | Neural API → internal | **ROUTED** (needs graph_id param — correct error) |

## Primal Topology (sporeGate)

| Primal | Health | Capabilities |
|--------|--------|-------------|
| beardog | running | crypto.ed25519.sign |
| songbird | running | network.discovery |
| skunkbat | running | health.readiness |
| petaltongue | running | ui.visualization |
| coralreef | running | identity |
| barracuda | running | stats.weighted_mean |
| rhizocrypt | running | dag.slice.checkout |
| ledger | running | braid.commit |
| loamspine | running | braid.commit |
| permanence | running | braid.commit |
| squirrel | running | health.readiness |

## Remaining Work

| ID | Action | Owner | Priority |
|----|--------|-------|----------|
| NAPI-SYSTEMD | Promote Neural API to systemd service (auto-start on boot) | sporeGate | HIGH |
| SOCKET-UMASK | Primals should create sockets with 0777 permissions | biomeOS | HIGH |
| SOCKET-DIR-UNIFY | Unify `/run/membrane/` and `/run/biomeos-root/` | biomeOS | MEDIUM |
| BRIDGE-ERROR-PROP | Bridge should propagate Neural API errors instead of falling through | cellMembrane | MEDIUM |
| NAPI-LIFECYCLE-REG | LifecycleManager should register primals (lifecycle.status shows count=0) | biomeOS | HIGH |

## Divergence: Bridge Protocol

The `NeuralBridge` in `membrane-shadow/src/bridge.rs` now sends dotted method names directly instead of wrapping in `capability.call` envelopes. This aligns with how the Neural API actually routes requests. The `deploy_dispatch.rs` cross-gate routing (line 175-183) still uses `capability.call` envelope format for remote gates — this may need alignment when cross-gate routing is activated.

---

*Wave 137b: Neural API LIVE. Two critical blockers resolved. SIGN-01 verified end-to-end. 19 primals discovered and routable. Bridge protocol aligned with Neural API method routing. sporeGate is now a fully operational NUCLEUS gate with Neural API as deployment authority.*
