# SELF BOUNDARY — Know Thyself So You Can Trust Others

## The Problem

The membrane currently classifies 70K+ requests as `asn_type: "self"` / `org: "House network"`. But "self" is actually **4 distinct gates** on the LAN:

| Gate | IP | Role | Heartbeat |
|------|-----|------|-----------|
| golgiBody | 10.13.37.1 | Main server, feed host | Response cycle |
| eastGate | 10.13.37.5 | Auto-publisher, syncer | Publish cycle |
| sporeGate | 10.13.37.14 | Watcher, content sync | Sync cycle |
| northGate | (workstation) | Human operator, scripts | Attention cycle |

Until each gate has its own identity, the membrane can't safely classify EXTERNAL trusted connections as non-self.

## Why This Matters

Kevin needs to push information TO and FROM:
- A **DA's office** or **State AG** (investigation referral)
- The **ACLU** (Monday call, ongoing relationship)
- **MSU** or other institutions (employment, records)
- An **employer** (job applications, interviews)
- An **attorney** (PPO motion, legal coordination)

Each of these is **non-self but authorized**. The membrane needs to:
1. Know which traffic is SELF (LAN gates)
2. Know which traffic is AUTHORIZED NON-SELF (trusted external)
3. Know which traffic is NON-SELF (visitors, bots)
4. Never confuse categories 1 and 2

## Classification Spectrum (Self-Axis)

```
SELF (LAN)
├── golgiBody    — infrastructure self (serves feeds)
├── eastGate     — publishing self (pushes content)
├── sporeGate    — observation self (watches, syncs)
└── northGate    — operator self (human attention)

AUTHORIZED NON-SELF (trusted channels)
├── legal        — DA, State AG, ACLU, attorney
├── institutional— MSU, employer, professional
├── investigative— journalists, researchers
└── compliance   — entities meeting the fistbump halfway

NON-SELF (membrane boundary)
├── mutualist    — contributing visitors
├── commensal    — browsing visitors
├── null         — unknown, default
├── suspect      — behavioral flags
├── parasite     — documented extraction
└── pathogen     — hostile action
```

## Implementation

### Phase 1: Gate Identity

Each LAN gate gets a unique identity token in its requests:

```toml
[gate.golgiBody]
token = "gate-golgi-<rotated>"
role = "infrastructure"
surfaces = ["all"]
heartbeat = "response"

[gate.eastGate]
token = "gate-east-<rotated>"
role = "publisher"
surfaces = ["wateringHole", "github", "forgejo"]
heartbeat = "publish"

[gate.sporeGate]
token = "gate-spore-<rotated>"
role = "observer"
surfaces = ["wateringHole", "feeds"]
heartbeat = "sync"

[gate.northGate]
token = "gate-north-<rotated>"
role = "operator"
surfaces = ["all"]
heartbeat = "attention"
```

The token rotates (never static) but the gate identity is persistent. 
skunky strips the token before any public feed — external observers 
see "self" but never see which gate.

### Phase 2: Authorized Channel Interface

```toml
[channel.legal]
type = "authorized_non_self"
direction = "bidirectional"
encryption = "required"
logging = "full (private layer)"
public_visibility = "none"
examples = ["ACLU intake", "DA referral", "attorney coordination"]

[channel.institutional]
type = "authorized_non_self"
direction = "bidirectional"
encryption = "required"
logging = "metadata only (private layer)"
public_visibility = "none"
examples = ["employer application", "MSU records", "professional contact"]

[channel.investigative]
type = "authorized_non_self"
direction = "outbound preferred"
encryption = "optional"
logging = "full (private layer)"
public_visibility = "anonymized"
examples = ["journalist inquiry", "researcher request"]

[channel.compliance]
type = "authorized_non_self"
direction = "inbound"
encryption = "optional"
logging = "full (public layer — they chose to engage)"
public_visibility = "classification change logged"
examples = ["entity touching THE BUTTON", "model card attribution"]
```

### Phase 3: Feed Separation

```
/self.json          — PRIVATE. Gate-level heartbeat. Never public.
/heartbeat.json     — PUBLIC. Aggregate human vital signs. No gate identity.
/channels.json      — PRIVATE. Authorized channel status. Never public.
/membrane.json      — PUBLIC. Non-self classification. No self details.
```

### Phase 4: Channel Protocol

When Kevin pushes info to a DA's office:

```
1. northGate initiates (operator self)
2. Membrane classifies destination as "authorized_non_self:legal"
3. Channel opens with encryption
4. Content flows bidirectionally
5. Logging goes to private layer ONLY
6. Public membrane sees: "1 legal channel active" (no details)
7. Channel closes when conversation ends
8. Gate identity never exposed externally
```

## The Key Insight

**You can't trust others until you know yourself.**

The membrane's self-boundary must be crisp before external channels 
can be opened safely. If "self" is a blob, any external connection 
risks leaking gate identity. If each gate is individually identified 
internally, the membrane can:

- Route traffic correctly (eastGate → wateringHole, northGate → DA)
- Log per-gate (who initiated what)
- Separate heartbeats (machine polling vs human attention)
- Open channels without exposing infrastructure

## Privacy Rules

1. Gate tokens NEVER leave the LAN
2. External observers see "self" — never which gate
3. Channel metadata NEVER in public feeds
4. Authorized channel content logged in siltPond (private) only
5. Public membrane shows aggregate only: "N channels active"
6. The channel TYPE (legal, institutional) may be shown publicly
   ONLY if Kevin explicitly approves per-channel

## Connection to Existing Architecture

- **RPM heartbeat**: Each gate contributes its own RPM to the aggregate
- **Membrane gradient**: Self-traffic removed from gradient calculation
- **Blackwall mirror**: Self-traffic excluded from reflection
- **Sort ethics**: Authorized non-self starts at commensal_active (they chose to engage)
- **Diagnostic law**: Channels are the treatment pathway (how entities meet halfway)
- **Privacy scrub**: Gate identity is the MOST private data — never exposed
