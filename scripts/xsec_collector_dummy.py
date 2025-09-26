import sys, yaml
input_file = sys.argv[1]
output_file = sys.argv[2]

print(f"[DUMMY] Collecting MC cross-sections from {input_file} -> {output_file}")

mc_data = {
    "PROD1": {"xsec": 1.0, "nevents": 1000},
    "PROD2": {"xsec": 0.5, "nevents": 2000},
    "PROD3": {"xsec": 2.0, "nevents": 1500},
}

with open(output_file, "w") as f:
    yaml.dump(mc_data, f)
