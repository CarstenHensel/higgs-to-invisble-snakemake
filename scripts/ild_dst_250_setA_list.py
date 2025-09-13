#!/usr/bin/env python3
"""
This script runs a Dirac command to list DST files in the ILD MC production.

**Important:** Before running this script, you must execute:
    source /cvmfs/clicdp.cern.ch/DIRAC/bashrc
    dirac-proxy-init -g ilc_user

It will save the output to a timestamped file and log each execution.
"""

import subprocess
from datetime import datetime
import os

# Base name for the output files
output_base = "all_files"

# Dirac command and arguments
dirac_command = [
    "dirac-ilc-find-in-FC",
    "/ilc/prod/ilc/mc-2020/ild/dst/250-SetA/",
    "Energy=250",
    "Datatype=DST"
]

def run_dirac_command():
    """Run the Dirac command and save output to a timestamped file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_base}_{timestamp}.txt"
    
    try:
        # Run the command and capture stdout
        result = subprocess.run(dirac_command, capture_output=True, text=True, check=True)
        
        # Write output to file
        with open(output_file, "w") as f:
            f.write(result.stdout)
        
        print(f"Output saved to {output_file}")
        log_execution(output_file)
    
    except subprocess.CalledProcessError as e:
        print("Error running Dirac command:")
        print(e.stderr)

def log_execution(output_file):
    """Log the execution time and output file to a log file."""
    log_file = "dirac_command.log"
    with open(log_file, "a") as log:
        log.write(f"{datetime.now()}: Ran dirac command, output saved to {output_file}\n")
    print(f"Execution logged in {log_file}")

if __name__ == "__main__":
    run_dirac_command()
