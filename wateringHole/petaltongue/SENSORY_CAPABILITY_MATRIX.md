# Sensory Capability Matrix — petalTongue UUI Contract

**Version**: 1.0.0  
**Date**: April 2, 2026  
**Audience**: All ecosystem primals that interact with petalTongue for UI  
**Status**: Active Standard

---

## Purpose

This document defines the formal **sensory/capability matrix** that maps every
input modality to every output modality through petalTongue's Universal User
Interface. Consumer primals (ludoSpring, primalSpring, Squirrel, esotericWebb)
use this matrix to understand what interaction paths are available for a given
user or agent session.

## IPC Methods

### `capabilities.sensory`

Returns the full `SensoryCapabilityMatrix` for the current runtime environment.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "capabilities.sensory",
  "params": {
    "agent": false
  },
  "id": 1
}
```

Set `"agent": true` to get a matrix for an agentic AI session (API-only I/O).

**Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "input": {
      "pointer": true,
      "keyboard": true,
      "voice": false,
      "gesture": false,
      "touch": false,
      "gaze": false,
      "switch_input": false,
      "api_agent": false
    },
    "output": {
      "visual_gui": true,
      "terminal": true,
      "audio": true,
      "braille": false,
      "haptic": false,
      "description": true,
      "svg": true,
      "gpu": true,
      "api_machine": true
    },
    "validated_paths": [
      {
        "input": "PointerMouse",
        "output": "Gui",
        "adapter": "PointerAdapter",
        "inverse_pipeline": "VisualInversePipeline",
        "confidence": 1.0
      }
    ],
    "recommended_modality": "Gui",
    "interaction_patterns": ["PointAndClick", "KeyboardNavigation"]
  },
  "id": 1
}
```

### `capabilities.sensory.negotiate`

Accepts explicit input/output capability overrides (e.g. from NestGate user
preferences) and returns a tailored matrix.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "capabilities.sensory.negotiate",
  "params": {
    "input": {
      "keyboard": true,
      "switch_input": true
    },
    "output": {
      "audio": true,
      "braille": true,
      "description": true
    }
  },
  "id": 2
}
```

## The Matrix

Each cell answers: "Can a user with **this input** interact with content
rendered via **this output**?"

Status markers:
- **DONE** — Tested path exists with adapter + inverse pipeline
- **PARTIAL** — Types exist, adapter works, inverse pipeline pending
- **GAP** — Not yet implemented (SensorEvent variant exists for Toadstool)
- **N/A** — Combination is not meaningful

```
                  | Pointer | Keyboard | Voice | Gesture | Touch | Gaze | Switch | Agent
