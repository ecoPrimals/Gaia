# Credential Vault

Encrypted API keys and tokens for data federation.

## Decrypt

```bash
gpg --decrypt cred_bundle.tar.gpg | tar xf -
```

Passphrase: ecosystem standard (`ecoPrimal-{gate}-{wave}-sovereign`)

## Accounts

| Service | Account | Type | Config |
|---------|---------|------|--------|
| NCBI Entrez/SRA | ecoprimal@orcid | API key (10 req/s) | `~/.ncbi_api_key` |
| Synapse (Sage) | ecoPrimal | JWT PAT | `~/.synapseConfig` |
| Copernicus CDS | eco Primal | API key | `~/.cdsapirc` |
| COSMIC (Sanger) | Academic licence | Basic auth | Session |
| BRENDA | eco.primal@pm.me | SOAP API | Session |

## Recovery

1. Clone wateringHole from golgiBody
2. `cd vault && gpg --decrypt cred_bundle.tar.gpg | tar xf -`
3. Copy token files to `~/` on the target gate
4. Install clients: `pip3 install synapseclient cdsapi`
