rule run_plotting:
    """
    Step 9: Create plots from Python analysis
    """
    input:
        python_analysis_output=config["paths"]["python_analysis_output"]
    output:
        plots=directory(config["paths"]["plots"])
    run:
        output_dir = str(output.plots)
        input_dir = str(input.python_analysis_output)

        script_name = 'plotting_dummy.py' if config['mode']=='dummy' else 'plotting.py'
        print(f"Running script: {script_name} {input_dir} {output_dir}")

        if config['mode'] == 'dummy':
            import pathlib
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            shell(f"python scripts/{script_name} {input_dir} {output_dir}")
