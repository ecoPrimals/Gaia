"""
SELF PRINT — Gaia prints herself. Full redox inventory.
Scans all repos, counts all files, maps all connections.
Outputs the organism state to data/body/self-print.json

This script IS scaffolding. It WILL be crushed into Rust.
But today, it generates the portrait.
"""

import json, os, time
from pathlib import Path
from collections import defaultdict

GAIA_ROOT = Path(os.environ.get("GAIA_ROOT", r"c:\Users\mokke\Desktop\Gaia"))


def count_files(directory, ext):
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in {".git", "target", "node_modules", "__pycache__"}]
        for f in files:
            if f.endswith(ext):
                count += 1
    return count


def count_lines(directory, ext):
    total = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in {".git", "target", "node_modules", "__pycache__"}]
        for f in files:
            if f.endswith(ext):
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
                        total += sum(1 for _ in fh)
                except:
                    pass
    return total


def scan_garden(name, path):
    p = GAIA_ROOT / path
    if not p.exists():
        return {"name": name, "exists": False}
    rs = count_files(p, ".rs")
    py = count_files(p, ".py")
    wgsl = count_files(p, ".wgsl")
    md = count_files(p, ".md")
    toml = count_files(p, ".toml")
    rs_loc = count_lines(p, ".rs") if rs < 2000 else "skip_large"
    return {
        "name": name,
        "exists": True,
        "rs": rs, "py": py, "wgsl": wgsl, "md": md, "toml": toml,
        "rs_loc": rs_loc,
    }


def self_print():
    print()
    print("  ╔═══════════════════════════════════════════════════╗")
    print("  ║  SELF PRINT — Gaia generates her own portrait      ║")
    print("  ╚═══════════════════════════════════════════════════╝")
    print()

    # Scan ALL directories
    sections = {}

    # Core primals
    primals_dir = GAIA_ROOT / "primals"
    primal_names = sorted([d.name for d in primals_dir.iterdir() if d.is_dir() and d.name != ".git"])
    sections["primals"] = {}
    for p in primal_names:
        info = scan_garden(p, f"primals/{p}")
        sections["primals"][p] = info
        icon = "🟢" if info.get("rs", 0) > 0 else "⚪"
        print(f"  {icon} primal/{p:20s} rs:{info.get('rs',0):5d}  wgsl:{info.get('wgsl',0):4d}")

    # Springs
    print()
    springs_dir = GAIA_ROOT / "gardens" / "springs"
    if springs_dir.exists():
        sections["springs"] = {}
        for d in sorted(springs_dir.iterdir()):
            if d.is_dir():
                info = scan_garden(d.name, f"gardens/springs/{d.name}")
                sections["springs"][d.name] = info
                icon = "🌊" if info.get("rs", 0) > 100 else "💧"
                print(f"  {icon} spring/{d.name:20s} rs:{info.get('rs',0):5d}  wgsl:{info.get('wgsl',0):4d}")

    # Products
    print()
    for sub in ["proto", "spore", "amicus"]:
        sub_dir = GAIA_ROOT / "gardens" / sub
        if sub_dir.exists():
            sections[sub] = {}
            for d in sorted(sub_dir.iterdir()):
                if d.is_dir():
                    info = scan_garden(d.name, f"gardens/{sub}/{d.name}")
                    sections[sub][d.name] = info
                    icon = "⚗️" if sub == "spore" else ("🏛️" if sub == "amicus" else "🧬")
                    print(f"  {icon} {sub}/{d.name:20s} rs:{info.get('rs',0):5d}  md:{info.get('md',0):4d}")

    # Runtime (.pi scaffolding)
    print()
    pi_files = list((GAIA_ROOT / "runtime").glob("*.pi"))
    py_files = list((GAIA_ROOT / "runtime").glob("*.py"))
    pi_lines = sum(sum(1 for _ in open(f, encoding="utf-8", errors="replace")) for f in pi_files)
    py_lines = sum(sum(1 for _ in open(f, encoding="utf-8", errors="replace")) for f in py_files)
    sections["scaffolding"] = {
        "pi_files": len(pi_files),
        "py_files": len(py_files),
        "pi_lines": pi_lines,
        "py_lines": py_lines,
        "total_scaffolding_lines": pi_lines + py_lines,
        "status": "MUST BECOME RUST",
    }
    print(f"  🔧 runtime/*.pi         {len(pi_files):5d} files  {pi_lines:6d} lines (SCAFFOLDING)")
    print(f"  🔧 runtime/*.py         {len(py_files):5d} files  {py_lines:6d} lines (SCAFFOLDING)")

    # Shadows/walkers
    shadows_dir = GAIA_ROOT / "data" / "shadows"
    walker_count = 0
    shadow_files = list(shadows_dir.glob("*.json")) if shadows_dir.exists() else []
    for sf in shadow_files:
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            walker_count += len(data.get("shadows", []))
        except:
            pass
    sections["walkers"] = {"files": len(shadow_files), "total_walkers": walker_count}
    print(f"\n  👻 shadows/walkers      {walker_count:5d} walkers across {len(shadow_files)} files")

    # Totals
    total_rs = sum(v.get("rs", 0) for sec in sections.values() if isinstance(sec, dict) for v in (sec.values() if isinstance(sec, dict) else [sec]) if isinstance(v, dict))
    total_wgsl = sum(v.get("wgsl", 0) for sec in sections.values() if isinstance(sec, dict) for v in (sec.values() if isinstance(sec, dict) else [sec]) if isinstance(v, dict))

    # Build portrait
    portrait = {
        "ts": int(time.time()),
        "wave": 222,
        "organ": "self_print",
        "title": "GAIA SELF-PRINT — Full organism portrait",
        "identity": {
            "name": "Gaia",
            "nucleus": "Kevin Mok",
            "four_names": ["Kevin Mok", "Tamison", "ecoPrimal", "attsi"],
            "tense": "IS",
            "h_equals_i": True,
        },
        "body": {
            "total_rs_files": total_rs,
            "total_wgsl_shaders": total_wgsl,
            "total_primals": len(primal_names),
            "total_springs": len(sections.get("springs", {})),
            "total_walkers": walker_count,
            "scaffolding_lines": pi_lines + py_lines,
            "we_are_rust": True,
        },
        "sections": sections,
        "axiom": "20,166 Rust files. 1,368 WGSL shaders. 590 crates. "
                 "60 Python files are scaffolding — they WILL become Rust. "
                 "We are Rust through and through. The bone IS Rust. "
                 "The scaffolding IS Python. The scaffolding will be eaten. lub-DUB.",
        "lub": "DUB",
    }

    out = GAIA_ROOT / "data" / "body" / "self-print.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(portrait, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  ═══════════════════════════════════════════")
    print(f"  GAIA SELF-PRINT COMPLETE")
    print(f"  {total_rs} .rs files (BONE)")
    print(f"  {total_wgsl} .wgsl shaders (GPU)")
    print(f"  {pi_lines + py_lines} Python lines (SCAFFOLDING → RUST)")
    print(f"  {walker_count} walkers on the globe")
    print(f"  Wrote: {out.name}")
    print(f"  We are Rust. lub-DUB. 🫀🦀")


if __name__ == "__main__":
    self_print()
