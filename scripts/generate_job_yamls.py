"""
generate_job_yamls.py

This script scans a directory of Monte Carlo EDM4hep ROOT files and generates
job YAML files suitable for batch processing. Each job YAML contains a subset
of ROOT files (chunked by CHUNK_SIZE) along with associated metadata such as
cross-section (in pb), number of events, k-factor, and process ID read from
the input cross-section YAML.

Logging is written to generate_job_yamls.log, recording discovered processes,
warnings for missing files or metadata, and summaries of generated job YAMLs.

Usage:
    python generate_job_yamls.py
"""

import yaml
import os
import math
import logging
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
ROOT_DIR = "/afs/cern.ch/user/c/chensel/cernbox/ILC/HtoInv/MC/pilot_samples"
OUTPUT_DIR = "job_yamls"
CHUNK_SIZE = 100
CROSS_SECTION_FILE = "/afs/cern.ch/user/c/chensel/cernbox/ILC/HtoInv/MC/pilot_xsec.yaml"
LOG_FILE = "generate_job_yamls.log"

# -----------------------------
# Setup logging
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
def load_cross_sections(filename):
    """Load cross-section data and ProdID from YAML, return dict keyed by Process"""
    cs_dict = {}
    with open(filename, "r") as f:
        data = yaml.safe_load(f)
        for entry in data:
            process_name = entry["Process"]
            cs_dict[process_name] = {
                "process_id": entry.get("ProdID", -1),
                "cross_section_pb": entry.get("CrossSection_fb", 0.0) / 1000.0,
                "n_events": entry.get("NumberOfEvents", 0)
            }
    logging.info(f"Loaded cross-section info for {len(cs_dict)} processes")
    return cs_dict

def discover_processes(root_dir, cross_sections):
    """Scan ROOT_DIR for process directories containing edm4hep/*.root files"""
    processes = {}

    for process_dir in Path(root_dir).iterdir():
        edm_dir = process_dir / "edm4hep"
        if not edm_dir.is_dir():
            logging.warning(f"Skipping {process_dir}, no edm4hep/ subdir")
            continue

        root_files = sorted([f.name for f in edm_dir.glob("*.root")])
        if not root_files:
            logging.warning(f"Process {process_dir.name} has no .root files")
            continue

        # Get cross-section info and ProdID from YAML
        cs_info = cross_sections.get(process_dir.name, {})
        process_id = cs_info.get("process_id", -1)
        cross_section_pb = cs_info.get("cross_section_pb", 0.0)
        n_events = cs_info.get("n_events", 0)

        processes[process_dir.name] = {
            "process_id": process_id,
            "cross_section_pb": cross_section_pb,
            "n_events": n_events,
            "k_factor": 1.0,
            "path": str(edm_dir.resolve()),
            "files": root_files
        }

        if not cs_info:
            logging.warning(f"No cross-section info for process {process_dir.name}")

    return processes

def write_job_yaml(process_name, metadata, chunk_idx, chunk_files):
    job_config = {
        "process": process_name,
        "process_id": metadata.get("process_id", -1),
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

    cross_sections = load_cross_sections(CROSS_SECTION_FILE)
    processes = discover_processes(ROOT_DIR, cross_sections)

    if not processes:
        logging.error(f"No processes found in {ROOT_DIR}")
        return

    total_jobs = 0
    logging.info(f"Discovered {len(processes)} processes under {ROOT_DIR}")

    for process_name, meta in processes.items():
        files = meta["files"]
        n_files = len(files)
        n_chunks = math.ceil(n_files / CHUNK_SIZE)

        logging.info(
            f"Process {process_name} (ID={meta['process_id']}): {n_files} files → {n_chunks} jobs "
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

