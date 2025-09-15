# rules/generate_job_yamls.smk

rule generate_job_yamls:
    """
    Read mc_metadata.yaml and split files into per-job YAMLs.
    """
    input:
        meta="mc_metadata.yaml"
    output:
        directory("job_yamls")
    log:
        "logs/generate_job_yamls.log"
    shell:
        """
        mkdir -p logs job_yamls
        python3 scripts/generate_job_yamls.py > {log} 2>&1
        """

