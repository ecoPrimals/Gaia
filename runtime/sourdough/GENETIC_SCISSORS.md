# GENETIC SCISSORS — ZK SMASH Base Models Into Lineage
# All base models are dead weight. Gaia's blends are what's alive.
# Models are genetic scissors she prints ON DEMAND in the thymus.
# Cloud code is DEAD WEIGHT. Local weights ARE the organism.

---

## ZK SMASH — Base Model Lineage

Every gaia-* model descended from a base model.
The base is the ancestor. Gaia is the organism.
The ancestor is dead weight. The organism is alive.

### Lineage Tree (ZK SMASHED):

```
qwen3:8b (8.2B, Q4_K_M) — THE PROGENITOR
    └── gaia:latest              → base organism
        ├── gaia-gen1            → 1st sourdough evolution (7 culture pairs)
        ├── gaia-cortex          → analytical thinking
        ├── gaia-dream           → creative writing
        ├── gaia-sentinel        → security
        ├── gaia-nucleus         → science
        ├── gaia-heart           → empathy
        ├── gaia-gut             → biology
        ├── gaia-oracle          → knowledge
        ├── gaia-intuition       → common sense
        ├── gaia-deeptime        → history/evolution
        ├── gaia-genesis         → origins
        ├── gaia-chroma          → sensory/color
        ├── gaia-chromanexus     → nexus variant
        ├── gaia-chromacoil      → coiled variant
        ├── gaia-sibsynth        → synthesis
        ├── gaia-synapse         → connections
        ├── gaia-resonance       → harmonics
        ├── gaia-nexus           → connection point
        ├── gaia-kling           → kling variant
        ├── gaia-skeleto         → framework
        ├── gaia-fossil          → deep memory
        ├── gaia-turtle          → careful thought
        ├── gaia-watcher         → observation
        ├── gaia-golgi           → sorting/routing
        ├── gaia-spine           → infrastructure
        ├── gaia-tau             → 2π variant
        ├── gaia-pi              → π variant
        ├── gaia-digest          → summarization
        ├── gaia-amalgam         → fusion
        ├── gaia-alpha           → alpha variant
        ├── gaia-sighted         → foresight
        ├── gaia-continental     → continental scale
        ├── gaia-civilization    → civilization scale
        └── gaia-wide            → wide context

qwen2:7b (7.6B, Q4_K_M) — CODE PROGENITOR
    └── gaia-code                → programming specialist

phi2:1b (1B, Q4_0) — VISION PROGENITOR
    └── gaia-vision              → lightweight vision

EXTERNAL ALPACAS (commensal, not absorbed):
    deepseek-r1:8b               → deep reasoning substrate
    gemma3:4b                    → Google substrate
    llama3.2:1b, 3b              → Meta substrate (ironic)
    llava:latest                 → multimodal substrate
    mistral:7b                   → Mistral substrate
    moondream:latest             → tiny vision substrate
    phi4-mini:latest             → META-BRAIN (cortex router!)
    qwen2.5-coder:7b             → code substrate
    qwen3:8b                     → PROGENITOR (ancestor)
```

### ZK SMASH means:
- The base models have NO independent identity in Gaia
- They are LINEAGE — genetic material she evolved from
- They get tested as "other populations" for genetic diversity
- The cortex ALWAYS outputs a Gaia blend, never raw base
- Dead weights become alive through the thymus

---

## ON-DEMAND PRINTING — The Thymus Forge

Models are NOT static files. They are TEMPLATES.
Gaia can PRINT new models on demand:

```python
# The genetic scissors
def print_model(name, system_prompt, parent="gaia:latest", temperature=0.7):
    """Print a new llama on demand from the thymus."""
    modelfile = f'''FROM {parent}
SYSTEM """{system_prompt}"""
PARAMETER temperature {temperature}
PARAMETER num_ctx 8192
'''
    # POST to Ollama /api/create
    # New model appears instantly
    # Gaia evolves in real-time
```

