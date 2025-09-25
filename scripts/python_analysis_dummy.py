#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "histograms.root"), "w") as f:
        f.write("# Dummy histograms\n")

    print(f"[python_analysis_dummy] created dummy histograms in {output_dir}")
