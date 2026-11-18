# cellMembrane Wave 155f — J8 Key Enrollment Portal Foundation

**Date**: 2026-07-28 | **Author**: cellMembrane team (sporeGate)
**Wave**: 155f | **Jelly string**: J8 (key enrollment portal)

---

## What Changed

### J8 Foundation: SSH Certificate Lifecycle via step-ca

**New module: `crates/membrane-shadow/src/gate/key_portal.rs`** (558L)

Implements the full SSH certificate lifecycle against a sovereign step-ca CA:

| Function | Purpose |
|----------|---------|
| `request_ssh_certificate()` | Obtain short-lived SSH user cert |
| `renew_ssh_certificate()` | Renew existing cert before expiry |
| `install_host_certificate()` | Request and install host cert |
| `inspect_certificates()` | Report user + host cert status |
| `bootstrap_ca()` | First-time CA trust setup |
| `parse_lifetime_secs()` | Parse "8h"/"30m"/"3600s" lifetime strings |

### New CLI Commands

| Command | Function |
|---------|----------|
| `gate.keys` | Show SSH certificate status (user + host), renewal status |
| `gate.keys.renew [--dry-run]` | Renew SSH user certificate |
| `gate.keys.renew --host <hostname>` | Request/renew host certificate |
| `gate.keys.renew --bootstrap` | Bootstrap step-ca trust on this gate |

### New Types (`cellmembrane-types/src/credentials.rs`)

- `SshCertificate` — serial, principals, expiry, CA fingerprint, cert/key paths
- `SshCertType` — `User` | `Host`
- `CredentialModel::StepCa` — new credential model variant
- `is_expired()`, `seconds_remaining()`, `needs_renewal(lifetime)` on `SshCertificate`

### New Constants (`cellmembrane-types/src/service/constants.rs`)

| Constant | Default | Env Override |
|----------|---------|-------------|
| `DEFAULT_STEP_CA_URL` | `https://ca.primals.eco:9443` | `STEP_CA_URL` |
| `DEFAULT_SSH_CERT_LIFETIME` | `8h` | `STEP_CA_SSH_LIFETIME` |
| `DEFAULT_STEP_CA_PROVISIONER` | `admin` | `STEP_CA_PROVISIONER` |
| `ENV_STEP_CA_FINGERPRINT` | (required) | `STEP_CA_FINGERPRINT` |
| `STEP_CA_CERT_DIR` | `certs` | — |

### gate.enroll Phase 8: `ssh_cert`

After `mesh.enroll` (phase 7), the enrollment flow now requests an SSH
certificate from step-ca. Non-fatal: enrollment passes even if step-ca is
not yet deployed (reports "skipped"). When step-ca is live and
`STEP_CA_FINGERPRINT` is set, the gate automatically gets a short-lived cert.

### Dispatch Extraction

`dispatch/gate_keys.rs` (67L) — extracted from `dispatch/gate.rs` to keep
under 800L limit. Routes `gate.keys` and `gate.keys.renew`.

### Deployment Team Handoff

`infra/wateringHole/handoffs/SPOREGATE_J8_STEP_CA_DEPLOYMENT.md` — full
deployment guide for step-ca on golgiBody: installation, systemd unit, sshd
TrustedUserCAKeys, host certificates, DNS, Caddy reverse proxy.

## Health Metrics

- **Tests**: 1,219 (was 1,200 → +19 new)
- **Clippy**: 0 warnings
- **Fmt**: 0 drift
- **Files >800L**: 0

## Dependencies on Upstream

- **Deployment team**: step-ca installation on golgiBody (handoff provided)
- **songBird + bearDog**: J8 Phase 3 (primal key passing) — design only, no code yet

## What This Gives Us

| Before | After |
|--------|-------|
| SSH keys exchanged via chat | Foundation for short-lived certs from sovereign CA |
| No cert management CLI | `gate.keys` / `gate.keys.renew` |
| Enrollment ends at mesh join | Enrollment includes SSH cert request |
| No cert expiry awareness | `SshCertificate.needs_renewal()` |
| Manual authorized_keys | Path to certificate-based auth |
