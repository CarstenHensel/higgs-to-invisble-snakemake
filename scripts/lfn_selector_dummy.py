import sys
input_file = sys.argv[1]
output_file = sys.argv[2]

print(f"[DUMMY] Selecting LFNs from {input_file} -> {output_file}")

with open(output_file, "w") as f:
    f.write("LFN1\nLFN2\nLFN3\n")
