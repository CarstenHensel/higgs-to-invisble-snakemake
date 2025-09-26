rule extract_prod_ids:
    """
    Step 4: Extract unique production IDs from LFN list.
    """
    input:
        config["paths"]["converted_dir"]
    output:
        config["paths"]["prod_ids"]
    run:
        input_dir = str(input)
        output_file = str(output)
        script_name = 'extract_ids_dummy.py' if config['mode']=='dummy' else 'extract_ids.py'
        print(f"Running script: {script_name} {input_dir} {output_file}")
        shell(f"python scripts/{script_name} {input_dir} {output_file}")

