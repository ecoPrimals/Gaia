# Anchoring Standard

**Ecosystem-Wide Public Chain Anchoring Guidance**

**Status**: ACTIVE
**Date**: May 20, 2026
**Audience**: All primals, springs, and gardens
**Origin**: loamSpine WS-3 (River Delta), gen4/architecture/ANCHORING_PIPELINE

---

## Purpose

This document defines how any primal, spring, or garden contributes to
public chain anchoring. It is the canonical ecosystem stance on
cryptocurrency, gas costs, community pooling, and verification.

**Read this if you**:
- Build a spring that produces provenance-worthy results
- Want to understand how ecoPrimals ties into public record
- Need to verify an anchored result
- Are designing new data flows that touch permanence

---

## The Short Version

1. Your experiment produces a DAG (rhizoCrypt)
2. The DAG dehydrates to loamSpine (permanent record)
3. loamSpine aggregates N state hashes into a single 32-byte Merkle root
4. That root anchors to one or more public chains for gas cost only
5. Each individual result has a Merkle proof against the aggregate root

**Cost**: $0.001 per result (Bitcoin, aggregated) or $0.000005 (Ethereum L2)

---

## Crypto Stance: Ledger, Not Currency

This is the canonical ecosystem position. All primals and springs
must align to this framing:

| Use | Don't use |
|-----|-----------|
| Bitcoin as a public timestamp ledger | Bitcoin as a currency |
| Ethereum as a programmable timestamp ledger | Ethereum tokens, DeFi, NFT marketplaces |
| L2 rollups as cheap, fast timestamp ledgers | L2 bridges for financial transactions |
| Gas fees as postage for public record | Wallets, exchanges, token economics |

**Gas cost is postage.** We pay the minimum fee to write 32 bytes to
a public append-only store. We don't hold positions, trade tokens, or
participate in blockchain economic systems beyond the gas transaction.

Currency (BTC, ETH) is an abstraction of the blockchain's own
economics. Bitcoin miners accept BTC for including transactions.
That's the extent of our interaction with cryptocurrency.

### What IS possible (for others)

The anchor surface is a bridge. A holder of a Loam Certificate
(a Novel Ferment Transcript) COULD use L2 smart contracts to transfer
digital assets cryptographically — the certificate's `state_hash` is
already on-chain. A bridge contract could verify ownership via the
Merkle inclusion proof.

These capabilities are **possible** because the infrastructure is
chain-compatible. They are **not required** because the ecosystem is
sovereign.

---

## The Compression Pipeline

```
Layer 1: rhizoCrypt DAG          (GB of data, thousands of vertices)
    │ Merkle root
    ▼
Layer 2: 32 bytes                (session root)
    │ dehydrate (session.commit)
    ▼
Layer 3: loamSpine entry         (certificate + merkle root + metadata)
    │ Blake3(tip)
    ▼
Layer 4: 32 bytes                (state_hash)
    │ aggregate N state hashes
    ▼
Layer 5: 32 bytes                (aggregate root)
    │ OP_RETURN / calldata / TSA
    ▼
Layer 6: Public chain            (one transaction)
```

The compression ratio is astronomical. Gigabytes of computation,
thousands of DAG vertices, hundreds of spine entries — all committed
by 32 bytes on-chain. The chain stores the commitment. The sovereign
infrastructure stores the data.

---

## What Springs Need to Do

### Minimum (provenance-ready)

1. **Wire rhizoCrypt session recording** into your experiment harness
2. At experiment completion, call `session.commit` to dehydrate to loamSpine
3. Your experiment is now permanently recorded with Merkle-provable history

This is already implemented in esotericWebb V4 (exp061, 317 checks)
and validated across the provenance trio (rhizoCrypt + loamSpine +
sweetGrass).

### Optional (anchor-ready)

4. After `session.commit`, call `anchor.publish` to record a single
   anchor receipt on the spine
5. Or batch with other springs via `anchor.publish_batch` for
   community aggregation

Springs do NOT submit transactions directly to public chains. loamSpine
records the anchor metadata. The chain-anchor primal (or external
service) handles actual chain submission.

---

## What the Anchor Costs

### Single anchor

| Target | Cost | Latency | Permanence |
|--------|------|---------|------------|
| Bitcoin OP_RETURN | $0.10–$2.00 | 10–60 min | 15+ years, proof-of-work |
| Ethereum L1 calldata | $0.10–$2.00 | ~15 sec | 10+ years, proof-of-stake |
| Ethereum L2 (Arbitrum, Base) | $0.001–$0.01 | near-instant | L1 security inheritance |
| RFC 3161 TSA | Free | <1 sec | TSA CA chain lifetime |

### Aggregated (community pooling)

| Results batched | BTC cost per result | ETH L2 cost per result |
|-----------------|--------------------|-----------------------|
| 1 | $1.00 | $0.005 |
| 10 | $0.10 | $0.0005 |
| 100 | $0.01 | $0.00005 |
| 1,000 | $0.001 | $0.000005 |

