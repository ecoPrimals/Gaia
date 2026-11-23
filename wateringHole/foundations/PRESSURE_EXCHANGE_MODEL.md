# Pressure & Exchange — Membrane Osmotic Model

**Purpose**: Replace binary rate limits with biological pressure curves  
**Wave**: 178b+  
**Status**: SPEC — evolving iptables/caddy walls into membrane curves

---

## The Problem: Walls vs Membranes

Current system uses **walls** — binary allow/deny:

```
  iptables:     6 connections in 60s → DROP (step function)
  fail2ban:     3 bad logins → BAN 10min (binary)
  caddy_bridge: antibody match → BLOCK (binary IP inject)
  epitope:      score > threshold → triggered (binary flag)
```

A biological membrane doesn't work this way. It uses **pressure differentials**
and **exchange rates** — continuous curves, not step functions.

---

## The Curves

### Sigmoid (S-curve) — Throttle Pressure

The sigmoid is nature's binary, but it's **continuous**. It transitions
smoothly from fully-open to fully-closed:

```
  σ(x) = 1 / (1 + e^(-k(x - x₀)))

  k  = steepness (how sharp the transition)
  x₀ = midpoint (where 50% throttle occurs)
```

Use for: **connection rate throttling**

```
  Instead of:  6 connections/60s → DROP
  Use:         σ(connections/60s, k=2, x₀=10)

  connections:  1  → σ = 0.00 → 0% delay
  connections:  5  → σ = 0.01 → 10ms delay  
  connections:  8  → σ = 0.12 → 120ms delay
  connections: 10  → σ = 0.50 → 500ms delay (midpoint)
  connections: 12  → σ = 0.88 → 880ms delay
  connections: 15  → σ = 0.99 → 990ms delay (nearly closed)
  connections: 20+ → σ ≈ 1.00 → connection refused
```

The membrane BREATHES. It slows before it stops. The entity FEELS the
pressure increasing and can back off naturally.

### Logarithmic — Diminishing Returns

The log curve represents **diminishing returns on repeated access**:

```
  delay(n) = a · ln(n + 1)

  n = request count in window
  a = scaling factor
```

Use for: **repeated request patterns** (scanning, crawling)

```
  request 1:    0ms delay    (instant — welcome)
  request 10:   23ms delay   (barely noticeable)
  request 100:  46ms delay   (slight resistance)
  request 1000: 69ms delay   (feeling it)
  request 10000: 92ms delay  (significant friction)
```

The more you take, the harder it gets. But it never fully closes.
Human-scale access (10-100 pages) feels instant. Fleet-scale (10K+)
feels like wading through honey.

### Exponential Decay — Cooldown

The decay curve represents **recovery after pressure**:

```
  pressure(t) = P₀ · e^(-t/τ)

  P₀ = peak pressure at time of event
  τ  = time constant (how fast pressure bleeds off)
  t  = time since last high-pressure event
```

Use for: **after blocks/bans** — gradual return to normal, not instant flip

```
  ban triggered:   pressure = 1.0 (full block)
  30s later:       pressure = 0.61 (slowed, not blocked)
  60s later:       pressure = 0.37 (recovering)
  120s later:      pressure = 0.14 (nearly normal)
  300s later:      pressure = 0.01 (fully recovered)
```

No "you're banned for 10 minutes then instantly free." The membrane
heals gradually. The entity is slowly re-admitted.

### Exchange Rate — Osmotic Pressure

The exchange rate is the **osmotic pressure** across the membrane.
High external concentration (many requests) creates pressure. The
membrane regulates flow based on the differential:

```
  Π = iMRT  (van't Hoff equation for osmotic pressure)

  i = selectivity coefficient (self=0.1, partial=0.5, non_self=0.9, null=0.3)
  M = request concentration (requests/second from this entity class)
  R = membrane constant (infrastructure capacity factor)
  T = temperature (current system load / available RAM)
```

This is beautiful: when the system is cool (low load), the membrane is
more permeable. When the system is hot (high load), osmotic pressure
increases and flow is restricted. **The membrane responds to its own state.**

---

