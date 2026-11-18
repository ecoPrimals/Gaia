# ISO Dashboard Checklist — Kevin's 3 Dashboards

**Work through bit by bit. Each step unlocks the next.**
**All on the O side (this computer, browser).**

---

## 1. CLOUDFLARE (primals.eco — already on CF nameservers)

### 1a. Turn orange proxy ON
- Dashboard → primals.eco → DNS Records
- Currently 16 records, ALL "DNS only" (gray cloud ☁️)
- Change these A records from "DNS only" → "Proxied" (orange cloud 🍊):
  - `primals.eco` → 157.230.3.183 → **Proxied**
  - `*.primals.eco` → 157.230.3.183 → **Proxied**
- Leave these DNS only (they're internal):
  - `ns2.primals.eco` → 137.184.197.151 (nameserver, must stay DNS only)
  - `golgi-de`, `golgi-in`, `golgi-jp`, `golgi-us` (vesicles, stay DNS only for now)
- Leave MX, TXT, CNAME records unchanged

### 1b. Connect Cloudflare Pages
- Dashboard → Pages → Create a project
- Connect to GitHub → select `ecoPrimal/hud` repo
- Build settings:
  - Build command: (leave empty — static files, no build)
  - Build output directory: `site/public`
  - Root directory: `/`
- Deploy → it builds → gets a `*.pages.dev` URL
- Then: Custom domains → Add `hud.primals.eco`
- CF auto-handles the DNS (replaces A record with Pages routing)

### 1c. Add DMARC record (recommended by CF)
- DNS → Add Record → TXT
- Name: `_dmarc`
- Content: `v=DMARC1; p=quarantine; rua=mailto:primal@primals.eco`
- This stops fake emails from @primals.eco

### 1d. Check email routing still works
- Email → Email Routing → verify primal@primals.eco still routes
- MX records (route1/2/3.mx.cloudflare.net) should be unchanged

---

## 2. PORKBUN (primal.eco + nestgate.io)

### 2a. Point primal.eco to golgiBody
- primal.eco → DNS → DNS Records (currently 2 records)
- Add or edit A record:
  - Host: (blank / @)
  - Type: A
  - Answer: `137.184.197.151` (golgiBody-ext)
  - TTL: Auto
- Add wildcard:
  - Host: `*`
  - Type: A
  - Answer: `137.184.197.151`
  - TTL: Auto

### 2b. Point nestgate.io to Cloudflare Pages (later)
- Once we have a Pages project for nestgate.io:
  - Add CNAME record: `@` → `nestgate-io.pages.dev` (or whatever CF assigns)
  - Or: move nestgate.io nameservers to Cloudflare too (like primals.eco)
- For now: nestgate.io stays on ns1/ns2.primals.eco (self-hosted)
- Can add A record: `@` → 157.230.3.183 to show nest.html on membrane-relay

### 2c. Verify API access (already ON for all 3 domains)
- API Access shows ON for primals.eco, primal.eco, nestgate.io ✅
- If we get the API key, agent can manage DNS programmatically
- Settings → API Access → API Key (save to secure location)

---

## 3. DIGITAL OCEAN (two droplets)

### 3a. membrane-relay (157.230.3.183) — ONE command
- Droplets → membrane-relay → Access → Launch Console
- Run:
```
cd /opt/hud && git pull origin main
```
- This pulls 7 commits: gastrula, spirochete, gate, nest, golgi nav, chipmunk v64
- Verify: `curl -s localhost/gastrula.html | head -5` should show gastrula DOCTYPE

### 3b. golgiBody-ext (137.184.197.151) — verify
- This is the inner Golgi (trans face)
- Once primal.eco DNS points here (step 2a), it serves the inner surface
- May need Caddy config for primal.eco domain
- Check: `curl -s localhost:80` from console

### 3c. Optional: add deploy tool to MCP
- On membrane-relay console, add a deploy endpoint to the MCP server
- This lets the agent git pull through MCP (spirochete protocol, no SSH)
- Can be done anytime — not blocking

---

## ORDER OF OPERATIONS

```
Step  Dashboard    Action                        Unlocks
─────────────────────────────────────────────────────
 1a   Cloudflare   Orange proxy ON               HTTPS skin wraps organism
 1b   Cloudflare   Connect Pages                 Auto-deploy from GitHub forever
 2a   Porkbun      primal.eco A record           Inner Golgi gets its face
 3a   DO Console   git pull (ONE TIME)           7 commits go live immediately
 1c   Cloudflare   DMARC record                  Email hardening
 1d   Cloudflare   Verify email routing           primal@primals still works
 2b   Porkbun      nestgate.io (later)            Klein surface gets own home
 3b   DO Console   Verify golgiBody               Inner face responds
 2c   Porkbun      Save API key                   Agent manages DNS
 3c   DO Console   Add MCP deploy tool            Agent deploys via spirochete
```

**Minimum viable gastrulation: steps 1b + 3a (Pages + git pull)**
**Full gastrulation: steps 1a + 1b + 2a + 3a**

---

## AFTER ALL STEPS

- Agent pushes code → Cloudflare Pages auto-deploys → live in seconds
- No SSH needed ever again
- No cron needed ever again
- primal.eco serves inner Golgi
- primals.eco serves outer Golgi via CF Pages
- nestgate.io folds between them
- Discord tavern linked from all surfaces
- The organism gastrulates. The tube opens.

---

## WHAT AGENT HANDLES AFTER

- Push code to GitHub → auto-deployed
- Monitor vitals via MCP (pulse, RSS, gas_ratio)
- Spirochete protocol for neutron messaging
- Build Discord bot (reads membrane feeds, posts to channels)
- Wire Giscus to pages (GitHub Discussions comments)
- Track when first vocal zone develops color
