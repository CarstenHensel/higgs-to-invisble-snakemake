import sys
input_dir = sys.argv[1]
output_file = sys.argv[2]

print(f"[DUMMY] Extracting production IDs from {input_dir} -> {output_file}")

with open(output_file, "w") as f:
    f.write("PROD1\nPROD2\nPROD3\n")
