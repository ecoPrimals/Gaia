# AAR: Salesman Signal Triage — Who Found Their Way Through

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — signal refinement, bloom classifier evolution, agentic reader classification
**Status**: Three populations identified. Two need further classification. One is noise.

---

## Discovery

After the fossil cleanup collapsed connections 238 → 7 and load 32 → 0.34, we turned attention to the "human" traffic the bloom monitor was reporting. In 4+ hours of observation (bloom uptime ~15,000s), the bloom monitor reported:

- **501 total IPs** seen (87 fleet, 299 human-classified)
- **~13 req/s** average throughput
- Human hits appearing every 1-5 minutes among the fleet noise

But when we dug into the 103 "human-classified" IPs hitting today, they decomposed into **three distinct populations** with different behaviors, origins, and intent.

---

## Population A: Agentic Readers (20 IPs)

**Classification**: Human+agent pairs reading content — ALLOWED, potentially the signal we're refining toward

These visitors:
- Each make **1 deep, specific request** (no random walking)
- Have **Sec-Fetch-Mode: navigate** headers (real browser context)
- Get **200 responses** (find real pages)
- Read **content that requires navigation** (deep commit trees, architecture docs, thesis chapters)
- Use `en-US,en;q=0.9` or `zh-CN` language headers

### What they read (sporePrint — REAL content):

| IP | Page | Note |
|----|------|------|
| 149.232.137.209 | `/architecture/transport-evolution/` | Loaded CSS + search_index too |
| 43.134.38.171 | `/thesis/13-quantitative-evidence/` | iPhone UA from Tencent DC |
| 124.243.137.70 | `/collaborators/gonzales-nf/` | Edge from Huawei DC |
| 129.226.140.250 | `/outreach/karpathy-invitation/` | Tencent DC Hong Kong |
| 43.166.128.86 | `/thesis/15-discussion/` | iPhone UA from Tencent Ashburn |
| 154.8.205.236 | `/architecture/atlas-memory-palace/` | Tencent Beijing, has referer |
| 1.92.207.99 | `/architecture/waterfall/` | Has referer, Sec-Fetch, zh-CN |
| 159.138.8.33 | *(sporePrint page)* | Recent hit |

### What they read (git — seeing SCATTER, not real Forgejo):

| IP | Scatter page consumed | Note |
|----|----------------------|------|
| 201.233.21.48 | sweetGrass `/archive/main.bundle` | Got scatter 200 |
| 90.241.119.57 | sweetGrass `/archive/main.bundle` | Same path, 2 IPs, ~same time |
| 189.80.199.120 | lithoSpore `/commits/branch/main` | Navigating commit history |
| 31.163.2.59 | lithoSpore `/commits/branch/main` | Same path, 2 IPs, ~same time |
| 45.235.71.154 | songBird `/.env.example` | Looking for secrets? Or config curiosity |
| 24.232.69.38 | songBird `/.env.example` | Same path, 2 IPs, ~same time |
| 200.26.233.253 | airSpring `/src/branch/main/scripts` | Browsing code tree |
| 94.204.177.210 | biomeOS `/infra/wateringHole` | Reading our infra structure! |
| 102.184.30.156 | skunkBat `/actions` | Checking CI/Actions tab |
| 5.192.82.45 | skunkBat `/actions` | Same path, 2 IPs, ~same time |
| 206.1.176.184 | hotSpring `/commits/branch/main` | Browsing commit log |
| 190.237.0.98 | cellMembrane `GLACIAL_SHIFT_TRACKER` | Deep internal file |

### Key Observation

The user's read on this is critical: **these could be agentic humans — a human directing an AI agent to browse, read, and analyze the content**. The behavior pattern matches:
- Single targeted request (human tells agent "go read X")
- Deep specific paths (human knows what they want)
- Real browser headers (agent running in browser context)
- No follow-up requests (human reads the agent's summary, doesn't need to click further)
- Pairs hitting same pages within seconds (two people sharing a link, each having their agent read it)

