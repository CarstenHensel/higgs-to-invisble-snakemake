rule run_python_analysis:
    """
    Step 8: Run Python analysis to produce histograms/cutflows
    """
    input:
        key4hep_output=config["paths"]["key4hep_output"]
    output:
        python_analysis_output=directory(config["paths"]["python_analysis_output"])
    run:
        output_dir = str(output.python_analysis_output)
        input_dir = str(input.key4hep_output)

        script_name = 'python_analysis_dummy.py' if config['mode']=='dummy' else 'python_analysis.py'
        print(f"Running script: {script_name} {input_dir} {output_dir}")

        if config['mode'] == 'dummy':
            import pathlib
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            shell(f"python scripts/{script_name} {input_dir} {output_dir}")
