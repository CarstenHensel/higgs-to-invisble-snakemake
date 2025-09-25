rule generate_plots:
    """
    Step 9: Generate plots from Python analysis.
    """
    input:
        config["paths"]["analysis_output"]
    output:
        directory(config["paths"]["plots"])
    run:
        input_dir = str(input)
        output_dir = str(output)
        script_name = 'plotting_dummy.py' if config['mode']=='dummy' else 'plotting.py'
        print(f"Running script: {script_name} {input_dir} {output_dir}")
        shell(f"python scripts/{script_name} {input_dir} {output_dir}")

