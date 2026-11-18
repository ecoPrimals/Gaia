# Cursor IDE Hooks — K-NOME Context Integration

Reference copies of the Cursor hook and rule files that implement the K-NOME workflow:
context braids auto-injected into IDE sessions on start.

## Installation

Copy these files to your workspace `.cursor/` directory:

```bash
# From workspace root (e.g. ~/Development/ecoPrimals)
mkdir -p .cursor/hooks .cursor/rules
cp infra/wateringHole/hooks/cursor/hooks.json .cursor/hooks.json
cp gardens/cellMembrane/deploy/hooks/cursor/context-sense.sh .cursor/hooks/context-sense.sh
cp infra/wateringHole/hooks/cursor/context-braid-workflow.rule.md .cursor/rules/context-braid-workflow.md
chmod +x .cursor/hooks/context-sense.sh
```

> **Note**: `context-sense.sh` lives in `cellMembrane` (its code owner). wateringHole
> provides the hook config and rule (comms layer); cellMembrane provides the script.

## What it does

On `sessionStart`, the hook:

1. Runs `membrane context.sense --all` — loads all context braids across the gate mesh
2. Runs `membrane potential.sense` — checks for pending impulses requiring action
3. Injects the combined output as `additional_context` for the agent

The rule file provides fallback instructions for agents when the hook mechanism
is not available (e.g. on gates without Cursor hook support).

## Requirements

- `membrane` binary in PATH or built at `gardens/cellMembrane/target/release/membrane`
- `python3` available for JSON escaping
- `.gate` file at workspace root (or `GATE_NAME` env var) for identity resolution

## K-NOME Pattern

The blurb IS the program. `context.weave` encodes the human directive.
`context.sense` delivers it to the agent. The membrane is the transport.
The hook automates delivery so the human says "proceed" and the agent
already has the program loaded.
