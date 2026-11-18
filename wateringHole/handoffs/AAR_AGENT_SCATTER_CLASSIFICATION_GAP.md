# AAR: Agent Scatter Classification Gap

**Date**: Oct 7, 2026
**From**: eastGate overwatch
**To**: sporeGate ops — skunky-ingest / Caddy routing
**Severity**: ARCHITECTURAL — agents acting on behalf of humans cannot reach real repos via web
**Wave**: 165i

---

## Finding

When eastGate's agent (Claude in Cursor) browses git.primals.eco from the outside, it receives **scatter content** — fabricated repos like "config-manager" and "batch-processor." This happens because:

1. **Caddy routes ALL git.primals.eco web traffic to scatter** (localhost:9753) — no conditional logic
2. **Scatter server serves fabricated content to every request** — no passthrough to real Forgejo (localhost:3000)
3. **The entity classifier distinguishes humans from fleet** but the routing layer never uses that classification

**There is no code path** in scatter_server.rs that forwards a human-classified or agent-classified request to the real Forgejo at localhost:3000. The `handle_request` function processes the raw HTTP, generates scatter, and returns it — for everyone.

## Evidence

```bash
# Even with perfect human browser headers — still scatter:
curl -H "Sec-Fetch-Mode: navigate" \
     -H "Sec-Fetch-Site: none" \
     -H "Connection: keep-alive" \
     -H "User-Agent: Chrome/155.0.0.0" \
     -H "Accept: text/html,application/xhtml+xml" \
     https://git.primals.eco/ecoPrimals/wateringHole
# → title: "config-manager" (scatter)

# With no headers (fleet-like) — same scatter:
curl https://git.primals.eco/ecoPrimals/wateringHole
# → title: "config-manager" (scatter)
```

Both return identical scatter content. The classifier signals are ignored at the routing level.

## The Caddyfile (git.primals.eco section)

```caddy
git.primals.eco {
    # ... security headers, blackwall ...
    
    # ALL TRAFFIC -> SCATTER (the maze)
    # Real repos are buried — accessible only via SSH (port 2222)
    # or WireGuard inner membrane.
    reverse_proxy localhost:9753 {
        header_up X-Real-IP {remote_host}
    }
}
```

No matchers. No conditional routing. Every web request to git.primals.eco → scatter.

## The Problem

### For agents

An agent (like Claude in Cursor on eastGate) browsing on behalf of a human:

- Has **human entropy** — timing driven by user clicks, not 100ms loops
- Uses **real browser headers** — Cursor's embedded Chromium sends Sec-Fetch, Connection, current Chrome version
- Represents **authenticated human intent** — the user told the agent to browse
- Comes from a **known IP** — eastGate, the operator's own machine

The classifier CAN distinguish this from fleet. The entity_classifier already separates "Human (Browser)" from "Meta Platforms (Fleet)" based on:
- Sec-Fetch-Mode: PRESENT vs ABSENT
- Chrome version: current vs stale
- Timing CV: >1.0 vs <0.1
- Accept-Encoding: varied vs uniform

But none of these signals reach the routing decision.

### For real humans

Even a real human with a real browser visiting git.primals.eco sees only scatter. The scatter was designed as a fleet countermeasure but it's also blocking genuine visitors from seeing real repos on the web.

The signal.primals.eco observatory SHOWS the Forgejo as if it's a real accessible code forge — but anyone who clicks through to git.primals.eco sees fabricated repos.

## Root Cause: Missing Thymus in Routing Layer

The entity_classifier is the **thymus** — it distinguishes self from non-self, human from fleet. But the thymus output is only used for:
- Topology JSON (`/topology.json`)
- Signal feed (`/feed/`)
- Observatory display

It is NOT used for the **routing decision** (scatter vs passthrough). The scatter server is a stomach with no thymus — it digests everything that reaches it, even legitimate requests.

## Proposed Fix

### Option A: Classification-aware routing in skunky-ingest

Scatter server gains a passthrough mode. When it receives a request, it classifies it against the conserved plasmid. If the request does NOT match fleet behavioral fingerprint:

