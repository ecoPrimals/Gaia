# ABG JupyterHub — Access Guide

**URL**: `https://lab.primals.eco`
**Host**: ironGate (i9-12900K, RTX 5070 Ti, 128GB RAM)
**Software**: JupyterHub v5.4.5
**Wave**: 138a

---

## Requesting Access

1. **Contact the operator** (Tamison) via Discord, email, or in-person with:
   - Preferred **username** (lowercase, no spaces — this becomes your Unix account)
   - **Email** (for notifications, optional)
   - Brief description of your **compute needs** (RNA-seq, alignment, general analysis)

2. Operator creates your account on ironGate and provides:
   - Username
   - Temporary password (change on first login)

3. **Login** at `https://lab.primals.eco/hub/login`
   - Select your server options (default is fine for most work)
   - You'll land in a JupyterLab environment with terminal access

---

## What You Get

| Resource | Details |
|----------|---------|
| **CPU** | Shared access to 24 threads (i9-12900K) |
| **RAM** | 128GB shared — sufficient for STAR, kallisto, salmon |
| **GPU** | RTX 5070 Ti (CUDA) — available for GPU-accelerated tools |
| **Storage** | Home directory on NVMe. Shared `/data/` for datasets. |
| **Network** | Sovereign TLS. No third-party analytics. No telemetry. |
| **Software** | Python, R, conda/mamba available. Request additional tools. |

### Pre-installed (or installable via conda)

```bash
# RNA-seq pipeline tools (install in your env)
mamba create -n rnaseq -c bioconda -c conda-forge \
  kallisto salmon star samtools fastp multiqc fastqc \
  subread htseq bioconductor-deseq2 r-base
```

---

## Architecture

```
You (browser)
  → https://lab.primals.eco (TLS, Caddy on golgi VPS)
    → WireGuard tunnel (encrypted)
      → sporeGate drawbridge (songBird proxy)
        → ironGate JupyterHub :8000 (your notebooks run here)
```

All traffic is end-to-end encrypted. No cloud provider sees your data.
The JupyterHub runs on sovereign hardware in a private network.

### Evolution Path

```
NOW:    ironGate = JupyterHub + compute (single node)
NEXT:   golgi VPS = JupyterHub hub (auth + routing)
        ironGate + strandGate = HPC backends (GPU + EPYC)
        songBird mesh routes jobs to best-fit hardware
FUTURE: ABG members run own gates, federate via primal.eco mesh
```

---

## Guidelines

- **Large datasets**: Upload to `/data/shared/` so others can access. Don't duplicate large reference genomes in home dirs.
- **Long jobs**: Use `screen` or `tmux` in a terminal — your notebook server may restart on JupyterHub updates.
- **GPU**: Request GPU access if running CUDA workloads. Default notebooks don't reserve GPU.
- **Storage limits**: No hard quotas yet. Be reasonable. NVMe is fast but finite.
- **Privacy**: Your home directory is private. `/data/shared/` is visible to all JupyterHub users.

---

## Support

- **Operator**: Tamison (Discord / in-person)
- **Issues**: Report via Discord or open a note in the shared JupyterHub `/data/shared/issues/` directory
- **Sovereignty**: This is not a cloud service. It's a sovereign research platform. Your data stays on hardware we physically control.

---

*lab.primals.eco — sovereign compute for collaborative science.*
