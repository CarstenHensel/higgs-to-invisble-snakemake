rule collect_xsec:
    """
    Step 5: Query cross-sections and number of events for MC productions.
    """
    input:
        config["paths"]["prod_ids"]
    output:
        config["paths"]["mc_xsec_yaml"]
    run:
        input_file = str(input)
        output_file = str(output)
        script_name = 'xsec_collector_dummy.py' if config['mode']=='dummy' else 'ilc_xsec_collector.py'
        print(f"Running script: {script_name} {input_file} {output_file}")
        shell(f"python scripts/{script_name} {input_file} {output_file}")

