#!/usr/bin/env python3
"""
ilc_xsec_collector.py

Script to extract unique production IDs from a list of ILCDirac LFNs,
query their cross sections and number of events via dirac-ilc-get-info, 
and store results in a YAML file.

Usage:
    ./ilc_xsec_collector.py -i lfns.txt -o production_info.yaml
"""

import re
import subprocess
import yaml
import logging
import argparse

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

    # Regex to extract process and production ID from filenames
    prod_pattern = re.compile(
        r'\.I\d{6}\.(.+?)\.n\d+_\d+\..*d_dst_(\d+)_\d+\.slcio'
    )

    prod_dict = {}  # key: prod_id, value: process_name

    # Step 1: Parse LFNs
    with open(args.input, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = prod_pattern.search(line)
            if match:
                process_name, prod_id = match.groups()
                prod_dict[prod_id] = process_name
                logging.debug(f"Found ProdID={prod_id}, Process={process_name}")
            else:
                logging.warning(f"Could not parse LFN: {line}")

    logging.info(f"Found {len(prod_dict)} unique production IDs.")

    results = []

    # Step 2 & 3: Query dirac-ilc-get-info
    for prod_id, process_name in prod_dict.items():
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

        # Step 4: Extract CrossSection
        cross_section_match = re.search(
            r'CrossSection\s+:\s+([\dEe\+\-\.]+)\s+fb\+/-([\dEe\+\-\.]+)fb', output
        )

        # Extract NumberOfEvents
        events_match = re.search(
            r'NumberOfEvents\s+:\s+(\d+)', output
        )

        if cross_section_match:
            xsec_value, xsec_error = cross_section_match.groups()
            entry = {
                "ProdID": int(prod_id),
                "Process": process_name,
                "CrossSection_fb": float(xsec_value),
                "CrossSectionError_fb": float(xsec_error)
            }
            if events_match:
                entry["NumberOfEvents"] = int(events_match.group(1))
            else:
                logging.warning(f"Could not extract NumberOfEvents for ProdID {prod_id}")
                entry["NumberOfEvents"] = None

            results.append(entry)
            logging.info(
                f"ProdID {prod_id}: CrossSection = {xsec_value} ± {xsec_error} fb, "
                f"NumberOfEvents = {entry['NumberOfEvents']}"
            )
        else:
            logging.warning(f"Could not extract CrossSection for ProdID {prod_id}")

    # Write results to YAML
    with open(args.output, 'w') as f:
        yaml.dump(results, f, sort_keys=False)

    logging.info(f"Saved production info for {len(results)} productions to {args.output}")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    main()
