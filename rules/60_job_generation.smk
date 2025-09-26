rule generate_job_yaml:
    """
    Step 6a: Generate HTCondor job YAML files.
    """
    input:
        config["paths"]["mc_xsec_yaml"]
    output:
        directory(config["paths"]["job_yaml_dir"])
    run:
        input_file = str(input)
        output_dir = str(output)
        script_name = 'job_gen_dummy.py' if config['mode']=='dummy' else 'generate_job_yamls.py'
        print(f"Running script: {script_name} {input_file} {output_dir}")
        shell(f"python scripts/{script_name} {input_file} {output_dir}")

rule generate_key4hep_options:
    """
    Step 6b: Generate Key4hep option files and HTCondor submission scripts.
    """
    input:
        config["paths"]["mc_xsec_yaml"]
    output:
        directory(config["paths"]["key4hep_dir"])
    run:
        input_file = str(input)
        output_dir = str(output)
        script_name = 'key4hep_condor_dummy.py' if config['mode']=='dummy' else 'generate_key4hep_options_and_htcondor.py'
        print(f"Running script: {script_name} {input_file} {output_dir}")
        shell(f"python scripts/{script_name} {input_file} {output_dir}")


