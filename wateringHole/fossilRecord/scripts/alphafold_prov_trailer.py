#!/usr/bin/env python3
# DEPRECATED: Trailer pattern superseded by inline braiding at ingress.
# native_braid.py handles incremental braiding; target replacement is
# Rust-native `membrane content.braid --incremental` via Neural API.
"""
AlphaFold provenance trailer — follows the bulk downloader and braids files.

Reads the .prov_queue file (written by the downloader) which contains one
line per downloaded file: filepath<TAB>size. Tracks braided line count so
it can seek past already-processed entries on restart.

Architecture:
  - Downloader appends to .prov_queue at download speed (43-74/s)
  - This trailer reads from .prov_queue and runs BLAKE3 → CAS → DAG event
  - No per-file spine entries — the DAG Merkle root binds all files
  - The trailer processes at UDS RPC speed (~30-40/s) and catches up during pauses
  - Every CHECKPOINT_INTERVAL files, the DAG is partially dehydrated
  - Provenance state is persisted for restart safety

Restart-safe: persists line offset + provenance session IDs.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bulk_ingest import (
    blake3_hash, cas_put,
    dag_session_create, dag_event_append, dag_event_append_batch,
    dag_partial_dehydrate,
    dag_dehydrate, spine_create,
    spine_session_commit, sign_merkle_root, braid_create,
)

DEST = Path("/mnt/nestgate/cold/zfs/data/alphafold_structures")
PROV_QUEUE = DEST / ".prov_queue"
PROV_STATE = DEST / ".prov_state"
DATASET_NAME = "alphafold_structures_v6"

BATCH_SIZE = 200
CHECKPOINT_INTERVAL = 2000
POLL_INTERVAL = 15
REPORT_INTERVAL = 60


def load_state():
    if PROV_STATE.exists():
        try:
            return json.loads(PROV_STATE.read_text())
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def save_state(session_id, spine_id, event_count, lines_processed, byte_offset=0):
    PROV_STATE.write_text(json.dumps({
        "session_id": session_id,
        "spine_id": spine_id,
        "event_count": event_count,
        "lines_processed": lines_processed,
        "byte_offset": byte_offset,
    }))


def init_provenance():
    state = load_state()
    if state and state.get("session_id") and state.get("spine_id"):
        print(f"Resuming: session={state['session_id'][:16]}... "
              f"events={state.get('event_count', 0)} "
              f"lines={state.get('lines_processed', 0)}")
        return (state["session_id"], state["spine_id"],
                state.get("event_count", 0), state.get("lines_processed", 0))

    session_id = dag_session_create(DATASET_NAME)
    spine_result = spine_create(DATASET_NAME)
    spine_id = spine_result.get("spine_id") if isinstance(spine_result, dict) else spine_result
    if not session_id or not spine_id:
        print("FATAL: provenance init failed", file=sys.stderr)
        sys.exit(1)
    save_state(session_id, spine_id, 0, 0)
    print(f"Provenance started: session={session_id[:16]}... spine={spine_id[:16]}...")
    return session_id, spine_id, 0, 0


def main():
    print(f"AlphaFold provenance trailer starting", flush=True)

    session_id, spine_id, event_count, lines_processed = init_provenance()
    state = load_state() or {}
    byte_offset = state.get("byte_offset", 0)
    total_braided = 0
    errors = 0
    t_start = time.time()
    last_report = t_start

    while True:
        if not PROV_QUEUE.exists():
            time.sleep(POLL_INTERVAL)
            continue

        batch = []
        with open(PROV_QUEUE, "rb") as f:
            f.seek(byte_offset)
            for raw_line in f:
                line = raw_line.decode("utf-8", errors="replace").strip()
                lines_processed += 1
                parts = line.split("\t")
                if len(parts) != 2:
                    continue
                filepath, size_str = parts
                batch.append((Path(filepath), int(size_str), lines_processed))
                if len(batch) >= BATCH_SIZE:
                    byte_offset = f.tell()
                    break
            else:
                byte_offset = f.tell()

        if not batch:
            now = time.time()
            if now - last_report > REPORT_INTERVAL:
                elapsed = now - t_start
                rate = total_braided / elapsed if elapsed > 0 else 0
                print(f"[{time.strftime('%H:%M:%S')}] "
                      f"braided={total_braided:,} events={event_count:,} "
                      f"line={lines_processed:,} rate={rate:.1f}/s "
                      f"err={errors} (idle)", flush=True)
                last_report = now
            time.sleep(POLL_INTERVAL)
            continue

        dag_batch = []
        for fp, sz, line_num in batch:
            try:
                h = blake3_hash(fp)
                cas_put(fp, h)
                dag_batch.append((h, fp.name, sz, DATASET_NAME))
                lines_processed = line_num
            except Exception as e:
                errors += 1
                lines_processed = line_num

        if dag_batch:
            result = dag_event_append_batch(session_id, dag_batch)
            if result:
                count = len(result) if isinstance(result, list) else 1
                event_count += count
                total_braided += count
            else:
                for h, fname, sz, ds in dag_batch:
                    vertex = dag_event_append(session_id, h, fname, sz, ds)
                    if vertex:
                        event_count += 1
                        total_braided += 1
                    else:
                        errors += 1

            if event_count > 0 and event_count % CHECKPOINT_INTERVAL < len(dag_batch):
                dag_partial_dehydrate(session_id)
                save_state(session_id, spine_id, event_count, lines_processed, byte_offset)
                print(f"  [CHECKPOINT] events={event_count:,} "
                      f"line={lines_processed:,}", flush=True)

        save_state(session_id, spine_id, event_count, lines_processed, byte_offset)

        now = time.time()
        if now - last_report > REPORT_INTERVAL:
            elapsed = now - t_start
            rate = total_braided / elapsed if elapsed > 0 else 0
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"braided={total_braided:,} events={event_count:,} "
                  f"line={lines_processed:,} rate={rate:.1f}/s "
                  f"err={errors}", flush=True)
            last_report = now


if __name__ == "__main__":
    main()
