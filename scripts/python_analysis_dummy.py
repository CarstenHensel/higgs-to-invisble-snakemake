import sys, os
input_files = sys.argv[1:-1]
output_dir = sys.argv[-1]

print(f"[DUMMY] Running Python analysis on {input_files} -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "python_analysis_dummy.root"), "w") as f:
    f.write("dummy ROOT histogram data\n")
