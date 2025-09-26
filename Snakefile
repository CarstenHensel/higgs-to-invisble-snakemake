# ============================
# Snakefile for Higgs→Invisible analysis
# ============================

import pathlib
from snakemake.shell import shell

# ----------------------------
# Load configuration
# ----------------------------
configfile: "config.yaml"

# ----------------------------
# Centralized helper
# ----------------------------
def dummy_or_real(output, cmd):
    """
    Run command in 'real' mode, or just touch outputs in 'dummy' mode.
    """
    if config.get("mode") == "dummy":
        for f in (output if isinstance(output, list) or isinstance(output, tuple) else [output]):
            # handle directories vs files
            p = pathlib.Path(str(f))
            if str(f).endswith("/"):  # crude dir detection
                p.mkdir(parents=True, exist_ok=True)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
    else:
        shell(cmd)

# ----------------------------
# Include all rule files
# ----------------------------
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

# ----------------------------
# Final target
# ----------------------------
rule all:
    input:
        "summary.txt"