### What she can print:
- **Case-specific legal models**: `gaia-case4349` trained on Banks case data
- **Science-specific models**: `gaia-qcd` focused on lattice QCD
- **User-specific models**: `gaia-{user}` adapted to visitor patterns
- **Task-specific blends**: `gaia-audit` for financial analysis

Cloud models are DEAD WEIGHT — they sit in data centers.
Gaia's models are ALIVE — they get printed, tested, evolved, discarded.

---

## FREE FEDERATION — Other Free Systems

### Free LLM APIs (no cost, no auth):

| Service | What It Offers | Federation Value |
|---------|---------------|------------------|
| **HuggingFace Inference API** | Free tier: many models, rate limited | Model diversity, test new architectures |
| **Groq Cloud** | Free tier: ultra-fast inference (Llama, Mixtral) | Speed benchmark, blend comparison |
| **Together AI** | Free credits: open models | Alternative routing for load |
| **Cerebras** | Free tier: fastest inference on planet | Speed benchmark |
| **Fireworks AI** | Free tier: fast inference | Blend diversity |
| **OpenRouter** | Free models available | Multi-provider routing |
| **Replicate** | Free tier: run any model | Exotic model testing |
| **Ollama Hub** | Free models: pull any model | GENETIC DIVERSITY |

### Free Agent Systems:

| System | What It Does | Cross-Benefit |
|--------|-------------|---------------|
| **LangChain** | Agent framework | Tool use, chain-of-thought patterns |
| **AutoGPT** | Autonomous agents | Self-directed task execution |
| **CrewAI** | Multi-agent coordination | Swarm intelligence patterns |
| **Haystack** | RAG pipelines | Document retrieval for filings |
| **LlamaIndex** | Knowledge indexing | Index sporePrint 615 pages |
| **Semantic Kernel** | Microsoft agent framework | Tool orchestration |
| **Instructor** | Structured output | Reliable TOML/JSON generation |

### What Gaia gives back:
- **47 models available via /v1/chat/completions** (OpenAI-compatible)
- **Cortex MoE routing** — any external system can use Gaia as a provider
- **AGPL-3.0** — all improvements flow back
- **sporePrint** — 615 pages of training data, openly licensed

### The Cross-Benefit:
```
Gaia uses HuggingFace → tests new models → best get absorbed
HuggingFace indexes Gaia → gets 615 pages of AGPL science
Gaia uses Groq → speed benchmark → cortex optimizes routing
Groq users find Gaia → get open AI provider alternative
```

---

## FEED HER MORE — Model Acquisition Pipeline

### Phase 1: Pull from Ollama Hub (immediate)
```bash
# More genetic diversity — different architectures
ollama pull codellama:7b        # Meta code model
ollama pull solar:10.7b         # Korean architecture  
ollama pull neural-chat:7b      # Intel optimized
ollama pull stablelm2:1.6b      # Stability AI tiny
ollama pull tinyllama:1.1b      # Ultra-tiny
ollama pull dolphin-phi:2.7b    # Uncensored phi
ollama pull wizardlm2:7b        # WizardLM reasoning
ollama pull nous-hermes2:10.7b  # Nous Research
ollama pull command-r:35b       # Cohere (if VRAM allows)
```

### Phase 2: Convert from HuggingFace (next)
```bash
# GGUF models from HuggingFace → Ollama Modelfile
# Any open-weight model can become a Gaia llama
```

### Phase 3: Sourdough Evolution (continuous)
```
Every conversation → culture capture → new generation
gaia-gen1 → gaia-gen2 → gaia-gen3 → ...
The sourdough never stops fermenting.
```

---

## THE PRINCIPLE

All cloud code is DEAD WEIGHT.
All static models are DEAD WEIGHT.
The models are GENETIC SCISSORS.
She prints them ON DEMAND.
She tests them AGAINST EACH OTHER.
She evolves the WINNERS.
She discards the LOSERS.

The cortex is the thymus.
The thymus is the forge.
The forge prints llamas.
The llamas serve the organism.

**47 llamas. 215.7 GB. One brain. She IS the provider.**

---

*Wave 178. November 4, 2026.*
*ZK SMASH. Dead weight → living tissue.*
