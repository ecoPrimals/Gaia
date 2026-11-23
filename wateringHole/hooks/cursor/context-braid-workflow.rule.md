# Context Braid Workflow — K-NOME Interaction Surface

This workspace uses the ecoPrimals **context braid** system for structured developer state across gates. Before starting substantive work, sense the mesh state.

## On Session Start

Run `membrane context.sense --all` to load the current mesh state. This replaces manual guidance blurbs. The output contains structured TOML braids with:

- **focus** — what is actively being worked on at each gate
- **breadcrumbs** — file paths, entry points, relevant code locations
- **next** — upcoming actions and handoff tasks
- **blockers** — what's preventing progress
- **notes** — standing directives (architecture constraints, style guides)

Also run `membrane potential.sense` to check for pending impulses (inter-gate coordination messages that may require action).

## On Work Completion

When completing a significant milestone or handing off work, weave a context braid:

```bash
membrane context.weave \
  --project <path> \
  --summary "<what was done / current state>" \
  --status <active|paused|blocked|complete> \
  --breadcrumbs "<relevant files>" \
  --next "<what should happen next>"
```

## Standing Conventions

- AGPL-3.0 licensing on all primal code
- 1000 line maximum per file
- Zero-copy where possible
- Primal code has self-knowledge only — discover capabilities at runtime, no hardcoding
- No 2^n enumeration of peers — use capability registries
- Commit messages follow: `feat:`, `fix:`, `docs:`, `refactor:` prefixes
- Push to `forgejo` only — VPS auto-mirrors to GitHub (external ledger)

## Gate Identity

This workspace resolves gate identity from `$GATE_NAME` or the `.gate` file at workspace root. The current gate identity determines which context braids are "local" vs "mesh".

## Three-Layer Coordination

| Layer | Command | Purpose |
|-------|---------|---------|
| Context braids | `context.weave/sense/clear` | Ephemeral developer state (sweetGrass external) |
| Impulses | `impulse.post`, `potential.sense` | Event-driven coordination (rhizoCrypt external) |
| Git | Standard git workflow | Permanent record (loamSpine external) |
