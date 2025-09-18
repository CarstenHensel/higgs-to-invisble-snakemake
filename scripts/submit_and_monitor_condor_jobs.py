#!/usr/bin/env python3
"""
submit_and_monitor_condor_jobs.py

Script to submit all HTCondor job scripts in the generated_jobs directory,
capture their Condor job IDs, and provide a live status summary.
"""

import subprocess
from pathlib import Path
import datetime
import time

# -----------------------------
# User-configurable parameters
# -----------------------------
GENERATED_JOBS_DIR = Path("generated_jobs")
SUMMARY_LOGFILE = Path(f"condor_submission_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
CHECK_QUEUE = True           # If True, queries condor_q after submission
SLEEP_BETWEEN_CHECKS = 10    # Seconds to wait between queue checks (optional)

# -----------------------------
# Helper functions
# -----------------------------
def submit_job(sub_file):
    """Submit a single .sub job and return the Condor cluster ID"""
    try:
        result = subprocess.run(
            ["condor_submit", str(sub_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        job_id = "Unknown"
        for line in result.stdout.splitlines():
            if "submitted to cluster" in line:
                job_id = line.strip().split()[-1].replace(".", "")
                break
        return job_id, result.stdout
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()

def query_condor_status(job_id):
    """Query condor_q for a given job ID and return status"""
    try:
        result = subprocess.run(
            ["condor_q", job_id, "-format", "%s\n", "JobStatus"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        status_map = {
            "1": "Idle",
            "2": "Running",
            "3": "Removed",
            "4": "Completed",
            "5": "Held",
            "6": "Transferring Output",
            "7": "Suspended"
        }
        status_code = result.stdout.strip()
        return status_map.get(status_code, f"Unknown({status_code})")
    except subprocess.CalledProcessError:
        return "NotInQueue"

# -----------------------------
# Main
# -----------------------------
def main():
    if not GENERATED_JOBS_DIR.exists():
        print(f"Error: {GENERATED_JOBS_DIR} does not exist.")
        return

    summary_lines = []
    summary_lines.append(f"{'Job Name':<30} | {'Job Dir':<80} | {'Condor Job ID':<12} | {'Status'}")
    summary_lines.append("-" * 140)

    submitted_jobs = {}

    # Submit all jobs
    for job_dir in sorted(GENERATED_JOBS_DIR.iterdir()):
        if job_dir.is_dir():
            sub_file = job_dir / "job.sub"
            if sub_file.exists():
                job_id, output = submit_job(sub_file)
                if job_id:
                    print(f"Submitted {job_dir.name} -> Condor job ID {job_id}")
                    submitted_jobs[job_dir.name] = {"dir": str(job_dir), "job_id": job_id}
                else:
                    print(f"Failed to submit {job_dir.name}: {output}")
            else:
                print(f"No .sub file found in {job_dir}, skipping.")

    # Query queue for job status
    if CHECK_QUEUE and submitted_jobs:
        print("\nChecking Condor queue status...")
        for job_name, info in submitted_jobs.items():
            status = query_condor_status(info["job_id"])
            summary_lines.append(f"{job_name:<30} | {info['dir']:<80} | {info['job_id']:<12} | {status}")
            print(f"{job_name:<30} | Job ID {info['job_id']} | Status: {status}")

    # Write summary to logfile
    SUMMARY_LOGFILE.write_text("\n".join(summary_lines))
    print(f"\nSubmission summary written to {SUMMARY_LOGFILE}")

if __name__ == "__main__":
    main()
