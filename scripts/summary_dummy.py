#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "summary.txt"), "w") as f:
        f.write("# Dummy summary report\n")

    print(f"[summary_dummy] created dummy summary in {output_dir}")
