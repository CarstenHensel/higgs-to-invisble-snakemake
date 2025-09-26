import sys, os
input_file = sys.argv[1]
output_dir = sys.argv[2]

print(f"[DUMMY] Generating Key4hep options and HTCondor scripts from {input_file} -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

for i in range(3):
    with open(os.path.join(output_dir, f"key4hep_{i}.txt"), "w") as f:
        f.write("option: dummy\n")
