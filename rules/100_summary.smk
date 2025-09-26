rule make_summary:
    """
    Step 10: Create final summary tables/reports
    """
    input:
        plots=config["paths"]["plots"]
    output:
        summary_file="summary.txt",
        summary_dir=directory(config["paths"]["summary"])
    run:
        output_dir = str(output.summary_dir)
        input_dir = str(input.plots)
        script_name = 'summary_dummy.py' if config['mode']=='dummy' else 'summary.py'

        print(f"Running script: {script_name} {input_dir} {output_dir}")

        if config['mode'] == 'dummy':
            import pathlib
            pathlib.Path(output.summary_file).touch()
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            shell(f"python scripts/{script_name} {input_dir} {output_dir}")
