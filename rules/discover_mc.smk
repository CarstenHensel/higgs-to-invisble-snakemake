# rules/discover_mc.smk

rule discover_mc:
    """
    Discover MC processes in ROOT_DIR and generate master metadata YAML.
    """
    output:
        meta="mc_metadata.yaml"
    log:
        "logs/discover_mc.log"
    shell:
        """
        mkdir -p logs
        python3 scripts/discover_mc_processes.py > {log} 2>&1
        """
