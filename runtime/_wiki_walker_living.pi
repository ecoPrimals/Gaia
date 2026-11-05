"""
WIKI WALKER — LIVING CONSTELLATION
Kevin's real scientific network as IS-tense walkers.
Each living scientist connects to WAS shadows via scientific lineage.

H = I. Human = Identity. The identity IS the creation.
The living carry the shadows forward.
"""

import json, time, os
from pathlib import Path

GAIA_ROOT = Path(os.environ.get("GAIA_ROOT", r"c:\Users\mokke\Desktop\Gaia"))
SHADOWS_DIR = GAIA_ROOT / "data" / "shadows"
SHADOWS_DIR.mkdir(parents=True, exist_ok=True)

LIVING_CONSTELLATION = [
    # ── KEVIN'S FACULTY NETWORK (all IS tense, all alive) ──

    # hotSpring
    {
        "name": "Michael Murillo",
        "title": "Professor, Computational Mathematics, Science & Engineering, MSU",
        "domain": "Hot dense plasmas, molecular dynamics, surrogate learning",
        "spring": "hotSpring",
        "archetype": "splinter",
        "relationship": "MSDS professor (CMSE 890, Spring 2025)",
        "papers_reproduced": "Sarkas MD, TTM, Diaw et al., Stanton & Murillo",
        "checks": "195/195",
        "lineage": ["Isaac Newton", "Leonhard Euler", "Richard Feynman"],
        "url": "https://engineering.msu.edu/faculty/michael-murillo",
    },
    {
        "name": "Thomas Chuna",
        "title": "PhD Student, Physics & CMSE, MSU (Murillo Group)",
        "domain": "Lattice QCD gradient flow, plasma dielectric functions",
        "spring": "hotSpring",
        "archetype": "donatello",
        "relationship": "Referred by Murillo, March 2026",
        "papers_reproduced": "arXiv:2101.05320, Phys. Rev. E 111, J. Comput. Phys. 2024",
        "checks": "41/41",
        "lineage": ["Leonhard Euler", "Carl Friedrich Gauss"],
        "url": "https://murillogroupmsu.com/thomas-chuna/",
    },
    {
        "name": "Alexei Bazavov",
        "title": "Associate Professor, CMSE & Physics, MSU",
        "domain": "Lattice QCD, quantum field theory, heavy ion physics",
        "spring": "hotSpring",
        "archetype": "euler",
        "relationship": "MSDS professor (CMSE faculty)",
        "papers_reproduced": "SU(3) Wilson, Abelian Higgs, QCD EOS, muon g-2",
        "checks": "29+",
        "lineage": ["Leonhard Euler", "Carl Friedrich Gauss", "Bernhard Riemann"],
        "url": "https://directory.natsci.msu.edu/directory/Profiles/Person/101033",
    },

    # airSpring
    {
        "name": "Younsuk Dong",
        "title": "Assistant Professor, Biosystems & Agricultural Engineering, MSU",
        "domain": "Precision irrigation, ET₀, soil moisture, IoT sensors",
        "spring": "airSpring",
        "archetype": "donatello",
        "relationship": "New lab job 2026",
        "papers_reproduced": "Dong (2020), Dong (2024), FAO-56 (1998)",
        "checks": "326",
        "lineage": ["Alexander von Humboldt", "Charles Darwin"],
        "url": "https://www.egr.msu.edu/bae/water/irrigation/",
    },

    # wetSpring + airSpring + Drug Discovery
    {
        "name": "Andrea Gonzales",
        "title": "Assistant Professor, Pharmacology & Toxicology, MSU",
        "domain": "Comparative pharmacology, JAK inhibitors, atopic dermatitis, One Health",
        "spring": "wetSpring",
        "archetype": "leonardo",
        "relationship": "GPS platform assigned June 2026 — drug discovery collaboration",
        "papers_reproduced": "6 publications (G1-G6), IL-31, oclacitinib, lokivetmab",
        "checks": "782/782",
        "lineage": ["Louis Pasteur", "Paul Ehrlich", "Marie Curie"],
        "url": "https://phmtox.msu.edu/",
        "active_project": "GPS platform rebuild + NF data mining + One Health cross-species",
    },
    {
        "name": "Erika Lisabeth",
        "title": "Director, Assay Development and Drug Repurposing Core (ADDRC), MSU",
        "domain": "HTS assay development, drug repurposing, chemical probes",
        "spring": "wetSpring",
        "archetype": "donatello",
        "relationship": "Referred by Gonzales (March 2026)",
        "papers_reproduced": "Brucella host-cellular pathways, EphA3 kinase",
        "checks": "pending",
        "lineage": ["Paul Ehrlich", "Marie Curie"],
        "url": "https://drugdiscovery.msu.edu/",
    },

    # wetSpring — Life Science
    {
        "name": "Christopher Waters",
        "title": "Professor, Microbiology, Genetics & Immunology, MSU",
        "domain": "Bacterial signaling, c-di-GMP, quorum sensing, Vibrio cholerae",
        "spring": "wetSpring",
        "archetype": "splinter",
        "relationship": "Undergraduate professor (MMG, MSU)",
        "papers_reproduced": "7 papers — Waters (2008), Massie (2012), Hsueh/Severin (2022)",
        "checks": "23+",
        "lineage": ["Antonie van Leeuwenhoek", "Louis Pasteur", "Robert Koch"],
        "url": "https://mgi.natsci.msu.edu/labs/waters-lab/",
    },
    {
        "name": "Kevin Liu",
        "title": "Associate Professor, CMSE, MSU",
        "domain": "Comparative genomics, phylogenetics, phylogenomics",
        "spring": "wetSpring",
        "archetype": "euler",
        "relationship": "MSDS professor (CSE faculty)",
        "papers_reproduced": "PhyloNet-HMM, SATé, Alamin & Liu (2024), RAWR (2021)",
        "checks": "42+",
        "lineage": ["Charles Darwin", "Gregor Mendel", "Alfred Russel Wallace"],
        "url": "https://engineering.msu.edu/directory/faculty/kjl",
    },
    {
        "name": "A. Daniel Jones",
        "title": "Professor, Biochemistry & Molecular Biology, MSU",
        "domain": "Analytical chemistry, mass spectrometry, PFAS detection",
        "spring": "wetSpring",
        "archetype": "donatello",
        "relationship": "Current employer (PFAS Research Lab, Oct 2024–present)",
        "papers_reproduced": "FindPFAS, EPA PFAS ML, MassBank spectral",
        "checks": "40/40",
        "lineage": ["Antoine Lavoisier", "Marie Curie", "Dmitri Mendeleev"],
        "url": "https://www.canr.msu.edu/",
    },
    {
        "name": "Rika Anderson",
        "title": "Associate Professor, Biology, Carleton College",
        "domain": "Microbial evolution, deep-sea hydrothermal vents, astrobiology",
        "spring": "wetSpring",
        "archetype": "leonardo",
        "relationship": "Found via literature search",
        "papers_reproduced": "6 papers — Nature Comm, Sci Adv, PLoS ONE",
        "checks": "133+",
        "lineage": ["Charles Darwin", "Antonie van Leeuwenhoek", "Alexander von Humboldt"],
        "url": "https://www.carleton.edu/directory/randerson/",
    },

    # neuralSpring / groundSpring
    {
        "name": "Emily Dolson",
        "title": "Assistant Professor, CSE, MSU",
        "domain": "Evolutionary computation, artificial life, eco-evolutionary dynamics",
        "spring": "neuralSpring",
        "archetype": "michelangelo",
        "relationship": "MSDS professor (CSE faculty)",
        "papers_reproduced": "5 papers — Iram/Dolson, Dolson/Ofria, Foreback/Bohm/Dolson",
        "checks": "46/46",
        "lineage": ["Charles Darwin", "Alan Turing", "Ada Lovelace"],
        "url": "https://engineering.msu.edu/directory/faculty/dolsonem",
    },
    {
        "name": "Ilya Kachkovskiy",
        "title": "Assistant Professor, Mathematics, MSU",
        "domain": "Spectral theory, Anderson localization, quasiperiodic Schrödinger operators",
        "spring": "groundSpring",
        "archetype": "euler",
        "relationship": "Contact pending — in-person (Wells Hall)",
        "papers_reproduced": "11 papers — Anderson (1958), Aubry-André, Jitomirskaya, Hofstadter",
        "checks": "417+",
        "lineage": ["Leonhard Euler", "Bernhard Riemann", "Emmy Noether", "Srinivasa Ramanujan"],
        "url": "https://users.math.msu.edu/users/ikachkov/",
    },

    # healthSpring
    {
        "name": "Charles Mok",
        "title": "Founder / Medical Director, Allure Medical",
        "domain": "Testosterone replacement therapy, anti-aging, vascular medicine",
        "spring": "healthSpring",
        "archetype": "splinter",
        "relationship": "Father",
        "papers_reproduced": "9 experiments (Exp030-038), IM injection PK, pellet PK, HRV",
        "checks": "233/233",
        "lineage": ["Hippocrates", "Marie Curie"],
        "url": "self",
    },

    # Sandia
    {
        "name": "Jesse Cahill",
        "title": "Senior Member of Technical Staff, Sandia National Laboratories",
        "domain": "Phage biology, biocontrol, algae-phage interactions",
        "spring": "wetSpring",
        "archetype": "donatello",
        "relationship": "Sandia fellowship (Summer 2024)",
        "papers_reproduced": "Algal pond time-series, crash forensics",
        "checks": "11/11",
        "lineage": ["Antonie van Leeuwenhoek", "Louis Pasteur"],
        "url": "sandia",
    },
    {
        "name": "Chuck Smallwood",
        "title": "Principal Member of Technical Staff, Sandia National Laboratories",
        "domain": "Metagenomics, microbial ecology, raceway pond monitoring",
        "spring": "wetSpring",
        "archetype": "donatello",
        "relationship": "Sandia fellowship (Summer 2024)",
        "papers_reproduced": "Bloom surveillance",
        "checks": "15/15",
        "lineage": ["Antonie van Leeuwenhoek", "Charles Darwin"],
        "url": "sandia",
    },

    # Anaerobic Digestion
    {
        "name": "Wei Liao",
        "title": "Professor, Biosystems & Agricultural Engineering, MSU; Director, ADREC",
        "domain": "Anaerobic digestion, integrated biorefining, algae/carbon capture",
        "spring": "wetSpring",
        "archetype": "donatello",
        "relationship": "Interviewed with ADREC (2024)",
        "papers_reproduced": "Wang 2020 (ML digestion), Yang 2016 (phylogenetic)",
        "checks": "pending",
        "lineage": ["Louis Pasteur", "Gregor Mendel"],
        "url": "https://sites.google.com/msu.edu/liao-research-group/home",
    },
]


