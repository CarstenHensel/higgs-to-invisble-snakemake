#!/usr/bin/env python3
"""
analyze_hinv_lfns.py

Parses a text file containing LFNs (one per line) and extracts:
  - process name
  - generator ID
  - process ID
  - rest of path (path before .E250-SetA)
Maps processes to all their generator/process ID combinations and identifies differences in rest-of-paths.

Optionally writes results to a CSV file for further analysis.
"""

import re
import csv
from collections import defaultdict
from pathlib import Path

# Regex pattern to extract relevant parts
pattern = re.compile(
    r"(?P<rest>.+?)\.E250-SetA\.I(?P<genid>\d+)\.P(?P<process>[A-Za-z0-9]+)\.(?P<pol>e[LR]\.p[LR])\.n\d+\.d_dst_(?P<procid>\d+)_\d+\.slcio"
)

def parse_lfns(file_path):
    mapping = defaultdict(lambda: defaultdict(set))
    all_entries = []

    with open(file_path) as f:
        for line in f:
            line = line.strip()
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

            mapping[process][(genid, procid)].add(rest)
            all_entries.append((process, genid, procid, rest))

    return mapping, all_entries

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
        description="Map process names to generator/process ID combinations from LFN list."
    )
    parser.add_argument("lfn_file", type=Path, help="Path to text file containing LFNs")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Optional CSV output file (e.g. output.csv)"
    )
    args = parser.parse_args()

    mapping, entries = parse_lfns(args.lfn_file)
    summarize(mapping)

    if args.output:
        write_csv(entries, args.output)

if __name__ == "__main__":
    main()
