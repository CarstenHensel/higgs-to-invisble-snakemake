#!/usr/bin/env python3
import sys, os

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "plot1.png"), "w") as f:
        f.write("# Dummy plot image\n")

    print(f"[plotting_dummy] created dummy plot in {output_dir}")
