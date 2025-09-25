rule make_summary:
    """
    Step 10: Create final summary.
    """
    input:
        config["paths"]["plots"]
    output:
        directory(config["paths"]["summary"])
    run:
        input_dir = str(input)
        output_dir = str(output)
        script_name = 'summary_dummy.py' if config['mode']=='dummy' else 'summary.py'
        print(f"Running script: {script_name} {input_dir} {output_dir}")
        shell(f"python scripts/{script_name} {input_dir} {output_dir}")