### Community pooling model

```
100 researchers × 10 results/month = 1,000 results
1 BTC aggregate anchor:  ~$1.50
1 ETH L2 aggregate anchor: ~$0.005
Dual-chain (BTC + L2):  ~$1.51 total

Per researcher: $0.015/month
Per result: $0.0015 (BTC) + $0.000005 (L2)
```

A community could publish on **every major chain** for less than cloud
data egress for a single export of the underlying data.

### Comparison

| Method | Cost per "publication" | Verification |
|--------|----------------------|-------------|
| Journal APC (Nature) | $5,500 | Trust the journal |
| arXiv preprint | $0 | No formal verification |
| Cloud provenance export | $0.09/GB egress | Trust the cloud |
| **Sovereign (BTC, aggregated)** | **$0.001** | **Cryptographic proof** |
| **Sovereign (L2, aggregated)** | **$0.000005** | **Cryptographic proof** |

---

## Aggregation Pattern

N spine state hashes form the leaves of a binary Merkle tree. The root
is 32 bytes regardless of N. Each leaf has a Merkle inclusion proof of
log2(N) hashes.

```
              aggregate_root (32 bytes)
             /                         \
        H(A,B)                        H(C,D)
       /      \                      /      \
  state_A   state_B            state_C   state_D
  (spine1)  (spine2)           (spine3)  (spine4)
```

loamSpine uses Blake3 for the aggregate tree (same hash function as
internal state hashes).

### The `0x6563` namespace

On-chain data is prefixed with `0x6563` ("ec" — ecoPrimals namespace)
to distinguish ecoPrimals anchors from other OP_RETURN / calldata
uses.

### How N springs contribute to one anchor batch

1. Each spring calls `session.commit` at experiment completion
2. loamSpine records the spine entry, producing a `state_hash`
3. A batch coordinator collects N state hashes
4. `anchor.publish_batch` computes the aggregate root and records
   individual `PublicChainAnchor` entries on each spine with the
   aggregate root and Merkle inclusion proof
5. One chain transaction covers all N results

---

## Verification

How to verify an anchored result (`ecoPrimals verify` flow):

1. **Recompute** the spine's `state_hash` from its tip entry
2. **Verify inclusion** — check the Merkle inclusion proof against
   the `aggregate_root` (if aggregated)
3. **Verify on-chain** — confirm the `aggregate_root` matches the
   on-chain `tx_ref` data
4. **Confirm timestamp** — check `block_height` and
   `anchor_timestamp` against chain state

Steps 1-2 are local (no chain access needed). Steps 3-4 require read
access to a public chain node (free, no authentication).

### RPC methods

| Method | Description |
|--------|-------------|
| `anchor.publish` | Record a single anchor receipt on one spine |
| `anchor.publish_batch` | Aggregate N spines, record anchors with inclusion proofs |
| `anchor.verify` | Verify anchor (single or aggregate) against spine state |

---

## L2 and Data Asset Transfer

### What L2 enables

Ethereum L2 rollups (Arbitrum, Base, Optimism) inherit L1 security at
100-1000x lower cost. With aggregation, L2 anchoring costs
$0.000005 per result — effectively free.

This makes high-frequency anchoring practical: a spring could anchor
every experiment run, not just milestones.

### Data asset transfer (optional, advanced)

Someone who holds a Loam Certificate could:
- Transfer it via an L2 smart contract
- Use a Merkle proof to demonstrate inclusion in an aggregate anchor
  to any EVM smart contract
- Build a verification contract that checks loamSpine anchor proofs
  entirely on-chain

This is **optional** — the ecosystem is sovereign without it. It
exists because the anchor surface is chain-compatible by design.

---

## For Primal / Spring Authors

### Vocabulary alignment

| Use | Don't use |
|-----|-----------|
| "public chain anchor" | "blockchain integration" |
| "gas cost" or "postage" | "transaction fee" |
| "Novel Ferment Transcript" | "NFT" (without context) or "blockchain NFT" |
| "anchor surface" | "crypto layer" |
| "sovereignty gradient" | "on-chain / off-chain split" |

### Files to reference

| File | Repo | Purpose |
|------|------|---------|
| `specs/ANCHORING_ARCHITECTURE.md` | loamSpine | Full architecture with code-level detail |
| `specs/PUBLIC_TIMESTAMPING.md` | loamSpine | Anchor target comparison |
| `gen4/architecture/ANCHORING_PIPELINE.md` | whitePaper | 5-layer pipeline and economics |
| `gen4/economics/NOVEL_FERMENT_TRANSCRIPTS.md` | whitePaper | Memory-bound digital objects |
| This document | wateringHole | Ecosystem-wide guidance |

---

*32 bytes. That's the width of the bridge between a home cluster and
every public chain on earth. The computation is sovereign. The proof
is global. The science speaks for itself.*
