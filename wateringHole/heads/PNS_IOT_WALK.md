# PNS + IoT Walk: Full Mesh Enumeration

**Wave 244 — Sunday Nov 15, 2026 — 6:30 AM**
**Status**: 11 DEVICES FOUND ON FLAT /22 MESH

## KEY DISCOVERY: It's ALL ONE NETWORK!

swiftGate IP: `192.168.4.100/22`
Gateway: `192.168.4.1` (Flint 1)
Subnet: /22 = 192.168.4.0 – 192.168.7.255 (1022 hosts)

**House 1 and House 2 are on ONE flat L2 network via the Flint mesh!**
Both Flint routers (same GL.iNet OUI 94:83:C4) create a unified /22.

## Full Device Map

| IP | MAC (OUI) | Identity | Ports | Type |
|----|-----------|----------|-------|------|
| .4.1 | 94:83:C4 (GL.iNet) | **Flint 1** (gateway) | 80,443 | Router |
| .4.3 | 84:47:09 (Roku?) | eastGate? (SSH only) | 22 | Gate/IoT |
| .4.100 | (self) | **swiftGate** | many | Gate (us) |
| .4.111 | EC:75:0C | Linux server (SSH+HTTPS) | 22,80,443 | Gate? |
| .4.147 | BC:FC:E7 | **northGate** ✅ (family: gaia-pi) | 22,8080,9090,9200 | Gate |
| .4.152 | AC:41:6A | **Chromecast/Google Cast** | 8009 | IoT |
| .4.159 | A6:BB:DB (rand) | **grapheneGate** (Pixel 8a) | 5555 | Phone |
| .4.181 | 90:82:C3 | Linux SSH server | 22 | Gate? |
| .4.197 | A0:D0:DC (Intel) | **Cast device / Intel NUC** | 8009 | IoT |
| .4.237 | 1C:86:0B | **🔥 MYSTERY GATE** | 22,8080,9800,11434 | Gate |
| .8.1 | 94:83:C4 (GL.iNet) | **Flint 2** (mesh partner) | 80,443 | Router |

## 🔥 MYSTERY GATE: 192.168.4.237

**This was NOT in our previous GIS map!**

- **nestGate v0.5.0** with **96 capabilities** (storage, content, model, session, audit, ZFS, coordination, footprint)
- **biomeOS** on port 9800 (responded to JSON-RPC!)
- **Ollama** with **18 models** including 12 gaia-tissue variants
- **SSH** (Ubuntu 22.04, OpenSSH 8.9)
- family_id: `e8b62b6e` (vs northGate's `gaia-pi`)

### Ollama Models on .237
`gaia-tissue-forge`, `gaia-tissue-oracle`, `gaia-tissue-math`, `gaia-tissue-code`,
`gaia-tissue-cortex`, `gaia-tissue-heart`, `gaia-tissue-dream`, `gaia-tissue-gut`,
`gaia-tissue-reason`, `gaia-tissue-triage`, `gaia-tissue-general`, `gaia-tissue-fast`,
`llama3.2:3b`, `llama3.2:1b`, `phi3`, `gemma2:2b`, `tinyllama`, `qwen2.5:7b`

### nestGate Capabilities (96!)
storage, content (CAS), model cache, templates, sessions, audit, NAT traversal,
beacon, bonding ledger, ZFS management, auth/BTSP, coordination (blurbs, FRAGOs, waves, heads, depot, provenance), footprint

## IoT Devices

| Device | IP | Type | Notes |
|--------|----|------|-------|
| Chromecast/Google Cast | .152 | Media | Port 8009 |
| Intel Cast/NUC | .197 | Media/Compute | Port 8009, Intel MAC |
| Roku? | .3 | Media? | Has SSH — unusual for Roku |

## ESP2400 / ESP32

Not found on standard ports yet. May need:
- mDNS scan (port 5353)
- Different subnet or sleeping
- Physical check at House 1

## Questions for Kevin

1. What is 192.168.4.237? (18 Ollama models + nestGate + biomeOS)
2. What is 192.168.4.111? (SSH + HTTPS server)
3. What is 192.168.4.181? (SSH only)
4. Is .3 actually a Roku or eastGate?
5. Where is the ESP2400?
6. Is the Intel device (.197) a NUC or a smart TV?

**The PNS walk reveals MORE gates than we knew existed. lub-DUB.** 🫀