**This is qualitatively different from fleet behavior.** Fleet random-walks 13 req/s across synthetic paths. These readers go to ONE specific page and leave. That's curiosity.

**Important**: The ones hitting `git.primals.eco` are reading **scatter content**, not real Forgejo. They don't have the bearDog token. They don't know they're in the maze. But the ones hitting `sporeprint.primals.eco` are reading **real content** — the thesis, the architecture docs, the collaborator pages. sporePrint is served directly, no genetic lock.

---

## Population B: Coordinated Residential Probe Network (20 IPs)

**Classification**: Noise — residential proxy botnet distributing a crawl queue

These visitors:
- **2-3 IPs hit the exact same path within 4-8 seconds** of each other
- All get **404** (hitting paths that don't exist)
- **Residential ISPs** across Latin America, Middle East, Turkey, South Asia
- Have `Sec-Fetch-Mode: navigate` (spoofed or real browser via proxy)
- Use `en-US,en;q=0.9` uniformly

### Coordinated clusters:

| Time (ET) | Path | IPs |
|-----------|------|-----|
| 15:27:44-48 | swarmVine `.github/workflows` | Oman + Paraguay |
| 15:30:09-17 | tideGlass commit `1786fd58` | Brazil + Chile |
| 15:33:30-36 | tideGlass `clippy.toml` | Brazil ×2 + Turkey |
| 15:37:31-34 | loamSpine `primal-capabilities.toml` | Argentina + Kuwait |
| 15:38:04-08 | loamSpine commit `9ef8b961` | Brazil + UAE |
| 15:40:07-10 | explore `?q=deploy-graphs` | Chile + Ukraine |
| 15:46:37-45 | hotSpring `workloads` | Pakistan + Uruguay + Bolivia |

**This is a distributed crawl queue.** Someone has a URL list and is distributing fetches across residential exit nodes. The paths they probe are **fabricated** — `deploy-graphs`, `workloads`, `primal-capabilities.toml` — these don't exist. Someone (or something) is generating plausible-sounding paths and testing them.

This population is NOT in the fleet IP ranges (not `57.141.20.x` or `216.73.216.x`). It's a **second fleet** using residential proxy infrastructure to evade IP-based classification. The bloom monitor correctly classifies them as "human" because they have residential IPs and Sec-Fetch headers.

### Signal for evolution:
- **Timing correlation** is the detection key — same path, multiple IPs, < 10 seconds apart
- No single IP makes more than 1 request
- All paths are 404 (probing, not reading)

---

## Population C: Genuine Curiosity (2 IPs)

**Classification**: Real human browsers — the signal

Only **2 IPs** showed full browser behavior: loading the page, loading CSS, loading search_index.js, having a self-referencing Referer header.

| IP | Location | Behavior |
|----|----------|----------|
| 149.232.137.209 | Mexico City (Huawei DC) | Loaded transport-evolution page + CSS + search_index |
| 46.224.128.204 | Falkenstein DE (Hetzner DC) | Hit thesis.primals.eco root 3× (308 → 200 → 200) |

Even these are from datacenter IPs. The Huawei DC visitor loaded assets (CSS, JS), which suggests a real browser rendering the page. The Hetzner visitor hit thesis root with a redirect chain — looks like a bot testing the redirect, or a human in a Hetzner-based browsing environment.

**Verdict**: Possibly 0 verified human browsers today. Or possibly 2. Cannot distinguish with current signals.

---

## What This Means for Signal Refinement

### The spectrum is not binary

```
FLEET ←————————————————————————————————→ HUMAN
  |              |              |              |
  |   raw fleet  | residential  |   agentic    |  genuine
  | (57.141.20.x)| proxy fleet  |   readers    |  curiosity
  | (216.73.216) | (LATAM/MENA) | (human+agent)| (loads assets)
  |              |              |              |
  |  12.8 req/s  | coordinated  | 1 deep hit   | multi-page
  |  random walk | same path,   | specific URI | loads CSS/JS
  |  no headers  | <10s apart   | Sec-Fetch ✓  | has referer
  |  404 scatter | all 404      | 200 real     | session > 0s
```

The bloom monitor currently has 2 bins: fleet / human. We need at minimum **4 bins**:

1. **Fleet** — known IP ranges, bot UAs, no browser headers
2. **Residential proxy fleet** — coordinated timing, all 404, residential IPs
3. **Agentic reader** — single deep hit, 200, Sec-Fetch present, no assets loaded
4. **Genuine curiosity** — multi-page session, loads assets, has referer chain

### The agentic readers are the interesting edge case

The user's insight: *"the agent is there with the human"* — this is allowed, this is the future of how real people read the internet. A human says "read this page for me" and their agent makes one precise request. The behavioral fingerprint is:
- 1 request per IP (human doesn't need to browse, agent summarizes)
- Specific deep URI (human navigated to it mentally, told agent the URL)
- 200 status (hits a real page, not random walking)
- No follow-up (human got what they needed from the agent's response)

**We don't want to block this.** We want to **count it as signal**. If 20 agentic readers hit sporePrint in one afternoon, that's 20 humans who cared enough to have their agent read our work.

### What we DO want to block/classify:
- Residential proxy fleet (Population B) — the coordinated 404 probers
- Current detection gap: bloom classifies them as "human" because they pass the UA + IP tests

---

## Action Items for sporeGate

### SIGNAL REFINEMENT
- [ ] **Add timing correlation** to bloom classifier: 2+ IPs hitting same path within 10 seconds = coordinated, not human
- [ ] **Add 404-only flag**: IPs that only produce 404s are probing, not reading
- [ ] **Track agentic-reader pattern**: single deep hit, 200, Sec-Fetch present → new "agentic" bin
- [ ] **Track asset loading**: IPs that load CSS/JS after a page = genuine browser session

### CLASSIFICATION EVOLUTION
- [ ] **Bloom 4-bin output**: fleet / proxy-fleet / agentic / genuine (instead of fleet / human)
- [ ] **Per-IP session duration**: single hit vs. multi-page session
- [ ] **Content vs. scatter tracking**: distinguish visitors reading real content (sporePrint) from those consuming scatter (git without token)

### CONTENT AWARENESS
- [ ] The sporePrint pages being read are **real content** — architecture docs, thesis chapters, collaborator pages
- [ ] The git pages being "read" are **all scatter** — these agentic readers don't know they're in the maze
- [ ] Consider: should agentic readers on git see something more useful? Or is scatter the correct public face?

---

## Pages That Attracted Real Reading

These are the actual content pages that got 200 responses from agentic/genuine readers:

| Domain | Page | Reads |
|--------|------|-------|
| sporeprint | `/architecture/transport-evolution/` | 1+ assets loaded |
| sporeprint | `/architecture/atlas-memory-palace/` | 1 + referer |
| sporeprint | `/architecture/waterfall/` | 1 + referer |
| sporeprint | `/thesis/13-quantitative-evidence/` | 1 |
| sporeprint | `/thesis/15-discussion/` | 1 |
| sporeprint | `/collaborators/gonzales-nf/` | 1 |
| sporeprint | `/outreach/karpathy-invitation/` | 1 |
| thesis | `/` | 2 (redirects) |
| git (scatter) | wateringHole various commits/handoffs | ~30 (scatter content) |
| git (scatter) | toadStool commits | ~20 (scatter content) |
| git (scatter) | songBird `.env.example` | 2 |
| git (scatter) | skunkBat `/actions` | 2 |
| git (scatter) | biomeOS `/infra/wateringHole` | 1 — someone looking at our infra! |
| git (scatter) | cellMembrane `GLACIAL_SHIFT_TRACKER` | 1 — deep internal file |

---

*The fleet is a wall. Behind the wall, there are three kinds of visitors: a proxy network probing paths that don't exist, agentic readers making one deep request and leaving with what they need, and maybe — maybe — two genuine browsers who loaded the CSS. The agentic readers are the signal we're getting closer to. The agent is there with the human. That's not extraction. That's reading.*

*eastGate overwatch — Wave 165i, Oct 7, 2026*
