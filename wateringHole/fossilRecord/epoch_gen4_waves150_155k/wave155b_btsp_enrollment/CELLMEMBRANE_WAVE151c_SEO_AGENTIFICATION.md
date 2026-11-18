# cellMembrane Handoff: SEO Agentification — Wave 151c

**Date**: Jul 26, 2026 | **From**: eastGate overwatch
**To**: cellMembrane team (sporeGate)
**Priority**: P2

---

## Problem

Google Search Console management is manual browser work. The service
account is provisioned — wire it into cellMembrane so cascade reviews
surface SEO metrics and sporePrint deploys auto-submit sitemaps.

## Service Account

- **Email**: `sporeprint-seo@ecoprimals-seo.iam.gserviceaccount.com`
- **Project**: `ecoprimals-seo`
- **Permission**: Full (on `primals.eco` domain property)
- **API**: Google Search Console API (enabled)
- **Credential**: JSON key file — deploy to golgiBody via secure channel
  (rsync/scp), NOT git. Store at `/opt/ecoPrimals/credentials/gsc-service-account.json`
  with `chmod 600`.

## Commands to Implement

### `membrane seo.submit-sitemap`

Submit sitemap URL to Google Search Console.

```
membrane seo.submit-sitemap https://sporeprint.primals.eco/sitemap.xml
```

API: `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}`

Trigger: Run automatically after sporePrint deploy (wire into post-deploy hook).

### `membrane seo.status`

Pull and display search performance summary.

```
membrane seo.status [--days 28] [--unbranded]
```

API: `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`

Output:
- Total impressions, clicks, CTR, average position
- Top 10 queries (optionally filtered to unbranded)
- Top 10 pages by impressions
- Indexing coverage summary

The `--unbranded` flag filters OUT queries containing: ecoPrimals, primals,
sporePrint, wetSpring, barraCuda, songBird, bearDog, skunkBat, nestGate.

### `membrane seo.request-index <url>`

Request Google to re-crawl and index a specific URL.

```
membrane seo.request-index https://sporeprint.primals.eco/science/dada2-gpu-benchmark/
```

API: `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`

### `membrane seo.coverage`

Show indexing coverage — how many pages are indexed vs excluded.

API: Uses the URL Inspection API to sample key pages.

## Authentication Pattern

Use the `google-auth` Rust crate (or `yup-oauth2`) for service account
JWT authentication. The credential JSON file path should come from env:

```
MEMBRANE_GSC_CREDENTIALS=/opt/ecoPrimals/credentials/gsc-service-account.json
MEMBRANE_GSC_SITE=sc-domain:primals.eco
```

## Integration Points

1. **Post-deploy hook**: After sporePrint content deploys to golgiBody,
   auto-run `membrane seo.submit-sitemap`
2. **Cascade review**: `membrane seo.status --unbranded` output surfaces
   in dimensional reviews under Dim 5 (Public Surface)
3. **sporePrint deploy**: New pages trigger `membrane seo.request-index`

## Credential Deployment

The JSON key lives on:
- **golgiBody**: `/opt/ecoPrimals/credentials/gsc-service-account.json` (production)
- **northGate**: Downloads folder (backup copy, user has it)

Do NOT commit credentials to git. The `.gitignore` in plasmidBin already
covers `*.age` files — store the credential encrypted at rest if needed.

---

*User task DONE: Google Cloud project created, Search Console API enabled,
service account provisioned and added with Full permission. Credential
JSON key downloaded. cellMembrane team wires the API calls.*
