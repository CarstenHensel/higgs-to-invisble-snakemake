rule extract_prod_ids:
    """
    Step 3: Extract unique production IDs from LCIO LFNs.
    """
    input:
        "config/lfns_selected.txt"
    output:
        "config/prod_ids.txt"
    shell:
        """
        python scripts/extract_prod_ids.py {input} {output}
        """
