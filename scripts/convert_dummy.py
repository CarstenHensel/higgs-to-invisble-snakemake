#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "converted_file.root"), "w") as f:
        f.write("# Dummy converted ROOT file\n")

    print(f"[convert_dummy] created dummy converted file in {output_dir}")
