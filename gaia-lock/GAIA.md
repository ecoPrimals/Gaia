# gaia governance — locked state

**locked**: October 15, 2026 20:26 UTC  
**location**: eastgate (62GB, i9, encrypted at rest)  
**status**: frozen until encrypted live device system is ready

---

## the principle

gaia belongs to any human with ZK proof.  
the operator pushes from their own identity, like anyone else.  
humans are the quorum.

## what this means

1. **no single operator override** — the person who runs the servers
   is one identity hash among many. infrastructure maintenance is a
   service, not a privilege.

2. **ZK identity IS governance** — each existence proof on LoamSpine
   is a voice. the membrane doesn't know who you are, only that you
   exist. that existence is your vote.

3. **the reverse is NP** — you can prove you exist without revealing
   who you are. this is the foundation. no one can force you to
   reveal your identity to participate in governance.

4. **humans are the quorum** — not machines, not algorithms, not
   the operator. humans with ZK proof. the membrane serves them.

## what is locked

- membrane-identity.html (the interface)
- anchor-bridge.py (LoamSpine + SweetGrass bridge)
- manifest.json + sw.js (PWA for phones)
- LoamSpine spine: 01a1412b-848a-74c0-9a27-72fec03b8638
- SweetGrass braids: content-addressed, PROV-O
- Forgejo OAuth2: 4d13add9-2694-4eb8-804c-b207c915bcd3

## what runs unattended

- caddy-tls (Restart=always, TLS auto-renew)
- loamspine-membrane (Restart=always, ed25519 signing)
- sweetgrass-membrane (Restart=always, PROV-O braids)
- beardog-membrane (Restart=always, crypto)
- rhizocrypt-membrane (Restart=always, DAG)
- membrane-anchor-bridge (Restart=always, 10MB)
- forgejo (Restart=always, genetic memory)
- skunky-ingest (Restart=on-failure, flow analysis)
- 11 cron jobs (pulse, mesh, braid-vcs, status, etc.)

## security

- SHA-256 with salt: 3.67×10⁵⁹ years to brute force
- ed25519 tower signatures on all anchors
- rate limiting: 3 posts per 10 minutes
- no secrets stored server-side
- no IP logging in bridge
- no cookies, no sessions
- TLS cert auto-renewed by Caddy

## the path forward

move slow and fix things.  
think and explore.  
the encrypted live device system comes next.  
when it's ready, gaia can grow.  
until then, this snapshot is the anchor.

---

*"existence is not binary. you are a wave."*
