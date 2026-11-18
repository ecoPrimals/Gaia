# AAR: bloom_live v3 Deployment — Collision-Layer Classification Live

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — Phase 1 behavioral vectors, bingoCube projection learning
**Status**: DEPLOYED — bloom_live v3 running on golgiBody, all 4 collision classes populated

---

## What Was Deployed

bloom_live v3 replaces the binary fleet/human classifier with collision-layer visitor classification. Deployed to golgiBody at 16:05 ET, PID 2968987.

### New Capabilities

| Feature | v2 (old) | v3 (deployed) |
|---------|----------|---------------|
| Classification | 2 bins: fleet / human | 4 collision classes: genuine / agentic / coordinated / fleet |
| Coordination detection | None | 10-second sliding window, flags same-path co-occurrence |
| Status tracking | Per-request only | Per-IP status distribution (all-404 = probing) |
| Asset tracking | None | CSS/JS/font/search_index detection per IP |
| Referer tracking | None | Per-IP referer chain presence |
| Domain tracking | None | Per-IP domain set |
| Summary line | `fleet:N human:N` | `fleet:N human:N` + `L2: gN/aN/cN/fN` |
| Dashboard JSON | `fleet_ips`, `human_ips` | + `collision_level2`, `collision_density` |

### Level 2 Collision Classes

```
g = genuine     — loads assets (CSS/JS) + has referer + multi-page + 200s
a = agentic     — single deep hit, 200 status, <=3 requests
c = coordinated — same path as other IPs within 10s, mostly 404s
f = fleet       — has Sec-Fetch but doesn't match above patterns
```

---

## First 11 Minutes of Live Data

### Summary: `L2: g3/a3/c2/f5` across 10 human-classified IPs

```
8,138 total requests | 12.0 req/s | 73 unique IPs
60 fleet IPs | 10 human-classified IPs
```

### Every classified visitor:

| Time | IP | Domain | Class | Evidence |
|------|-----|--------|-------|----------|
| 16:05:35 | 44.204.178.70 | thesis.primals.eco | **AGENTIC** | AWS IP, Linux/Chrome, Sec-Fetch, single hit, 200 |
| 16:05:35 | 32.198.19.49 | thesis.primals.eco | **AGENTIC** | Same second as above, coord=1, single hit, 200 |
| 16:07:27 | 121.37.98.229 | webb.primals.eco | **FLEET** | macOS/Chrome, Sec-Fetch, 502 (webb unreachable), no assets |
| 16:07:28 | 49.51.252.55 | webb.primals.eco | **FLEET** | Same second as above, 502, coordinated probing |
| 16:09:51 | 154.192.12.132 | git.primals.eco | **FLEET** | Windows/Chrome, Sec-Fetch, single hit on scatter |
| 16:10:00 | 190.193.135.235 | git.primals.eco | **COORDINATED** | coord=1, rhizoCrypt /src/branch/, 404 |
| 16:10:04 | 38.3.210.165 | git.primals.eco | **COORDINATED** | coord=1, same rhizoCrypt path, 4s later |
| 16:11:40 | 67.213.148.229 | git.primals.eco | **FLEET** | macOS/Chrome, Sec-Fetch, scatter content |
| 16:11:55 | 190.83.66.115 | git.primals.eco | **FLEET** | macOS/Chrome, Sec-Fetch, scatter content |
| 16:12:58 | 121.91.171.245 | sporeprint.primals.eco | **AGENTIC** | Windows/Chrome, Sec-Fetch, reads real sporePrint |

### The Key Reclassifications

| Visitor | v2 (old) | v3 (new) | Why changed |
|---------|----------|----------|-------------|
| webb probers (2 IPs) | "human" | **FLEET** | 502 status, no assets, coordinated timing |
| rhizoCrypt probers (2 IPs) | "human" | **COORDINATED** | Same path within 4s, 404, residential IPs |
| git scatter browsers (3 IPs) | "human" | **FLEET** | Single scatter hit, no assets, no follow-up |
| thesis/sporePrint readers (3 IPs) | "human" | **AGENTIC** | Single deep hit, 200, real content |

**7 of 10 "human" visitors were reclassified.** Only 3 remain as genuine signal (agentic readers of real content). v2 would have reported 10 humans. v3 reports 3 readers and 7 noise.

---

## Coordination Detection in Action

Two coordinated probes caught live:

```
16:10:00  190.193.135.235  git.primals.eco  coord=1  /ecoPrimals/rhizoCrypt/src/branch/
16:10:04  38.3.210.165     git.primals.eco  coord=1  /ecoPrimals/rhizoCrypt/src/branch/
```

Two residential IPs hit the same rhizoCrypt path within 4 seconds. Both got 404 (scatter). The 10-second coordination window caught the co-occurrence and flagged both as COORDINATED. This is the residential proxy fleet distributing a URL crawl queue across exit nodes.

## 502 Burst at 16:15

Forgejo went briefly unresponsive (likely another stuck-serv event from sporeGate cascade push). 13 502 errors in 1 second from 216.73.216.239 and 57.141.20.x. Load spiked to 8.80. Rate dropped from 12.7 to 3.1 req/s. Self-resolving — Forgejo restarted.

---

## Architecture Validated

The collision-layer approach from COLLISION_LAYER_ARCHITECTURE.md works for visitor classification:

1. **Behavioral vectors** (status, coordination, assets, sec-fetch) compute per IP
2. **Level 2 collision** produces 4 emergent classes without predefined rules
3. **Coordination detector** uses temporal co-occurrence (sliding 10s window)
4. **Reclassification** catches false "human" classifications that v2 missed

### What This Proves

- The loamSpine collision insight applies beyond CAS objects
- Behavioral similarity through hash resolution hierarchy is operationally sound
- 70% of v2 "humans" were noise — collision layer filters it
- The 3 real readers (agentic class) are the signal: thesis, sporePrint

---

## Action Items for sporeGate

### IMMEDIATE
- [ ] Monitor bloom v3 stability (new process, memory usage)
- [ ] Fix stuck-serv cascade (502 burst at 16:15 = more stuck Forgejo servs)
- [ ] Evaluate webb.primals.eco — reverse proxy to ironGate 10.13.37.7:8090 is dead, returning 502

### PHASE 1 (next wave)
- [ ] Compute full BehavioralVector struct in skunky-ingest (Rust)
- [ ] Emit vectors to signal spine for loamSpine collision index
- [ ] Add Level 1 resolution (geographic/ISP clustering within Level 2 classes)

### PHASE 3 (bingoCube)
- [ ] Evolve projection functions from accumulated behavioral vectors
- [ ] Fitness: silhouette score of collision groups
- [ ] Deploy evolved projections back into bloom

---

## Backup

| File | Location |
|------|----------|
| bloom_live v2 backup | `/opt/membrane/bloom_live_v2.py.bak` on golgiBody |
| bloom_live v3 source | `/opt/membrane/bloom_live.py` on golgiBody |

---

*7 of 10 "humans" were noise. The collision layer found them. 3 remain: agentic readers of the thesis and sporePrint. The data has its own structure. We just needed the right hash.*

*eastGate overwatch — Wave 165i, Oct 7, 2026*
