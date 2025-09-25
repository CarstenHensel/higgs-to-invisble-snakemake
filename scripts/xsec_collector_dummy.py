#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write("# Dummy MC cross-sections\nprod_001: 123 pb\nprod_002: 456 pb\n")

    print(f"[xsec_collector_dummy] wrote dummy xsec data to {output_file}")
