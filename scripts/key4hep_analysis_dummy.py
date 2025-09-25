#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "analysis_results.root"), "w") as f:
        f.write("# Dummy Key4hep analysis output\n")

    print(f"[key4hep_analysis_dummy] created dummy analysis file in {output_dir}")
