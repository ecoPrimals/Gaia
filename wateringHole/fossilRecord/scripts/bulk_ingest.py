#!/usr/bin/env python3
# DEPRECATED: Superseded by native_braid.py (Wave 157e), which will itself be
# replaced by Rust-native `membrane content.braid` + biomeOS graph composition.
# See nest.capabilities Neural API for the target surface.
"""
Bulk Data Ingestion Pipeline — westGate CAS + Full Provenance Trio

Ingests datasets through the canonical provenance chain:
  Per file: BLAKE3 hash → nestGate CAS → rhizoCrypt DAG event (4ms, O(1))
  Per dataset (once): dehydrate → loamSpine session.commit
    → bearDog Ed25519 signature → sweetGrass attribution braid

Per-file spine entries are NOT created — the DAG Merkle root cryptographically
binds all files. loamSpine receives one SessionCommit at dehydration time.
See PROVENANCE_TRIO_ARCHITECTURE.md for architectural rationale.

Usage:
  python3 bulk_ingest.py --files /path/to/data.db --dataset "ChEMBL 37"
  python3 bulk_ingest.py --dir /path/to/lincs/ --dataset "LINCS L1000"
  python3 bulk_ingest.py --files a.gz,b.gz --dataset "MyData" --license CC-BY-4.0
  python3 bulk_ingest.py --dir /data/pdb/ --dataset "PDB" --checkpoint 500
"""

import argparse
import base64
import json
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

MEMBRANE = "/run/user/1000/membrane"
RIBOCIPHER_PREFIX = struct.pack("BB", 0xEC, 0x01)

SOCKETS = {
    "nestgate":   f"{MEMBRANE}/nestgate-westgate-tower-155f.sock",
    "rhizocrypt": f"{MEMBRANE}/rhizocrypt-westgate-tower-155f.sock",
    "loamspine":  f"{MEMBRANE}/loamspine-westgate-tower-155f.sock",
    "sweetgrass": f"{MEMBRANE}/sweetgrass-westgate-tower-155f.sock",
    "beardog":    f"{MEMBRANE}/beardog-westgate-tower-155f.sock",
}

MAX_CAS_SIZE = 100 * 1024 * 1024
COMMITTER_DID = "did:eco:westgate"


def rpc(primal, method, params=None, timeout=30):
    """JSON-RPC 2.0 call over UDS with ribocipher prefix."""
    sock = SOCKETS[primal]
    req = json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 1})
    use_prefix = primal != "beardog"
    data = (RIBOCIPHER_PREFIX if use_prefix else b"") + req.encode() + b"\n"

    r = subprocess.run(
        ["socat", "-t10", "-", f"UNIX-CONNECT:{sock}"],
        input=data, capture_output=True, timeout=timeout,
    )
    if not r.stdout:
        return None

    raw = r.stdout
    if raw[:2] == RIBOCIPHER_PREFIX:
        raw = raw[2:]
    for line in raw.split(b"\n"):
        line = line.strip()
        if line:
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def rpc_result(primal, method, params=None, timeout=30):
    """Call RPC and return just the result, or None on error."""
    r = rpc(primal, method, params, timeout)
    if r and "result" in r:
        return r["result"]
    return None


def hex_to_content_hash(hex_str):
    """Convert 64-char hex BLAKE3 hash to [u8; 32] byte array for ContentHash serde."""
    return list(bytes.fromhex(hex_str))


