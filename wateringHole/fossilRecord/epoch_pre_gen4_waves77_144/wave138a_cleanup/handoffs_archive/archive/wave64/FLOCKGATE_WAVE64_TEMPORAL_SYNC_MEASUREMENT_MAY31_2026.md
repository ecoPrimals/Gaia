# Temporal Sync Sustained Measurement — Wave 64

**Date:** May 31, 2026
**Gate:** flockGate (WAN shadow)
**Target:** Validate K-Derm relay chain under sustained push load

---

## Methodology

Push 6 commits from flockGate over the Wave 64 session. Measure:
1. Push latency to Forgejo (SSH, port 2222)
2. Push latency to GitHub (SSH, direct)
3. Forgejo → GitHub relay propagation time

---

## Results

### Push Latency (gate → remote)

| # | Target | Commit | Time (ms) | Notes |
|---|--------|--------|-----------|-------|
| 1 | forgejo | Gallery template | 1,408 | First push of session |
| 2 | forgejo | wateringHole AAR | 1,316 | Different repo |
| 3 | origin | Rebased gallery | 1,143 | Direct to GitHub |
| 4 | forgejo | Sync rebased head | 1,201 | Force-with-lease |
| 5a | forgejo | Build metrics | 1,319 | — |
| 5b | origin | Build metrics | 1,152 | Same commit, sequential |
| 6 | forgejo | Relay test marker | 1,404 | Forgejo-only (relay test) |

**Summary:**
- Forgejo (WAN SSH): **1.2–1.4s** per push (consistent)
- GitHub (direct SSH): **1.1–1.2s** per push (consistent)
- Delta: ~150-200ms overhead for Forgejo route vs direct GitHub

### Relay Propagation (Forgejo → GitHub)

| Test | Commit | Wait | Result |
|------|--------|------|--------|
| Push 1 | Gallery template | 9s | NOT PROPAGATED |
| Push 6 | Relay marker | 36s | NOT PROPAGATED |

**Finding:** The Forgejo → GitHub relay chain is **not active for sporePrint**.
The commit pushed only to Forgejo did not appear on GitHub within 36 seconds
of polling (3s intervals, 12 checks).

### Relay Chain Analysis

The ~3s relay propagation reported earlier likely applies to repos with
Forgejo post-receive hooks configured (e.g., wateringHole via peptidoglycan
relay). sporePrint may not have the relay hook installed on golgiBody's
Forgejo instance.

**Hypothesis:** The relay hook at `hooks/forgejo/` is configured per-repo.
sporePrint needs its hook registered.

---

## Recommendations for eastGate

1. **Install Forgejo relay hook for sporePrint**: The push relay
   (golgiBody → peptidoglycan → golgiBody-ext → GitHub) needs to be
   enabled for the `ecoPrimals/sporePrint` repository.

2. **Verify relay hook inventory**: Which repos have the push relay active?
   Document in GATE_SETUP_STANDARD or wateringHole README.

3. **Dual-push workaround**: Until relay is configured, flockGate pushes to
   both `forgejo` and `origin` manually. This works but defeats the purpose
   of sovereign-first architecture.

---

## Gate Performance (flockGate WAN)

| Operation | p50 | p95 | Notes |
|-----------|-----|-----|-------|
| git push forgejo | 1.3s | 1.4s | SSH over WAN (VPS in NY) |
| git push origin | 1.1s | 1.2s | SSH to GitHub |
| zola build (226p) | 746ms | — | i9-13900K, NVMe |
| cargo build (release) | 5.56s | — | spore-validate, clean |
| cargo test (80 tests) | 0.6s | — | All passing |

---

## Conclusion

**Push latency is stable and fast** — both Forgejo and GitHub receive pushes
within 1.1-1.4s from flockGate WAN. The network path is reliable with no
observed failures or retries across 6 pushes.

**Relay chain is inactive for sporePrint** — this is the key finding.
The automatic Forgejo → GitHub propagation that was validated for other repos
needs to be explicitly enabled for sporePrint. Until then, dual-push works.

No drift, failures, or retry scenarios encountered during measurement.
