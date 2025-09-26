import sys, os
input_files = sys.argv[1:-1]
output_dir = sys.argv[-1]

print(f"[DUMMY] Running Key4hep analysis on {input_files} -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "analysis_dummy.txt"), "w") as f:
    f.write("key4hep analysis dummy output\n")
