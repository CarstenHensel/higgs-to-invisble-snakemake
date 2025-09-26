import sys, os
input_file = sys.argv[1]
output_dir = sys.argv[2]

print(f"[DUMMY] Preprocessing LFNs from {input_file} -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "dummy_preprocessed.txt"), "w") as f:
    f.write("dummy_data\n")
