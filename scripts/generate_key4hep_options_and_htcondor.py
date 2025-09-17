#!/usr/bin/env python3
"""
generate_key4hep_options_and_htcondor.py

Automates the generation of Key4hep options files, run scripts, and a single HTCondor
submission file for a batch of jobs.

Features:
- Reads YAML files describing MC samples
- Generates customized Key4hep options files based on default_options_file.py
- Inserts YAML file paths into the `files = [...]` list
- Updates myalg parameters: cross_section, n_events_generated, processName, processID
- Sets the number of events (EvtMax) from user input
- Creates run scripts for each job
- Generates a single HTCondor submission file for all jobs
- Logs all actions to a timestamped logfile
"""

import yaml
from pathlib import Path
import logging
from datetime import datetime
import re

# -----------------------------
# Configuration
# -----------------------------
JOBS_DIR = Path("/path/to/job_yamls")        # Directory with your YAML files
OPTIONS_TEMPLATE = Path("/path/to/default_options_file.py")
OUTPUT_OPTIONS_DIR = Path("key4hep_options")
OUTPUT_SCRIPT_DIR = Path("htcondor_jobs")
LOGS_DIR = Path("htcondor_logs")
EVTMAX = 1000  # Number of events per job (customizable)

# Setup logging
LOGFILE = f"generate_key4hep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create output directories
OUTPUT_OPTIONS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.info("Starting generation of Key4hep options, run scripts, and HTCondor .sub file.")

# -----------------------------
# Helper Functions
# -----------------------------
def read_yaml(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)

def generate_options_newtemplate(yaml_info, template_text, evtmax):
    """
    Generates a Key4hep options file for the new template.
    - Replaces `files = [...]` with the list of files from the YAML
    - Replaces `EvtMax=<number>` with evtmax
    - Sets myalg parameters from YAML
    """
    # Prepare files list string
    files_list_str = ",\n    ".join([f'"{yaml_info["path"]}/{f}"' for f in yaml_info["files"]])
    files_assignment = f"files = [\n    {files_list_str}\n]\n"

    # Replace the existing files = [...] block
    template_text = re.sub(r'files\s*=\s*\[.*?\]', files_assignment, template_text, flags=re.DOTALL)

    # Replace EvtMax=...
    template_text = re.sub(r'EvtMax\s*=\s*\d+', f"EvtMax={evtmax}", template_text)

    # Update myalg parameters
    myalg_lines = (
        f"myalg.cross_section = {yaml_info['cross_section_pb']}\n"
        f"myalg.n_events_generated = {yaml_info['n_events']}\n"
        f"myalg.processName = '{yaml_info['process']}'\n"
        f"myalg.processID = {yaml_info['process_id']}\n"
    )
    # Insert after "myalg = HtoInvAlg()" line
    template_text = re.sub(r'(myalg\s*=\s*HtoInvAlg\(\))', r'\1\n' + myalg_lines, template_text)

    return template_text

# -----------------------------
# Main
# -----------------------------
# Read template
with open(OPTIONS_TEMPLATE, "r") as f:
    template_text = f.read()

yaml_files = list(JOBS_DIR.glob("*.yaml"))
logging.info(f"Found {len(yaml_files)} YAML files.")

htcondor_sub_file = Path("submit_all_jobs.sub")
with open(htcondor_sub_file, "w") as subf:
    # Write common HTCondor header
    subf.write(f"""universe = vanilla
request_cpus = 1
request_memory = 2GB
getenv = True
""")

    for yaml_file in yaml_files:
        try:
            yaml_info = read_yaml(yaml_file)
            job_num = yaml_file.stem.split("_job")[-1]

            # Generate options file
            options_filename = f"higgsTo_invisible_{yaml_info['process']}_{job_num}.py"
            options_path = OUTPUT_OPTIONS_DIR / options_filename
            options_text = generate_options_newtemplate(yaml_info, template_text, EVTMAX)
            with open(options_path, "w") as f:
                f.write(options_text)

            # Generate run script
            script_filename = f"run_{yaml_info['process']}_{job_num}.sh"
            script_path = OUTPUT_SCRIPT_DIR / script_filename
            with open(script_path, "w") as f:
                f.write(f"""#!/bin/bash
k4run {options_path}
""")
            script_path.chmod(0o755)

            # Add entry to HTCondor .sub file
            subf.write(f"""
executable = {script_path}
output = {LOGS_DIR}/run_{yaml_info['process']}_{job_num}.out
error = {LOGS_DIR}/run_{yaml_info['process']}_{job_num}.err
log = {LOGS_DIR}/run_{yaml_info['process']}_{job_num}.log
queue
""")
            logging.info(f"Generated options: {options_path}, script: {script_path}")

        except Exception as e:
            logging.error(f"Failed to process {yaml_file}: {e}")

logging.info(f"HTCondor submission file created: {htcondor_sub_file}")
logging.info("Finished generation of all options, run scripts, and .sub file.")
print(f"Finished. See logfile {LOGFILE} for details.")

