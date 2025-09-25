rule generate_condor_jobs:
    """
    Step 6: Generate condor job yamls and Key4hep option files.
    """
    input:
        "config/master_mc.yaml"
    output:
        "config/condor_jobs/",
        "config/key4hep_options/"
    shell:
        """
        mkdir -p {output}
        python scripts/generate_job_yamls.py {input} config/condor_jobs/
        python scripts/generate_key4hep_options_and_htcondor.py {input} config/key4hep_options/
        """
