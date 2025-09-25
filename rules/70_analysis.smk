rule run_key4hep:
    """
    Step 7: Run Key4hep analysis (HTCondor submission).
    """
    input:
        directory(config["paths"]["processed_data"]),
        "config/key4hep_options/"
    output:
        directory(config["paths"]["key4hep_output"])
    shell:
        """
        mkdir -p {output}
        # This would submit jobs to HTCondor in real workflow
        for f in {input[0]}/*.slcio; do
            sample=$(basename $f .slcio)
            python scripts/run_key4hep.py $f {output}/$sample_analysis.root
        done
        """
