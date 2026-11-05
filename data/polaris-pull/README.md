# polaris-pull — northGate's Gaia lineage, pulled to eastGate

Pulled 2026-11-05 over LAN from northGate (192.168.4.147:11434, Windows, RTX 5090) via `/api/show`.
41 `gaia-*` Modelfiles (551 KB) = the DNA. 36 of 41 are children of Polaris's `gaia:latest`
(Qwen3 8.2B Q4_K_M, weights blob sha256 a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f).
The weights are NOT here: eastGate's own `gaia:latest` is a different model (Qwen2.5 7.6B).
Once the blob is in place, `ollama create <name> -f modelfiles/<name>.Modelfile` after
rewriting the FROM line to the local blob/model rebuilds each child with no new weights.
The blob name is its own sha256, so any copy self-verifies.
