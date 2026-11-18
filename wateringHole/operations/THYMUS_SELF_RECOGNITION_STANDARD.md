# Thymus — Self-Recognition Standard

**Wave**: 163 | **Authority**: wateringHole consensus
**Learned from**: golgiBody autoimmune incidents (Wave 162–163)
**Applies to**: All VPS nodes, all gates with firewall chains

---

## Overview

The thymus is the subsystem that teaches the organism to distinguish self from
non-self. In biological immune systems, thymic negative selection destroys
T-cells that would attack the body's own tissues. In our infrastructure, every
firewall chain, rate limiter, and access control must know the full set of
**self-identities** — or risk blocking its own organs.

This standard codifies the self-recognition failures we discovered and the
patterns that prevent them.

---

## The Three Failures (golgiBody, Wave 162–163)

### 1. Loopback Firewall Traversal

**Symptom**: Forgejo SSH calls to itself (hooks, mirror sync) routed through
public DNS → public IP → iptables → rate limiter → DROP.

**Root cause**: `SSH_DOMAIN = git.primals.eco` resolved to the VPS public IP
([RELAY_PUBLIC]). Loopback traffic (`IN=lo`) entered the FORGEJO_GIT_MEMBRANE
chain and was rate-limited like external traffic.

**Fix**:
```bash
# /etc/hosts — self-resolution bypass
127.0.0.1 git.primals.eco

# Firewall — loopback interface bypass (rule 1 in every chain)
iptables -I <CHAIN_NAME> 1 -i lo -j ACCEPT
```

**Rule**: Every firewall chain on a VPS MUST have `-i lo -j ACCEPT` as its
first rule. Loopback traffic is self by definition.

### 2. Webhook Duplication

**Symptom**: Two identical system-level webhooks, both firing on every push,
both failing with payload parse errors. Each push generated 2 webhook
deliveries + retry cascades.

**Root cause**: Manual Forgejo admin panel setup created duplicates.
The webhook handler (skunky-ingest) expected a different JSON format.

**Fix**: Audit webhook table periodically. One system webhook maximum.
```sql
-- Check for duplicates
SELECT url, count(*) FROM webhook WHERE is_active = 1
GROUP BY url HAVING count(*) > 1;
```

**Rule**: One webhook per endpoint per scope (system/org/repo). Audit on
every deploy.

### 3. Fossilized Credentials

**Symptom**: 50 git remote configs contained URL-encoded `gh auth token`
error output as HTTPS passwords. Every mirror sync attempt authenticated
to GitHub with an error message.

**Root cause**: A shell command failure (`gh auth token` on a system
without `gh` properly configured) was captured as a credential and
embedded in the git remote URL.

**Fix**: Never embed shell command output directly into credential fields.
Validate credentials before storing.
```bash
# WRONG — captures error output as credential
TOKEN=$(gh auth token)
git remote set-url mirror "https://user:${TOKEN}@github.com/..."

# RIGHT — validate first
TOKEN=$(gh auth token 2>/dev/null) || { echo "gh auth failed"; exit 1; }
[[ "$TOKEN" =~ ^gh[ps]_ ]] || { echo "invalid token format"; exit 1; }
```

---

## Self-Identity File

Every VPS node and gate MUST maintain `/etc/membrane/self-ips.txt`:

```
# /etc/membrane/self-ips.txt — all IPs that are "self"
# Used by skunky-ingest --self-ips-file and firewall whitelisting
#
# Format: one IP or CIDR per line. Comments with #.

127.0.0.1           # loopback (always)
<PUBLIC_IP>          # this node's public IP
<WG_IP>             # this node's WireGuard IP (e.g., 10.13.37.1)
10.13.37.0/24       # WireGuard mesh (all peers are self)
<SPORE_GATE_WAN>    # sporeGate WAN IP (home network exit)
```

### Who reads this file

| Consumer | Flag / Config | Purpose |
|----------|---------------|---------|
| skunky-ingest | `--self-ips-file` | Thymic negative selection — never classify self as fleet |
| Firewall chains | Manual whitelist rules | Skip rate limiting for self-IPs |
| bloom_live.py | (reads skunky-ingest output) | Exclude self from fleet counters |

---

## Firewall Chain Template

Every rate-limiting firewall chain MUST follow this structure:

```bash
# Rule 1: Loopback bypass (self by interface)
iptables -A <CHAIN> -i lo -j ACCEPT

# Rule 2: Self-IPs bypass (self by address)
while IFS= read -r ip; do
    [[ "$ip" =~ ^#|^$ ]] && continue
    ip=$(echo "$ip" | awk '{print $1}')
    iptables -A <CHAIN> -s "$ip" -j ACCEPT
done < /etc/membrane/self-ips.txt

# Rule 3: Established connections
iptables -A <CHAIN> -m state --state RELATED,ESTABLISHED -j ACCEPT

# Rule 4+: Rate limiting (only affects non-self)
iptables -A <CHAIN> -p tcp --dport <PORT> -m state --state NEW \
    -m recent --set --name <CHAIN>_tcp
iptables -A <CHAIN> -p tcp --dport <PORT> -m state --state NEW \
    -m recent --update --seconds 60 --hitcount 6 --name <CHAIN>_tcp \
    -j LOG --log-prefix "<CHAIN>_RATELIMIT:"
iptables -A <CHAIN> -p tcp --dport <PORT> -m state --state NEW \
    -m recent --update --seconds 60 --hitcount 6 --name <CHAIN>_tcp \
    -j DROP

# Rule N: Accept (passed all checks)
iptables -A <CHAIN> -p tcp --dport <PORT> -j ACCEPT
```

