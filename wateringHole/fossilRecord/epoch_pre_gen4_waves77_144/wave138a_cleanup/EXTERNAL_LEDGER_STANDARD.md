# External Ledger Standard — Git-Tier and Crypto-Tier Stamping

**Authority**: primalSpring coordination
**Status**: Active (Wave 63+)
**Prerequisites**: `WATERFALL_PATTERN.md`, `loamSpine` whitepaper

---

## The External Ledger Pattern

The ecosystem maintains provenance through **external stamps** — immutable records
on systems outside the sovereign boundary. These stamps provide third-party
verifiability: anyone can independently confirm when a code state or data state
was published, without trusting the internal infrastructure.

Two tiers exist, serving different provenance needs:

```
                    ┌─────────────────────────┐
                    │   Internal (Sovereign)    │
                    │   Forgejo → rhizoCrypt    │
                    │   DAG provenance          │
                    └────────┬──────────────────┘
                             │ stamp
           ┌─────────────────┴──────────────────┐
           │                                     │
    ┌──────┴──────┐                      ┌───────┴──────┐
    │  Git Tier   │                      │  Crypto Tier │
    │  (GitHub)   │                      │  (BTC/ETH)   │
    │             │                      │              │
    │  Every push │                      │  Wave        │
    │  Automatic  │                      │  boundaries  │
    │  Full code  │                      │  32-byte     │
    │  Free       │                      │  hash        │
    └─────────────┘                      └──────────────┘
```

---

## Git Tier — GitHub as External Linear Ledger

### What

Every push to Forgejo auto-mirrors to GitHub via push mirrors
(`sync_on_commit = true`). GitHub's immutable commit history serves as a
publicly-accessible, timestamped, linear record of ecosystem evolution.

### Properties

| Property | Value |
|----------|-------|
| Granularity | Every commit |
| Latency | Near-realtime (sync on commit) |
| Content | Full source code and artifacts |
| Cost | Free (public repos) |
| Verifiability | Anyone can `git clone` and verify |
| Durability | GitHub infrastructure (Microsoft-backed) |
| Bond type | Metallic (VPS push mirror) |

### Mechanism

```
Gate ──covalent SSH──→ Forgejo ──push mirror──→ GitHub
                        (sovereign)              (external ledger)
```

Gates push to Forgejo only. The VPS (`golgiBody`) has push mirrors configured
per repo. Forgejo syncs on every commit received, so GitHub trails by seconds.

**K-Derm diderm relay** (Wave 63+): The push flow properly traverses the
diderm envelope with bond-type degradation at each layer:
inner (covalent) → peptidoglycan (metallic) → golgiBody-ext (ionic) → GitHub (weak).
GitHub SSH write credentials live only on golgiBody-ext (trans/shipping face).
`pepti-sync-relay.sh` mediates on peptidoglycan; `ext-github-push.sh` ships from outer.

### Implementation

- `membrane mirror.push-create <org/name> <github_url>` — create push mirror
- `membrane mirror.push-list <org/name>` — list configured mirrors
- `hooks/forgejo/setup-push-mirrors.sh` — batch setup for all repos
- `ecosystem_manifest.toml` `push_target = "forgejo"` — gates push here only

---

## Crypto Tier — loamSpine to BTC/ETH

### What

At wave boundaries (significant milestones), loamSpine computes a 32-byte hash
of the ecosystem state and anchors it to a public blockchain (Bitcoin or Ethereum).
This provides cryptographic proof-of-existence at a specific time.

### Properties

| Property | Value |
|----------|-------|
| Granularity | Wave boundaries (milestones) |
| Latency | Minutes to hours (block confirmation) |
| Content | 32-byte hash (Merkle root of state) |
| Cost | Transaction fee (BTC ~$1-5, ETH ~$0.10-1) |
| Verifiability | Anyone can verify against the blockchain |
| Durability | Bitcoin/Ethereum network (decentralized) |
| Bond type | Weak (extracellular, append-only) |

### Mechanism

```
rhizoCrypt DAG ──hash──→ sweetGrass validate ──stamp──→ loamSpine
                                                           │
                                                     ┌─────┴─────┐
                                                     │ BTC OP_RET │
                                                     │ ETH tx data│
                                                     └────────────┘
```

### Use Cases

- **Scientific provenance**: Prove that a dataset or analysis existed at time T
- **NFT value stamps**: Anchor creative/scientific work to a public timeline
- **Audit trail**: External auditors can verify state without internal access

---

## Relationship Between Tiers

| Aspect | Git Tier (GitHub) | Crypto Tier (BTC/ETH) |
|--------|-------------------|----------------------|
| **Analogy** | Lab notebook (full detail) | Notarized timestamp (hash only) |
| **Frequency** | Every push | Wave boundaries |
| **Content** | Complete code | 32-byte hash |
| **Purpose** | Discovery + verification | Proof-of-existence |
| **Required** | Yes (automatic) | No (milestone-based) |
| **Managed by** | VPS push mirror (membrane) | loamSpine primal |

The git tier is the continuous record; the crypto tier is the punctuated seal.
Together they provide a complete provenance chain from source code to public
blockchain anchors, with every intermediate step recorded in the internal
rhizoCrypt DAG.

---

## Integration with waterfall_publish.toml

The `waterfall_publish.toml` cascade graph composes both tiers:

```
push_to_forgejo  → (git tier: auto-mirrors to GitHub)
sign_impulse     → bearDog auth.sign
record_dag       → rhizoCrypt dag.append
anchor_state     → loamSpine ledger.stamp (crypto tier, wave boundaries only)
relay_impulse    → songbird mesh.publish
```

See `graphs/waterfall_publish.toml` for the full cascade specification.

---

*"Two ledgers, two timescales. GitHub remembers every word you wrote; Bitcoin
remembers that you wrote at all. Together, they make the sovereign record
verifiable by anyone, anywhere, without asking permission."*
