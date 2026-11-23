# sporeGate: Depot Rebuild + NUCLEUS Redeploy + Automated Pipeline — Wave 155k

**Date**: Jul 30, 2026 | **From**: eastGate overwatch | **Wave**: 155k
**Priority**: P1 (depot freshness) + P2 (pipeline automation)

---

## CONTEXT

All code-team P1s are SHIPPED. Three Windows binaries are stale in the depot
because they were blocked by platform-gating bugs at last rebuild (155i-nucleus).
Those bugs are now fixed. biomeOS shipped v4.47 NUCLEUS orchestrator. bearDog
shipped crypto.sign_ed25519. The depot and NUCLEUS deployment need to catch up.

## PHASE 1: CASCADE + REBUILD 3 STALE `.exe` (P1)

### Step 1a: Pull the fixes

These 3 primals have new commits since your last build:

| Primal | Fix Commit | What Changed |
|--------|------------|--------------|
| bearDog | `d6b1003bb` | `#[cfg(unix)]` gate on `UnixStream` — beardog.exe now cross-compiles |
| toadStool | `2df71399b` | S347 — `toadstool-runtime-gpu` moved to cross-platform optional dep |
| coralReef | `edcd696` | `unix_jsonrpc` imports platform-gated + `--bind` alias |

Also pull these for NUCLEUS freshness:

| Primal | Commit | What Changed |
|--------|--------|--------------|
| biomeOS | `bd202674` | v4.47 NUCLEUS orchestrator — riboCipher fix, socket unification, composition lifecycle |
| biomeOS | `076d4743` | cellMembrane boot_order integration |
| bearDog | `3739e7078` | crypto.sign_ed25519 real signing (Provenance 7/7 unblock) |
| cellMembrane | `2b82722` | dns.configure/dns.apply generators |

```bash
cd ~/Development/ecoPrimals
for d in primals/bearDog primals/toadStool primals/coralReef primals/biomeOS \
         gardens/cellMembrane; do
  echo "=== $(basename $d) ==="
  (cd "$d" && git pull --rebase origin main)
done
```

### Step 1b: Rebuild the 3 blocked Windows binaries

```bash
membrane plasmid.harvest \
  --primal bearDog --primal toadStool --primal coralReef \
  --target x86_64-pc-windows-gnu \
  --push
```

Or if `--primal` flag isn't supported for selective rebuild:

```bash
for primal in bearDog toadStool coralReef; do
  echo "=== Building $primal for Windows ==="
  (cd primals/$primal && cargo build --release --target x86_64-pc-windows-gnu)
done
membrane plasmid.push
```

### Step 1c: Rebuild biomeOS + bearDog for ALL targets

These shipped major new functionality. All depot targets need fresh binaries:

```bash
membrane plasmid.harvest \
  --primal biomeOS --primal bearDog \
  --target x86_64-unknown-linux-musl \
  --target x86_64-unknown-linux-gnu \
  --target x86_64-pc-windows-gnu \
  --push
```

### Step 1d: Verify depot

```bash
membrane plasmid.verify --checksums
curl -sf https://depot.primals.eco/primals/x86_64-pc-windows-gnu/beardog.exe -o /dev/null && echo "beardog.exe OK"
curl -sf https://depot.primals.eco/primals/x86_64-pc-windows-gnu/toadstool.exe -o /dev/null && echo "toadstool.exe OK"
curl -sf https://depot.primals.eco/primals/x86_64-pc-windows-gnu/coralreef.exe -o /dev/null && echo "coralreef.exe OK"
```

**Expected**: All 3 return HTTP 200. BLAKE3 checksums match.

---

## PHASE 2: REDEPLOY NUCLEUS WITH biomeOS v4.47

sporeGate already achieved NUCLEUS (9/11 healthy probes). Now redeploy with
the v4.47 orchestrator which adds:

- `composition.start` RPC — health-gated prerequisite checking
- Capability persistence — registry survives restart (evaporation fix)
- Socket unification — all paths under `membrane/`
- Graph executor riboCipher fix — can reach primals with enforcement on
- cellMembrane boot_order integration — startup ordering from manifest

### Step 2a: Stop existing biomeOS

```bash
sudo systemctl stop biomeos-membrane
```

### Step 2b: Deploy new binary

```bash
curl -fsSL "https://depot.primals.eco/primals/x86_64-unknown-linux-musl/biomeos" \
  -o ~/.local/bin/biomeos
chmod +x ~/.local/bin/biomeos
```

Or from local build if depot not yet refreshed:

```bash
cd primals/biomeOS && cargo build --release
cp target/release/biomeos ~/.local/bin/biomeos
```

### Step 2c: Start with composition lifecycle

```bash
sudo systemctl start biomeos-membrane
# Verify composition lifecycle
biomeos composition.start --composition nucleus
```

### Step 2d: Validate NUCLEUS

```bash
biomeos tower.health
# Expected: { "status": "healthy" }

biomeos neural.capabilities
# Expected: 1,742+ capabilities, all ACTIVE

biomeos composition.status
# Expected: all 13 primals managed, startup order enforced
```

---

## PHASE 3: AUTOMATED PUBLISH PIPELINE (P2 — kill jelly strings)

**Goal**: Every `git push` to a primal on Forgejo triggers: cascade → build →
checksum → push to golgiBody depot. No human runs `plasmid.harvest` manually.

### Current state (what we have)

| Component | Status |
|-----------|--------|
| `plasmid.harvest --push` | SHIPPED (J1+J2) — builds + pushes in one command |
| `temporal.cascade` | SHIPPED — pulls all repos from Forgejo |
| Per-primal `depot_sync` | SHIPPED — Rust-native SSH per-primal push |
| BLAKE3 checksums | SHIPPED — auto-generated on harvest |
| `gate.configure` + `gate.apply` | SHIPPED (J6) — manifest-driven service config |
| Forgejo webhooks | EXISTS — Forgejo can POST on push events |

