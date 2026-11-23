# Forgejo VPS Hooks — K-Derm Diderm Relay Chain

Server-side hooks for the three-node K-Derm diderm envelope. The push flow
traverses each layer with proper bond-type degradation:

```
Gate ──covalent──→ golgiBody-inner (cis: receives)
                       │
                       │ metallic bond (post-receive webhook)
                       ▼
                   peptidoglycan (structural: sync + impulse cascade)
                       │
                       │ ionic bond (SSH relay)
                       ▼
                   golgiBody-ext (trans: ships to extracellular)
                       │
                       │ weak bond (git push)
                       ▼
                   GitHub (extracellular linear ledger)
```

## Scripts

> **Wave 66**: Scripts relocated to their code owners (`cellMembrane/deploy/hooks/forgejo/`).
> wateringHole retains this architecture reference as the K-Derm diderm relay spec.

| Script | Runs On | Bond | Owner |
|--------|---------|------|-------|
| `pepti-sync-relay.sh` | peptidoglycan | Metallic→Ionic | cellMembrane |
| `ext-github-push.sh` | golgiBody-ext | Ionic→Weak | cellMembrane |
| `impulse-relay-hook.sh` | peptidoglycan | — | cellMembrane |
| `setup-push-mirrors.sh` | — | — | Fossilized (pre-diderm) |

## K-Derm Diderm Flow

### Full relay chain (target architecture)

1. Gate pushes to Forgejo on golgiBody-inner (covalent SSH)
2. Forgejo post-receive webhook notifies peptidoglycan
3. `pepti-sync-relay.sh` on peptidoglycan:
   - Pulls from Forgejo (metallic: inner→structural)
   - Runs impulse cascade (detect + relay pending impulses)
   - SSHs to golgiBody-ext, triggers `ext-github-push.sh`
4. `ext-github-push.sh` on golgiBody-ext:
   - Pushes to GitHub (weak: outer→extracellular)
   - golgiBody-ext holds the only GitHub SSH write credentials

### SSH key placement (bonding model)

| Node | GitHub SSH | Forgejo SSH | Bond Types |
|------|-----------|-------------|------------|
| golgiBody-inner | None (revoked) | Yes (Forgejo owns it) | Covalent, Metallic |
| peptidoglycan | None (revoked) | Yes (pull from Forgejo) | Metallic |
| golgiBody-ext | **Yes (push to GitHub)** | Yes (pull from Forgejo) | Ionic, Weak |

Only the outer membrane (trans face) has extracellular write access.

## Setup

### peptidoglycan

```bash
# Scripts are deployed from cellMembrane
cd /opt/ecoPrimals/gardens/cellMembrane
membrane deploy.hooks --target peptidoglycan
```

### golgiBody-ext

```bash
# Scripts are deployed from cellMembrane
cd /opt/ecoPrimals/gardens/cellMembrane
membrane deploy.hooks --target golgiBody-ext
```

### golgiBody-inner (Forgejo webhook)

In Forgejo → wateringHole repo settings → Webhooks:
- URL: `http://[RELAY_PUBLIC]:3001/hooks/pepti-sync-relay`
- Content type: `application/json`
- Trigger: Push events
- Branch filter: `main`
