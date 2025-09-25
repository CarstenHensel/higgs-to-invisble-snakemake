rule xsec_collector:
    """
    Step 5: Query cross-sections + event counts using prod IDs.
    Produces a master MC metadata YAML file.
    """
    input:
        "config/prod_ids.txt"
    output:
        "config/master_mc.yaml"
    shell:
        """
        python scripts/{'xsec_collector_dummy.py' if config['mode']=='dummy' else 'ilc_xsec_collector.py'} {input} {output}
        """
