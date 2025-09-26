rule lfn_selector:
    """
    Step 1: Select relevant LFNs from the master list.
    """
    input:
        config["paths"]["master_lfn_list"]
    output:
        config["paths"]["lfn_list"]
    run:
        input_file = str(input)
        output_file = str(output)
        script_name = 'lfn_selector_dummy.py' if config['mode']=='dummy' else 'lfn_selector.py'
        print(f"Running script: {script_name} {input_file} {output_file}")
        shell(f"python scripts/{script_name} {input_file} {output_file}")
