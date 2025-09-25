rule final_summary:
    """
    Step 10: Aggregate all plots and results.
    """
    input:
        directory(config["paths"]["plots"])
    output:
        "{path}/final_summary.txt".format(path=config["paths"]["summary"])
    shell:
        """
        mkdir -p {config[paths][summary]}
        # TODO: add correct script name for 'real' mode.
        python scripts/{'summary_dummy.py' if config['mode']=='dummy' else '<real>.py'} {input} {output}
        """
