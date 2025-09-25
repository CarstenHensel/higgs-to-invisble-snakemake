rule make_plots:
    """
    Step 9: Generate plots from Python analysis outputs.
    """
    input:
        directory(config["paths"]["analysis_output"])
    output:
        directory(config["paths"]["plots"])
    shell:
        """
        mkdir -p {output}
        # TODO: add correct script name for 'real' mode
        python scripts/{'plotting_dummy.py' if config['mode']=='dummy' else '<real>.py'} {input} {output}
        done
        """
