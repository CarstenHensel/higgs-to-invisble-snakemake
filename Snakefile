import yaml
import os
import glob

# Load config
configfile: "config.yaml"

# Include all rule files
for rule_file in glob.glob("rules/*.smk"):
    include: rule_file

include: "rules/10_lfn_selector.smk"
include: "rules/20_preprocess.smk"
include: "rules/30_convert.smk"
include: "rules/40_extract_ids.smk"
include: "rules/50_xsec_collector.smk"
include: "rules/60_job_generation.smk"
include: "rules/70_analysis.smk"
include: "rules/80_python_analysis.smk"
include: "rules/90_plotting.smk"
include: "rules/100_summary.smk" 

conversion_target = f"{config['slcio_path']}/.conversion_done"
mc_targets = ["mc_metadata.yaml", "job_yamls"]

rule all:
    input:
        "xsecs.yaml",
        conversion_target,
        *mc_targets

