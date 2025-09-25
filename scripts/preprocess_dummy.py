#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "fetched_file.root"), "w") as f:
        f.write("# Dummy fetched ROOT file\n")

    print(f"[preprocess_dummy] created dummy fetched file in {output_dir}")
