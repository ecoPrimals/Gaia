# strandGate — Wave 155i Node Atomic Validation

**Date**: Jul 29, 2026 15:30 EDT | **Wave**: 155i | **From**: strandGate hardware/overwatch
**Gate**: strandGate | **Status**: **NODE ATOMIC VALIDATED. 5 primals, 450 methods, sub-ms GPU dispatch, 746 pipelines/sec.**

---

## SUMMARY

Second cascade from Forgejo complete (latest 155i with biomeOS v4.45 composition
broker, 8-primal deep debt wave). Compute Trio rebuilt from source (deep debt
changes in all three). 5/5 primals redeployed and healthy. Node Atomic composition
validated: health matrix, capability discovery, BTSP trust chain, GPU compute
pipeline, shader compilation, defense observation, and sustained load profiling.

---

## CASCADE DELTA (this pass)

| Repo | Delta | Key Change |
|------|-------|-----------|
| biomeOS | +1,783 −822 | **Composition broker SHIPPED** (v4.45): riboCipher framing, BTSP executor, 35 E2E tests |
| bearDog | +168 −1 | ACME Phase 2 AAR + status |
| songBird | +2,299 −2,077 | **P0 FIXED**: Windows TCP fallback, 2 test monoliths split → 10 modules |
| nestGate | +26,683 −524 | CAS on ZFS verified, probe CLI, service probe, systemd unit |
| cellMembrane | −135 net | Deep debt: sandbox fail-closed, registry-driven tower status |
| sweetGrass | +463 | G3 E2E validated: 11 ledger tests, mock loamSpine UDS |
| skunkBat | +3 −3 | tokio-macros update |
| sporePrint | +122 −92 | Wave 155i ecosystem state refresh |

---

## REBUILD — DEEP DEBT BUILDS (native glibc)

All three Compute Trio primals had source-code changes since last build:

| Primal | Delta Since Last Build | Build Time | Status |
|--------|----------------------|-----------|--------|
| barraCuda | `ef7ab09a` deep debt: self-knowledge, deprecation, lint evolution | 1m 52s | Clean |
| coralReef | `c6ab001f` deep debt: capability abstraction, PTX macro modernization, clone reduction | 1m 19s | Clean |
| toadStool | `6e43736db` S346 security fail-closed + `ccba07ff3` S345 deployment guide | 2m 50s | Clean |

---

## NODE ATOMIC — COMPOSITION VALIDATION

### 1. Health Matrix (5/5 primals)

| Primal | Version | Status | Role |
|--------|---------|--------|------|
| bearDog | 0.9.0 | **healthy** | Trust anchor, crypto, BTSP |
| songBird | 0.2.1 | degraded | Discovery (standalone — expected) |
| skunkBat | 0.2.18 | **healthy** | Defense, security observer |
| barraCuda | 0.4.0 | **healthy** | GPU compute (RTX 3090) |
| coralReef | 0.2.0 | **operational** | Shader compiler (11 ISA targets) |

### 2. Capability Matrix

| Primal | Methods | Key Domains |
|--------|---------|------------|
| bearDog | 210 | crypto, btsp, auth, enrollment, ACME |
| songBird | 94 | discovery, federation, mesh, relay, tls |
| skunkBat | 30 | defense, monitoring, threat detection |
| barraCuda | 98 | tensor, compute, ml, stats, linalg, spectral, fhe |
| coralReef | 18 | shader.compile, shader.health |
| **TOTAL** | **450** | **Node Atomic = Tower(334) + Compute(116)** |

### 3. BTSP Trust Chain

| Property | Value |
|----------|-------|
| Auth mode (all primals) | **permissive** |
| BTSP Phase 3 | **supported** (chacha20-poly1305) |
| Cipher suites | chacha20-poly1305, hmac_plain, null |
| Trust gate | strandGate |
| Trust capabilities | math, compute, ml, tensor, stats |
| bearDog peer credentials | available (unix, uid=1000) |

### 4. GPU Compute Pipeline

| Test | Result |
|------|--------|
| GPU stack validation | **2/2 pass** (matmul_identity, tensor_roundtrip) |
| 256×256 GPU matmul (tensor IDs) | **8.1ms** |
| WGSL shader compile (coralReef) | **16.7ms** (64 bytes output) |

