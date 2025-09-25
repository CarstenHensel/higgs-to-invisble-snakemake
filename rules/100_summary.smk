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
        python scripts/final_summary.py {input} {output}
        """
