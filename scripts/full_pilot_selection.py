#!/usr/bin/env python3
"""
Pilot selection for Higgs->Invisible analysis at 250 GeV (~50 fb^-1).

This version uses a pre-generated file all_files.txt containing all available LFNs.
It selects up to MAX_FILES_PER_PROCESS files per process for the pilot run.

Output:
  - LFNs written to pilot_lfns.txt
  - Directory structure samples/<process>/
"""

import os
import re
from collections import defaultdict
import subprocess

# Config
ALL_FILES = "all_files.txt"
LFN_FILE = "pilot_lfns.txt"
SAMPLES_DIR = "samples"
MAX_FILES_PER_PROCESS = 50
DRY_RUN = False  # Set to False to download files

# Load all files
with open(ALL_FILES, "r") as f:
    all_files = [line.strip() for line in f if line.strip()]

# Group files by process
files_by_process = defaultdict(list)
for lfn in all_files:
    # Extract process name from the filename
    # Pattern: .P<process>.<polarization>.nXXX_YYY.d_...
    match = re.search(r"\.P([a-zA-Z0-9_]+)\.", lfn)
    if match:
        process = match.group(1)
        files_by_process[process].append(lfn)
    else:
        # fallback if pattern fails
        files_by_process["unknown"].append(lfn)

# Select up to MAX_FILES_PER_PROCESS per process
selected_files = []
summary = []

for process, files in files_by_process.items():
    files.sort()  # deterministic order
    chosen = files[:MAX_FILES_PER_PROCESS]
    selected_files.extend(chosen)

    # Estimate total events per process from filename (pattern nXXX_YYY)
    total_events = 0
    for f in chosen:
        m = re.search(r"\.n(\d+)_\d+", f)
        if m:
            total_events += int(m.group(1))
        else:
            total_events += 1000
    summary.append((process, len(chosen), total_events))

# Write LFNs to file
with open(LFN_FILE, "w") as f:
    for lfn in selected_files:
        f.write(lfn + "\n")

print(f"✔ Wrote {len(selected_files)} LFNs to {LFN_FILE}")

# Create directories for each process
for process, _, _ in summary:
    os.makedirs(os.path.join(SAMPLES_DIR, process), exist_ok=True)

# Optional: download files
if not DRY_RUN:
    print("⬇ Downloading files...")
    subprocess.run(["dirac-dms-get-file", LFN_FILE])

    # Move downloaded files to process directories
    for lfn in selected_files:
        filename = os.path.basename(lfn)
        process = next((p for p in files_by_process if p in lfn), None)
        if process:
            target_dir = os.path.join(SAMPLES_DIR, process)
            source_path = os.path.join(os.getcwd(), filename)
            if os.path.exists(source_path):
                os.rename(source_path, os.path.join(target_dir, filename))
    print("✔ Files moved to samples/<process>/ directories")

# Print summary
print("\nPilot selection summary:")
print(f"{'Process':25s} {'#Files':>6s} {'#Events':>10s}")
for process, n_files, total_events in summary:
    print(f"{process:25s} {n_files:6d} {total_events:10d}")

print("\n✔ Ready for pilot download and analysis")
