rule convert_lcio:
    """
    Step 3: Convert fetched ROOT files to LCIO format.
    """
    input:
        directory(config["paths"]["raw_data"])
    output:
        directory(config["paths"]["processed_data"])
    shell:
        """
        mkdir -p {output}
        for f in {input}/*.root; do
            sample=$(basename $f .root)
            bash scripts/convert_lcio.sh $f {output}/$sample.slcio
        done
        """
