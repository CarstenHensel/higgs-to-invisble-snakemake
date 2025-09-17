#!/usr/bin/env python3
"""
generate_key4hep_options_and_htcondor.py

This script automates the generation of Key4hep options files and corresponding
HTCondor job scripts from a set of job YAML files. 

Features:
- Reads YAML files describing MC samples (process, process ID, cross-section, etc.)
- Generates customized Key4hep options files for each job
- Inserts the list of input files, myalg parameters, and user-defined number of events
- Creates corresponding HTCondor shell scripts to run each job via `k4run`
- Logs all actions to a timestamped logfile for traceability

Usage:
    python3 generate_key4hep_options_and_htcondor.py

Adjust the configuration section below to point to your YAML files, template options file,
and desired output directories.
"""

import yaml
from pathlib import Path
import logging
from datetime import datetime

# -----------------------------
# Configuration
# -----------------------------
JOBS_DIR = Path("job_yamls")        # Directory with your YAML files
OPTIONS_TEMPLATE = Path(
        "/afs/cern.ch/user/c/chensel/ILD/workarea/May2025/k4-project-template/k4ProjectTemplate/options/default_options_file.py"
        )  # Your default key4hep options
OUTPUT_OPTIONS_DIR = Path("key4hep_options") # Where to store generated options files
OUTPUT_SCRIPT_DIR = Path("htcondor_jobs")    # Where to store HTCondor scripts
EVTMAX = 1                                # Number of events per job (customizable)

# Logfile
LOGFILE = f"generate_key4hep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create output directories if they don't exist
OUTPUT_OPTIONS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

logging.info("Starting generation of Key4hep options and HTCondor scripts.")
logging.info(f"Jobs directory: {JOBS_DIR}")
logging.info(f"Template file: {OPTIONS_TEMPLATE}")
logging.info(f"Output options dir: {OUTPUT_OPTIONS_DIR}")
logging.info(f"Output scripts dir: {OUTPUT_SCRIPT_DIR}")
logging.info(f"Events per job (EvtMax): {EVTMAX}")

# -----------------------------
# Helper Functions
# -----------------------------
def read_yaml(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)

def generate_options(yaml_info, template_text, evtmax):
    # Prepare files list for lcio_read.Files
    files_list = [f'"{yaml_info["path"]}/{f}"' for f in yaml_info["files"]]
    files_line = "lcio_read.Files = [\n    " + ",\n    ".join(files_list) + "\n]\n"

    # Add myalg info
    myalg_lines = (
        f"myalg.cross_section = {yaml_info['cross_section_pb']}\n"
        f"myalg.numberOfEvents = {yaml_info['n_events']}\n"
        f"myalg.processName = '{yaml_info['process']}'\n"
        f"myalg.processID = {yaml_info['process_ID']}\n"
    )

    # Replace placeholders in template
    new_text = template_text.replace("###LCIO_FILES###", files_line)
    new_text = new_text.replace("###MYALG_PARAMS###", myalg_lines)
    new_text = new_text.replace("###EVTMAX###", str(evtmax))
    
    return new_text

# -----------------------------
# Main
# -----------------------------
# Read template once
with open(OPTIONS_TEMPLATE, "r") as f:
    template_text = f.read()

# Iterate over all YAML files
yaml_files = list(JOBS_DIR.glob("*.yaml"))
logging.info(f"Found {len(yaml_files)} YAML files.")

for yaml_file in yaml_files:
    try:
        yaml_info = read_yaml(yaml_file)
        job_num = yaml_file.stem.split("_job")[-1]
        options_text = generate_options(yaml_info, template_text, EVTMAX)

        # Define output options file
        options_filename = f"higgsTo_invisible_{yaml_info['process']}_{job_num}.py"
        options_path = OUTPUT_OPTIONS_DIR / options_filename
        with open(options_path, "w") as f:
            f.write(options_text)

        # Create HTCondor script
        script_filename = f"run_{yaml_info['process']}_{job_num}.sh"
        script_path = OUTPUT_SCRIPT_DIR / script_filename
        with open(script_path, "w") as f:
            f.write(f"""#!/bin/bash
# HTCondor submission script for {yaml_file.name}
k4run {options_path}
""")
        script_path.chmod(0o755)

        logging.info(f"Generated options: {options_path} and script: {script_path}")

    except Exception as e:
        logging.error(f"Failed to process {yaml_file}: {e}")

logging.info("Finished generation of all options and HTCondor scripts.")
print(f"Finished. See logfile {LOGFILE} for details.")

