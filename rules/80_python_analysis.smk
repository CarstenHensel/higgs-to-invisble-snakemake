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
        for f in {input}/*.root; do
            sample=$(basename $f _analysis.root)
            python scripts/python_analysis.py $f {output}/$sample_histos.root
        done
        """
