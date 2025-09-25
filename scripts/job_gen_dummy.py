#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_file = sys.argv[1]
    job_dir = sys.argv[2]
    key4hep_dir = sys.argv[3]

    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(key4hep_dir, exist_ok=True)

    with open(os.path.join(job_dir, "job1.yaml"), "w") as f:
        f.write("# Dummy Condor job yaml\n")
    with open(os.path.join(key4hep_dir, "job1.opts"), "w") as f:
        f.write("# Dummy Key4hep options\n")

    print(f"[job_gen_dummy] created dummy jobs in {job_dir} and {key4hep_dir}")
