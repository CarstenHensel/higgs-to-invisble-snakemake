#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Script: filter_and_merge_mc_samples.py
#
# Purpose:
#   This script builds a clean, inclusive MC sample list for the Higgs-to-Invisible
#   background analysis. It takes a full LFN list as input and performs the following:
#     1. Removes all SUSY processes (to avoid signal contamination)
#     2. Groups LFNs by physics process
#     3. Keeps only the latest recommended version per process (e.g. v02-02-03)
#     4. Outputs a combined, duplicate-free LFN file ready for analysis
#
# Outputs:
#   - filtered_LFNs.txt          → main list for analysis
#   - skipped_SUSY_LFNs.txt      → SUSY processes (for verification)
#   - process_summary.txt        → overview of all processes and chosen versions
#
# Notes:
#   - The SUSY process list is based on known naming patterns (n1n1h, e2e2h, etc.).
#     Update SUSY_KEYWORDS if new naming conventions appear in future productions.
#   - The script ignores differences in file numbering (e.g. “000/”, “001/”) since
#     those reflect splitting within a single production, not distinct datasets.
#   - Recommended versions may evolve (e.g. v02-02 → v02-02-03); always verify
#     the latest production recommendations on the MC production website before running.
#
# Author: Carsten (with GPT-5 assistance)
# -----------------------------------------------------------------------------

import re
import argparse
from collections import defaultdict

# ----------------------------
# Configuration
# ----------------------------

# Known SUSY process patterns
SUSY_KEYWORDS = [
    "n1n1h", "n23n23h", "e1e1h", "e2e2h", "e3e3h",
    "n23n23h_dd", "n23n23h_uu", "n23n23h_ss",
    "n1n1h_dd", "n1n1h_uu", "n1n1h_ss",
    "e3e3h_dd", "e3e3h_uu", "e3e3h_ss",
    "e2e2h_dd", "e2e2h_uu", "e2e2h_ss",
    "e1e1h_dd", "e1e1h_uu", "e1e1h_ss"
]

# Regex to extract version and process name
pattern = re.compile(
    r"/ild/dst/[^/]+/(?P<process>[^/]+)/ILD_[^/]+/(?P<version>v\d{2}-\d{2}(?:-\d{2})?)"
)

# ----------------------------
# Helpers
# ----------------------------

def is_susy(lfn: str) -> bool:
    return any(tag in lfn for tag in SUSY_KEYWORDS)

def version_key(version: str) -> tuple:
    """Convert version string like 'v02-02-03' → (2, 2, 3) for comparison"""
    parts = version.strip("v").split("-")
    return tuple(int(p) for p in parts)

# ----------------------------
# Main function
# ----------------------------

def main(input_file: str, output_file: str, susy_file: str, summary_file: str):
    with open(input_file) as f:
        lfns = [line.strip() for line in f if line.strip()]

    susy_lfns = []
    process_versions = defaultdict(lambda: defaultdict(list))

    for lfn in lfns:
        if is_susy(lfn):
            susy_lfns.append(lfn)
            continue

        m = pattern.search(lfn)
        if not m:
            print(f"⚠️ Could not parse: {lfn}")
            continue

        process = m.group("process")
        version = m.group("version")
        process_versions[process][version].append(lfn)

    # Keep latest version per process
    selected = []
    summary_lines = []
    summary_lines.append(f"{'Process':40} | {'Versions Found':35} | Selected\n" + "-"*90)

    for process, versions in sorted(process_versions.items()):
        all_versions = sorted(versions.keys(), key=version_key)
        latest_version = all_versions[-1]
        selected.extend(versions[latest_version])
        summary_lines.append(
            f"{process:40} | {', '.join(all_versions):35} | {latest_version}"
        )

    # Output results
    with open(output_file, "w") as out:
        out.write("\n".join(sorted(selected)))
    with open(susy_file, "w") as out:
        out.write("\n".join(sorted(susy_lfns)))
    with open(summary_file, "w") as out:
        out.write("\n".join(summary_lines))

    print(f"\n✅ Output written to {output_file}")
    print(f"✅ Skipped SUSY LFNs written to {susy_file}")
    print(f"✅ Process summary written to {summary_file}")
    print(f"Processes kept (latest versions only): {len(process_versions)}")
    print(f"Skipped SUSY files: {len(susy_lfns)}\n")

    print("\n".join(summary_lines[:15]))
    if len(summary_lines) > 15:
        print(f"... ({len(summary_lines)-15} more processes) ...")

# ----------------------------
# CLI entry
# ----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and combine ILD MC LFN list")
    parser.add_argument("input_file", help="Input LFN list (one per line)")
    parser.add_argument("-o", "--output", default="filtered_LFNs.txt", help="Output LFN file")
    parser.add_argument("-s", "--susy", default="skipped_SUSY_LFNs.txt", help="Output file for skipped SUSY LFNs")
    parser.add_argument("-t", "--summary", default="process_summary.txt", help="Process summary output file")
    args = parser.parse_args()
    main(args.input_file, args.output, args.susy, args.summary)