def blake3_hash(filepath):
    size_gb = filepath.stat().st_size / (1024**3)
    timeout = max(300, int(size_gb * 60) + 120)
    r = subprocess.run(
        ["b3sum", "--no-names", str(filepath)],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.stdout.strip()


def cas_put(filepath, b3hash):
    """Store in CAS. For files > MAX_CAS_SIZE, store hash reference only."""
    size = filepath.stat().st_size
    if size <= MAX_CAS_SIZE:
        file_b64 = base64.b64encode(filepath.read_bytes()).decode()
        r = rpc_result("nestgate", "content.put", {
            "data": file_b64, "hash_type": "blake3",
        }, timeout=60)
        if r:
            return True, "stored"
        return False, "rpc_fail"
    else:
        ref = json.dumps({
            "type": "large_file_reference",
            "blake3": b3hash,
            "size": size,
            "path": str(filepath),
            "gate": "westgate",
        }).encode()
        ref_b64 = base64.b64encode(ref).decode()
        r = rpc_result("nestgate", "content.put", {
            "data": ref_b64, "hash_type": "blake3",
        }, timeout=30)
        if r:
            return True, "reference"
        return False, "rpc_fail"


def guess_mime(filepath):
    ext = filepath.suffix.lower()
    return {
        ".gz": "application/gzip",
        ".tar": "application/x-tar",
        ".db": "application/x-sqlite3",
        ".sqlite": "application/x-sqlite3",
        ".gctx": "application/x-hdf5",
        ".csv": "text/csv",
        ".tsv": "text/tab-separated-values",
        ".txt": "text/plain",
        ".json": "application/json",
        ".smi": "chemical/x-daylight-smiles",
        ".sdf": "chemical/x-mdl-sdfile",
        ".pdb": "chemical/x-pdb",
        ".cif": "chemical/x-cif",
        ".fasta": "application/x-fasta",
        ".fastq": "application/x-fastq",
        ".h5": "application/x-hdf5",
        ".hdf5": "application/x-hdf5",
        ".obo": "application/x-obo",
        ".owl": "application/rdf+xml",
        ".xml": "application/xml",
        ".zip": "application/zip",
        ".bz2": "application/x-bzip2",
        ".xz": "application/x-xz",
    }.get(ext, "application/octet-stream")


# ── rhizoCrypt DAG operations ──────────────────────────────────────

def dag_session_create(dataset):
    """Open a DAG session for this dataset ingestion."""
    return rpc_result("rhizocrypt", "dag.session.create", {
        "session_type": "General",
        "description": f"Data federation ingest: {dataset}",
    })


def dag_event_append(session_id, b3hash, filename, size, dataset):
    """Append a data-ingested event to the DAG session."""
    return rpc_result("rhizocrypt", "dag.event.append", {
        "session_id": session_id,
        "event_type": {"DataCreate": {}},
        "metadata": [
            ["dataset", dataset],
            ["filename", filename],
            ["blake3", b3hash],
            ["size", str(size)],
        ],
        "payload_ref": b3hash,
        "parents": [],
    })


def dag_event_append_batch(session_id, events):
    """Append multiple events in a single RPC call (G31 batch).
    
    events: list of (b3hash, filename, size, dataset) tuples.
    Returns list of vertex IDs or None on failure.
    """
    requests = [
        {
            "session_id": session_id,
            "event_type": {"DataCreate": {}},
            "metadata": [
                ["dataset", dataset],
                ["filename", filename],
                ["blake3", b3hash],
                ["size", str(size)],
            ],
            "payload_ref": b3hash,
            "parents": [],
        }
        for b3hash, filename, size, dataset in events
    ]
    return rpc_result("rhizocrypt", "dag.event.append_batch", {
        "requests": requests,
    })


def dag_partial_dehydrate(session_id):
    """Compute partial Merkle root without closing session."""
    return rpc_result("rhizocrypt", "dag.partial_dehydrate", {
        "session_id": session_id,
    })


def dag_dehydrate(session_id):
    """Finalize DAG session → 64-char hex Merkle root. Closes session."""
    return rpc_result("rhizocrypt", "dag.dehydration.trigger", {
        "session_id": session_id,
    })


# ── loamSpine ledger operations ────────────────────────────────────

def spine_create(dataset):
    """Create a spine for this dataset."""
    return rpc_result("loamspine", "spine.create", {
        "name": f"federation:{dataset}",
        "owner": "westgate",
    })


def spine_session_commit(spine_id, session_id, merkle_root_hex, vertex_count):
    """Commit the DAG session's Merkle root to the spine."""
    return rpc_result("loamspine", "session.commit", {
        "spine_id": spine_id,
        "session_id": session_id,
        "session_hash": hex_to_content_hash(merkle_root_hex),
        "vertex_count": vertex_count,
        "committer": COMMITTER_DID,
    })


# ── bearDog + sweetGrass ───────────────────────────────────────────

def sign_merkle_root(merkle_root_hex, dataset):
    """Sign the dataset's Merkle root via bearDog Ed25519."""
    sign_msg = base64.b64encode(
        f"federation:{dataset}:{merkle_root_hex}".encode()
    ).decode()
    result = rpc_result("beardog", "crypto.sign_ed25519", {"message": sign_msg})
    if result:
        sig = result.get("signature", "") if isinstance(result, dict) else str(result)
        return sig if len(sig) > 20 else None
    return None


def braid_create(b3hash, mime_type, size, dataset, license_id,
                 session_id=None, merkle_root=None, signature=None):
    """Create an attribution braid via sweetGrass, linked to DAG session.
    
    When signature is provided, it's included in the braid metadata to close
    the provenance loop (bearDog Ed25519 over Merkle root).
    """
    params = {
        "data_hash": b3hash,
        "mime_type": mime_type,
        "size": size,
        "name": dataset,
        "description": f"Data federation: {dataset}",
        "tags": ["data-federation", "westgate"],
    }
    if session_id:
        params["source_session"] = session_id
    if merkle_root:
        params["source_merkle_root"] = merkle_root
    if signature:
        params["ed25519_signature"] = signature
        params["signature_scope"] = "merkle_root"
        params["signer"] = "did:eco:westgate:beardog"
    return rpc_result("sweetgrass", "braid.create", params)


# ── Per-file ingestion ─────────────────────────────────────────────

def ingest_file(filepath, dataset, license_id, session_id):
    """Ingest one file through CAS + DAG event (canonical per-file path)."""
    filepath = Path(filepath)
    result = {"file": filepath.name, "path": str(filepath), "steps": {}}
    t0 = time.time()

    size = filepath.stat().st_size
    result["size"] = size

    print(f"  BLAKE3 hashing {filepath.name} ({size / 1024 / 1024:.1f} MB)...", end="", flush=True)
    b3 = blake3_hash(filepath)
    hash_ms = int((time.time() - t0) * 1000)
    throughput = size / (time.time() - t0) / 1e9 if (time.time() - t0) > 0 else 0
    print(f" {b3[:16]}... ({hash_ms}ms, {throughput:.1f} GB/s)")
    result["blake3"] = b3
    result["hash_ms"] = hash_ms

    ok, mode = cas_put(filepath, b3)
    result["steps"]["cas"] = "PASS" if ok else "FAIL"
    result["cas_mode"] = mode

    vertex_id = dag_event_append(session_id, b3, filepath.name, size, dataset)
    result["steps"]["dag.event.append"] = "PASS" if vertex_id else "FAIL"
    if vertex_id:
        result["vertex_id"] = vertex_id

    result["elapsed_ms"] = int((time.time() - t0) * 1000)
    return result


# ── Dataset-level orchestration ────────────────────────────────────

def run(files, dataset, license_id, checkpoint_interval=1000):
    total = len(files)
    results = []
    total_bytes = 0
    t_start = time.time()

    print(f"\n{'=' * 70}")
    print(f"  BULK INGESTION — {dataset}")
    print(f"  Files: {total}")
    print(f"  Pipeline: BLAKE3 → CAS → DAG event (per file)")
    print(f"            → dehydrate → session.commit → sign → braid (per dataset)")
    print(f"  License: {license_id}")
    print(f"  Checkpoint every: {checkpoint_interval} files")
    print(f"{'=' * 70}\n")

    # 1. Create DAG session
    print("  [INIT] Creating rhizoCrypt DAG session...", end="", flush=True)
    session_id = dag_session_create(dataset)
    if not session_id:
        print(" FAIL — rhizoCrypt unreachable or session creation failed")
        sys.exit(1)
    print(f" {session_id}")

    # 2. Create loamSpine
    print("  [INIT] Creating loamSpine...", end="", flush=True)
    spine_id = spine_create(dataset)
    if not spine_id:
        print(" FAIL — loamSpine unreachable or spine creation failed")
        sys.exit(1)
    print(f" {spine_id}")

    print()

    # 3. Ingest each file
    event_count = 0
    for i, f in enumerate(files):
        f = Path(f)
        if not f.exists():
            print(f"  [{i+1}/{total}] {f.name}  SKIP (not found)")
            results.append({"file": f.name, "steps": {"fetch": "SKIP"}})
            continue

        result = ingest_file(f, dataset, license_id, session_id)
        results.append(result)
        total_bytes += result.get("size", 0)

        if result["steps"].get("dag.event.append") == "PASS":
            event_count += 1

        steps = result.get("steps", {})
        passed = sum(1 for v in steps.values() if v == "PASS")
        total_s = len(steps)
        status = f"{passed}/{total_s}" if passed < total_s else "FULL CHAIN"

        print(f"  [{i+1}/{total}] {result['file']:50s} {result['size']/1024/1024:>10.1f} MB  "
              f"{result['elapsed_ms']:>6d}ms  {status}")

        failures = [k for k, v in steps.items() if v != "PASS"]
        if failures:
            print(f"           FAILED: {', '.join(failures)}")

        # 4. Partial dehydration checkpoint
        if checkpoint_interval > 0 and event_count > 0 and event_count % checkpoint_interval == 0:
            print(f"\n  [CHECKPOINT] Partial dehydration at {event_count} events...", end="", flush=True)
            partial = dag_partial_dehydrate(session_id)
            if partial:
                merkle = partial.get("merkle_root", partial) if isinstance(partial, dict) else partial
                sealed = partial.get("sealed_count", "?") if isinstance(partial, dict) else "?"
                print(f" root={str(merkle)[:16]}... sealed={sealed}")
            else:
                print(" FAIL (non-fatal, continuing)")
            print()

    # 5. Final dehydration — close session, get Merkle root
    print(f"\n  [FINALIZE] Dehydrating DAG session ({event_count} events)...", end="", flush=True)
    merkle_root = dag_dehydrate(session_id)
    if merkle_root:
        merkle_hex = merkle_root if isinstance(merkle_root, str) else str(merkle_root)
        print(f" root={merkle_hex[:16]}...")
    else:
        merkle_hex = None
        print(" FAIL (session may already be closed)")

    # 6. Commit session to loamSpine
    if merkle_hex and spine_id:
        print(f"  [FINALIZE] Committing session to loamSpine...", end="", flush=True)
        commit = spine_session_commit(spine_id, session_id, merkle_hex, event_count)
        if commit:
            print(f" committed (index={commit.get('index', '?') if isinstance(commit, dict) else '?'})")
        else:
            print(" FAIL")

    # 7. Sign the Merkle root
    signature = None
    if merkle_hex:
        print(f"  [FINALIZE] Signing Merkle root via bearDog...", end="", flush=True)
        signature = sign_merkle_root(merkle_hex, dataset)
        print(" PASS" if signature else " FAIL")

    # 8. Create attribution braid (with signature to close provenance loop)
    print(f"  [FINALIZE] Creating sweetGrass attribution braid...", end="", flush=True)
    braid = braid_create(
        b3hash=merkle_hex or "0" * 64,
        mime_type="application/x-dataset",
        size=total_bytes,
        dataset=dataset,
        license_id=license_id,
        session_id=session_id,
        merkle_root=merkle_hex,
        signature=signature,
    )
    print(" PASS" if braid else " FAIL")

    wall = time.time() - t_start

    # ── Summary ──
    print(f"\n{'=' * 70}")
    print(f"  RESULTS — {dataset}")
    print(f"{'=' * 70}")
    print(f"  Files:         {total}")
    print(f"  Total data:    {total_bytes:,} bytes ({total_bytes/1024/1024/1024:.2f} GB)")
    print(f"  Wall time:     {wall:.1f}s")
    print(f"  DAG session:   {session_id}")
    print(f"  Spine:         {spine_id}")
    print(f"  DAG events:    {event_count}")
    print(f"  Merkle root:   {merkle_hex or 'NONE'}")
    print(f"  Signature:     {'PRESENT' if signature else 'NONE'}")
    print(f"  Braid:         {'CREATED' if braid else 'NONE'}")

    step_names = ["cas", "dag.event.append"]
    print(f"\n  Per-file step results:")
    for step in step_names:
        p = sum(1 for r in results if r.get("steps", {}).get(step) == "PASS")
        print(f"    {step:25s}  {p}/{total}")

    finalize_steps = {
        "dag.dehydration.trigger": "PASS" if merkle_hex else "FAIL",
        "session.commit":          "PASS" if (merkle_hex and commit) else "FAIL",
        "crypto.sign_ed25519":     "PASS" if signature else "FAIL",
        "braid.create":            "PASS" if braid else "FAIL",
    }
    print(f"\n  Dataset-level finalization:")
    for step, status in finalize_steps.items():
        print(f"    {step:25s}  {status}")

    cas_info = rpc_result("nestgate", "health.check")
    if cas_info:
        print(f"\n  nestGate: v{cas_info.get('version')}, "
              f"uptime {int(cas_info.get('uptime_s', 0))//3600}h")

    print(f"{'=' * 70}")

    report_dir = Path("/tmp") / f"{dataset.lower().replace(' ', '_')}_report"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "ingest_report.json"
    with open(report, "w") as fp:
        json.dump({
            "gate": "westGate",
            "dataset": dataset,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "session_id": session_id,
            "spine_id": spine_id,
            "merkle_root": merkle_hex,
            "event_count": event_count,
            "count": len(results),
            "total_bytes": total_bytes,
            "wall_seconds": wall,
            "signature": "present" if signature else None,
            "braid": "created" if braid else None,
            "results": results,
        }, fp, indent=2)
    print(f"\n  Report: {report}")

    return results


def fetch_and_ingest(url, dest_dir, dataset, filename=None, license_id="CC0-1.0",
                     rate_limit="50M", timeout=600):
    """Download a URL and immediately ingest through the full provenance chain.
    
    Per-file: BLAKE3 hash, CAS put, DAG event. Per-dataset: dehydrate,
    session.commit, sign, braid. No per-file spine entries.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    fname = filename or url.rsplit("/", 1)[-1]
    outfile = dest / fname

    if outfile.exists() and outfile.stat().st_size > 100:
        print(f"  EXISTS: {outfile} ({outfile.stat().st_size} bytes)")
    else:
        print(f"  FETCH: {url} → {outfile}")
        result = subprocess.run([
            "curl", "-fSL", "--limit-rate", rate_limit,
            "-A", "ecoPrimals/1.0 (sovereign-science; westGate)",
            "--connect-timeout", "15", "--max-time", str(timeout),
            "-o", str(outfile), url,
        ], capture_output=True, text=True, timeout=timeout + 30)
        if result.returncode != 0 or not outfile.exists() or outfile.stat().st_size < 100:
            print(f"  FAIL: download failed (rc={result.returncode})")
            if outfile.exists() and outfile.stat().st_size < 100:
                outfile.unlink()
            return None

    return run([str(outfile)], dataset, license_id)


def main():
    parser = argparse.ArgumentParser(
        description="Bulk data ingestion through westGate full provenance pipeline"
    )
    parser.add_argument("--files", type=str, help="Comma-separated file paths")
    parser.add_argument("--dir", type=str, help="Directory of files to ingest")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    parser.add_argument("--license", type=str, default="CC0-1.0", help="License ID")
    parser.add_argument("--glob", type=str, default="*", help="Glob pattern for --dir")
    parser.add_argument("--checkpoint", type=int, default=1000,
                        help="Partial dehydration every N files (0 = disabled)")
    args = parser.parse_args()

    if args.files:
        files = [f.strip() for f in args.files.split(",")]
    elif args.dir:
        d = Path(args.dir)
        files = sorted(str(f) for f in d.glob(args.glob) if f.is_file())
    else:
        print("Provide --files or --dir")
        sys.exit(1)

    if not files:
        print("No files found")
        sys.exit(1)

    print(f"Found {len(files)} files to ingest")
    run(files, args.dataset, args.license, args.checkpoint)


if __name__ == "__main__":
    main()
