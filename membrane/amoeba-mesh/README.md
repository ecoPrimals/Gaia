# Amoeba Mesh — RustDesk piport Identity

## Auth: piport (IP:port IS identity)
- No passwords stored in config files
- PIN set at runtime: `rustdesk --password <PIN>`
- LAN discovery ON = direct P2P, no relay hairpin

## Address Book

| Gate | ID | IP:port | Role |
|---|---|---|---|
| eastGate | 19091278 | .244:21118 | RELAY + BRAIN |
| sporeGate | 1871544996 | .3:21118 | EYE + EAR |
| northGate | ? | .147:21118 | HEART + CHAIR |
| ironGate | pending | .237:21118 | FORGE 2 |
| deckGate | ? | .161 | DISPLAY |
| Pixel | — | .166 | DIAMOND LENS |

## Relay
- Host: 192.168.4.244
- HBBS: :21116 (rendezvous)
- HBBR: :21117 (relay)
- Direct: :21118 (P2P)
- Key: NULL (LAN trust)

## Setup
```bash
cp northgate-rustdesk-config.toml ~/.config/rustdesk/RustDesk2.toml
rustdesk --password <PIN>  # runtime only
sudo systemctl restart rustdesk
```
