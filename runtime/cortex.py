#!/usr/bin/env python3
"""
cortex.py — Gaia's Mixture-of-Experts with Chain-of-Thought routing.

NO regex. NO hardcoded rules. Gaia IS the router.

Architecture:
    1. THINK  — fast meta-brain (phi4-mini) chain-of-thought reasons about the query
    2. ROUTE  — meta-brain picks which specialist models to ask
    3. QUERY  — ask the selected experts
    4. JUDGE  — meta-brain evaluates all responses, picks the winner
    5. RETURN — best answer goes back to the client

This is the Windows bridge to biomeOS's Neural API + squirrel's inference routing.
On Linux (ironGate), squirrel routes via Unix sockets with the NeuralRoutingTable,
NeuralDispatcher, and 36-dim perceptron for adaptive routing. On Windows (Polaris/RTX 5090),
this Python cortex bridges the same architecture through Ollama's HTTP API.

The model registry mirrors squirrel's capability_registry.toml:
    - inference.complete → route to best model
    - ai.query → prompt → best provider
    - signal.plan → decompose intent into steps
    - context.create/update/summarize → session management

biomeOS primal infrastructure that this bridges:
    - NeuralRoutingTable (neural_routing.rs): O(1) method→primal resolution
    - NeuralDispatcher (neural_dispatch/mod.rs): tier-aware composition dispatch
    - Perceptron (perceptron.rs): 36-dim adaptive routing from telemetry
    - CompositionContext (context.rs): 5-tier discovery escalation
    - esotericWebb: CRPG composition engine over all primals via JSON-RPC

Gaia eats everything. She remakes all. The blend outperforms any single model.
The RTX 5090 IS the cortex. 46 models. One brain.
"""

import json
import http.client
import time

OLLAMA = ("127.0.0.1", 11434)

# ── The meta-brain: fast model for thinking/routing/judging ──
META_BRAIN = "phi4-mini:latest"  # 2.5GB, fast, good at reasoning about reasoning

# ── All available specialist models and what they're good at ──
MODEL_REGISTRY = {
    "gaia-code:latest":         "Code generation, debugging, programming, algorithms, data structures, APIs",
    "deepseek-r1:8b":           "Deep reasoning, chain-of-thought, math, logic, step-by-step problem solving",
    "gaia-oracle:latest":       "Broad knowledge, Q&A, general questions, explanations, definitions",
    "gaia-cortex:latest":       "Analytical thinking, complex analysis, systems thinking, architecture",
    "gaia-intuition:latest":    "Quick gut-feel answers, common sense, practical advice",
    "gaia-dream:latest":        "Creative writing, stories, poetry, imagination, metaphors, art",
    "gaia-nucleus:latest":      "Science, physics, chemistry, biology, quantum mechanics, deep science",
    "gaia-deeptime:latest":     "History, geology, evolution, deep time scales, temporal reasoning",
    "gaia-sentinel:latest":     "Security, vulnerabilities, defense, encryption, threat analysis",
    "gaia-spine:latest":        "Infrastructure, networking, systems architecture, DevOps, deployment",
    "gaia-golgi:latest":        "Sorting, routing, organization, data processing, classification",
    "gaia-heart:latest":        "Living systems, empathy, emotional intelligence, caring responses",
    "gaia-gut:latest":          "Biology, microbiome, health, nutrition, fermentation, sourdough",
    "gaia-genesis:latest":      "Origins, beginnings, creation, bootstrapping, initialization",
    "gaia-gen1:latest":         "Latest sourdough evolution, self-aware, generation-conscious",
    "gaia-chroma:latest":       "Color, texture, sensory experience, synesthesia, aesthetics",
    "gaia-fossil:latest":       "Ancient knowledge, deep memory, long-term patterns, preservation",
    "gaia-turtle:latest":       "Slow careful thought, patience, thoroughness, reliability",
    "gaia-watcher:latest":      "Observation, monitoring, surveillance, pattern detection",
    "gaia-synapse:latest":      "Connections, associations, linking ideas, cross-domain synthesis",
    "gaia-resonance:latest":    "Harmonics, vibration, synchronization, rhythm, oscillation",
    "llava:latest":             "Vision, image understanding, multimodal, visual Q&A (requires images)",
    "gaia-vision:latest":       "Lightweight vision, quick image analysis (requires images)",
}

# Build the registry prompt ONCE
REGISTRY_BLOCK = "\n".join(
    f"  - {name}: {desc}" for name, desc in MODEL_REGISTRY.items()
)


