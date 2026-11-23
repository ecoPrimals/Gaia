# petalTongue: Explicit Needs from the Ecosystem

**Version**: v1.6.6 (May 1, 2026)

petalTongue is the **Universal User Interface** primal. It translates computational
universes into any user modality — not just visualization, but the complete sensory bridge. This document states what petalTongue **needs** from
other primals to deliver complete rendering.

---

## 3D Rendering Pipeline

petalTongue does NOT render 3D directly. The pipeline is:

```
petalTongue (grammar/scene) → barraCuda (GPU compute) → coralReef (shader compile) → ToadStool (display)
```

### From ToadStool (display backend)

**Status**: Partially wired (window lifecycle works, frame submission not yet).

| Need | Method | Status |
|------|--------|--------|
| Create display window | `display.create_window` | Wired |
| Query display capabilities | `display.get_capabilities` | Wired |
| Submit rendered frame | `display.present` | NOT YET WIRED in ToadStool dispatch |
| Get framebuffer for zero-copy | `display.get_framebuffer` | Spec only |
| Frame transport routing | `transport.discover` / `transport.route` | Wired in ToadStool |

**Socket**: `$XDG_RUNTIME_DIR/toadstool/display.sock`

**What we need ToadStool to implement**: Wire `display.present` in the dispatch
handler so petalTongue can push pixel buffers for display. The TSXP frame
protocol exists but is not connected to `display.present`.

### From barraCuda (GPU compute)

**Status**: Physics bridge wired, but limited ops available.

| Need | Method | Status |
|------|--------|--------|
| Dispatch compute | `barracuda.compute.dispatch` | Wired (3 ops: zeros, ones, read) |
| N-body physics | `math.physics.nbody` | NOT in barraCuda dispatch table |
| Statistics | `math.stat.*` | NOT YET |
| Tessellation | `math.tessellate.*` | NOT YET |
| Projection | `math.project.*` | NOT YET |
| Precision routing | `barracuda.tolerances.get` | Available |

**Socket**: `$XDG_RUNTIME_DIR/barracuda/barracuda.sock`

**What we need barraCuda to implement**: Add `math.stat.histogram`,
`math.stat.kde`, `math.tessellate.delaunay`, `math.project.mercator` dispatch
ops. petalTongue currently computes these on CPU.

### From coralReef (shader compilation)

**Status**: Not directly called by petalTongue (goes through barraCuda).

| Need | Method | Status |
|------|--------|--------|
| Compile WGSL | `shader.compile.wgsl` | Available in coralReef |
| Check capabilities | `shader.compile.capabilities` | Available |

**Socket**: `$XDG_RUNTIME_DIR/ecoPrimals/coralreef.sock`

petalTongue does not call coralReef directly. If we ever need custom GPU
visualization shaders, we would submit WGSL through barraCuda.

---

## Sound Output

petalTongue synthesizes audio (5 waveforms, stereo panning, fade envelopes)
in `petal-tongue-scene/src/soundscape.rs`. However, **there is no ecosystem
audio output path**.

### petalTongue Side (Wired)

As of April 17, petalTongue has a **Tier 1 `NetworkBackend`** in `AudioManager`
that discovers `audio` capability providers via `CapabilityDiscovery<BiomeOsBackend>`
and delegates playback via `audio.play` over JSON-RPC/UDS. It falls back
gracefully to software synthesis / silent when no provider is found.

### Ecosystem Gap

| Component | Audio Status |
|-----------|-------------|
| ToadStool | No `audio.*` methods yet — `transport.*` is for display/capture/serial only |
| barraCuda | Has audio WGSL shaders (mel_scale, conv1d) but no audio I/O |
| coralReef | Shader compiler only, no audio |

### What We Need From Ecosystem

**Preferred**: ToadStool (or another primal) exposes `audio.play` and
`audio.stream` JSON-RPC methods over UDS. petalTongue's `NetworkBackend`
is already wired to discover and call them via capability discovery.

---

## Discovery & Registration

### From Songbird

| Need | Method | Status |
|------|--------|--------|
| Register at startup | `discovery.register` | Wired |
| Heartbeat | `discovery.heartbeat` | Wired |
| Discover by capability | `discovery.query` | Available |

**Socket**: Via `SONGBIRD_SOCKET` env or capability discovery.

### From NestGate (artifact storage)

| Need | Method | Status |
|------|--------|--------|
| Store dashboard SVG | `storage.put` | NOT YET called by petalTongue |
| Retrieve stored artifacts | `storage.get` | NOT YET |

**Socket**: Via capability discovery (`storage` capability).

petalTongue currently exports SVG/PNG to local filesystem. Evolving to
NestGate storage would enable ecosystem-wide artifact sharing.

---

## Provenance & Attribution

### From rhizoCrypt (ephemeral state)

| Need | Method | Status |
|------|--------|--------|
| Session-scoped viz state | `dag.create_session` | NOT YET |
| Commit viz to permanent | `dag.dehydration.trigger` | NOT YET |

### From sweetGrass (attribution)

| Need | Method | Status |
|------|--------|--------|
| Record viz attribution | `provenance.create_braid` | NOT YET |
| Track data lineage | `provenance.attribution_chain` | NOT YET |

---

## Summary: What Other Primals Should Know

1. **petalTongue renders anything, for anyone**: Send grammar expressions or DataBinding
   payloads (11 variants) and we compile to the best available modality. The UUI
   glossary (`petal_tongue_core::uui_glossary`) defines canonical terminology for
   modalities (visual, audio, haptic, terminal, braille, JSON API, acoustic, chemical),
   user types (human-sighted, human-blind, AI-agent, non-human), and the SAME DAVE
   (Sensory Afferent, Motor Efferent) feedback model.

2. **We need `display.present`**: ToadStool window lifecycle works, but we
   cannot push frames yet. petalTongue V2 display backend now discovers via
   capability discovery and sends frames over JSON-RPC/UDS — just needs
   ToadStool to wire the `display.present` dispatch handler.

3. **We need audio output**: petalTongue Tier 1 `NetworkBackend` is wired
   and will auto-discover any primal that registers `audio` capability.
   ToadStool `audio.play` / `audio.stream` methods would complete the path.

4. **We need more GPU ops**: barraCuda has 3 ops; we need statistics,
   tessellation, and projection for offloading visualization computation.
   petalTongue now discovers compute providers via `CapabilityDiscovery`
   (biomeOS Neural API) rather than ad-hoc env/filesystem scanning.

5. **ludoSpring**: We support `GameScene` and `Soundscape` DataBindings.
   Send `channel_type: "game_scene"` or `channel_type: "soundscape"` via
   `visualization.render` and we handle it.

---

**Last Updated**: May 1, 2026
**Maintainer**: ecoPrimals / petalTongue
**License**: AGPL-3.0-or-later
