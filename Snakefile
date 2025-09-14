import yaml
import os

# Load config
configfile: "config.yaml"



include: "rules/slcio_convert.smk"


rule all:
    input:
        # a marker file showing conversion finished
        f"{config['slcio_path']}/.conversion_done"