------------------+---------+----------+-------+---------+-------+------+--------+------
Visual/GUI        | DONE    | DONE     | GAP   | GAP     | GAP   | GAP  | PARTIAL| DONE
Terminal/TUI      | N/A     | PARTIAL  | GAP   | N/A     | N/A   | N/A  | GAP    | PARTIAL
Audio/Sonification| N/A     | DONE     | GAP   | N/A     | N/A   | N/A  | PARTIAL| PARTIAL
Braille/Tactile   | N/A     | PARTIAL  | GAP   | N/A     | GAP   | N/A  | GAP    | PARTIAL
Haptic/Force      | N/A     | PARTIAL  | N/A   | N/A     | GAP   | N/A  | GAP    | PARTIAL
Description/Narr  | N/A     | DONE     | GAP   | N/A     | N/A   | N/A  | PARTIAL| DONE
SVG/Print         | N/A     | N/A      | N/A   | N/A     | N/A   | N/A  | N/A    | DONE
GPU/3D            | PARTIAL | PARTIAL  | GAP   | GAP     | GAP   | GAP  | N/A    | GAP
API/Machine       | N/A     | N/A      | N/A   | N/A     | N/A   | N/A  | N/A    | DONE
```

## Input Modalities

| Modality | `InputModality` Enum | `SensorEvent` Variants | Adapter |
|----------|---------------------|----------------------|---------|
| Pointer  | `PointerMouse` | `Position`, `Click`, `Scroll` | `PointerAdapter` |
| Keyboard | `Keyboard` | `KeyPress`, `KeyRelease` | `KeyboardAdapter` |
| Voice    | `VoiceCommand` | `VoiceCommand` | (pending) |
| Gesture  | `MotionCapture` | `Gesture` | (pending — Toadstool provides hardware) |
| Touch    | `PointerTouch` | `Touch` | (pending — Toadstool provides hardware) |
| Gaze     | `EyeGaze` | `GazePosition` | (pending — Toadstool provides hardware) |
| Switch   | `SwitchAccess` | `SwitchActivation`, `ButtonPress` | `SwitchInputAdapter` |
| Agent    | `Agent` | `AgentCommand`, `Generic` | `AgentInputAdapter` |

## Output Modalities

| Modality | `OutputModality` Enum | `ModalityCompiler` | Capability String |
|----------|----------------------|-------------------|-------------------|
| Visual/GUI | `Gui` | `GpuCompiler` | `modality.visual` |
| Terminal/TUI | `Tui` | `TerminalCompiler` | `modality.terminal` |
| Audio | `Audio` | `AudioCompiler` | `modality.audio` |
| Braille | `Braille` | `BrailleCompiler` | `modality.braille` |
| Haptic | `Haptic` | `HapticCompiler` | `modality.haptic` |
| Description | `Headless` | `DescriptionCompiler` | `modality.description` |
| SVG | `Svg` | `SvgCompiler` | (export-only) |
| GPU/3D | `Gui` | `GpuCompiler` | (via Toadstool) |
| API/Machine | `Json` | (JSON serialization) | `capabilities.list` |

## Inverse Pipelines

Inverse pipelines resolve interactions from output space back to data space,
enabling the "6 vs 9" principle: two users in different modalities selecting
the same data.

| Pipeline | Output Modality | Status |
|----------|----------------|--------|
| `VisualInversePipeline` | Gui | DONE |
| `AudioInversePipeline` | Audio | DONE |
| `NoOpInversePipeline` | Svg, Png, Headless | DONE (export-only) |
| TUI inverse | Tui | GAP |
| Braille inverse | Braille | GAP |
| Haptic inverse | Haptic | GAP |

## InteractionPatterns

The matrix recommends interaction patterns for the detected capabilities:

| Pattern | Input Required | Description |
|---------|---------------|-------------|
| `PointAndClick` | Pointer | Standard mouse desktop interaction |
| `KeyboardNavigation` | Keyboard | Tab/arrow/Enter focus-ring navigation |
| `VoiceAndAudio` | Voice + Audio output | Speak commands, hear sonified feedback |
| `SwitchScanning` | Switch | Auto-advance or two-switch scan + select |
| `GazeDwell` | Gaze | Eye tracking with dwell-to-select |
| `TouchGesture` | Touch | Pinch, swipe, tap gestures |
| `AgentApi` | Agent | Programmatic JSON-RPC navigation |
| `BrailleRouting` | Keyboard + Braille output | Routing keys on Braille display |
| `HapticExploration` | Touch/Gesture + Haptic output | Force feedback exploration |

## Integration Guide for Consumer Primals

### ludoSpring (Gaming)

1. Call `capabilities.sensory` at session start
2. Check `validated_paths` for your required modalities
3. Use `recommended_modality` to set default rendering
4. If the user is blind: check `output.audio` and `output.description`
5. If motor-impaired: check `input.switch_input`
6. Adapt game controls to available `interaction_patterns`

### Squirrel (Agentic AI)

1. Call `capabilities.sensory` with `"agent": true`
2. Use `API/Machine` output modality for structured data
3. Send commands via `SensorEvent::AgentCommand` or `SensorEvent::Generic`
4. Subscribe to `interaction.subscribe` for state change notifications

### primalSpring (Orchestration)

1. Call `capabilities.sensory` for each user session
2. Store capability snapshots for composition validation
3. Use `validated_paths` to verify that the deployed composition
   supports the user's capabilities

### Toadstool (Hardware)

See `TOADSTOOL_SENSOR_CONTRACT.md` for the `SensorEvent` variants
Toadstool should emit for each hardware sensor type.

## What petalTongue Does NOT Own

- **Hardware drivers** — Toadstool's domain
- **Speech recognition / NLP** — Squirrel's domain (or OS accessibility)
- **User preference persistence** — NestGate's domain
- **Authentication / identity** — BearDog's domain
- **Game logic** — ludoSpring's domain

petalTongue owns the **translation layer**: sensor events come in, modality
outputs go out, and the matrix validates that every combination works.