## Current → Evolved

| Current (binary) | Evolved (curve) | Function |
|-------------------|-----------------|----------|
| iptables: 6/60s → DROP | Sigmoid throttle: gradual delay 0→1000ms | σ(rate, k=2, x₀=10) |
| fail2ban: 3 fails → BAN 10min | Exponential decay: gradual heal | P₀·e^(-t/τ) |
| caddy_bridge: match → BLOCK IP | Log diminishing: increasing resistance | a·ln(n+1) |
| epitope: score > threshold → flag | Vitality sigmoid: continuous confidence | σ(score, k=3, x₀=threshold) |
| skunky window: fixed 30s | Osmotic window: load-adaptive | Π = iMRT |
| scatter ratio: fixed 0.3 | Exchange sigmoid: load-responsive | σ(load, k=1, x₀=capacity) |

---

## Where Each Curve Lives

### Layer 1: Network (iptables → nftables + curves)

Replace iptables `recent` module binary DROP with nftables `meter` +
graduated delays using `tc` traffic control:

```
  # Instead of DROP at 6 connections:
  # Use tc-netem to add delay proportional to sigmoid(connection_count)
  # The membrane slows before it stops
```

This requires evolving from iptables to nftables (which supports
expressions and can feed into tc). The iptables binary rules become
nftables expressions with curve math.

### Layer 2: HTTP (Caddy → response delay)

Caddy can add response delay via a handler. The caddy_bridge already
writes fleet snippets. Evolve the snippets to include delay headers
that a handler reads:

```
  header X-Membrane-Pressure "0.73"  # sigmoid output
  header X-Membrane-Decay "0.14"     # exponential cooldown
```

PetalTongue reads these headers and applies proportional delay.

### Layer 3: Classification (skunky → continuous scoring)

The entity_profile already has vitality scoring:
```rust
  let v = (1.0 - (score - threshold).abs() / threshold).max(0.0);
```

This is a triangular peak. Evolve to sigmoid:
```rust
  let v = 1.0 / (1.0 + (-k * (score - threshold)).exp());
```

The fleet_confidence calculation becomes:
```rust
  // Old: fleet_raw * (1.0 - eff_vit) — linear
  // New: sigmoid(fleet_raw, k=5, x₀=0.5) * decay(eff_vit) — curved
```

### Layer 4: Scatter (exchange rate)

The scatter_ratio is currently fixed at 0.3 (30% chance a fleet entity
gets scatter content). Evolve to osmotic:

```rust
  let temperature = system_load / max_capacity;  // 0.0 to 1.0
  let concentration = fleet_requests_per_sec / baseline;
  let osmotic = selectivity * concentration * temperature;
  let scatter_ratio = sigmoid(osmotic, k=2, x₀=1.0);
```

When the system is cool and fleet is light → low scatter (save resources).
When the system is hot and fleet is heavy → high scatter (fight back hard).

---

## The Biology

| Concept | Membrane | Math |
|---------|----------|------|
| Osmotic pressure | Request concentration differential | Π = iMRT |
| Semi-permeable | Self passes, non-self resisted | Selectivity coefficient i |
| Active transport | Priority for known-good entities | Negative delay (pre-fetch, cache warm) |
| Facilitated diffusion | Known patterns get channels | Pattern-specific thresholds |
| Endocytosis | Absorbing a commensal into the mesh | Tier promotion (beacon → family → sovereign) |
| Exocytosis | Publishing feeds outward | Signal broadcast (negentropy, stories) |
| Turgor pressure | System load pushes back | Temperature T in Π = iMRT |
| Plasmolysis | Overload → membrane shrinks services | Graceful degradation curve |

---

## Files

- `entity_profile.rs` — vitality scoring (triangular → sigmoid)
- `caddy_bridge.rs` — fleet pressure (binary block → graduated delay)
- `scatter_server.rs` — scatter ratio (fixed → osmotic)
- iptables chains — rate limits (binary DROP → graduated slowdown)
- `/etc/membrane/Caddyfile` — static config + fleet snippets
- `skunky-ingest --window-secs 30` — fixed window → adaptive window
