rule preprocess_fetch:
    """
    Step 2: Preprocess LFNs.
    """
    input:
        config["paths"]["lfn_list"]
    output:
        directory(config["paths"]["preprocess_dir"])
    run:
        input_file = str(input)
        output_dir = str(output)
        script_name = 'preprocess_dummy.py' if config['mode']=='dummy' else 'preprocess.py'
        print(f"Running script: {script_name} {input_file} {output_dir}")
        shell(f"python scripts/{script_name} {input_file} {output_dir}")

