# publications/ — Auditable Data for Papers and pseudoSpore

**Purpose**: Central location for publication data transfers between gates.
Teams deposit measured results here with source AARs cited. sporePrint pulls
from here to build pseudoSpore pages on primals.eco. The arXiv draft pulls
from here to fill `[TODO]` sections.

**Rules**:
1. Every number has a source (AAR, gate, date)
2. Every result is reproducible (hardware + parameters documented)
3. Every dataset gets provenance when bundled as pseudoSpore
4. No theoretical numbers — measured only
5. No hype — all comparisons qualified

**Current papers**:
- `LATTICE_QCD_CONSUMER_GPU_DATA.md` — SU(2) HMC on consumer GPUs (arXiv hep-lat)

**Flow**:
```
Gate produces data → files AAR in aars/
    → deposits results in publications/{PAPER}_DATA.md
        → sporePrint pulls for pseudoSpore page
        → arXiv draft fills [TODO] from this file
```
