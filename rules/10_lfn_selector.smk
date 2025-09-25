rule create_lfn_list:
    """
    Step 0: Create filtered LFN list from master list (all_files.txt).
    Previously called 'full_pilot_selection.py' → rename to 'lfn_selector.py'.
    """
    input:
        "all_files.txt"
    output:
        "config/lfns_selected.txt"
    shell:
        """
        python scripts/lfn_selector.py {input} {output}
        """
