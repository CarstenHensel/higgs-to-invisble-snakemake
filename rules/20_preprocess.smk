rule preprocess_fetch:
    """
    Step 2: Download MC files from selected LFNs.
    """
    input:
        "config/lfns_selected.txt"
    output:
        directory(config["paths"]["raw_data"])
    shell:
        """
        mkdir -p {output}
        while read lfn; do
            sample=$(basename $lfn .slcio)
            bash scripts/fetch_mc.sh $sample {output}
        done < {input}
        """
