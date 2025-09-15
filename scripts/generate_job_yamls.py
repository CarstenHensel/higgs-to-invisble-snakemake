#!/usr/bin/env python3
"""
generate_job_yamls.py

Reads `mc_metadata.yaml` (created by discover_mc_processes.py).
Splits each process' file list into job-sized chunks.
Writes one YAML config per job in `job_yamls/`.

Each job YAML contains:
- process name
- cross-section, n_events, k_factor
- path (absolute path stored once)
- list of filenames for this chunk

Also writes a logfile `generate_job_yamls.log`.
"""

import yaml
import os
import math
import logging
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
METADATA_FILE = "mc_metadata.yaml"
OUTPUT_DIR = "job_yamls"
CHUNK_SIZE = 100   # files per job

LOG_FILE = "generate_job_yamls.log"

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -----------------------------
# Helpers
# -----------------------------
def load_metadata(file):
    with open(file, "r") as f:
        return yaml.safe_load(f)

def write_job_yaml(process_name, metadata, chunk_idx, chunk_files):
    """Write one job config YAML file"""
    job_config = {
        "process": process_name,
        "cross_section_pb": metadata.get("cross_section_pb", 0.0),
        "n_events": metadata.get("n_events", 0),
        "k_factor": metadata.get("k_factor", 1.0),
        "path": metadata.get("path"),
        "files": chunk_files
    }
    out_name = f"{process_name}_job{chunk_idx:03d}.yaml"
    out_path = Path(OUTPUT_DIR) / out_name
    with open(out_path, "w") as f:
        yaml.dump(job_config, f, sort_keys=False)
    return out_name

# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metadata = load_metadata(METADATA_FILE)

    processes = metadata.get("processes", {})
    if not processes:
        logging.error("No processes found in metadata")
        return

    total_jobs = 0
    logging.info(f"Generating jobs from {len(processes)} processes")

    for process_name, meta in processes.items():
        files = meta.get("files", [])
        n_files = len(files)
        if n_files == 0:
            logging.warning(f"Process {process_name} has no files")
            continue

        n_chunks = math.ceil(n_files / CHUNK_SIZE)
        logging.info(
            f"Process {process_name}: {n_files} files → {n_chunks} jobs "
            f"(chunk size {CHUNK_SIZE})"
        )

        for i in range(n_chunks):
            chunk_files = files[i*CHUNK_SIZE : (i+1)*CHUNK_SIZE]
            out_yaml = write_job_yaml(process_name, meta, i, chunk_files)
            logging.info(f"  Wrote {out_yaml} with {len(chunk_files)} files")
        total_jobs += n_chunks

    logging.info(f"Finished: {total_jobs} job YAMLs written to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
