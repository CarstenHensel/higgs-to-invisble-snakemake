rule run_key4hep:
    """
    Step 7: Run Key4hep analysis (HTCondor submission).
    """
    input:
        config["paths"]["converted_dir"],    # data files to analyze
        config["paths"]["key4hep_dir"]       # HTCondor / Key4hep options
    output:
        directory(config["paths"]["analysis_output"])
    shell:
        """
        mkdir -p {output}
        # This would submit jobs to HTCondor in real workflow
        ### TODO: add corrct script for the 'real' mode
        python scripts/{'key4hep_analysis_dummy.py' if config['mode']=='dummy' else '<real>.py'} {input} {output}
        done
        """
