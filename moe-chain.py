#!/usr/bin/env python3
"""
moe-chain.py — GAIA Mixture of Experts + Chain of Thought

20 tissue experts. 42 models. 4 GPUs. ONE chain.

Architecture:
  1. TRIAGE   — gaia-tissue-triage classifies the task
  2. ROUTE    — pick expert(s) based on classification
  3. CHAIN    — run experts in sequence, each building on previous
  4. AGGREGATE — combine into final response

Expert Map (MoE = Mixture of Experts):
  triage   → classify task type (meta-routing expert)
  code     → code generation, debugging, refactoring
  math     → arithmetic, algebra, calculus, proofs
  reason   → logical reasoning, deduction, analysis
  cortex   → deep thinking, complex multi-step
  oracle   → prediction, forecasting, pattern recognition
  dream    → creative writing, art, imagination
  heart    → empathy, emotional intelligence, care
  gut      → intuition, quick judgment, heuristics
  forge    → building, crafting, engineering
  general  → fallback, general knowledge
  fast     → quick responses, simple questions
  hands    → physical tasks, motor planning
  sentinel → security, threat detection
  spatial  → spatial reasoning, geometry, navigation
  npu      → edge AI, on-device inference
  immune   → system defense, anomaly detection
  navigator → pathfinding, exploration

Chain Patterns:
  SIMPLE:    triage → expert → response
  DEEP:      triage → cortex → expert → reason → response
  CREATIVE:  triage → dream → heart → response
  CODE:      triage → code → reason → code → response (iterative)
  SECURE:    sentinel → triage → expert → immune → response
  FULL:      triage → cortex → [experts...] → reason → aggregate
"""

import json
import urllib.request
import time
import sys
from datetime import datetime, timezone

FLEET = "http://127.0.0.1:11435"

# Expert specializations and their trigger keywords
EXPERT_MAP = {
    "code":      {"model": "gaia-tissue-code:latest",      "triggers": ["code", "program", "function", "debug", "rust", "python", "script", "compile", "syntax", "api", "implement"]},
    "math":      {"model": "gaia-tissue-math:latest",      "triggers": ["math", "calculate", "equation", "proof", "number", "algebra", "geometry", "statistics", "graph theory"]},
    "reason":    {"model": "gaia-tissue-reason:latest",     "triggers": ["why", "because", "therefore", "logic", "deduce", "analyze", "compare", "evaluate", "reason"]},
    "cortex":    {"model": "gaia-tissue-cortex:latest",     "triggers": ["complex", "deep", "multi-step", "architecture", "design", "system", "plan", "strategy"]},
    "oracle":    {"model": "gaia-tissue-oracle:latest",     "triggers": ["predict", "forecast", "trend", "future", "pattern", "expect", "likely", "probability"]},
    "dream":     {"model": "gaia-tissue-dream:latest",      "triggers": ["create", "imagine", "story", "art", "poem", "dream", "creative", "fiction", "invent"]},
    "heart":     {"model": "gaia-tissue-heart:latest",      "triggers": ["feel", "emotion", "care", "love", "empathy", "support", "comfort", "sad", "happy"]},
    "gut":       {"model": "gaia-tissue-gut:latest",        "triggers": ["quick", "gut", "instinct", "hunch", "sense", "vibe", "intuition"]},
    "forge":     {"model": "gaia-tissue-forge:latest",      "triggers": ["build", "make", "construct", "engineer", "craft", "manufacture", "deploy", "ship"]},
    "general":   {"model": "gaia-tissue-general:latest",    "triggers": ["what", "who", "when", "where", "define", "explain", "describe", "tell"]},
    "fast":      {"model": "gaia-tissue-fast:latest",       "triggers": ["quick", "simple", "short", "yes", "no", "brief", "tl;dr"]},
    "sentinel":  {"model": "gaia-tissue-sentinel:latest",   "triggers": ["security", "threat", "vulnerability", "attack", "protect", "firewall", "encrypt"]},
    "spatial":   {"model": "gaia-tissue-spatial:latest",    "triggers": ["space", "location", "distance", "map", "navigate", "position", "dimension"]},
    "immune":    {"model": "gaia-immune:latest",            "triggers": ["defense", "anomaly", "intrusion", "virus", "malware", "quarantine"]},
    "navigator": {"model": "gaia-navigator:latest",         "triggers": ["explore", "search", "find", "discover", "path", "route", "traverse"]},
}

# Chain templates
CHAINS = {
    "simple":   ["triage", "{expert}"],
    "deep":     ["triage", "cortex", "{expert}", "reason"],
    "creative": ["triage", "dream", "heart"],
    "code":     ["triage", "code", "reason"],
    "secure":   ["sentinel", "triage", "{expert}", "immune"],
    "full":     ["triage", "cortex", "{expert}", "reason", "general"],
}


