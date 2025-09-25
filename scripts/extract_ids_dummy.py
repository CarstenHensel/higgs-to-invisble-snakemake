#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write("# Dummy production IDs\nprod_001\nprod_002\n")

    print(f"[extract_ids_dummy] wrote dummy production IDs to {output_file}")