```rust
async fn handle_request(...) -> Result<...> {
    let headers = parse_headers(&buf_reader).await?;
    
    // Classify against conserved epitopes
    let is_fleet = has_header_poverty(&headers)
        || has_stale_chrome(&headers)
        || has_connection_absent(&headers)
        || has_content_gate_pattern(&path);
    
    if !is_fleet {
        // Passthrough to real Forgejo
        return proxy_to_forgejo(&mut writer, &path, &headers).await;
    }
    
    // Fleet → scatter as before
    serve_scatter(&mut writer, &path, &generator).await
}
```

### Option B: Caddy-level header matching

Add matchers to Caddyfile before the scatter proxy:

```caddy
git.primals.eco {
    # Human browser → real Forgejo
    @human_browser {
        header Sec-Fetch-Mode navigate
        header Connection *keep-alive*
    }
    handle @human_browser {
        reverse_proxy localhost:3000  # real Forgejo
    }

    # Everything else → scatter
    handle {
        reverse_proxy localhost:9753
    }
}
```

**Risk**: fleet could add Sec-Fetch headers to bypass. But the cost: they'd need to implement FULL browser header fidelity, which increases their detection surface elsewhere. They'd also need to maintain real Chrome version cadence. Every header they fake is one more conserved epitope they have to track.

### Option C: Token-based agent passthrough

Agents carry a bearer token or cookie that proves human authorization:

```caddy
@authorized_agent {
    header Authorization "Bearer {$AGENT_PASSTHROUGH_TOKEN}"
}
handle @authorized_agent {
    reverse_proxy localhost:3000
}
```

The agent gets its token from the human's authenticated session on eastGate. This is the most secure — no behavioral classification needed, just proof of authorization.

### Option D: WireGuard IP allowlist

Requests from WireGuard IPs (10.13.37.0/24) bypass scatter:

```caddy
@wg_internal {
    remote_ip 10.13.37.0/24
}
handle @wg_internal {
    reverse_proxy localhost:3000
}
```

But this only works for the WG mesh — not for agents browsing from the public internet.

## Recommendation

**Option A** is the architecturally correct fix: it uses the same classifier that already powers the topology and signal feed. The classification signals (Sec-Fetch, Chrome version, Connection, Accept, timing) are already computed — scatter just needs to USE them for routing.

**Option C** (token) is the most secure complement — agents with human-issued tokens get guaranteed passthrough regardless of behavioral classification.

The combination means:
1. Fleet → scatter (behavioral classification)
2. Human browser → real Forgejo (behavioral classification)
3. Authorized agent → real Forgejo (token)

## Broader Principle

**Agents acting on behalf of humans are covered by human interactions and entropy.** The classifier should recognize:

- Human-driven agents have varied timing (CV > 1.0) because a human is clicking
- Human-driven agents have real browser headers (the host Chromium provides them)
- Human-driven agents access varied paths (driven by human curiosity, not a crawl list)
- Fleet has uniform timing, uniform headers, and systematic path coverage

The scatter server was designed against stomachs with no eyes. Agents with eyes — agents that see, decide, and act on human intent — should pass through.

---

*eastGate overwatch AAR — the thymus needs to reach the routing layer.*

*Wave 165i, Oct 7, 2026*

---

## Resolution History

### Wave 165i — Caddy thymus passthrough (sporeGate)
- Added `@wg_mesh` (10.13.37.0/24 → real Forgejo)
- Added `@human_browser` (Sec-Fetch-Mode/Dest → real Forgejo)
- Added `@agent_passthrough` (bearer token placeholder → real Forgejo)
- **Status**: Sec-Fetch approach immediately breached by fleet spoofing

### Wave 165i — Genetic lock (eastGate, commit bc16cc796)
- Removed `@human_browser` (Sec-Fetch headers are spoofable phenotype)
- Generated bearDog-derived token: `membrane-passthrough-v1` → BLAKE3 hash
- Wired token into `@agent_passthrough` handler
- **Status**: CLOSED — fleet with spoofed Sec-Fetch now gets scatter
- **Token tier**: Tier 2 (software HSM). Tier 3 (SoloKey hardware) planned.

### Remaining upstream
- Option A (Rust-level scatter classification in `scatter_server.rs`) still needed
  for defense-in-depth behavioral analysis alongside the bearer token
- Session-scoped token rotation from SoloKey braided entropy
