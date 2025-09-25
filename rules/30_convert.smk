rule convert_lcio:
    """
    Step 3: Convert LCIO to EDM4hep format.
    """
    input:
        config["paths"]["preprocess_dir"]
    output:
        directory(config["paths"]["converted_dir"])
    run:
        input_dir = str(input)
        output_dir = str(output)
        script_name = 'convert_dummy.py' if config['mode']=='dummy' else 'slcio2edm4hep_validate_crawler.py'
        print(f"Running script: {script_name} {input_dir} {output_dir}")
        shell(f"python scripts/{script_name} {input_dir} {output_dir}")

