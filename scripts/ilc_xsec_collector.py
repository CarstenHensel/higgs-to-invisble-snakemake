#!/usr/bin/env python3
"""
ilc_xsec_collector.py

Modified to combine multiple production IDs of the same process
into a single YAML entry with summed number of events.
SUSY processes are filtered out.
"""

import re
import subprocess
import yaml
import logging
import argparse
from collections import defaultdict

# -------------------------------
# SUSY process keywords
# -------------------------------
SUSY_KEYWORDS = [
    "n1n1h", "n23n23h", "e1e1h", "e2e2h", "e3e3h",
    "n23n23h_dd", "n23n23h_uu", "n23n23h_ss",
    "n1n1h_dd", "n1n1h_uu", "n1n1h_ss",
    "e3e3h_dd", "e3e3h_uu", "e3e3h_ss",
    "e2e2h_dd", "e2e2h_uu", "e2e2h_ss",
    "e1e1h_dd", "e1e1h_uu", "e1e1h_ss",
    "qqh_e2e2", "qqh_e3e3"
]

def is_susy_process(process_name: str) -> bool:
    """Check if the process name matches a SUSY keyword."""
    return any(tag in process_name for tag in SUSY_KEYWORDS)

# -------------------------------
# Argument parsing
# -------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract production IDs, cross sections, and number of events from ILCDirac LFNs."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Text file with LFNs, one per line."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="YAML file to store results."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug-level logging."
    )
    return parser.parse_args()

# -------------------------------
# Main logic
# -------------------------------
def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Regex to extract generator ID, process name, and production ID
    prod_pattern = re.compile(
        r'\.I(\d{6})\.P([^\.]+)\..*d_dst_(\d+)_\d+\.slcio'
    )

    # Group info by (generatorID, process)
    process_dict = defaultdict(lambda: {
        "ProductionIDs": [],
        "CrossSection_fb": None,
        "CrossSectionError_fb": None,
        "NumberOfEvents": 0
    })

    # Step 1: Parse LFNs
    with open(args.input, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = prod_pattern.search(line)
            if match:
                gen_id, process_name, prod_id = match.groups()

                # --- SUSY filter ---
                if is_susy_process(process_name):
                    logging.info(f"Skipping SUSY process: {process_name}, ProdID={prod_id}")
                    continue
                # -------------------

                key = (gen_id, process_name)
                if prod_id not in process_dict[key]["ProductionIDs"]:
                    process_dict[key]["ProductionIDs"].append(prod_id)
                logging.debug(f"Found ProdID={prod_id}, Process={process_name}, GenID={gen_id}")
            else:
                logging.warning(f"Could not parse LFN: {line}")

    logging.info(f"Found {len(process_dict)} unique process entries (by GenID + Process) after SUSY filtering.")

    # Step 2 & 3: Query dirac-ilc-get-info per production
    for (gen_id, process_name), info in process_dict.items():
        for prod_id in info["ProductionIDs"]:
            logging.info(f"Querying production {prod_id} ({process_name})")
            try:
                cmd = ["dirac-ilc-get-info", "-p", prod_id]
                result = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, check=True
                )
                output = result.stdout
            except subprocess.CalledProcessError as e:
                logging.error(f"Error querying ProdID {prod_id}: {e.stderr.strip()}")
                continue

            # Extract CrossSection
            cross_section_match = re.search(
                r'CrossSection\s+:\s+([\dEe\+\-\.]+)\s+fb\+/-([\dEe\+\-\.]+)fb', output
            )
            # Extract NumberOfEvents
            events_match = re.search(
                r'^\s*NumberOfEvents\s*:\s*(\d+)', output, re.MULTILINE
            )

            if cross_section_match:
                xsec_value, xsec_error = cross_section_match.groups()
                xsec_value = float(xsec_value)
                xsec_error = float(xsec_error)

                # Store cross-section if not set yet, else verify consistency
                if info["CrossSection_fb"] is None:
                    info["CrossSection_fb"] = xsec_value
                    info["CrossSectionError_fb"] = xsec_error
                else:
                    if abs(info["CrossSection_fb"] - xsec_value) > 1e-6:
                        logging.warning(
                            f"CrossSection mismatch for process {process_name}, ProdID {prod_id}"
                        )

                if events_match:
                    info["NumberOfEvents"] += int(events_match.group(1))
                else:
                    logging.warning(f"Could not extract NumberOfEvents for ProdID {prod_id}")

            else:
                logging.warning(f"Could not extract CrossSection for ProdID {prod_id}")

    # Prepare output list
    results = []
    for (gen_id, process_name), info in process_dict.items():
        entry = {
            "GeneratorID": int(gen_id),
            "Process": process_name,
            "ProductionIDs": sorted([int(pid) for pid in info["ProductionIDs"]]),
            "CrossSection_fb": info["CrossSection_fb"],
            "CrossSectionError_fb": info["CrossSectionError_fb"],
            "NumberOfEvents": info["NumberOfEvents"]
        }
        results.append(entry)

    # Write results to YAML
    with open(args.output, 'w') as f:
        yaml.dump(results, f, sort_keys=False)

    logging.info(f"Saved consolidated production info for {len(results)} processes to {args.output}")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    main()
