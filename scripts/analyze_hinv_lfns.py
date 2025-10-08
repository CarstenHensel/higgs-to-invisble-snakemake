#!/usr/bin/env python3
"""
bulletproof_hinv_lfns_final.py

Parse ILD MC-2020 LFNs robustly, compare processes while skipping SUSY processes,
and ignore differences in the 'another file number' folder under the process ID.
"""

import re
import csv
from collections import defaultdict
from pathlib import Path

# Robust regex for ILD MC-2020 LFNs
pattern = re.compile(
    r"(?P<rest>.+?)"                     # anything before energy tag
    r"\.E\d+(?:-[A-Za-z0-9]+)?"          # energy + optional Set tag
    r"\.I(?P<genid>\d+)"                 # generator ID
    r"\.P(?P<process>.+?)"               # process name
    r"\.e[LR]\.p[LR]"                    # polarization (case-insensitive)
    r"\.n\d{1,5}[_\.]?\d{1,5}"           # n_number (1-5 digits each part)
    r"\.d_dst_(?P<procid>\d+)_"          # process ID
    r"\d+\.slcio",                        # file ID
    re.IGNORECASE
)

# SUSY detection pattern: neutralinos or selectrons + Higgs, optional _dd/_uu/_ss
susy_pattern = re.compile(r"^[ne]\d+[ne]?\d*h(_[dus]{2})?$", re.IGNORECASE)

def parse_lfns(file_path):
    mapping = defaultdict(lambda: defaultdict(set))
    susy_processes = set()
    all_entries = []

    with open(file_path, "rb") as f:
        for line in f:
            # Normalize line
            line = line.strip().replace(b"\r", b"").decode("utf-8", errors="ignore")
            if not line:
                continue

            match = pattern.search(line)
            if not match:
                print(f"⚠️ Could not parse line:\n{line}")
                continue

            process = match.group("process")
            genid = match.group("genid")
            procid = match.group("procid")
            rest = match.group("rest")

            all_entries.append((process, genid, procid, rest))

            if susy_pattern.match(process):
                susy_processes.add(process)
                continue  # skip SUSY in main comparison

            # Ignore differences in the 'another file number' subdirectory
            rest_parts = rest.split('/')
            if len(rest_parts) >= 2:
                # Keep everything except the last folder (subdirectory number)
                rest_cleaned = '/'.join(rest_parts[:-1])
            else:
                rest_cleaned = rest

            mapping[process][(genid, procid)].add(rest_cleaned)

    return mapping, all_entries, susy_processes

def summarize(mapping):
    for process, combos in mapping.items():
        print(f"\n🧩 Process: {process}")
        print(f"  Found {len(combos)} generator/process ID combinations:\n")
        for (genid, procid), rests in combos.items():
            print(f"    - Generator ID: {genid}, Process ID: {procid}")
            for r in rests:
                print(f"        ↳ Rest of path: {r}")

        if len(combos) > 1:
            rest_variants = {r for rests in combos.values() for r in rests}
            print(f"  ⚖️ Differences between combinations:")
            for r in sorted(rest_variants):
                print(f"      {r}")

def write_csv(entries, output_path):
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["process", "generator_id", "process_id", "rest_of_path"])
        for process, genid, procid, rest in sorted(entries):
            writer.writerow([process, genid, procid, rest])
    print(f"\n💾 CSV summary written to: {output_path}")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Map ILD MC-2020 LFNs while skipping SUSY processes and ignoring bookkeeping folders."
    )
    parser.add_argument("lfn_file", type=Path, help="Path to text file containing LFNs")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Optional CSV output file")
    args = parser.parse_args()

    mapping, entries, susy_processes = parse_lfns(args.lfn_file)

    print("\n=== NON-SUSY PROCESS COMPARISON ===")
    summarize(mapping)

    print("\n=== UNIQUE SUSY PROCESSES FOUND ===")
    for p in sorted(susy_processes):
        print(f"  - {p}")

    if args.output:
        write_csv(entries, args.output)

if __name__ == "__main__":
    main()