### What's missing (jelly strings to kill)

| Jelly String | What Happens Now | What Should Happen |
|--------------|------------------|-------------------|
| **J9: Cascade trigger** | Human runs `temporal.cascade` | Forgejo webhook POST → sporeGate `temporal.cascade --source forgejo` |
| **J10: Build trigger** | Human runs `plasmid.harvest` | Post-cascade diff detection → auto `plasmid.harvest --primal <changed> --push` |
| **J11: Multi-target build** | Human specifies `--target` per arch | Manifest-driven: read gate compositions, build all required targets |
| **J12: blueGate sub-builder** | Not wired | sporeGate dispatches Windows builds to blueGate via IPC when blueGate is on mesh |
| **J13: Depot freshness probe** | sporeGate checks manually | Continuous: compare `heads/*.toml` SHAs against depot binary provenance → alert on drift |

### Architecture: Automated depot pipeline

```
Forgejo push webhook
  │
  ▼
sporeGate: temporal.cascade (pulls changed repos)
  │
  ▼
sporeGate: diff detection (compare HEAD SHAs vs depot provenance.toml)
  │
  ├─ Changed primal detected
  │   │
  │   ▼
  │   plasmid.harvest --primal <name> --target <all-needed> --push
  │   │
  │   ├─ Linux targets: build locally on sporeGate
  │   │
  │   └─ Windows targets: dispatch to blueGate (sub-builder via songBird IPC)
  │       │
  │       ▼
  │       blueGate: plasmid.harvest --primal <name> --target x86_64-pc-windows-gnu
  │       blueGate: plasmid.push (back to golgiBody)
  │
  ▼
sporeGate: plasmid.verify --checksums (post-build integrity check)
  │
  ▼
sporeGate: update heads/sporeGate.toml + push to wateringHole
  │
  ▼
Done — depot fresh, no human involved
```

### Implementation path

1. **J9 first** (easiest win): Forgejo already supports webhooks. cellMembrane
   needs a `webhook.receive` handler that triggers `temporal.cascade`. This is
   a small addition to `webhook/pipeline.rs` (the module already exists).

2. **J10 second**: After cascade, compare `git log --oneline HEAD..origin/main`
   per primal. If any primal advanced, trigger harvest for that primal. The
   diff detection is trivial — compare `heads/sporeGate.toml` SHAs against
   current HEAD.

3. **J13 third**: Continuous freshness probe. Read `provenance.toml` in depot,
   compare against `heads/*.toml`. Alert (via songBird mesh broadcast) when
   drift > threshold.

4. **J11+J12 last**: Multi-target and sub-builder dispatch. These require
   blueGate to be on the mesh with build authority active and songBird IPC
   working for cross-gate dispatch. Do after blueGate NUCLEUS is stable.

### Handoff to cellMembrane team

cellMembrane owns J9 and J10. The `webhook/pipeline.rs` module already has
the webhook receiver structure. What's needed:

```rust
// In webhook/pipeline.rs — pseudocode
async fn handle_forgejo_push(payload: ForgejoPushEvent) -> Result<()> {
    let primal = payload.repository.name;
    temporal_cascade_single(&primal).await?;
    let head_before = read_head_sha(&primal)?;
    let head_after = current_head_sha(&primal)?;
    if head_before != head_after {
        plasmid_harvest(&primal, &all_needed_targets()).await?;
    }
    Ok(())
}
```

---

## PHASE 4: blueGate AS SUB-BUILDER

blueGate is enrolled (WG 10.13.37.12, Forgejo SSH key registered) and has
`build_authority = true` in its manifest. Once Tower Atomic is stable on
blueGate and songBird IPC is reachable:

1. sporeGate sends `build.dispatch` IPC to blueGate via songBird
2. blueGate runs `plasmid.harvest --primal <name> --target x86_64-pc-windows-gnu`
3. blueGate runs `plasmid.push` to send `.exe` to golgiBody
4. sporeGate verifies via `plasmid.verify --remote`

This means Windows binaries are built *on Windows* natively rather than
cross-compiled from Linux. Native builds avoid mingw edge cases and produce
binaries that exactly match the deployment target.

**Prerequisite**: blueGate pulls fresh depot binaries (Phase 1 must complete
first so blueGate gets working `.exe` files to bootstrap).

---

## SUCCESS CRITERIA

| Phase | Done When |
|-------|-----------|
| 1 | beardog.exe + toadstool.exe + coralreef.exe serve HTTP 200 from depot. biomeOS v4.47 in depot. BLAKE3 verified. |
| 2 | sporeGate NUCLEUS running with biomeOS v4.47. `composition.start` manages startup order. Capability persistence survives restart. |
| 3 | Forgejo push to any primal triggers auto-build + depot push within 10 minutes. No human `plasmid.harvest`. |
| 4 | blueGate builds Windows binaries natively and pushes to depot on dispatch from sporeGate. |

---

## AAR

File your AAR as: `infra/wateringHole/aars/SPOREGATE_DEPOT_NUCLEUS_PIPELINE_155k_AAR.md`

Update `heads/sporeGate.toml` with new SHAs after rebuild.

---

*Wave 155k — 3 Windows .exe ready for rebuild (all code-team fixes shipped).
biomeOS v4.47 NUCLEUS orchestrator ready for deployment. Pipeline automation
(J9–J13) identified as next jelly strings to kill. blueGate sub-builder
pattern defined. Every ad-hoc step is a jelly string.*
