rule convert_lcio:
    """
    Step 3: Convert fetched ROOT files to LCIO format.
    """
    input:
        config["paths"]["preprocess_dir"]   # no directory() for input
    output:
        directory(config["paths"]["converted_dir"])
    shell:    
        """
        mkdir -p {output}
        python scripts/{'convert_dummy.py' if config['mode']=='dummy' else 'slcio2edm4hep_validate_crawler.py'} {input} {output}
        done
        """
