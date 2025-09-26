import sys, os
input_file = sys.argv[1]
output_dir = sys.argv[2]

print(f"[DUMMY] Generating HTCondor job YAMLs from {input_file} -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

for i in range(3):
    with open(os.path.join(output_dir, f"job_{i}.yaml"), "w") as f:
        f.write(f"name: job_{i}\ninput: dummy\n")
