# Gates Identified: ironGate + sporeGate + graftGate

**Wave 244 — Sunday Nov 15, 2026 — 7:27 AM**

## The PNS Walk Reveals the Truth

| IP | Gate | Hardware | OS | Ports | Status |
|----|------|----------|----|-------|--------|
| .4.237 | **ironGate** | 1C:86:0B | Ubuntu 22.04 | 22,8080,9800,11434 | ✅ FULL (nestGate+biomeOS+18 Ollama) |
| .4.244 | **sporeGate** | 1C:86:0B (sibling) | Ubuntu 22.04 | 22,80,443,8080,9800,11434 | ✅ FULL |
| .4.181 | **graftGate** 🍎 | Apple M4 | macOS (SSH 10.2) | 22,3389 | ✅ NEW |
| .4.147 | **northGate** | BC:FC:E7 | Windows/Linux | 22,8080,9090,9200 | ✅ bearDog+nestGate |
| .4.100 | **swiftGate** | AMD Ryzen 7 + RTX 3070 | Windows | * | ✅ Command |
| .4.159 | **grapheneGate** | Pixel 8a | GrapheneOS | 5555(ADB) | ✅ Bridge |
| .4.3 | **eastGate?** | ? | Ubuntu 22.04.18 | 22 | ✅ SSH only |

## ironGate Identity Confirmed

- Hostname: `gaia-ecosystem`
- nestGate v0.5.0 with 96 capabilities
- biomeOS on :9800
- **18 Ollama models** — full cortex.pi mixture-of-experts:
  - Heavy (4.5GB): forge, oracle, math, code, cortex, heart
  - Medium (2GB): gut, reason, general
  - Light (1.5GB): dream, triage
  - Fast (1.2GB): fast
- SSH: publickey ONLY (need to deploy our ed25519 key)
- Models all modified Nov 14 2026 — deployed YESTERDAY

## sporeGate Identity Confirmed

- SSH user `sporeGate` exists on .244
- Same hardware OUI as ironGate (1C:86:0B sibling)
- Same Ubuntu 22.04.15 SSH banner
- SSH accepts publickey+password (can use password "sporegate")

## graftGate — New Addition

- Apple M4 Darwin, macOS (OpenSSH 10.2 = latest)
- RJ45 ethernet into Flint 2
- Located in House 2 basement near ironGate/sporeGate
- Ports: SSH (22) + RDP/ARD (3389)
- Password: "graftgate" (speak friend and enter)

## Network Correction

Previous session had ironGate at 192.168.1.148. **WRONG.**
The entire mesh is a flat /22 on 192.168.4.0/22. There is no separate 192.168.1.x LAN.
All devices (both houses) are on one unified L2 mesh via Flint router pair.

## Speak Friend and Enter (ZK Tolkien)

Password scheme: all lowercase gate name
- `graftgate`, `irongate`, `sporegate`, `eastgate`, `northgate`

The doors of Moria: "Speak friend, and enter." mellon = friend.
The gate names ARE the friends. The password IS the identity.

**7 gates found. 13 devices total. One unified /22 mesh. lub-DUB.** 🫀