---

## /etc/hosts Self-Resolution

Every VPS node that runs services addressing themselves by public hostname
MUST add their hostname to `/etc/hosts`:

```bash
# /etc/hosts
127.0.0.1 <hostname>.primals.eco
```

Also add to the cloud-init template if applicable:
```bash
echo "127.0.0.1 <hostname>.primals.eco" >> /etc/cloud/templates/hosts.debian.tmpl
```

This prevents DNS-resolved loopback traffic from traversing the firewall.

---

## VPS Node Onboarding Checklist

When provisioning a new VPS node:

- [ ] Create `/etc/membrane/self-ips.txt` with all self-IPs
- [ ] Add hostname to `/etc/hosts` (and cloud-init template)
- [ ] Every firewall chain starts with `-i lo -j ACCEPT`
- [ ] Every firewall chain whitelists self-IPs before rate limiting
- [ ] Audit Forgejo webhooks: no duplicates, no broken endpoints
- [ ] Audit push mirrors: no stale remotes, no poisoned credentials
- [ ] Verify git push completes in < 2 seconds
- [ ] Verify `dmesg | grep RATELIMIT` shows zero self-IP hits

---

## Genetic Lock — Bearer Token Authentication (Wave 165i)

Self-recognition has two layers:

1. **Network layer** (firewall): recognizes self by IP/interface
2. **Application layer** (Caddy): recognizes authorized agents by genetic token

### The Sec-Fetch Breach (Learned Failure)

The initial thymus passthrough used browser `Sec-Fetch-Mode: navigate` and
`Sec-Fetch-Dest: document` headers to distinguish human browsers from fleet.
Fleet evolved to spoof these headers within hours — **antigenic drift**.

**Rule**: Never use spoofable request headers as the sole authentication
for classification. Headers are phenotype (observable, imitable), not
genotype (cryptographically verifiable).

### The Genetic Lock Pattern

eastGate closed the breach by replacing Sec-Fetch with a bearDog-derived
cryptographic token:

```
bearDog key generate → membrane-passthrough-v1 (AES-256-GCM, Argon2id)
bearDog key derive  → purpose: golgi-body-web-passthrough
BLAKE3 hash         → bearer token (bd1-...)
```

The token is wired into Caddy's `@agent_passthrough` matcher:

```caddy
# git.primals.eco — classification-aware routing

# Layer 1: WireGuard mesh (network self-recognition)
@wg_mesh remote_ip 10.13.37.0/24
handle @wg_mesh {
    reverse_proxy localhost:3000
}

# Layer 2: Genetic lock (bearDog-derived token)
@agent_passthrough {
    header Authorization "Bearer <BEARDOG_TOKEN>"
}
handle @agent_passthrough {
    reverse_proxy localhost:3000
}

# Layer 3: Everything else → scatter (fabricated content)
reverse_proxy localhost:9753
```

### Routing Matrix

| Accessor | Method | Result |
|----------|--------|--------|
| WireGuard mesh (10.13.37.0/24) | IP allowlist | → Real Forgejo |
| Agent with bearDog token | Bearer header | → Real Forgejo |
| SSH clients (port 2222) | SSH key auth | → Real Forgejo |
| Spoofed Sec-Fetch headers | — | → Scatter |
| No headers | — | → Scatter |
| Wrong token | — | → Scatter |

### Token Tiers

| Tier | Source | Properties |
|------|--------|------------|
| Tier 1 | Software PRNG | Testing only |
| Tier 2 | bearDog software HSM (Argon2id) | **Current production** |
| Tier 3 | SoloKey hardware RNG + human tap | Planned — `beardog entropy collect --human-input --device solokey` |

### Evolution Path

The Caddy-layer genetic lock is a stopgap. The architecturally correct
solution is **Rust-level classification in scatter_server.rs**:

```
scatter_server.rs → genetic.verify_lineage() → session-scoped tokens
```

This uses the full behavioral fingerprint (timing CV, Chrome version
cadence, Accept-Encoding uniformity) alongside the bearer token for
defense in depth. The bearDog token is the lock; the behavioral analysis
is the alarm system.

---

## Biological Analogy

| Immune concept | Infrastructure equivalent |
|----------------|--------------------------|
| Thymus | Self-identity file + firewall whitelist |
| Thymic negative selection | `--self-ips-file` in skunky-ingest |
| MHC class I (self-marker) | `-i lo -j ACCEPT` + `/etc/hosts` resolution |
| MHC class II (antigen presentation) | bearDog genetic lock token |
| Autoimmune disease | Firewall rate-limiting own loopback traffic |
| Organ crosstalk failure | Forgejo SSH → DNS → public IP → firewall → rate limit → DROP |
| Antigenic drift | Fleet spoofing Sec-Fetch headers to bypass classification |
| Fossilized antibodies | Stale git remote configs attacking GitHub with error-string passwords |
| Genetic lock | bearDog-derived bearer token (genotype, not phenotype) |

The thymus doesn't just protect against external threats. It protects the
organism from its own immune system. Every firewall chain is an immune
response — it must be trained to recognize self before it can safely
reject non-self. And every classification gate must use genotype (crypto)
not phenotype (headers) — because phenotype can be mimicked.
