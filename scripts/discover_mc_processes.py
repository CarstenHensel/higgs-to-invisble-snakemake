#!/usr/bin/env python3
"""
discover_mc_processes.py

Scans a root directory for MC processes.
Each process is assumed to have the structure:

  ROOT_DIR/ProcessName/edm4hep/*.root

Produces a master metadata YAML (`mc_metadata.yaml`) that contains:
- process name
- placeholder cross-section / n_events / k_factor
- absolute path (stored once)
- list of .root files

Also writes a logfile `discover_mc_processes.log`.
"""

import yaml
import logging
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
ROOT_DIR = "/afs/cern.ch/user/c/chensel/cernbox/ILC/HtoInv/MC/pilot_samples"   # TODO: adjust
OUTPUT_FILE = "mc_metadata.yaml"
LOG_FILE = "discover_mc_processes.log"

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
# Discover function
# -----------------------------
def discover_processes(root_dir: str):
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

        processes[process_dir.name] = {
            "cross_section_pb": 0.0,   # placeholder
            "n_events": 0,             # placeholder
            "k_factor": 1.0,
            "path": str(edm_dir.resolve()),
            "files": root_files
        }
        logging.info(f"Discovered {len(root_files)} files for {process_dir.name}")
    return processes

# -----------------------------
# Main
# -----------------------------
def main():
    processes = discover_processes(ROOT_DIR)

    if not processes:
        logging.error("No processes found!")
        return

    with open(OUTPUT_FILE, "w") as f:
        yaml.dump({"processes": processes}, f, sort_keys=False)

    logging.info(f"Metadata written to {OUTPUT_FILE} with {len(processes)} processes")

if __name__ == "__main__":
    main()
