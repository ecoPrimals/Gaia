# blueGate After Action Review — Fresh Depot Deployment (Wave 155k)

**Date**: Jul 30, 2026 09:55 EDT | **Wave**: 155k | **Gate**: blueGate (Windows)
**Session**: Cascade + 14/14 depot refresh + NUCLEUS restart + feature validation

---

## What Worked

### 1. Depot rebuild quality (sporeGate)
All 14 binaries downloaded and started on first attempt. No more source-build
workarounds. songBird 0.2.1 runs natively on Windows — the P0 fix is baked in.
Binary sizes generally decreased (bearDog 25% smaller, songBird 11% smaller).

### 2. Boot ordering discipline
Tower → Nest → Node → biomeOS LAST. All primals found their dependencies.
biomeOS discovered all primals on startup. No ordering failures.

### 3. bearDog crypto.sign (the big feature)
`crypto.sign_ed25519` returns valid Ed25519 signatures with public key and key_id.
Both `crypto.sign` and `crypto.sign_ed25519` methods work. DID key generation
functional. This unblocks Provenance 7/7 on Windows.

### 4. Memory efficiency
131.1 MB for 13 primals (down from 147.5 MB). Fresh toolchain + optimizations
yielded a 11% reduction. squirrel (17.2 MB) remains the highest per-primal.

### 5. Cascade clean
12 repos updated, 28 already current, 0 merge conflicts. The fossilRecord
system means clean handoff directories for new wave content.

---

## What Didn't Work (or Changed)

### 1. bearDog FAMILY_SEED requirement (BREAKING)
bearDog v0.9.0 refuses to start without `FAMILY_SEED` or `BEARDOG_FAMILY_SEED`
env var. Previous versions accepted `FAMILY_ID` alone. First start failed silently
(process exited immediately). Error message is clear once you run foreground, but
`Start-Process` hides stderr.

**Impact**: Any automated deployment script from Wave 155i will break.
**Fix**: Set `FAMILY_SEED` env var (32-byte base64 encoded random bytes).
**Upstream**: Document this in deployment guides. Consider a `--generate-seed` flag.

### 2. PRIMAL_BIND_MODE value mismatch
Previous sessions used `tcp_only` as the env var value. bearDog v0.9.0 expects
`tcp` (no `_only` suffix). The `--bind-mode` help shows enum: `auto`, `filesystem`,
`abstract`, `tcp`. Using `tcp_only` silently falls back to `auto` mode.

**Impact**: Primals may attempt UDS binding when TCP was intended.
**Upstream**: Standardize on `tcp` across all documentation and scripts.

### 3. biomeOS API returns 403 on all endpoints
biomeOS v4.47 enforces BTSP authentication on all `/api/v1/*` endpoints.
Only `/health` is accessible without auth. This is correct security posture
but means external monitoring/tooling needs BTSP client implementation.

**Impact**: No external visibility into composition state, capabilities, endpoints.
**Upstream**: Document BTSP client auth flow. Consider `/api/v1/health` or
`/api/v1/status` as unauthenticated informational endpoints.

### 4. sporePrint branch corruption
`infra/sporePrint` has a broken branch head. Non-blocking (sporePrint is config
data, not a runtime primal) but needs attention.

**Fix**: `git -C infra/sporePrint fetch origin && git -C infra/sporePrint reset --hard origin/main`

### 5. coralReef noisy --version output
coralReef emits an ERROR-level log line when called with `--version`, making
version parsing unreliable for automated tooling.

### 6. petalTongue IPC protocol change
petalTongue v1.7.0 forcibly closes TCP connections on standard JSON-RPC health
probes. The primal is running (process visible, memory allocated) but the
IPC protocol may have changed from previous versions.

---

## Divergence from Blurb

| Blurb Expectation | Actual | Gap |
|-------------------|--------|-----|
| "Pull fresh `.exe`" | 14/14 pulled, all start | **CLOSED** |
| "lifecycle-managed NUCLEUS" | biomeOS running, enforcing BTSP | **PARTIAL** — can't verify lifecycle management without BTSP client |
| "sub-builder activation" | Not attempted this session | **OPEN** — needs songBird IPC + sporeGate coordination |
| Boot order: Tower → Nest → Node → biomeOS | Followed exactly | **CLOSED** |
| 131.1 MB footprint | Down from 147.5 MB | **BETTER** than expected |

---

## What Needs to Evolve

### Deployment Automation
1. **Startup script**: Need a `Start-Nucleus.ps1` that handles FAMILY_SEED generation,
   correct PRIMAL_BIND_MODE, boot ordering with health-check gates between atomics.
2. **Health monitoring**: A `Test-Nucleus.ps1` that probes all 13 primals including
   riboCipher framing for toadStool and BTSP auth for biomeOS.
3. **Service registration**: Windows services or scheduled tasks for auto-restart.

### BTSP Client
biomeOS API is gated behind BTSP. Need a lightweight BTSP client (PowerShell or
standalone tool) that can:
- Exchange trust with bearDog
- Obtain ionic tokens
- Present tokens to biomeOS API

### Sub-Builder Pipeline (J12)
blueGate's next milestone is sub-builder dispatch via songBird IPC:
- songBird v0.2.1 has TCP registration with shared ServiceRegistry
- sporeGate needs to register blueGate as a build target
- songBird IPC needs to be validated for cross-gate build dispatch

### Platform Maturity Tracking

| Concern | Wave 155i | Wave 155k | Delta |
|---------|-----------|-----------|-------|
| Depot binaries | 14/14 (stale) | 14/14 (fresh) | **CURRENT** |
| songBird source build | Required (P0 fix) | Not needed | **RESOLVED** |
| bearDog crypto.sign | Stub | **WORKING** | **RESOLVED** |
| toadStool riboCipher | Enforced | **VALIDATED** | Confirmed |
| biomeOS lifecycle | Basic | **BTSP-gated** | Evolved |
| FAMILY_SEED | Not required | **REQUIRED** | Breaking change |
| Memory footprint | 147.5 MB | 131.1 MB | 11% reduction |

---

## Registration

```
Gate:     blueGate
Platform: Windows 10 (x86_64-pc-windows-gnu)
Wave:     155k
Primals:  13/13 RUNNING
Memory:   131.1 MB
Depot:    14/14 fresh (Jul 30 rebuild)
Repos:    40 synced (12 updated this cascade)
Transport: TCP-only
BTSP:     bearDog v0.9.0 with FAMILY_SEED
Crypto:   Ed25519 sign/verify WORKING
RiboCipher: toadStool enforcement CONFIRMED
biomeOS:  v4.47, BTSP auth on API
```

---

*Wave 155k AAR — blueGate fresh depot deployment. 13/13 NUCLEUS running on Windows.
bearDog crypto.sign VALIDATED. songBird depot build works (no source build needed).
131.1 MB total. BTSP auth enforced. Sub-builder activation NEXT.*
