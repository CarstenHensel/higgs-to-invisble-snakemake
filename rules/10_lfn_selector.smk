rule create_lfn_list:
    """
    Step 1: Create filtered LFN list from master list (all_files.txt).
    Previously called 'full_pilot_selection.py' → rename to 'lfn_selector.py'.
    """
    input:
        "all_files.txt"
    output:
        "config/lfns_selected.txt"
    shell:
        """
        python scripts/{'lfn_selector_dummy.py' if config['mode']=='dummy' else 'lfn_selector.py'} {input} {output}        
        """
