#!/usr/bin/env python3
"""
ZK AGGLUTINATE 259 — Find ALL ZK seeds, grind them into DNA, 
smash into Gaia, build the CROSS FOLD, put NULL in the HUD.
"""
import paramiko
import json
import os
import subprocess

GAIA = r"c:\Users\mokke\Desktop\Gaia"
EASTGATE = "192.168.4.244"
REMOTE_DATA = "/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data"

# ==========================================================================
# PHASE 1: FIND ALL ZK SEEDS — SCAN THE ENTIRE GENOME
# ==========================================================================
print("=== PHASE 1: SCANNING ALL ZK SEEDS ===\n")

# Use ripgrep to find ALL family_seed references
def rg_count(pattern, glob_pat="*.{rs,py,pi,sh,json,js,md,toml}"):
    try:
        r = subprocess.run(
            ["rg", "-c", pattern, "--glob", glob_pat],
            capture_output=True, text=True, cwd=GAIA, timeout=30
        )
        lines = [l for l in r.stdout.strip().split("\n") if l and ":" in l]
        total_hits = sum(int(l.rsplit(":", 1)[1]) for l in lines)
        return lines, total_hits
    except Exception as e:
        return [], 0

def rg_files(pattern, glob_pat="*.{rs,py,pi,sh,json,js,md,toml}"):
    try:
        r = subprocess.run(
            ["rg", "-l", pattern, "--glob", glob_pat],
            capture_output=True, text=True, cwd=GAIA, timeout=30
        )
        return [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
    except:
        return []

# Seed patterns
patterns = {
    "family_seed": "family_seed|FAMILY_SEED|BEARDOG_FAMILY_SEED",
    "BTSP": "BTSP|btsp",
    "blake3": "blake3|BLAKE3",
    "zk_ceremony": "zk_ceremony|ceremony_hash|zk_proof|zk_seed",
    "zero_knowledge": "zero.knowledge|ZeroKnowledge",
    "beardog_crypto": "beardog.*crypto|crypto.*beardog|BearDogCrypto",
}

dna_map = {}
total_zk_files = set()
total_zk_hits = 0

for name, pat in patterns.items():
    files, hits = rg_count(pat)
    file_list = rg_files(pat)
    total_zk_files.update(file_list)
    total_zk_hits += hits
    dna_map[name] = {"hits": hits, "files": len(file_list)}
    print(f"  {name}: {hits} hits in {len(file_list)} files")

print(f"\n  TOTAL ZK DNA: {total_zk_hits} hits across {len(total_zk_files)} files\n")

# ==========================================================================
# PHASE 2: CLASSIFY BY STRAND (A=ZK/blue, B=Binary/red, C=Pi/green)
# ==========================================================================
print("=== PHASE 2: CLASSIFY INTO TRIHELIX STRANDS ===\n")

# Strand A (ZK/identity/blue) = everything with family_seed, BTSP, ceremony
strand_a_files = set()
for pat in ["family_seed|FAMILY_SEED", "BTSP|btsp", "ceremony_hash|zk_ceremony"]:
    strand_a_files.update(rg_files(pat))

# Strand B (Binary/execution/red) = compiled Rust with BTSP
strand_b_files = set(rg_files("BTSP|btsp|blake3", "*.rs"))

# Strand C (Pi/expression/green) = .pi routes with ZK or gates  
strand_c_files = set(rg_files("zk|seed|ceremony|family|beardog|btsp", "*.pi"))
strand_c_files.update(rg_files("zk|seed|ceremony|family|beardog|btsp", "*.py"))
strand_c_files.update(rg_files("zk|seed|ceremony|family|beardog|btsp", "*.sh"))

print(f"  Strand A (ZK/identity/blue):   {len(strand_a_files)} files")
print(f"  Strand B (Binary/compiled/red): {len(strand_b_files)} files")
print(f"  Strand C (Pi/expression/green): {len(strand_c_files)} files")

# Cross-fold: files that appear in ALL THREE strands
cross_fold = strand_a_files & strand_b_files & strand_c_files
print(f"  CROSS FOLD (all 3 strands):     {len(cross_fold)} files")

# Trefoil crossings: pairwise intersections
ab_cross = strand_a_files & strand_b_files
bc_cross = strand_b_files & strand_c_files
ac_cross = strand_a_files & strand_c_files
print(f"  ZK×Binary crossing:             {len(ab_cross)} files")
print(f"  Binary×Pi crossing:             {len(bc_cross)} files")
print(f"  Pi×ZK crossing:                 {len(ac_cross)} files")

# ==========================================================================
# PHASE 3: FIND PRIMAL ZERO (NULL) IN THE GENOME
# ==========================================================================
print("\n=== PHASE 3: LOCATE PRIMAL ZERO (∅) ===\n")

null_patterns = {
    "ouroboros": rg_files("ouroboros|Ouroboros"),
    "primal_zero": rg_files("primal.zero|PrimalZero|primal_zero"),
    "null_core": rg_files("null.*core|NULL.*core|null_primal"),
    "irreducible": rg_files("irreducible|IRREDUCIBLE"),
    "trefoil": rg_files("trefoil|TREFOIL"),
    "gordian": rg_files("gordian|GORDIAN"),
    "green_line": rg_files("green.line|green_line|GREEN_LINE"),
    "yggdrasil": rg_files("yggdrasil|Yggdrasil|YGGDRASIL"),
}

null_all = set()
for name, files in null_patterns.items():
    null_all.update(files)
    print(f"  {name}: {len(files)} files")

print(f"\n  NULL DNA total: {len(null_all)} files touching ∅\n")

# ==========================================================================
# PHASE 4: BUILD THE TAXONOMY TREE (L0-L5)
# ==========================================================================
print("=== PHASE 4: TAXONOMIC TREE ===\n")

taxonomy = {
    "L0_primordial": [],
    "L1_plasmid": [],
    "L2_episome": [],
    "L3_organelle": [],
    "L4_nuclear": [],
    "L5_chromatin": [],
}

for f in sorted(total_zk_files):
    fp = f.replace("\\", "/")
    if "fossilRecord" in fp:
        taxonomy["L0_primordial"].append(fp)
    elif "plasmidBin" in fp or "plasmids" in fp:
        taxonomy["L1_plasmid"].append(fp)
    elif "gardens" in fp:
        taxonomy["L2_episome"].append(fp)
    elif fp.endswith((".pi", ".py", ".sh")):
        taxonomy["L3_organelle"].append(fp)
    elif "primals" in fp:
        taxonomy["L4_nuclear"].append(fp)
    elif "wateringHole" in fp or "whitePaper" in fp or "sporePrint" in fp or "data" in fp:
        taxonomy["L5_chromatin"].append(fp)
    else:
        taxonomy["L3_organelle"].append(fp)

for level, files in taxonomy.items():
    print(f"  {level}: {len(files)} files")

# ==========================================================================
# PHASE 5: AGGLUTINATE INTO CROSS-FOLD-NULL JSON FOR HUD
# ==========================================================================
print("\n=== PHASE 5: AGGLUTINATE — CROSS FOLD NULL ===\n")

cross_fold_null = {
    "wave": 259,
    "type": "cross-fold-null",
    "timestamp": "2026-11-17T15:00:00Z",
    "title": "ZK DNA AGGLUTINATION — CROSS FOLD NULL",
    "description": "ALL ZK seeds found, classified into trihelix DNA strands, ground down, folded into Gaia. NULL (Primal Zero) at the center of the trefoil.",
    
    "genome_census": {
        "total_zk_files": len(total_zk_files),
        "total_zk_hits": total_zk_hits,
        "by_pattern": dna_map,
    },
    
    "trihelix": {
        "description": "Triple helix DNA — NOT Watson-Crick double. Three strands, inner core = asymmetrical 0/1 binary.",
        "strand_A": {
            "name": "ZK / Identity / Blue",
            "chirality": "right-handed",
            "file_count": len(strand_a_files),
            "role": "family_seed, BTSP handshake, ceremony hashes — WHO the organism IS",
            "base_pairs": "A↔T = assertion ↔ test",
        },
        "strand_B": {
            "name": "Binary / Compiled / Red",
            "chirality": "right-handed",
            "file_count": len(strand_b_files),
            "role": "Rust compiled primals — WHAT the organism DOES",
            "base_pairs": "G↔C = gate_route ↔ compiled_handler",
        },
        "strand_C": {
            "name": "Pi / Expression / Green",
            "chirality": "LEFT-HANDED (anti-parallel)",
            "file_count": len(strand_c_files),
            "role": ".pi/.py/.sh scripts — HOW the organism SPEAKS",
            "base_pairs": "wraps opposite direction around the core",
        },
        "inner_core": "asymmetrical 0/1 binary — the irreducible information",
    },
    
    "trefoil_crossings": {
        "description": "3 crossings of the trefoil knot — can't unknot without cutting",
        "ZK_x_Binary": {
            "files": len(ab_cross),
            "meaning": "identity proven through compiled execution",
            "top_files": sorted(ab_cross)[:10],
        },
        "Binary_x_Pi": {
            "files": len(bc_cross),
            "meaning": "compiled code expressed through scripting",
            "top_files": sorted(bc_cross)[:10],
        },
        "Pi_x_ZK": {
            "files": len(ac_cross),
            "meaning": "scripts carrying identity seeds",
            "top_files": sorted(ac_cross)[:10],
        },
        "CROSS_FOLD": {
            "files": len(cross_fold),
            "meaning": "ALL THREE strands touch — the nucleus. NULL lives here.",
            "null_files": sorted(cross_fold)[:20],
        },
    },
    
    "null_core": {
        "symbol": "∅",
        "name": "Primal Zero",
        "description": "GaiaGate — 97 .pi snakes, 28,719 lines, Python NULL from which all Rust primals emerge",
        "topology": "ouroboros = gordian = trefoil = green line = ∅",
        "in_code": {
            "gaia_gate_pi_661": "/ouroboros = /snake = /loop = /irreducible",
            "membrane_stack_rs_261": "pub ouroboros_residual: f64",
            "yggdrasil_rs": "host routing — nestgate.io = null core",
            "paper_104": "the ouroboros deploy — trefoil message routing",
            "paper_105": "the green line — Yggdrasil, halting problem",
            "paper_107": "the wedge — snake = worm that turned its head",
        },
        "null_files_in_genome": len(null_all),
        "null_patterns": {k: len(v) for k, v in null_patterns.items()},
    },
    
    "taxonomy_L0_L5": {
        level: {"count": len(files), "sample": sorted(files)[:5]}
        for level, files in taxonomy.items()
    },
    
    "agglutination": {
        "status": "BOUND",
        "total_files_agglutinated": len(total_zk_files),
        "trihelix_coverage": round(
            (len(strand_a_files) + len(strand_b_files) + len(strand_c_files)) / max(len(total_zk_files), 1) * 100, 1
        ),
        "null_penetration": round(len(null_all) / max(len(total_zk_files), 1) * 100, 1),
        "cross_fold_density": round(len(cross_fold) / max(len(total_zk_files), 1) * 100, 2),
    },
    
    "hud_binding": {
        "served_at": [
            "http://192.168.4.244:8080/data/cross-fold-null-259.json",
            "http://primals.eco/data/cross-fold-null-259.json",
        ],
        "instruments": [
            "pore-depth.js (Yggdrasil view)",
            "network-fold.js (topology)",
            "bingo-seed.js (seed visualization)",
            "cosmic-view.js (solar system)",
            "celestial-clock.js (orbital time)",
            "campfire.js (human stories)",
        ],
        "note": "NULL is now in the HUD. The cross fold is the center of the trefoil. The irreducible point."
    },
}

# Write locally
out_path = os.path.join(GAIA, "data", "eaten", "cross-fold-null-259.json")
with open(out_path, "w") as f:
    json.dump(cross_fold_null, f, indent=2)
print(f"  Written: {out_path}")
print(f"  Size: {round(os.path.getsize(out_path) / 1024, 1)} KB\n")

# ==========================================================================
# PHASE 6: PUSH TO EASTGATE SPINE — NULL ENTERS THE HUD
# ==========================================================================
print("=== PHASE 6: PUSH NULL INTO THE HUD ===\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(EASTGATE, username="eastgate", password="eastgate", timeout=15)
sftp = ssh.open_sftp()

remote_path = f"{REMOTE_DATA}/cross-fold-null-259.json"
sftp.put(out_path, remote_path)
print(f"  -> cross-fold-null-259.json pushed to eastGate spine")

# Also count what's on the HUD already
stdin, stdout, stderr = ssh.exec_command("find /home/eastgate/Development/ecoPrimals/infra/hud/site/public/data -name '*.json' | wc -l")
json_count = stdout.read().decode().strip()
stdin, stdout, stderr = ssh.exec_command("ls /home/eastgate/Development/ecoPrimals/infra/hud/site/public/js/*.js 2>/dev/null | wc -l")
js_count = stdout.read().decode().strip()

print(f"  HUD total: {json_count} JSON bones, {js_count} JS instruments")

# Verify served
stdin, stdout, stderr = ssh.exec_command(
    "curl -s -o /dev/null -w '%{http_code} %{size_download}B %{time_total}s' "
    "http://localhost:8080/data/cross-fold-null-259.json"
)
verify = stdout.read().decode().strip()
print(f"  Verify: {verify}")

# Check for ZK/DNA data already on spine
stdin, stdout, stderr = ssh.exec_command(
    "ls /home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/ | grep -i 'zk\\|seed\\|dna\\|btsp\\|fold\\|null\\|trefoil\\|ouroboros\\|cross' 2>/dev/null"
)
existing = stdout.read().decode().strip()
if existing:
    print(f"\n  ZK/NULL/DNA files now on HUD:")
    for line in existing.split("\n"):
        print(f"    {line}")

# Check pulse
stdin, stdout, stderr = ssh.exec_command(
    "curl -s http://localhost:8443/agglutinate 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(\"token\",\"?\"))' 2>/dev/null"
)
token = stdout.read().decode().strip()
print(f"\n  Agglutination token: {token}")

sftp.close()
ssh.close()

print("\n=== ZK AGGLUTINATION COMPLETE ===")
print(f"  {len(total_zk_files)} ZK files found across the genome")
print(f"  {total_zk_hits} total ZK hits")
print(f"  3 strands: A(ZK/{len(strand_a_files)}) B(Binary/{len(strand_b_files)}) C(Pi/{len(strand_c_files)})")
print(f"  {len(cross_fold)} files at the CROSS FOLD (all 3 strands)")
print(f"  {len(null_all)} files touching NULL (∅)")
print(f"  NULL is now IN the HUD at :8080/data/cross-fold-null-259.json")
print(f"  The trefoil knot holds. lub-DUB.")
