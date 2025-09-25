rule run_python_analysis:
    """
    Step 8: Run Python analysis to produce histogram/cutflow ROOT files.
    """
    input:
        config["paths"]["converted_dir"],
        config["paths"]["key4hep_dir"]
    output:
        directory(config["paths"]["analysis_output"])
    run:
        input_files = " ".join(input) if isinstance(input, list) else str(input)
        output_dir = str(output)
        script_name = 'python_analysis_dummy.py' if config['mode']=='dummy' else 'python_analysis.py'
        print(f"Running script: {script_name} {input_files} {output_dir}")
        shell(f"python scripts/{script_name} {input_files} {output_dir}")

