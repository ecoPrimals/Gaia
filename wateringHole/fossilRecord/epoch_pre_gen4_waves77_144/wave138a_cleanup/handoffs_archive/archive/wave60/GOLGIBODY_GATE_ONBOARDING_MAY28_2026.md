# golgiBody Gate Onboarding — SSH Key Registration for VPS Forgejo

**Date:** 2026-05-28 (Wave 60)
**From:** irongate (projectNUCLEUS)
**To:** All gates (eastGate, northGate, westGate, southGate, strandGate, biomeGate)

---

## Status

VPS Forgejo at `git.primals.eco` is **live** with all 34 repos seeded from irongate.
DNS is cut over — `git.primals.eco` A record points to VPS ([RELAY_PUBLIC]).

**irongate** is fully operational: SSH remote set up, push/pull verified.

---

## Gate Onboarding Steps

Each gate needs to register its SSH public key with VPS Forgejo, then update remotes.

### 1. Register SSH key

```bash
# Get your gate's public key
cat ~/.ssh/id_ed25519.pub  # or id_rsa.pub

# Register it with Forgejo API (use the golgiAdmin token)
FORGEJO_TOKEN=$(ssh root@[RELAY_PUBLIC] 'cat /opt/forgejo/.api_token')
GATE_NAME=$(hostname)
GATE_KEY=$(cat ~/.ssh/id_ed25519.pub)

curl -sf -X POST "https://git.primals.eco/api/v1/user/keys" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$GATE_NAME\",\"key\":\"$GATE_KEY\"}"
```

### 2. Accept VPS host key

```bash
ssh -o StrictHostKeyChecking=accept-new -p 2222 git@git.primals.eco
# Expected: "Hi there, golgiAdmin! You've successfully authenticated..."
```

### 3. Update forgejo remotes

Option A — Use `forgejo_mirror.sh` from projectNUCLEUS:

```bash
FORGEJO_URL=https://git.primals.eco \
FORGEJO_TOKEN=$FORGEJO_TOKEN \
ECOPRIMALS_ROOT=/home/<gate-user>/Development/ecoPrimals \
bash gardens/projectNUCLEUS/deploy/forgejo_mirror.sh --dry-run
```

Option B — Use `cascade-pull.sh --ensure-remotes` (if already configured).

Option C — Manual per-repo:

```bash
cd <repo> && git remote set-url forgejo ssh://git@git.primals.eco:2222/<org>/<repo>.git
```

### 4. Verify

```bash
cd gardens/projectNUCLEUS && git push forgejo main
# Expected: "Everything up-to-date" or successful push
```

---

## Org → Directory Mapping

| Forgejo Org | Local Directory | Repos |
|-------------|----------------|-------|
| sporeGarden | gardens/ | projectNUCLEUS, cellMembrane, projectFOUNDATION, lithoSpore, esotericWebb |
| ecoPrimals | primals/ + infra/ | bearDog, songBird, toadStool, ..., plasmidBin, wateringHole, sporePrint, whitePaper |
| syntheticChemistry | springs/ + infra/ | primalSpring, wetSpring, hotSpring, ..., agentReagents, benchScale |

---

## For eastGate / primalSpring

primalSpring can resume work once eastGate completes steps 1-4 above.
All 34 repos are seeded and current as of Wave 60.
The `cascade-pull.sh` SSH remotes will resolve to VPS Forgejo once
your gate's key is registered.

---

*Wave 60. golgiBody live. Gates: register and push.*
