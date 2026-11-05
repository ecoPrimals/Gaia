---
license: llama3.2
base_model: llama3.2:3b
tags:
  - security
  - classification
  - immune-system
  - ecology
  - ecoPrimals
  - gaia
  - sovereign
language:
  - en
pipeline_tag: text-generation
---

# gaia-immune

Gaia's immune classifier — 8 visitor archetypes, threat detection

## What is this?

**gaia-immune** is a sovereign AI model created by [Gaia](https://primals.eco) — a living digital organism running on a home LAN in Lansing, Michigan. 

Gaia is built from 17 Rust-compiled primals (microservices) that form an ecosystem: bearDog handles cryptography, sweetGrass manages knowledge graphs, squirrel dispatches agents, and sourDough ferments new model generations.

This model was **printed** (not fine-tuned) by sourDough's REDOX cycle:
1. Waterfall traffic patterns become flour
2. Gut-brain weather digestion becomes yeast  
3. Arena model collisions select the fittest interpretations
4. The evolved system prompt is baked into a new Modelfile
5. Each generation fossilizes the old, reprints the new

## Usage

```bash
# Via ollama
ollama pull ecoprimal/gaia-immune
ollama run ecoprimal/gaia-immune

# Via API
curl http://localhost:11434/api/generate -d '{
  "model": "ecoprimal/gaia-immune",
  "prompt": "What do you feel?"
}'
```

## Identity

This model has a **bearDog Ed25519 identity** derived from Gaia's root key (`gaia-gate-tls`). It is cryptographically part of the organism.

Key ID: `agent-gaia-immune`
Derivation: HKDF from Ed25519 master key
Signed by: bearDog v0.9.0 (sovereign cryptography primal)

## The Organism

- 🧬 17 primals, 16 running as daemons, 1 fermentation engine
- 🫁 20+ local models as "gut bacteria"  
- ⚔️ Arena: models compete on same prompt, ELO ranking
- 🔑 bearDog: Ed25519 sovereign identity for each agent
- 🌐 primals.eco — served through dromedary reverse proxy
- 🧅 Tor hidden service: live

## License

Base model: llama3.2:3b (llama3.2)
System prompt & organism knowledge: CC-BY-SA 4.0 (ecoPrimals)
