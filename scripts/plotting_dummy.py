import sys, os
input_dir = sys.argv[1]
output_dir = sys.argv[2]

print(f"[DUMMY] Creating plots from {input_dir} -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "plot_dummy.png"), "w") as f:
    f.write("dummy plot image\n")
