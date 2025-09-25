rule run_python_analysis:
    """
    Step 8: Run Python analysis to produce histogram/cutflow ROOT files.
    """
    input:
        config["paths"]["converted_dir"],  # converted LCIO/ROOT files
        config["paths"]["key4hep_dir"]     # Key4hep option files
    output:
        directory(config["paths"]["analysis_output"])
    shell:
        """
        mkdir -p {output}
        # Dummy/real switch
        python scripts/{'python_analysis_dummy.py' if config['mode']=='dummy' else 'python_analysis.py'} {input} {output}
        """
