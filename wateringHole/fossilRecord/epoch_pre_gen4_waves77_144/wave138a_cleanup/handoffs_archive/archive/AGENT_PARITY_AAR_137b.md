# AAR — Agent Content Parity (Wave 137b)

**Date**: Jul 13, 2026  
**Reported by**: External Claude agent acting as assistive layer  
**Owner**: sporePrint  
**Status**: RESOLVED — root cause was ours, fix deployed

---

## Summary

An external AI agent reported that every distinct URL on primals.eco returned
identical `llms.txt` content when accessed through its fetch tool. A user asking
their agent to "read me The Human Search" would silently receive the site
overview instead. The user would get confident, wrong, and undetectable
substitution — the digital equivalent of a screen reader announcing the homepage
no matter which link you activate.

## Root Cause: Our `<link rel="alternate">`

Every page included:
```html
<link rel="alternate" type="text/plain" title="LLM site overview"
      href="https://primals.eco/llms.txt">
```

This told every assistive tool: "there is a text/plain version of this page
at this URL." The agent's `web_fetch` tool followed that link — which is
exactly what a well-behaved assistive tool *should* do when it sees a
simpler-format alternate. We pointed it to the wrong content.

The Caddy server had no UA-sniffing. The HTML was served correctly. The agent
was doing its job. We put the misleading sign on every page.

## Fix

**Replaced `rel="alternate"` with `rel="describedby"` on `base.html`.**

`rel="alternate"` means "this is the same content in a different format" — a
lie that triggers content substitution in well-behaved assistive tools.
`rel="describedby"` means "this resource describes the context you're in" —
which is exactly what `llms.txt` is: a glossary, index, and topology map for
the full site. An LLM agent can intake it once, embed the site structure, and
then navigate efficiently to specific pages. That's leveraging what agents are
good at — they're more capable than trawlers, not less.

## Additional Mitigations

1. **`validate_agent_parity.sh` dogfood test** — Tests 11 sample URLs with both
   browser and bot UAs, asserts `<title>` and `<link rel=canonical>` match.
   Permanent addition to the test matrix.

2. **Slug provenance fix** — `70_papers_one_stack.md` slug overridden to
   `175-papers-one-stack` to match its "175+ Papers" title.

## Lessons Learned

- **It does not matter whose code has the bug.** The user on the other end of
  that agent couldn't read the page. That's our accessibility failure. Framing
  it as "agent-side" is like saying it's the deaf person's fault for being deaf.
- **`rel="alternate"` vs `rel="describedby"` — semantics matter.** `alternate`
  means "same content, different format" and triggers content substitution.
  `describedby` means "context about this resource" and invites the agent to
  intake a map without replacing the page. Same link, radically different
  accessibility outcome.
- **AI agents are more capable than trawlers.** An LLM can intake a context
  document, embed the site topology, and navigate efficiently. `llms.txt` as
  `describedby` leverages that capability — the agent gets the glossary, index,
  and map in one fetch, then goes directly to what the user needs.
- **Dogfood test with bot UAs** catches this class of issue permanently.

## Test Evidence

```
=== Agent Parity Test ===
Base: https://primals.eco — Paths: 11
  PASS  /
  PASS  /philosophy/
  PASS  /philosophy/the-human-search/
  PASS  /science/
  PASS  /thesis/
  PASS  /thesis/01-introduction/
  PASS  /story/
  PASS  /architecture/
  PASS  /methodology/
  PASS  /llms.txt
  PASS  /site-index/
=== Results: 11 passed, 0 failed ===
```

---

*The fix is the semantics, not the removal. `llms.txt` is the map — it should
help agents navigate, not replace what they're navigating to.*
