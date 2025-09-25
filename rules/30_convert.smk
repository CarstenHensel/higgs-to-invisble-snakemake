rule convert_lcio:
    """
    Step 3: Convert fetched ROOT files to LCIO format.
    """
    input:
        directory(config["paths"]["preprocess_dir"])
    output:
        directory(config["paths"]["processed_data"])
    shell:
        """
        mkdir -p {output}
        python scripts/{'convert_dummy.py' if config['mode']=='dummy' else 'slcio2edm4hep_validate_crawler.py'} {input} {output}
        done
        """
