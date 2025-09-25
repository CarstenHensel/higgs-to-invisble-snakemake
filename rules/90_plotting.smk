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
        for f in {input}/*.root; do
            sample=$(basename $f _histos.root)
            python scripts/make_plots.py $f {output}/$sample_summary.pdf
        done
        """
