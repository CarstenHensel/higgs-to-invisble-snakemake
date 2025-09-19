#!/usr/bin/env python3
"""
generate_htcondor_jobs.py

Script to generate Key4hep options files and corresponding HTCondor job scripts
from job YAML files. Each job will run with its own unique configuration and
ROOT output files.

Features:
- Reads input job YAMLs (process info, file lists, cross section, etc.)
- Injects values into a Key4hep options template
- Adds myalg parameters including cross-section, n_events, processName, processID,
  targetLumi, and a unique myalg.root_output_file
- Ensures unique output ROOT filenames for parallel job safety
- Creates corresponding Condor job submission scripts (.sh and .sub)
- Produces both a master logfile (with timestamp) and per-job Condor logs
"""

import os
import re
import yaml
import logging
import datetime
from pathlib import Path

# -----------------------------
# User-configurable parameters
# -----------------------------

# Base directory of the repo (script’s parent folder or git root)
BASE_DIR = Path(__file__).resolve().parent.parent  # adjust if script is in scripts/

EVTMAX = 3                # Max events per job
TARGETLUMINOSITY = 1000.0   # Target luminosity for myalg
YAML_DIR = BASE_DIR / "job_yamls"      # Directory with YAML job descriptions
TEMPLATE_FILE = "/afs/cern.ch/user/c/chensel/ILD/workarea/May2025/k4-project-template/k4ProjectTemplate/options/default_options_file.py"  # Options template
OUTPUT_DIR = BASE_DIR / "generated_jobs"              # Where all jobs will be written
EOS_OUTPUT_DIR = "root://eosuser.cern.ch//eos/home-c/chensel/ILC/KEY4HEP_OUTPUT/PILOT_MC_RUN" # the directory on eos


# -----------------------------
# Setup logging (master logfile with timestamp)
# -----------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOGFILE = f"generate_jobs_{timestamp}.log"

logging.basicConfig(
    filename=LOGFILE,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# Helpers
# -----------------------------
def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def generate_options_newtemplate(yaml_info, template_text, evtmax, target_lumi, job_num):
    """
    Generates a Key4hep options file:
    - Replaces files = [...] with YAML file list
    - Replaces EvtMax with evtmax
    - Adds myalg parameters from YAML and targetLumi
    - Ensures unique output.root and myalg.root_output_file
    """
    # Prepare files list
    files_list_str = ",\n    ".join(
        [f'"{yaml_info["path"]}/{f}"' for f in yaml_info["files"]]
    )
    files_assignment = f"files = [\n    {files_list_str}\n]\n"
    template_text = re.sub(r'files\s*=\s*\[.*?\]', files_assignment, template_text, flags=re.DOTALL)

    # Replace EvtMax
    template_text = re.sub(r'EvtMax\s*=\s*\d+', f"EvtMax={evtmax}", template_text)

    # Unique filenames
    root_filename = f"output_higgsTo_invisible_{yaml_info['process']}_{job_num}.root"
    myalg_root_filename = f"myalg_higgsTo_invisible_{yaml_info['process']}_{job_num}.root"

    template_text = re.sub(r'output\.filename\s*=.*', f"output.filename = '{root_filename}'", template_text)

    # myalg params
    myalg_lines = (
        f"myalg.cross_section = {yaml_info['cross_section_pb']}\n"
        f"myalg.n_events_generated = {yaml_info['n_events']}\n"
        f"myalg.processName = '{yaml_info['process']}'\n"
        f"myalg.processID = {yaml_info['process_id']}\n"
        f"myalg.targetLumi = {target_lumi}\n"
        f"myalg.root_output_file = '{myalg_root_filename}'\n"
    )
    template_text = re.sub(r'(myalg = HtoInvAlg\(\))', r'\1\n' + myalg_lines, template_text)

    return template_text

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def generate_run_script(options_file, job_dir):
    """Creates .sh run script for Condor"""
    run_script = f"""#!/bin/bash
echo "Starting job on $(date)"
echo "Running on host $(hostname)"
echo "Current directory: $(pwd)"

# --- Setup environment ---
source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2025-01-28
cd /afs/cern.ch/user/c/chensel/ILD/workarea/May2025/k4-project-template
source setup.sh

# --- Run job ---
cd {job_dir}
k4run {options_file}

# --- Copy output to EOS ---
for f in *.root; do
    echo "Copying ${{f}} to EOS: {EOS_OUTPUT_DIR}"
    xrdcp -f "$f" "{EOS_OUTPUT_DIR}/$f"
    if [ $? -eq 0 ]; then
        echo "Copy successful, removing local file $f"
        rm -f "$f"
    else
        echo "Copy failed for $f, keeping local copy"
    fi
done


echo "Job finished on $(date)"
"""
    script_path = Path(job_dir) / "run_job.sh"
    write_file(script_path, run_script)
    os.chmod(script_path, 0o755)
    return script_path

def generate_condor_sub(run_script, job_dir):
    """Creates .sub HTCondor submission file with resource requests"""

    run_script_abs = Path(run_script).resolve()

    sub_file = f"""universe   = vanilla
executable = {run_script_abs}
arguments  = 

output     = {Path(job_dir)/'job.out'}
error      = {Path(job_dir)/'job.err'}
log        = {Path(job_dir)/'job.log'}

# Resource requests
request_cpus   = 1
request_memory = 4000
request_disk   = 2GB
+MaxRuntime    = 43200  

queue
"""

    sub_path = Path(job_dir) / "job.sub"
    write_file(sub_path, sub_file)
    return sub_path



# -----------------------------
# Main
# -----------------------------
def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    template_text = Path(TEMPLATE_FILE).read_text()

    yaml_files = list(Path(YAML_DIR).glob("*.yaml"))
    if not yaml_files:
        logging.error("No YAML files found.")
        print("No YAML files found. Exiting.")
        return

    logging.info(f"Found {len(yaml_files)} job YAMLs.")

    for yaml_file in yaml_files:
        try:
            info = load_yaml(yaml_file)
            job_name = Path(yaml_file).stem
            job_dir = Path(OUTPUT_DIR) / job_name
            job_dir.mkdir(exist_ok=True)

            options_filename = f"higgsTo_invisible_{info['process']}_{job_name.split('_')[-1]}.py"
            options_path = job_dir / options_filename

            options_text = generate_options_newtemplate(info, template_text, EVTMAX, TARGETLUMINOSITY, job_name.split('_')[-1])
            write_file(options_path, options_text)

            run_script = generate_run_script(options_path, job_dir)
            generate_condor_sub(run_script, job_dir)

            logging.info(f"Generated job {job_name} -> {options_filename}")
        except Exception as e:
            logging.error(f"Failed to process {yaml_file}: {e}")

    logging.info("All jobs generated successfully.")
    
    # ✅ Print the master logfile path
    master_log_path = Path(LOGFILE).resolve()
    print(f"\nAll jobs generated. Master logfile: {master_log_path}")


if __name__ == "__main__":
    main()