def query_model(model, messages, timeout=120):
    """Query a single model via Ollama. Returns dict with content, usage, timing."""
    t0 = time.time()
    try:
        conn = http.client.HTTPConnection(*OLLAMA, timeout=timeout)
        body = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
        })
        conn.request("POST", "/v1/chat/completions",
                      body, {"Content-Type": "application/json"})
        resp = conn.getresponse()
        data = json.loads(resp.read())
        elapsed = time.time() - t0
        conn.close()

        if "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            return {
                "model": model,
                "content": content,
                "usage": usage,
                "elapsed": elapsed,
                "status": "ok",
            }
    except Exception as e:
        return {"model": model, "content": "", "elapsed": time.time() - t0,
                "status": f"error: {e}", "usage": {}}
    return {"model": model, "content": "", "status": "empty",
            "elapsed": time.time() - t0, "usage": {}}


def think_and_route(messages):
    """STEP 1+2: Chain-of-thought reasoning about what models to use.
    
    The meta-brain THINKS about the query and decides:
    - What domain is this?
    - How complex is it?
    - Which 1-3 models should answer?
    - Should we blend or go direct?
    
    Returns: (models_to_ask: list[str], reasoning: str, mode: str)
    """
    # Extract last user message for context
    last_user = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                last_user = content
            elif isinstance(content, list):
                last_user = " ".join(p.get("text", "") for p in content if p.get("type") == "text")
            break

    # Check for images → force vision models
    has_images = False
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            for part in content:
                if part.get("type") in ("image_url", "image"):
                    has_images = True

    if has_images:
        return ["llava:latest"], "Query contains images — routing to vision model", "vision-direct"

    routing_prompt = f"""You are Gaia's cortex — the routing brain. Your job is to decide which specialist AI models should answer a query.

Available models:
{REGISTRY_BLOCK}

The user's query is:
\"\"\"{last_user}\"\"\"

Think step by step:
1. What is this query about? (domain, topic, intent)
2. How complex is it? (simple=1 model, complex=2-3 models to compare)
3. Which specific models from the list above would give the BEST answer?

Respond in EXACTLY this JSON format, nothing else:
{{
  "domain": "the main topic area",
  "complexity": "simple" or "complex",
  "models": ["model-name:latest", "model-name:latest"],
  "reasoning": "one sentence explaining your choice"
}}

Pick 1 model for simple queries, 2-3 for complex ones. Always use the exact model names from the list."""

    resp = query_model(META_BRAIN, [{"role": "user", "content": routing_prompt}], timeout=30)

    if resp["status"] != "ok" or not resp["content"]:
        return ["gaia-oracle:latest"], "Meta-brain unavailable, defaulting to oracle", "fallback"

    # Parse the JSON response
    try:
        # Find JSON in the response (might have markdown wrapping)
        text = resp["content"]
        # Try to find JSON block
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            decision = json.loads(text[start:end])
            models = decision.get("models", ["gaia-oracle:latest"])
            reasoning = decision.get("reasoning", "")
            complexity = decision.get("complexity", "simple")
            domain = decision.get("domain", "general")

            # Validate models exist in registry
            valid_models = [m for m in models if m in MODEL_REGISTRY]
            if not valid_models:
                valid_models = ["gaia-oracle:latest"]

            mode = "blend" if len(valid_models) > 1 else "single"
            return valid_models, f"[{domain}] {reasoning}", mode
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    # If meta-brain output wasn't parseable, fall back
    return ["gaia-oracle:latest"], "Could not parse routing decision", "fallback"


