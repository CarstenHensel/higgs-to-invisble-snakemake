import yaml
import os

# Load config
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

# Convert LCIO -> EDM4hep
rule convert:
    input:
        lambda wildcards: cfg['datasets'][wildcards.dataset]['path']
    output:
        "edm4hep/{dataset}.root"
    params:
        script = cfg['transformations']['convert']['script']
    shell:
        "python {params.script} {input} {output}"

# Run analysis
rule analyze:
    input:
        "edm4hep/{dataset}.root"
    output:
        "ntuples/{dataset}.root"
    params:
        script = cfg['transformations']['analysis']['script']
    shell:
        "python {params.script} {input} {output}"

# Optional: Add plotting or validation steps here
# rule plot:
#     input:
#         "ntuples/{dataset}.root"
#     output:
#         "plots/{dataset}.pdf"
#     shell:
#         "python scripts/plot_analysis.py {input} {output}"

# Final target
rule all:
    input:
        expand("ntuples/{dataset}.root", dataset=cfg['datasets'].keys())
        # For plots: expand("plots/{dataset}.pdf", dataset=cfg['datasets'].keys())
