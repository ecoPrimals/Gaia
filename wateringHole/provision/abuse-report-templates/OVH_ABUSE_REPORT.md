# Abuse Report — OVHcloud (OVH SAS)
# Template for fleet activity observed on OVH infrastructure

**To:** abuse@ovh.net
**Subject:** Collecte automatisée non autorisée par Meta Platforms ciblant un service hébergé chez OVH / Unauthorized automated scraping from Meta Platforms targeting OVH-hosted service

---

## Summary / Résumé

I am reporting unauthorized automated scraping activity targeting my OVH VPS. The scraping fleet is operated by **Meta Platforms, Inc.** (confirmed via WHOIS: FB-BLOCK, 57.141.0.0/13, registered to Meta Platforms Ireland Limited).

Je signale une activité de scraping automatisé non autorisée ciblant mon VPS OVH. La flotte de scraping est exploitée par **Meta Platforms, Inc.** (confirmé par WHOIS: FB-BLOCK, 57.141.0.0/13, enregistré sous Meta Platforms Ireland Limited).

## Violations

1. **OVHcloud Conditions Générales de Service** — Utilisation abusive des services
2. **Code pénal français, Art. 323-1 à 323-3** — Accès frauduleux à un système de traitement automatisé de données
3. **RGPD / GDPR** — Collecte automatisée de données sans base légale
4. **Directive européenne sur le droit d'auteur** — Violation de licence AGPL-3.0-or-later
5. **CNIL** — Compétence territoriale pour les violations RGPD sur infrastructure française

## Server Details / Détails du serveur

- **OVH VPS IP:** [LAYER_IP]
- **Hostname:** [LAYER_DOMAIN]
- **Datacenter:** [OVH_DATACENTER] (e.g., Gravelines)
- **Account:** [OVH_ACCOUNT]

## Attacking Infrastructure / Infrastructure attaquante

| Bloc réseau | Enregistrement | Entité WHOIS | Contact abus |
|---|---|---|---|
| 57.141.0.0/13 | FB-BLOCK | Meta Platforms Ireland Limited | domain@fb.com |
| 173.252.0.0/16 | FACEBOOK-INC | Facebook, Inc. | domain@facebook.com |

## Evidence / Preuves

### Fingerprint comportemental

Six signatures comportementales conservées identifient cette flotte:

1. `header_poverty` — En-têtes Chrome obligatoires absents (100% de la flotte)
2. `stale_chrome` — Version Chrome obsolète codée en dur (100%)
3. `connection_absent` — En-tête Connection absent (100%)
4. `content_gate` — >50% des requêtes ciblent le code source (99%)
5. `accept_monoculture` — En-tête Accept universel `*/*` (89%)
6. `blame_ratio` — >10% des requêtes ciblent /blame/ pour l'attribution d'auteurs (67%)

### Violation robots.txt

Le fichier robots.txt interdit tout accès automatisé. La flotte le lit et l'ignore.

### Volume

- **Requêtes observées:** [INSERT_COUNT]
- **Période:** [INSERT_PERIOD]
- **Données consommées:** [INSERT_MB] Mo

## Contexte CNIL

OVH étant un hébergeur français, la CNIL a compétence territoriale sur les violations RGPD commises via l'infrastructure OVH. Meta Platforms Ireland Limited, en tant que responsable du traitement des données, est soumis au RGPD via sa filiale irlandaise. La collecte automatisée sans base légale constitue une violation des articles 5 et 6 du RGPD.

Meta a déjà été sanctionné par la CNIL (390 millions d'euros en janvier 2023 pour violations du consentement publicitaire).

## Action demandée

1. Accuser réception de ce signalement
2. Enregistrer ce rapport dans vos dossiers
3. Noter que les IP attaquantes sont les blocs réseau propres de Meta Platforms

## Documentation complète

- **Observatoire:** https://signal.primals.eco/
- **Flux de renseignements:** https://signal.primals.eco/feed/conserved-plasmid.json
- **Bibliothèque de preuves:** https://detroit.primals.eco/

---

*Déposé par: ecoPrimal*
*Date: [DATE]*
*Référence: signal.primals.eco couche d'observation [LAYER_NAME]*
