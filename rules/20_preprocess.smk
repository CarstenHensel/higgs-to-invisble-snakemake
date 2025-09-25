rule preprocess_fetch:
    """
    Step 2: Download MC files from selected LFNs.
    """
    input:
        "config/lfns_selected.txt"
    output:
        directory(config["paths"]["preprocess_dir"])
    shell:
        """
        mkdir -p {output}
        python scripts/{'preprocess_dummy.py' if config['mode']=='dummy' else '<real>.py'} {input} {output}
        done < {input}
        """
