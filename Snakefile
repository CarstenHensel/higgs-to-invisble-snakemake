import yaml
import os

# Load config
configfile: "config.yaml"

# Include all rule files
for rule_file in glob.glob("rules/*.smk"):
    include: rule_file


conversion_target = f"{config['slcio_path']}/.conversion_done"
mc_targets = ["mc_metadata.yaml", "job_yamls"]

rule all:
    input:
        conversion_target,
        *mc_targets

