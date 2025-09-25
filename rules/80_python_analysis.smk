rule run_python_analysis:
    """
    Step 8: Run Python analysis to produce histogram/cutflow ROOT files.
    """
    input:
        directory(config["paths"]["key4hep_output"])
    output:
        directory(config["paths"]["analysis_output"])
    shell:
        """
        mkdir -p {output}
        ### TODO: add correct script for 'real' mode
        python scripts/{'python_analysis_dummy.py' if config['mode']=='dummy' else '<real>.py'} {input} {output}
        done
        """
