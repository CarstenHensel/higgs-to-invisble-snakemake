rule make_summary:
    """
    Step 10: Create final summary.
    """
    input:
        config["paths"]["plots"]
    output:
        "summary.txt",
        directory(config["paths"]["summary"])
    run:
        # Separate outputs
        summary_file = str(output[0])
        summary_dir = str(output[1])

        # Choose script based on mode
        script_name = 'summary_dummy.py' if config.get('mode') == 'dummy' else 'summary.py'

        print(f"Running script: {script_name} {input} {summary_dir}")

        if config.get('mode') == 'dummy':
            # In dummy mode, just create placeholder files
            import pathlib
            pathlib.Path(summary_file).touch()
            pathlib.Path(summary_dir).mkdir(parents=True, exist_ok=True)
        else:
            # Run real script
            shell(f"python scripts/{script_name} {input} {summary_dir}")
