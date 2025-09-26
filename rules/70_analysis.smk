rule run_key4hep:
    """
    Step 7: Run Key4hep analysis (HTCondor submission)
    """
    input:
        converted=config["paths"]["converted_dir"],
        key4hep_config=config["paths"]["key4hep_dir"]
    output:
        key4hep_output=directory(config["paths"]["key4hep_output"])
    run:
        output_dir = str(output.key4hep_output)
        input_files = f"{input.converted} {input.key4hep_config}"

        script_name = 'key4hep_analysis_dummy.py' if config['mode']=='dummy' else 'key4hep_analysis.py'
        print(f"Running script: {script_name} {input_files} {output_dir}")

        if config['mode'] == 'dummy':
            import pathlib
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            shell(f"python scripts/{script_name} {input_files} {output_dir}")
