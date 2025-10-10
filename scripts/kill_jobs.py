#!/usr/bin/env python3
import re
import subprocess

# Path to your file containing the submitted job IDs
input_file = "job_ids.txt"

# Regular expression to extract all numeric job IDs inside [ ]
job_id_pattern = re.compile(r"\[(.*?)\]")

# Collect all job IDs
job_ids = []
with open(input_file) as f:
    for line in f:
        matches = job_id_pattern.findall(line)
        for match in matches:
            job_ids.extend(re.findall(r"\d+", match))

print(f"Found {len(job_ids)} jobs to kill.")

# Loop and kill each job
for job_id in job_ids:
    print(f"Killing job {job_id} ...")
    subprocess.run(["dirac-wms-job-kill", job_id])

print("All listed jobs have been killed (or attempted).")