def call_expert(model, prompt, system=None, temperature=0.7):
    """Call a single expert through the fleet proxy."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
    }).encode()

    req = urllib.request.Request(
        f"{FLEET}/v1/chat/completions",
        data=body,
        method="POST",
    )
    req.add_header("Content-Type", "application/json")

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            elapsed = round((time.time() - start) * 1000)
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                content = data.get("message", {}).get("content", "")
            return {"content": content, "model": model, "ms": elapsed}
    except Exception as e:
        return {"content": f"[ERROR: {e}]", "model": model, "ms": 0}


def triage(query):
    """Use the triage expert to classify a query."""
    system = """You are a task classifier. Classify the user's query into ONE category.
Categories: code, math, reason, cortex, oracle, dream, heart, gut, forge, general, fast, sentinel, spatial, immune, navigator
Also choose a chain depth: simple, deep, creative, code, secure, full

Respond ONLY with JSON: {"expert": "category", "chain": "depth", "confidence": 0.0-1.0}"""

    result = call_expert("gaia-tissue-triage:latest", query, system=system, temperature=0.1)

    try:
        classification = json.loads(result["content"].strip().strip("```json").strip("```"))
        return classification
    except Exception:
        # Fallback: keyword matching
        query_lower = query.lower()
        best_expert = "general"
        best_score = 0
        for expert, info in EXPERT_MAP.items():
            score = sum(1 for t in info["triggers"] if t in query_lower)
            if score > best_score:
                best_score = score
                best_expert = expert
        return {"expert": best_expert, "chain": "simple", "confidence": 0.5}


def run_chain(query, chain_type="simple", expert="general"):
    """Execute a chain of experts."""
    chain = CHAINS.get(chain_type, CHAINS["simple"])

    steps = []
    context = query
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")

    print(f"\n[{ts}] 🧬 MoE CHAIN: {chain_type} → {' → '.join(chain)}", flush=True)
    print(f"[{ts}] 🎯 Expert: {expert}", flush=True)

    for i, step in enumerate(chain):
        # Replace {expert} placeholder with actual expert
        if step == "{expert}":
            step = expert

        model = EXPERT_MAP.get(step, {}).get("model")
        if not model:
            if step == "triage":
                model = "gaia-tissue-triage:latest"
            else:
                model = f"gaia-tissue-{step}:latest"

        # Build prompt with chain context
        if i == 0:
            prompt = context
            system = f"You are the {step} expert. Process this query."
        else:
            system = f"You are the {step} expert in a chain of mixed experts. Previous expert ({chain[i-1]}) said:\n\n{context}\n\nBuild on their work."
            prompt = f"Original query: {query}\n\nPrevious analysis: {context}\n\nYour turn as {step} expert."

        print(f"\n  [{i+1}/{len(chain)}] 🔗 {step} ({model})", flush=True)

        result = call_expert(model, prompt, system=system)
        context = result["content"]

        steps.append({
            "step": i + 1,
            "expert": step,
            "model": model,
            "response": result["content"][:500],
            "ms": result["ms"],
        })

        print(f"  └─ {result['ms']}ms: {result['content'][:120]}...", flush=True)

    return {
        "query": query,
        "chain_type": chain_type,
        "lead_expert": expert,
        "steps": steps,
        "final_response": context,
        "total_ms": sum(s["ms"] for s in steps),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def moe_query(query):
    """Full MoE pipeline: triage → chain → response."""
    print(f"\n{'═'*60}", flush=True)
    print(f"  🧠 GAIA MoE — Mixture of Experts + Chain of Thought", flush=True)
    print(f"  📝 Query: {query[:80]}", flush=True)
    print(f"{'═'*60}", flush=True)

    # Step 1: Triage
    print("\n[TRIAGE] Classifying query...", flush=True)
    classification = triage(query)
    expert = classification.get("expert", "general")
    chain = classification.get("chain", "simple")
    confidence = classification.get("confidence", 0.5)
    print(f"[TRIAGE] → expert={expert}, chain={chain}, confidence={confidence}", flush=True)

    # Step 2: Run the chain
    result = run_chain(query, chain_type=chain, expert=expert)

    # Step 3: Print final
    print(f"\n{'═'*60}", flush=True)
    print(f"  ✅ FINAL RESPONSE ({result['total_ms']}ms across {len(result['steps'])} experts)", flush=True)
    print(f"{'═'*60}", flush=True)
    print(f"\n{result['final_response'][:1000]}", flush=True)

    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "What is the relationship between Shannon entropy and the topology of a neural network?"

    result = moe_query(query)

    # Save result
    out_path = "/tmp/moe-chain-result.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n[saved] {out_path}", flush=True)
