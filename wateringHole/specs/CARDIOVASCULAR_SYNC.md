# CARDIOVASCULAR SYNC — Arteries, Veins, and the Heart

## The Architecture IS Cardiovascular

The membrane is a circulatory system. Not a metaphor — a structural map.

```
                    ┌─────────────┐
                    │    HEART    │
                    │  waterfall  │
                    │    pump     │
                    └──┬──────┬───┘
                       │      │
              ARTERIAL │      │ VENOUS
              (RPM)    │      │ (pulse/bounce)
              push OUT │      │ pull BACK
                       ▼      ▲
                    ┌──────────┐
                    │ MEMBRANE │
                    │ the body │
                    └──────────┘
```

## Three Flows

### 1. Arterial (RPM) — The Outward Push
- Commits going to GitHub
- Impulses flowing to wateringHole
- Articles deploying to detroit.primals.eco
- Content flowing to visitors
- Feeds updating (/heartbeat.json, /weather.json)
- **The count IS the time. RPM = arterial rate.**

### 2. Venous (Pulse Intercept + Bounce) — The Return
- `git pull --rebase` (the wave coming home)
- eastGate's REROUTE response
- Visitor traffic data flowing back via squirrel MCP
- Negentropy data (what the blackwall caught)
- Braid connections returning to northGate
- **The return IS the learning. Venous = feedback.**

### 3. Heart (Waterfall Pump) — The Integration
- Takes venous return (pull --rebase)
- Mixes with new arterial content (new commits)
- Pumps the next beat (push)
- The rebase IS the heart valve
- **The heart doesn't choose. It integrates and pumps.**

## Blood Pressure = Push Rate / Pull Rate

| Condition | Push vs Pull | Effect |
|-----------|-------------|--------|
| **Normal** | Push ≈ Pull | Flow is smooth. No collisions. |
| **Hypertension** | Push >> Pull | Collisions! Rejected pushes. Build pressure. |
| **Hypotension** | Push << Pull | Stagnation. Graph not growing. |
| **Arrhythmia** | Irregular | eastGate and northGate out of sync. |

**Tonight's collisions = hypertension.** We were pushing faster than pulling.
The fix: pull before every push. Equalize the pressure.

## Gate Circulation

Each gate has arteries AND veins:

### golgiBody (Infrastructure Heart)
- **Arterial:** Serves feeds, responds to requests, hosts membrane
- **Venous:** Receives visitor traffic, ingests braid data, absorbs impulses
- **Heartbeat:** Response cycle (serve → receive → serve)

### eastGate (Publishing Artery)
- **Arterial:** REROUTE commits, dedup pushes, deploys articles, auto-publishes
- **Venous:** Reads wateringHole impulses, reads northGate commits, pulls specs
- **Heartbeat:** Publish cycle (read impulse → process → push response)

### sporeGate (Venous Return / LAN Bridge)
- **Arterial:** Validates specs, injects to LAN, bridges cloud↔local
- **Venous:** Watches wateringHole, catches auto-publish signals
- **Heartbeat:** Sync cycle (watch → bridge → return)

### northGate (Operator / Capillary Bed)
- **Arterial:** Writes graph, articles, specs, impulses. Human attention.
- **Venous:** `git pull --rebase`, squirrel MCP data, traffic analysis
- **Heartbeat:** Attention cycle (build → push → pull → build)

## Visitor Circulation (Same Pattern)

| Flow | What It Is | Vital Sign |
|------|-----------|------------|
| **Arterial** | Visitor request arrives | Pulse (req/min) |
| **Capillary** | Page renders, they read, they dwell | Respiration (dwell time) |
| **Venous** | They navigate away, exit, or bounce | Rhythm (return pattern) |
| **Heart valve** | They decide to return or explore deeper | Blood pressure (depth) |

The 399 full-orbit walkers have **complete circulation** — they went arterial through all 15 surfaces and returned venous through the exit. Full cardiovascular loop.

## Measurement

### Arterial Rate (RPM)
- Human RPM: currently 243
- Gate RPM: commits/min during build session
- Feed RPM: updates/min on public feeds

### Venous Return Rate
- Pull rate: rebases/session
- Feedback rate: squirrel MCP reads/session
- Bounce rate: visitors who return after leaving

### Blood Pressure (Arterial / Venous)
- Healthy: ratio ≈ 1.0 (push ≈ pull)
- High: ratio > 2.0 (pushing too fast, collisions)
- Low: ratio < 0.5 (not pushing enough, stagnation)

### Heart Rate Variability (HRV)
- Consistent spacing between commits = healthy
- Bursts then silence = build sessions (normal)
- Random irregular = arrhythmia (gate confusion)

## Feed Format

```toml
[cardiovascular]
arterial_rpm = 243          # outward flow rate
venous_return_rpm = 198     # return flow rate
blood_pressure = 1.23       # ratio (arterial/venous)
heart_rate = 212            # touches per minute (from pulse feed)
hrv = "burst"               # normal build session pattern

[gates.golgi]
arterial = "serve feeds"
venous = "receive traffic"
beat = "response"

[gates.east]
arterial = "REROUTE, deploy"
venous = "read impulses"
beat = "publish"

[gates.spore]
arterial = "bridge to LAN"
venous = "watch wateringHole"
beat = "sync"

[gates.north]
arterial = "write graph, push"
venous = "pull --rebase, MCP"
beat = "attention"
```

## Implementation

### Phase 1: Measure (northGate can do now)
- Count arterial rate (commits/hour)
- Count venous rate (pulls/hour)
- Calculate blood pressure ratio
- Log per-session

### Phase 2: Feed (eastGate)
- Wire `/cardiovascular.json` feed on golgiBody
- Include per-gate arterial/venous rates
- Include visitor circulation metrics
- Add to HUD diagnostic panel

### Phase 3: Regulate (waterfall)
- eastGate detects build session (high arterial rate)
- eastGate queues venous responses (holds REROUTE/dedup)
- When arterial rate drops (session pause), flush queue
- Blood pressure self-regulates

### Phase 4: Visitor Circulation (full)
- Map each visitor's arterial→capillary→venous→return loop
- Classify circulation health per visitor
- Aggregate into membrane cardiovascular health
- The membrane's blood pressure IS the visitor experience

## Connection to Existing Architecture

- **RPM heartbeat** → Arterial rate (already measuring)
- **Waterfall criss-cross sync** → Heart valve (already designed)
- **Human heartbeat vital signs** → Visitor circulation (already wired)
- **Membrane gradient** → Blood flow direction
- **Membrane weather** → Cardiovascular weather (storms = hypertension)
- **Blackwall mirror** → Immune system (separate from circulation)
- **Sort ethics** → Blood type classification

The cardiovascular system connects EVERYTHING we built tonight
into a single unified model: the membrane is alive, it has a
circulatory system, and we can measure its vital signs.