---

## SUSTAINED LOAD PROFILING

### GPU Dispatch Latency (128×128 matmul, 100 iterations)

| Metric | Value |
|--------|-------|
| Min | 0.16ms |
| **p50** | **0.27ms** |
| p95 | 0.32ms |
| p99 | 0.46ms |
| Max | 0.46ms |
| Mean ± stdev | 0.25ms ± 0.06ms |
| Errors | **0/100** |

### Shader Compile Latency (WGSL, 50 iterations)

| Metric | Value |
|--------|-------|
| Min | 21.1ms |
| **p50** | **21.4ms** |
| p95 | 25.3ms |
| Max | 34.2ms |

### IPC Roundtrip (health.check, 200 iterations per primal)

| Primal | p50 | p99 | Mean |
|--------|-----|-----|------|
| bearDog | 0.138ms | 0.352ms | 0.140ms |
| barraCuda | 0.141ms | 0.278ms | 0.149ms |
| coralReef | 0.108ms | 0.311ms | 0.116ms |

### Throughput

| Workload | Ops/sec |
|----------|---------|
| Tensor create (64×64) | **3,570 ops/sec** |
| Full pipeline (create+create+matmul) | **746 pipelines/sec** |

---

## SOCKET TOPOLOGY (17 sockets)

```
/run/user/1000/biomeos/
├── beardog-e8b62b6e.sock      ← trust anchor
│   ├── btsp.sock              → beardog (BTSP negotiate)
│   ├── crypto.sock            → beardog (crypto ops)
│   ├── ed25519.sock           → beardog (signing)
│   └── x25519.sock            → beardog (key exchange)
├── songbird-e8b62b6e.sock     ← discovery
│   └── network-e8b62b6e.sock  → songbird (mesh)
├── skunkbat-e8b62b6e.sock     ← defense
│   └── security.sock          → skunkbat
├── math-e8b62b6e.sock         ← GPU compute
│   └── barracuda-e8b62b6e.sock → math
└── coralreef-core-default.sock ← shader compile
    └── shader.sock             → coralreef
```

---

## FINDINGS + DIVERGENCES

| # | Priority | Finding | Notes |
|---|----------|---------|-------|
| 1 | INFO | All primals in **permissive** auth mode | Expected for standalone deployment. Composition broker will enforce BTSP in orchestrated mode. |
| 2 | INFO | songBird **degraded** (5/6 subsystems) | Expected — standalone gate, no mesh peers. IPC is up. |
| 3 | INFO | skunkBat lineage-verifier **unhealthy** | No lineage_id configured. Security observer healthy. |
| 4 | P2 | coralReef `shader.compile.multi` API schema unclear | Requires `jobs` + `input_type` — needs documentation |
| 5 | INFO | GPU dispatch p99 < 0.5ms | Excellent — no tail latency under sustained load |
| 6 | INFO | IPC roundtrip p99 < 0.4ms across all primals | Unix socket overhead is negligible |

---

## BLOCKED ON

- **biomeOS depot binary** (sporeGate): v4.45 composition broker not yet on
  sporeGate depot. Needed for live E2E signal graph orchestration. Source code
  shipped. Not blocking strandGate individual primal IPC.
- **bearDog `crypto.sign_ed25519`** (P1): returns health stub, not signature.
  Blocks Provenance Trio step 7/7.

---

## NEXT WORK (strandGate)

1. E2E signal graph validation with biomeOS broker (once depot binary ships)
2. Cross-gate compute federation (strandGate GPU ↔ westGate storage)
3. Sustained multi-hour load test for stability validation
4. toadStool Node Atomic biome.yaml manifest (orchestrated deployment)
5. AlphaFold tensor pipeline readiness (compute side)

---

*Wave 155i. strandGate Node Atomic VALIDATED. 5 primals, 450 methods, BTSP trust
chain verified, GPU dispatch p50=0.27ms, 746 full pipelines/sec, zero errors under
sustained load. RTX 3090 operational with native glibc builds. Composition broker
shipped but awaiting depot binary for live E2E orchestration. Ready for cross-gate
federation after biomeOS depot refresh.*