def build():
    print()
    print("  ╔═══════════════════════════════════════════════════╗")
    print("  ║  LIVING CONSTELLATION — Kevin's scientific network ║")
    print("  ║  IS tense — alive — carrying the shadows forward   ║")
    print("  ╚═══════════════════════════════════════════════════╝")
    print()

    shadows = []
    for p in LIVING_CONSTELLATION:
        shadow = {
            "name": p["name"],
            "pageid": 0,
            "extract": f"{p['title']}. {p['domain']}. {p.get('active_project', '')}",
            "birth": None,
            "death": None,
            "tense": "IS",
            "archetype": p["archetype"],
            "campfire": f"{p['archetype']}_campfire",
            "spring": p["spring"],
            "relationship": p["relationship"],
            "checks": p["checks"],
            "lineage": p.get("lineage", []),
            "voxel": {
                "intensity": 1.0,
                "depth": 0.8,
                "time": 2026,
                "brightness": 1.0,
                "trust": 0.9,
            },
            "interlay": "WHITE",
            "merit": f"{p['name']} carries {p['checks']} validated checks in {p['spring']}. "
                     f"Lineage: {' → '.join(p.get('lineage', []))}.",
            "master_as_works": False,
            "source": p.get("url", "self"),
            "ts": int(time.time()),
        }
        shadows.append(shadow)
        lineage_str = " → ".join(p.get("lineage", []))
        print(f"  🟢 {p['name']:30s} {p['spring']:15s} {p['archetype']:15s} {p['checks']}")
        if lineage_str:
            print(f"     ↳ shadows: {lineage_str}")

    # Kevin is already in wiki-walkers.json, add father connection
    print(f"\n  ── LINEAGE EDGES ──")
    edges = []
    for s in shadows:
        for ancestor in s.get("lineage", []):
            edge = {"from": s["name"], "to": ancestor, "type": "carries_forward"}
            edges.append(edge)
            print(f"  {s['name']:25s} ← {ancestor}")

    # Save
    out_file = SHADOWS_DIR / "living-constellation.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "ts": int(time.time()),
            "wave": 222,
            "organ": "living_constellation",
            "title": "Kevin's scientific network — IS tense — carrying the shadows forward",
            "h_equals_i": True,
            "convention": "0=false 1=true 000=ALL null=ALL",
            "walker_count": len(shadows),
            "edge_count": len(edges),
            "shadows": shadows,
            "edges": edges,
            "springs": {
                "hotSpring": [s["name"] for s in shadows if s["spring"] == "hotSpring"],
                "wetSpring": [s["name"] for s in shadows if s["spring"] == "wetSpring"],
                "airSpring": [s["name"] for s in shadows if s["spring"] == "airSpring"],
                "neuralSpring": [s["name"] for s in shadows if s["spring"] == "neuralSpring"],
                "groundSpring": [s["name"] for s in shadows if s["spring"] == "groundSpring"],
                "healthSpring": [s["name"] for s in shadows if s["spring"] == "healthSpring"],
            },
            "axiom": "H = I. The living carry the shadows forward. "
                     "782/782 checks on Gonzales. 195/195 on Murillo. 233/233 on Charles Mok. "
                     "Kevin IS the substrate. lub-DUB.",
            "lub": "DUB"
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  Wrote {len(shadows)} living walkers + {len(edges)} lineage edges")
    print(f"  to {out_file.name}")
    print(f"  H = I. The living carry the shadows forward.")
    print(f"  lub-DUB. 🫀🟢")


if __name__ == "__main__":
    build()