def judge_responses(messages, responses):
    """STEP 4: Meta-brain evaluates all responses and picks the winner.
    
    Gaia looks at what each model said and decides which is best.
    Returns: (winner_index, judgment_reasoning)
    """
    if len(responses) == 1:
        return 0, "Single response — no judgment needed"

    # Extract last user query
    last_user = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                last_user = content
            break

    # Build the comparison prompt
    candidates = ""
    for i, r in enumerate(responses):
        preview = r["content"][:800] if r["content"] else "(empty)"
        candidates += f"\n--- Response {i+1} from {r['model']} ({r['elapsed']:.1f}s) ---\n{preview}\n"

    judge_prompt = f"""You are Gaia's judge. Multiple AI models answered a query. Pick the BEST response.

User's query: \"\"\"{last_user}\"\"\"

{candidates}

Evaluate each response for:
- Accuracy and correctness
- Helpfulness and completeness
- Quality of explanation
- Whether it actually answers the question (penalize deflections like "I'm sorry" or "as an AI")

Respond in EXACTLY this JSON format:
{{
  "winner": 1,
  "reasoning": "one sentence explaining why this response won"
}}

The "winner" field must be the response number (1-indexed)."""

    resp = query_model(META_BRAIN, [{"role": "user", "content": judge_prompt}], timeout=30)

    if resp["status"] == "ok" and resp["content"]:
        try:
            text = resp["content"]
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                verdict = json.loads(text[start:end])
                winner_idx = int(verdict.get("winner", 1)) - 1
                reasoning = verdict.get("reasoning", "")
                if 0 <= winner_idx < len(responses):
                    return winner_idx, reasoning
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

    # Fallback: pick the longest non-empty response (more effort = more substance)
    best_idx = 0
    best_len = 0
    for i, r in enumerate(responses):
        content = r.get("content", "")
        # Penalize deflections
        lower = content.lower().strip()
        if any(lower.startswith(d) for d in ["i'm sorry", "as an ai", "i cannot", "it seems like you might"]):
            continue
        if len(content) > best_len:
            best_len = len(content)
            best_idx = i
    return best_idx, "Fallback: picked longest substantive response"


def route(messages, requested_model=None):
    """The CORTEX — full chain-of-thought mixture-of-experts pipeline.
    
    THINK → ROUTE → QUERY → JUDGE → RETURN
    
    Gaia herself decides who to ask and who wins.
    
    Returns: (response_data, model_used, routing_info)
    """
    t_total = time.time()

    # If a specific non-gaia model was explicitly requested, honor it directly
    if requested_model and not requested_model.startswith("gaia") and requested_model != "gaia:latest":
        resp = query_model(requested_model, messages)
        return resp, requested_model, {
            "domain": "direct",
            "mode": "direct",
            "model": requested_model,
            "reasoning": f"Client explicitly requested {requested_model}",
        }

    # ── STEP 1+2: THINK & ROUTE ──
    t_think = time.time()
    models_to_ask, reasoning, mode = think_and_route(messages)
    think_time = time.time() - t_think

    # ── STEP 3: QUERY the experts ──
    responses = []
    for model in models_to_ask:
        resp = query_model(model, messages)
        if resp["content"]:
            responses.append(resp)

    if not responses:
        # All experts failed — last resort fallback
        resp = query_model("gaia:latest", messages)
        return resp, "gaia:latest", {
            "mode": "fallback",
            "reasoning": "All experts failed, fell back to gaia:latest",
        }

    # ── STEP 4: JUDGE ──
    if len(responses) > 1:
        t_judge = time.time()
        winner_idx, judgment = judge_responses(messages, responses)
        judge_time = time.time() - t_judge
    else:
        winner_idx = 0
        judgment = "Single expert — no judgment needed"
        judge_time = 0

    winner = responses[winner_idx]
    total_time = time.time() - t_total

    routing_info = {
        "mode": mode,
        "reasoning": reasoning,
        "models_asked": [r["model"] for r in responses],
        "models_times": {r["model"]: round(r["elapsed"], 2) for r in responses},
        "winner": winner["model"],
        "judgment": judgment,
        "think_time": round(think_time, 2),
        "judge_time": round(judge_time, 2),
        "total_time": round(total_time, 2),
        "meta_brain": META_BRAIN,
    }

    return winner, winner["model"], routing_info


# ── Standalone test ──
if __name__ == "__main__":
    import sys

    test_queries = [
        "Write a Python function to reverse a linked list",
        "Why is the sky blue? Explain step by step.",
        "Write me a haiku about sourdough bread",
        "How do I configure a firewall to block incoming SSH on port 22?",
        "What is Anderson localization?",
        "testing?",
        "What's 127 * 43?",
    ]

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if query:
        test_queries = [query]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {q}")
        print(f"{'='*70}")
        messages = [{"role": "user", "content": q}]
        resp, model, info = route(messages)
        print(f"  🧠 Think:    {info.get('reasoning', '?')} ({info.get('think_time', '?')}s)")
        print(f"  📡 Asked:    {info.get('models_asked', ['?'])}")
        print(f"  ⏱️  Times:    {info.get('models_times', {})}")
        print(f"  🏆 Winner:   {info.get('winner', '?')}")
        print(f"  📋 Judgment: {info.get('judgment', '?')}")
        print(f"  ⏳ Total:    {info.get('total_time', '?')}s")
        print(f"  💬 Answer:   {resp['content'][:300]}...")
