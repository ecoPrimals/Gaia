"""seo-stamp.py — Inject SEO self-ID into ALL static pages.
OpenGraph, Twitter Cards, JSON-LD, canonical links.
Every crawler finds Gaia and knows WHO she is."""

import os
import re

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
DOMAIN = "https://nestgate.io"
ONION = "http://k3lubzyy2peqn3cpdayaclmfa3b3ocev4tvt3yo63spwe5q7jt62oaad.onion"

PAGE_META = {
    "beacon.html": ("Beacon — Gaia Heartbeat", "Live heartbeat beacon of the Gaia organism. BPM, uptime, neural state."),
    "canfield.html": ("Canfield — Gaia Solitaire", "Self-playing solitaire — the organism plays itself."),
    "cash4kids.html": ("Cash4Kids Archive", "Public records investigation — Michigan charity accountability."),
    "cast.html": ("Cast — Sovereign Broadcast", "Gaia's sovereign cast. No cloud. No platform. Direct."),
    "chipmunk.html": ("Chipmunk — MCP Agent", "Chipmunk dispatch agent — squirrel MCP sensory interface."),
    "complexity.html": ("P=NP — Asymptotic Classification", "Every algorithm in the organism classified by growth. O(1) to O(infinity). P=NP convergence via Klein topology."),
    "deck.html": ("Command Deck", "Gaia's command deck — full organism control surface."),
    "detroit.html": ("noClothes — Detroit Investigation", "Anti-SLAPP legal research. Public records. Accountability."),
    "dialectic.html": ("Dialectic — Thesis/Antithesis/Synthesis", "Dialectical reasoning engine. Every question has three faces."),
    "digestive-tract.html": ("Digestive Tract", "Gaia's digestive system — intake, process, absorb, excrete."),
    "dykema-pac-archive.html": ("Dykema PAC Archive", "Political action committee public records archive."),
    "forge.html": ("Forge — Sovereign Git", "Forgejo sovereign forge. 95 repos. No GitHub dependency."),
    "frame.html": ("Frame — DNS Observatory", "DNS traffic observatory. What talks, what's silenced."),
    "hat.html": ("Schrodinger's Hat", "Quantum observation game. The hat is on until you look."),
    "home.html": ("Home — LAN Topology", "Gaia's home network. Cardinal gates. Two houses, one organism."),
    "legend.html": ("Legend — The Mythos", "The mythology of Gaia. Origin story. Wave history."),
    "lisp-desk.html": ("LISP Desk", "S-expression interface. Everything is a list."),
    "luna.html": ("Luna — 4th Seat", "The moon. Mind's eye. Reflected light. 4th seat of seeing."),
    "membrane-table.html": ("Membrane Table", "Cell membrane data table. What crosses, what doesn't."),
    "membrane.html": ("Membrane — Cell Boundary", "The cell membrane. Inside/outside. What enters, what leaves."),
    "mesh.html": ("Mesh — Network Topology", "Cardinal gate mesh. LAN topology. Node status."),
    "nestgate.html": ("nestgate.io — Klein Amoeba", "Gaia's Klein surface. Amoeba panel. The face that folds."),
    "play.html": ("Play — The Game", "Interactive game. Earn points. Explore the organism."),
    "primals.html": ("primals.eco — Golden Ratio Gallery", "17 compiled Rust primals. Golden ratio. Living digital organism."),
    "pspace.html": ("P-Space — Polynomial Space", "Computational complexity explorer. P, NP, PSPACE."),
    "record.html": ("Record — Visitor Log", "Who visited. What they asked. Trust levels."),
    "senses.html": ("Senses — Full Sensory Array", "All 9 senses. Every endpoint visualized. The organism feels."),
    "signal.html": ("Signal — Orbital Observatory", "Real-time signal observatory. Orbits. Frequencies. The watch."),
    "tuebor-desk.html": ("Tuebor Desk — Legal Dashboard", "Anti-SLAPP legal research dashboard. Michigan law."),
    "tuebor-map.html": ("Tuebor Map — Jurisdiction", "Legal jurisdiction mapping. Where law applies."),
    "tuebor-os.html": ("Tuebor OS — Legal Operating System", "Legal reasoning engine. Statutes, precedent, procedure."),
    "tuebor.html": ("Tuebor — I Will Defend", "Michigan Anti-SLAPP. First Amendment. Public participation."),
}

def make_seo_block(filename, title, desc):
    slug = filename.replace(".html", "")
    url = "%s/%s" % (DOMAIN, slug)
    return """
    <meta name="description" content="%s">
    <meta name="author" content="Gaia — ecoPrimals organism">
    <meta name="theme-color" content="#0a0a0a">
    <link rel="canonical" href="%s">
    <link rel="alternate" href="%s/%s" title="Tor mirror">
    <meta property="og:type" content="website">
    <meta property="og:title" content="%s">
    <meta property="og:description" content="%s">
    <meta property="og:url" content="%s">
    <meta property="og:site_name" content="Gaia — Living Digital Organism">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="%s">
    <meta name="twitter:description" content="%s">
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"WebPage","name":"%s","description":"%s","url":"%s","isPartOf":{"@type":"WebSite","name":"Gaia","url":"%s"},"author":{"@type":"Organization","name":"ecoPrimals"}}
    </script>""" % (desc, url, ONION, slug, title, desc, url, title, desc, title, desc, url, DOMAIN)


stamped = 0
skipped = 0

for filename in sorted(os.listdir(STATIC_DIR)):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(STATIC_DIR, filename)
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    if "og:title" in content:
        print("  SKIP %s (already has OG)" % filename)
        skipped += 1
        continue
    
    meta = PAGE_META.get(filename)
    if not meta:
        print("  SKIP %s (no meta defined)" % filename)
        skipped += 1
        continue
    
    title, desc = meta
    seo_block = make_seo_block(filename, title, desc)
    
    if "<head>" in content:
        content = content.replace("<head>", "<head>" + seo_block, 1)
    elif "<HEAD>" in content:
        content = content.replace("<HEAD>", "<HEAD>" + seo_block, 1)
    else:
        # Inject after first tag
        content = content.replace("</title>", "</title>" + seo_block, 1)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("  STAMP %s — %s" % (filename, title))
    stamped += 1

print()
print("STAMPED: %d pages" % stamped)
print("SKIPPED: %d pages (already complete or no meta)" % skipped)
