#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write("# Dummy LFN list\nlfn_001\nlfn_002\nlfn_003\n")

    print(f"[lfn_selector_dummy] wrote dummy LFN list to {output_file}")
