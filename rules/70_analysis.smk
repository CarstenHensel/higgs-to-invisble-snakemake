rule run_key4hep:
    """
    Step 7: Run Key4hep analysis (HTCondor submission).
    """
    input:
        config["paths"]["converted_dir"],
        config["paths"]["key4hep_dir"]
    output:
        directory(config["paths"]["analysis_output"])
    run:
        input_files = " ".join(input) if isinstance(input, list) else str(input)
        output_dir = str(output)
        script_name = 'key4hep_analysis_dummy.py' if config['mode']=='dummy' else 'key4hep_analysis.py'
        print(f"Running script: {script_name} {input_files} {output_dir}")
        shell(f"python scripts/{script_name} {input_files} {output_dir}")


